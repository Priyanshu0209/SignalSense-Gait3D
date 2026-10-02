import asyncio
import logging
from datetime import datetime, timezone
from app.db.session import AsyncSessionLocal
from app.schemas.processing import ProcessedDeviceState
from app.models.domain import RSSIHistoryModel, EventModel, DeviceModel
from sqlalchemy.future import select

logger = logging.getLogger("signalsense.services.database")

class DatabaseService:
    @staticmethod
    async def save_device_update(state: ProcessedDeviceState):

        async with AsyncSessionLocal() as session:
            try:
                from app.services.diagnostics.diagnostics_logger import get_diagnostics_logger
                logger_service = get_diagnostics_logger()
                logger_service.log_database_layer(
                    state.mac_address,
                    state.current_rssi,
                    f"Saving to SQLite. Manufacturer: {state.manufacturer}"
                )
                
                result = await session.execute(select(DeviceModel).filter(DeviceModel.mac_address == state.mac_address))
                device = result.scalars().first()
                
                db_op = "UPDATE" if device else "INSERT"
                
                try:
                    from app.services.diagnostics.database_verification import get_database_verification_service
                    db_verifier = get_database_verification_service()
                    if not db_verifier._running:
                        await db_verifier.start()
                    import time
                    import uuid
                    op_start_time = time.time()
                except ImportError:
                    db_verifier = None
                    
                if not device:
                    device = DeviceModel(
                        mac_address=state.mac_address,
                        first_seen=datetime.now(timezone.utc)
                    )
                    session.add(device)
                else:
                    # Create copy of old device for verification
                    class MockCopy: pass
                    device_old_copy = MockCopy()
                    for attr in ["hostname", "ip_address", "manufacturer", "device_type", "last_seen", "current_status"]:
                        setattr(device_old_copy, attr, getattr(device, attr, None))
                
                
                device.hostname = state.hostname
                device.ip_address = state.ip_address
                device.manufacturer = state.manufacturer
                device.device_type = state.device_type
                device.last_seen = state.last_seen
                device.current_status = "online" if state.online_status else "offline"
                
                if db_verifier:
                    # Log field changes
                    fields_to_check = {
                        "hostname": state.hostname,
                        "ip_address": state.ip_address,
                        "manufacturer": state.manufacturer,
                        "device_type": state.device_type,
                        "current_status": "online" if state.online_status else "offline"
                    }
                    for fname, fnew in fields_to_check.items():
                        fold = getattr(device_old_copy, fname, None) if 'device_old_copy' in locals() else None
                        validation_result = "PASS"
                        if fold is not None and fold != "Unknown" and fnew is None:
                            validation_result = "NULL_OVERWRITE"
                        elif fold is not None and fold != fnew and fname == "mac_address":
                            validation_result = "UNEXPECTED_OVERWRITE"
                            
                        if validation_result != "PASS" or db_op == "INSERT":
                            db_verifier.log_verification({
                                "Timestamp": datetime.now(timezone.utc).isoformat(),
                                "Discovery Scan ID": "unknown", # Normally passed via context, using unknown for now
                                "Correlation ID": "unknown",
                                "Database Operation": db_op,
                                "Table": "devices",
                                "Primary Key": device.id if hasattr(device, 'id') else "unknown",
                                "MAC Address": state.mac_address,
                                "Field Name": fname,
                                "Value Before": fold if fold is not None else "N/A",
                                "Value After": fnew if fnew is not None else "N/A",
                                "Expected Value": fnew if fnew is not None else "N/A",
                                "Validation Result": validation_result,
                                "Severity": "HIGH" if validation_result != "PASS" else "INFO",
                                "Execution Time": (time.time() - op_start_time) * 1000,
                                "Transaction ID": str(uuid.uuid4()),
                                "Thread": "Main",
                                "Exception": "None"
                            })
                
                # Insert RSSI history
                rssi_record = RSSIHistoryModel(
                    mac_address=state.mac_address,
                    timestamp=state.last_seen,
                    raw_rssi=state.current_rssi.value if hasattr(state.current_rssi, 'value') else state.current_rssi,
                    filtered_rssi=state.current_rssi.value if hasattr(state.current_rssi, 'value') else state.current_rssi,
                    moving_average=state.moving_average_rssi,
                    signal_classification=state.signal_classification.value,
                    distance_classification=state.distance_classification.value,
                    trend=state.signal_trend.value,
                    stability_score=state.stability_score
                )
                session.add(rssi_record)
                
                await session.commit()
                if db_verifier:
                    db_verifier.mark_transaction(success=True)
            except Exception as e:
                logger.error(f"Error saving device update to DB: {e}")
                await session.rollback()
                if 'db_verifier' in locals() and db_verifier:
                    db_verifier.mark_transaction(success=False)
                    db_verifier.log_verification({
                        "Timestamp": datetime.now(timezone.utc).isoformat(),
                        "Validation Result": "ROLLBACK",
                        "Exception": str(e)
                    })

    @staticmethod
    async def save_event(
        event_type: str, 
        mac_address: str, 
        message: str, 
        payload: str = None,
        entity_id: str = None,
        severity: str = None,
        category: str = None,
        source_module: str = None,
        correlation_id: str = None,
        search_tags: str = None
    ):
        async with AsyncSessionLocal() as session:
            try:
                event = EventModel(
                    event_type=event_type,
                    mac_address=mac_address,
                    message=message,
                    payload=payload,
                    entity_id=entity_id,
                    severity=severity,
                    category=category,
                    source_module=source_module,
                    correlation_id=correlation_id,
                    search_tags=search_tags
                )
                session.add(event)
                await session.commit()
            except Exception as e:
                logger.error(f"Error saving event to DB: {e}")
                await session.rollback()

    @staticmethod
    async def start_device_session(mac_address: str, timestamp: datetime):
        async with AsyncSessionLocal() as session:
            try:
                from app.models.domain import DeviceSessionModel
                new_session = DeviceSessionModel(
                    mac_address=mac_address,
                    connection_time=timestamp
                )
                session.add(new_session)
                await session.commit()
            except Exception as e:
                logger.error(f"Error starting device session: {e}")
                await session.rollback()

    @staticmethod
    async def end_device_session(mac_address: str, timestamp: datetime):
        async with AsyncSessionLocal() as session:
            try:
                from app.models.domain import DeviceSessionModel
                # Find the most recent open session
                result = await session.execute(
                    select(DeviceSessionModel)
                    .filter(DeviceSessionModel.mac_address == mac_address, DeviceSessionModel.disconnection_time == None)
                    .order_by(DeviceSessionModel.connection_time.desc())
                    .limit(1)
                )
                open_session = result.scalars().first()
                if open_session:
                    open_session.disconnection_time = timestamp
                    # Ensure timestamp format correctness
                    if open_session.connection_time.tzinfo is None:
                        conn_time = open_session.connection_time.replace(tzinfo=timezone.utc)
                    else:
                        conn_time = open_session.connection_time
                        
                    duration = (timestamp - conn_time).total_seconds()
                    open_session.session_duration = int(duration) if duration > 0 else 0
                    await session.commit()
            except Exception as e:
                logger.error(f"Error ending device session: {e}")
                await session.rollback()

    @staticmethod
    async def save_metadata_change(mac_address: str, field_name: str, old_value: str, new_value: str, timestamp: datetime):
        async with AsyncSessionLocal() as session:
            try:
                from app.models.domain import DeviceMetadataHistoryModel
                record = DeviceMetadataHistoryModel(
                    mac_address=mac_address,
                    timestamp=timestamp,
                    field_name=field_name,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None
                )
                session.add(record)
                await session.commit()
            except Exception as e:
                logger.error(f"Error saving metadata change: {e}")
                await session.rollback()
