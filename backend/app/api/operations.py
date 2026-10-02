import os
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.services.operations.health_monitor import get_health_monitor
from app.services.operations.backup_manager import get_backup_manager
from app.services.operations.diagnostics_engine import get_diagnostics_engine
from app.services.operations.report_generator import get_report_generator
from app.core.config import settings, fernet

router = APIRouter()

@router.get("/config")
async def get_config():
    # Return redacted config to the frontend
    return {
        "host": settings.ROUTER_HOST if settings.ROUTER_HOST != "auto" else "",
        "username": settings.ROUTER_USERNAME if settings.ROUTER_USERNAME != "root" else "",
        "adapter": settings.ROUTER_ADAPTER
    }

class ConfigRequest(BaseModel):
    host: str
    username: str
    password: str
    port: int = 22
    name: str = ""

@router.post("/config")
async def save_config(req: ConfigRequest):
    try:
        config_data = {
            "ROUTER_HOST": req.host,
            "ROUTER_USERNAME": req.username,
            "ROUTER_PASSWORD": req.password
        }
        decrypted_data = json.dumps(config_data)
        encrypted_data = fernet.encrypt(decrypted_data.encode("utf-8"))
        
        config_dir = os.path.expanduser("~/.signalsense")
        os.makedirs(config_dir, exist_ok=True)
        enc_config_path = os.path.join(config_dir, "config.enc")
        
        with open(enc_config_path, "wb") as f:
            f.write(encrypted_data)
            
        # Update current settings
        settings.ROUTER_HOST = req.host
        settings.ROUTER_USERNAME = req.username
        settings.ROUTER_PASSWORD = req.password
        
        # Trigger router manager reload
        from app.adapters.router.manager import router_manager
        if router_manager:
            # Re-initialize with new config
            router_manager.host = req.host
            router_manager.username = req.username
            router_manager.password = req.password
            
            # Reset and connect
            router_manager.is_connecting = False
            router_manager.adapter = None
            success = await router_manager.connect()
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to connect to router with provided credentials.")
            
            # Restart discovery loop to use new adapter
            from app.collectors.data_collector import get_background_discovery_service, DiscoveryState
            discovery_svc = get_background_discovery_service()
            discovery_svc.router_manager = router_manager
            # In a real app we'd gracefully restart the loop, but this works for prototype
            discovery_svc.state = DiscoveryState.CONNECTED

        return {"status": "success", "message": "Configuration saved securely."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    return get_health_monitor().get_system_metrics()

@router.get("/services")
async def get_services():
    return get_health_monitor().get_services_status()

class ServiceControlRequest(BaseModel):
    service_name: str
    action: str # "Start", "Stop", "Restart"

@router.post("/services/control")
async def control_service(req: ServiceControlRequest):
    hm = get_health_monitor()
    if req.action == "Start":
        hm.set_service_status(req.service_name, "Running")
    elif req.action == "Stop":
        hm.set_service_status(req.service_name, "Stopped")
    elif req.action == "Restart":
        hm.set_service_status(req.service_name, "Restarting")
        # In a real app we'd trigger an async restart, mock it by setting it back to Running shortly after
        import asyncio
        async def reset():
            await asyncio.sleep(2)
            hm.set_service_status(req.service_name, "Running")
        asyncio.create_task(reset())
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"status": "success"}

@router.get("/backups")
async def list_backups():
    return get_backup_manager().get_backups()

@router.post("/backups/create")
async def create_backup(req: dict):
    return get_backup_manager().create_backup(req.get("type", "Full System"))

@router.post("/backups/restore/{backup_id}")
async def restore_backup(backup_id: str):
    get_backup_manager().restore_backup(backup_id)
    return {"status": "restored"}

@router.get("/diagnostics")
async def run_diagnostics():
    return get_diagnostics_engine().run_diagnostics()

@router.post("/reports/generate")
async def generate_report():
    filepath = get_report_generator().generate_system_report()
    return {"file": filepath}
