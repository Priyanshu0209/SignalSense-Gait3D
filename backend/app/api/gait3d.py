import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.services.gait3d import (
    get_gait_time_series_collector,
    get_signal_filter_engine,
    get_motion_activity_engine,
    get_gait_analytics_engine,
    get_kinematic3d_generator,
    get_gait_experiment_orchestrator
)
from app.websockets.manager import websocket_manager

logger = logging.getLogger("signalsense.api.gait3d")
router = APIRouter()

# Background WebSocket broadcaster and telemetry logger task
_broadcast_task: Optional[asyncio.Task] = None
_broadcast_running = False

async def gait3d_broadcast_loop():
    global _broadcast_running
    _broadcast_running = True
    collector = get_gait_time_series_collector()
    activity_eng = get_motion_activity_engine()
    gait_eng = get_gait_analytics_engine()
    kinematic_eng = get_kinematic3d_generator()
    orchestrator = get_gait_experiment_orchestrator()
    
    logger.info("Gait3D real-time WebSocket broadcast loop initiated.")
    while _broadcast_running:
        try:
            # Record tick for ongoing scientific experiment trials if active
            orchestrator.record_tick()
            
            # Retrieve latest live analytics & kinematic frames
            activities = activity_eng.get_network_activity_summary()
            gait_metrics = gait_eng.get_all_gait_metrics()
            scene_frame = kinematic_eng.get_3d_scene_frame()
            subs = scene_frame.get("subjects", [])
            logger.info(f"[DEBUG LOG: WEBSOCKET BROADCAST] Emitting 'gait_3d_frame' payload containing exactly {len(subs)} connected subject(s) to frontend over WebSocket. IDs: {[s.get('id') for s in subs]}")
            
            # Broadcast over shared connection manager
            await websocket_manager.broadcast_event("gait_live_telemetry", {
                "activities": activities,
                "gait_metrics": gait_metrics,
                "simulation_enabled": collector.simulation_enabled
            })
            await websocket_manager.broadcast_event("gait_3d_frame", scene_frame)
            
            if orchestrator.is_recording and orchestrator.active_trial:
                await websocket_manager.broadcast_event("gait_experiment_progress", {
                    "trial_id": orchestrator.active_trial["id"],
                    "samples_recorded": len(orchestrator.recorded_samples)
                })
                
        except Exception as e:
            logger.warning(f"Error in Gait3D broadcast loop: {e}")
            
        await asyncio.sleep(0.35) # ~3 FPS real-time UI synchronization without network flooding

async def start_gait3d_background():
    global _broadcast_task, _broadcast_running
    collector = get_gait_time_series_collector()
    await collector.start()
    if not _broadcast_running:
        _broadcast_task = asyncio.create_task(gait3d_broadcast_loop())

async def stop_gait3d_background():
    global _broadcast_task, _broadcast_running
    _broadcast_running = False
    if _broadcast_task:
        _broadcast_task.cancel()
    await get_gait_time_series_collector().stop()

# --- REST Endpoints ---

@router.get("/state")
async def get_gait3d_state():
    return {
        "activities": get_motion_activity_engine().get_network_activity_summary(),
        "gait_metrics": get_gait_analytics_engine().get_all_gait_metrics(),
        "collector_status": {
            "is_running": get_gait_time_series_collector().is_running,
            "simulation_enabled": get_gait_time_series_collector().simulation_enabled,
            "monitored_endpoints": len(get_gait_time_series_collector().get_all_macs())
        }
    }

@router.get("/frame3d")
async def get_3d_scene_frame():
    return get_kinematic3d_generator().get_3d_scene_frame()

@router.get("/signal/{mac}")
async def get_device_signal_analysis(mac: str):
    collector = get_gait_time_series_collector()
    filter_eng = get_signal_filter_engine()
    samples = collector.get_recent_window(mac, duration_sec=10.0)
    
    raw = [s["raw_rssi"] for s in samples]
    filtered = filter_eng.apply_butterworth_lowpass(raw, cutoff_hz=3.5, sample_rate_hz=collector.sample_rate_hz)
    fft_res = filter_eng.compute_fft(filtered, sample_rate_hz=collector.sample_rate_hz)
    
    return {
        "mac": mac,
        "sample_count": len(samples),
        "timestamps": [round(s["timestamp"] - samples[0]["timestamp"], 2) for s in samples] if samples else [],
        "raw_rssi": raw,
        "filtered_rssi": filtered,
        "fft_spectrum": fft_res
    }

class SimulationToggleRequest(BaseModel):
    enabled: bool
    activity_override: Optional[str] = None

@router.post("/simulation")
async def toggle_gait_simulation(req: SimulationToggleRequest):
    get_gait_time_series_collector().set_simulation_state(req.enabled, req.activity_override)
    return {"status": "success", "enabled": req.enabled, "override": req.activity_override}

class RoomConfigRequest(BaseModel):
    width_x: float
    length_y: float
    height_z: float
    access_points: Optional[List[Dict[str, Any]]] = None

@router.post("/room/config")
async def update_room_configuration(req: RoomConfigRequest):
    res = get_kinematic3d_generator().configure_room(req.width_x, req.length_y, req.height_z, req.access_points)
    return res

class ExperimentStartRequest(BaseModel):
    title: str
    subject_id: str
    scenario: str
    walking_speed_ms: Optional[float] = 1.3
    room_name: Optional[str] = "RF Biomedical Motion Laboratory"
    environment: Optional[str] = "Indoor Laboratory (LOS / Soft Partitions)"
    router_model: Optional[str] = "Netgear Nighthawk X4S / IEEE 802.11ac"
    operator_name: Optional[str] = "Lead RF Sensing Researcher"
    ground_truth: Optional[Dict[str, Any]] = None

@router.post("/experiment/start")
async def start_experiment(req: ExperimentStartRequest):
    res = get_gait_experiment_orchestrator().start_trial(
        title=req.title,
        subject_id=req.subject_id,
        scenario=req.scenario,
        walking_speed_ms=req.walking_speed_ms or 1.3,
        room_name=req.room_name or "RF Biomedical Motion Laboratory",
        environment=req.environment or "Indoor Laboratory (LOS / Soft Partitions)",
        router_model=req.router_model or "Netgear Nighthawk X4S / IEEE 802.11ac",
        operator_name=req.operator_name or "Lead RF Sensing Researcher",
        ground_truth=req.ground_truth
    )
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@router.post("/experiment/stop")
async def stop_experiment():
    res = get_gait_experiment_orchestrator().stop_trial()
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@router.get("/experiments")
async def list_gait_experiments():
    return {
        "active_status": get_gait_experiment_orchestrator().get_status(),
        "experiments": get_gait_experiment_orchestrator().get_experiments()
    }
