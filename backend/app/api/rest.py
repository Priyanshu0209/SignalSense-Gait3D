from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from app.services.device_state_manager import get_device_state_manager
from app.adapters.router.manager import get_router_manager
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.domain_repos import device_repo, event_repo, rssi_repo, alert_repo
from app.api.responses import api_response

router = APIRouter()

@router.get("/devices")
async def get_current_devices():
    import time as _time
    _api_start = _time.time()
    
    manager = get_device_state_manager()
    devices = manager.get_all_devices()
    
    from app.services.diagnostics.diagnostics_logger import get_diagnostics_logger
    logger_service = get_diagnostics_logger()
    for dev in devices:
        logger_service.log_api_layer(
            dev.mac_address,
            dev.current_rssi,
            f"Delivering via REST API. Manufacturer: {dev.manufacturer}"
        )
        
    # Module 7: REST API Verification
    try:
        from app.services.diagnostics.rest_verification import get_rest_verification_service
        rest_verifier = get_rest_verification_service()
        if not rest_verifier._running:
            await rest_verifier.start()
            
        from datetime import datetime, timezone
        _serialization_start = _time.time()
        
        required_fields = {
            "MAC": ("mac_address", "str"),
            "IP": ("ip_address", "str"),
            "Hostname": ("hostname", "str"),
            "RSSI": ("current_rssi", "int"),
            "Signal Quality": ("signal_quality", "int"),
            "Upload": ("upload_mbps", "float"),
            "Download": ("download_mbps", "float"),
            "Latency": ("latency", "float"),
            "Frequency": ("frequency", "str"),
            "Channel": ("channel", "int"),
            "Manufacturer": ("manufacturer", "str"),
            "Vendor": ("manufacturer", "str"),
            "Firmware": ("firmware", "str"),
            "Model": ("model", "str"),
            "Connection Status": ("online_status", "bool")
        }
        
        for dev in devices:
            for field_label, (attr_name, expected_type) in required_fields.items():
                actual_value = getattr(dev, attr_name, None)
                actual_type = type(actual_value).__name__ if actual_value is not None else "NoneType"
                
                if actual_value is None:
                    validation_result = "NULL"
                    severity = "HIGH" if field_label in ("RSSI", "MAC") else "MEDIUM"
                elif actual_value == "Unknown" or actual_value == "":
                    validation_result = "MISSING"
                    severity = "MEDIUM"
                else:
                    validation_result = "PASS"
                    severity = "INFO"
                    
                if validation_result != "PASS":
                    rest_verifier.log_validation({
                        "Timestamp": datetime.now(timezone.utc).isoformat(),
                        "Endpoint": "/devices",
                        "HTTP Method": "GET",
                        "Status Code": 200,
                        "Discovery Scan ID": "N/A",
                        "Correlation ID": "N/A",
                        "MAC Address": dev.mac_address,
                        "Field": field_label,
                        "Expected Type": expected_type,
                        "Actual Type": actual_type,
                        "Expected Value": f"Valid {expected_type}",
                        "Actual Value": str(actual_value),
                        "Validation Result": validation_result,
                        "Severity": severity,
                        "Payload Size": 0,
                        "Serialization Time": 0.0,
                        "Response Time": (_time.time() - _api_start) * 1000,
                        "Thread": "FastAPI"
                    })
        
        _serialization_time = (_time.time() - _serialization_start) * 1000
        _response_time = (_time.time() - _api_start) * 1000
        rest_verifier.mark_request(payload_size=len(str(devices)), response_time=_response_time)
    except Exception as rest_err:
        import logging
        logging.getLogger("signalsense.api").error(f"REST verification error: {rest_err}")
        
    return api_response(devices)

@router.get("/devices/history")
async def get_device_history(db: AsyncSession = Depends(get_db)):
    history = await device_repo.get_all(db)
    return api_response(history)

@router.get("/rssi/history/{mac_address}")
async def get_rssi_history(mac_address: str, db: AsyncSession = Depends(get_db)):
    # This is a basic example; in a real scenario you'd use a specific repository method to filter by MAC
    # For now we just return a message or implement a specific method.
    return api_response({"message": "RSSI history endpoint"})

@router.get("/events")
async def get_events(db: AsyncSession = Depends(get_db)):
    events = await event_repo.get_all(db)
    return api_response(events)

@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    alerts = await alert_repo.get_all(db)
    return api_response(alerts)

@router.get("/router/status")
async def get_router_status():
    manager = get_router_manager()
    status = await manager.get_status()
    if not status:
        raise HTTPException(status_code=503, detail="Router status unavailable")
    return api_response(status)

@router.get("/router/diagnostics")
async def get_router_diagnostics():
    manager = get_router_manager()
    if not hasattr(manager, 'get_diagnostics'):
        raise HTTPException(status_code=501, detail="Not implemented")
    diagnostics = await manager.get_diagnostics()
    return api_response(diagnostics)

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    manager = get_device_state_manager()
    devices = manager.get_all_devices()
    online_count = sum(1 for d in devices if d.online_status)
    return api_response({
        "total_devices": len(devices),
        "online_devices": online_count,
        "offline_devices": len(devices) - online_count
    })

from app.services.diagnostics import diagnostics_service

@router.post("/diagnostics/run")
async def run_diagnostics():
    report = await diagnostics_service.run_all_diagnostics()
    return api_response(report)
