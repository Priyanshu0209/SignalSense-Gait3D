from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List
from pydantic import BaseModel
from app.services.dataset_manager import get_dataset_manager, DatasetCollectionConfig, GroundTruthConfig

router = APIRouter()

# Dependency to get manager
def get_manager():
    return get_dataset_manager()

@router.get("/state")
async def get_state(manager = Depends(get_manager)):

    return manager.get_state()

@router.put("/config")
async def set_config(config: DatasetCollectionConfig, manager = Depends(get_manager)):

    try:
        manager.set_config(config)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ground_truth", response_model=List[GroundTruthConfig])
async def get_all_ground_truth(manager = Depends(get_manager)):

    return manager.get_ground_truth()

@router.put("/device/{mac}/ground_truth")
async def set_device_ground_truth(mac: str, gt: GroundTruthConfig, manager = Depends(get_manager)):

    if mac != gt.mac_address:
        raise HTTPException(status_code=400, detail="MAC address in URL must match payload")
    manager.set_ground_truth(mac, gt)
    return {"status": "success"}

@router.post("/start")
async def start_collection(manager = Depends(get_manager)):
    await manager.start_collection()
    return {"status": "started"}

@router.post("/pause")
async def pause_collection(manager = Depends(get_manager)):

    await manager.pause_collection()
    return {"status": "paused"}

@router.post("/resume")
async def resume_collection(manager = Depends(get_manager)):

    await manager.resume_collection()
    return {"status": "resumed"}

@router.post("/stop")
async def stop_collection(manager = Depends(get_manager)):

    await manager.stop_collection()
    return {"status": "stopped"}
