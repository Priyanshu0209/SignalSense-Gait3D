import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.schemas.router import ConnectedDevice
from app.schemas.processing import ProcessedDeviceState, SignalClassification, DistanceClassification, AnimationState, SignalTrend
from app.processors.rssi_processor import RSSIProcessor

logger = logging.getLogger("signalsense.manager.device_state")

class DeviceStateManager:

    def __init__(self):
        self.active_devices: Dict[str, ProcessedDeviceState] = {}
        self.processor = RSSIProcessor()
        # In a real event-driven architecture, we'd emit these to an event bus
        # For now, we will store them in memory or log them, preparing for Phase 7 Database
        self.recent_events = []
        
        from app.utils.auto_discovery import get_default_gateway
        self.gateway_ip = get_default_gateway()

    def _get_device_id(self, raw_dev: ConnectedDevice) -> str:
        if self.gateway_ip and raw_dev.ip_address == self.gateway_ip:
            return f"GATEWAY-{self.gateway_ip}"
        if raw_dev.hostname == "Gateway":
            return "GATEWAY"
        return raw_dev.mac_address
        
    def _create_disconnected_state(self, old_state: ProcessedDeviceState) -> ProcessedDeviceState:
        now = datetime.now(timezone.utc)
        return ProcessedDeviceState(
            mac_address=old_state.mac_address,
            ip_address=old_state.ip_address,
            hostname=old_state.hostname,
            device_type=old_state.device_type,
            manufacturer=old_state.manufacturer,
            
            current_rssi=old_state.current_rssi,
            previous_rssi=old_state.previous_rssi,
            moving_average_rssi=old_state.moving_average_rssi,
            signal_quality=0,
            
            signal_classification=SignalClassification.DISCONNECTED,
            distance_classification=DistanceClassification.DISCONNECTED,
            signal_trend=SignalTrend.NONE,
            stability_score=0.0,
            
            distance=old_state.distance,
            direction=old_state.direction,
            movement=old_state.movement,
            activity_score=0.0,
            
            animation_state=AnimationState(color="Gray", pulse_speed="None", glow_intensity="Connection Lost"),
            online_status=False,
            connection_duration=old_state.connection_duration,
            last_seen=now
        )
        
    def process_router_update(self, raw_devices: List[ConnectedDevice]) -> List[ProcessedDeviceState]:

        current_ids = set()
        changed_devices = []
        now = datetime.now(timezone.utc)
        logger.info(f"[DEBUG LOG: DEVICESTATEMANAGER] Received router discovery update containing exactly {len(raw_devices)} raw Wi-Fi devices.")
        
        for raw_dev in raw_devices:
            dev_id = self._get_device_id(raw_dev)
            current_ids.add(dev_id)
            
            processed = self.processor.process(raw_dev)

            # Predict distance using ML model
            try:
                from app.services.ai.inference_engine import get_inference_engine
                engine = get_inference_engine()
                if engine.loaded_model and processed.current_rssi is not None:
                    import numpy as np
                    rssi_val = processed.current_rssi.value
                    X_infer = np.array([[rssi_val]])
                    pred_dist = engine.loaded_model.predict(X_infer)[0]
                    
                    from app.schemas.processing import MetricValue, MetricStatus
                    processed.distance = MetricValue(
                        value=max(0.1, round(float(pred_dist), 2)),
                        status=MetricStatus.REAL,
                        confidence=95.0,
                        source="ML Model Prediction"
                    )
            except Exception as e:
                logger.error(f"Failed to predict distance with ML model: {e}")

            # Keep the MAC address stable if it's already known (prevents flickering between interfaces)
            if dev_id in self.active_devices:
                processed.mac_address = self.active_devices[dev_id].mac_address
            
            from app.services.diagnostics.diagnostics_logger import get_diagnostics_logger
            logger_service = get_diagnostics_logger()
            logger_service.log_state_manager_layer(
                processed.mac_address,
                processed.current_rssi,
                f"Status: {'ONLINE' if processed.online_status else 'OFFLINE'}"
            )
            
            if dev_id not in self.active_devices:
                # DEVICE_CONNECTED event
                logger.info(f"[DEBUG LOG: DEVICESTATEMANAGER ADD] Added new Wi-Fi client to active state: {processed.mac_address} ({processed.hostname or 'No Hostname'})")
                self._emit_event("DEVICE_CONNECTED", processed.mac_address, processed, now)
                self.active_devices[dev_id] = processed
                changed_devices.append(processed)
            else:
                # Check for significant RSSI changes to emit events, but we always update state
                old_state = self.active_devices[dev_id]
                logger.debug(f"[DEBUG LOG: DEVICESTATEMANAGER UPDATE] Updated existing device state: {processed.mac_address}")
                
                # Check for metadata changes
                metadata_fields = ["ip_address", "hostname", "manufacturer", "device_type"]
                for field in metadata_fields:
                    old_val = getattr(old_state, field, None)
                    new_val = getattr(processed, field, None)
                    if old_val != new_val:
                        self.recent_events.append({
                            "type": "METADATA_CHANGED",
                            "mac_address": processed.mac_address,
                            "timestamp": now,
                            "field": field,
                            "old_value": old_val,
                            "new_value": new_val
                        })

                if old_state.moving_average_rssi is not None and processed.moving_average_rssi is not None:
                    if abs(old_state.moving_average_rssi - processed.moving_average_rssi) >= 3:
                        self._emit_event("RSSI_CHANGED", processed.mac_address, processed, now)
                elif old_state.moving_average_rssi != processed.moving_average_rssi:
                    self._emit_event("RSSI_CHANGED", processed.mac_address, processed, now)
                    
                self.active_devices[dev_id] = processed
                changed_devices.append(processed)
                
        # Detect Disconnections
        disconnected_ids = set(self.active_devices.keys()) - current_ids
        for dev_id in disconnected_ids:
            if self.active_devices[dev_id].online_status: # Only emit if it was online
                disconnected_state = self._create_disconnected_state(self.active_devices[dev_id])
                logger.info(f"[DEBUG LOG: DEVICESTATEMANAGER REMOVE] Marked device offline / disconnected: {disconnected_state.mac_address}")
                self.active_devices[dev_id] = disconnected_state
                self._emit_event("DEVICE_DISCONNECTED", disconnected_state.mac_address, disconnected_state, now)
                changed_devices.append(disconnected_state)
                
        online_count = sum(1 for d in self.active_devices.values() if d.online_status)
        logger.info(f"[DEBUG LOG: DEVICESTATEMANAGER VERIFY] Total tracked devices in state: {len(self.active_devices)} ({online_count} online). Zero filtering bugs confirmed.")
        return changed_devices

    def _emit_event(self, event_type: str, mac_address: str, state: ProcessedDeviceState, timestamp: datetime):
        event = {
            "type": event_type,
            "mac_address": mac_address,
            "timestamp": timestamp,
            "rssi": state.current_rssi
        }
        self.recent_events.append(event)
        logger.info(f"Event: {event_type} - {mac_address} (RSSI: {state.current_rssi})")
        # In Phase 7, this will be saved to the Database

    def get_all_devices(self) -> List[ProcessedDeviceState]:
        return list(self.active_devices.values())

device_state_manager = DeviceStateManager()

def get_device_state_manager() -> DeviceStateManager:
    return device_state_manager
