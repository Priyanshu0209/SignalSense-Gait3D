from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.services.device_state_manager import get_device_state_manager

router = APIRouter()

@router.get("/", response_class=PlainTextResponse)
async def metrics():

    state_manager = get_device_state_manager()
    devices = state_manager.get_all_devices()
    
    active_count = len([d for d in devices if d.online_status])
    total_count = len(devices)
    
    # Simple Prometheus output
    output = []
    output.append("# HELP signalsense_active_devices Number of online devices.")
    output.append("# TYPE signalsense_active_devices gauge")
    output.append(f"signalsense_active_devices {active_count}")
    
    output.append("# HELP signalsense_total_devices Total known devices in twin.")
    output.append("# TYPE signalsense_total_devices gauge")
    output.append(f"signalsense_total_devices {total_count}")
    
    return "\n".join(output) + "\n"
