from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.ai.dataset_service import get_dataset_service
from app.services.ai.model_registry import get_model_registry, ModelMetadata
from app.services.ai.experiment_manager import get_experiment_manager
from app.services.ai.training_engine import get_training_engine
from app.services.ai.inference_engine import get_inference_engine

router = APIRouter()

# Dataset Manager
@router.get("/datasets")
async def list_datasets():
    return get_dataset_service().get_all_datasets()

@router.delete("/datasets/{filename}")
async def delete_dataset(filename: str):
    success = get_dataset_service().delete_dataset(filename)
    if not success:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": "success"}

@router.get("/datasets/{filename}/download")
async def download_dataset(filename: str):
    filepath = os.path.join(get_dataset_service().datasets_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Dataset not found")
    return FileResponse(filepath, media_type="text/csv", filename=filename)

# Model Registry
@router.get("/models", response_model=List[ModelMetadata])
async def list_models():
    return get_model_registry().get_all_models()

@router.post("/models/{model_id}/activate")
async def activate_model(model_id: str):
    success = get_model_registry().activate_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"status": "success"}

@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    success = get_model_registry().delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"status": "success"}

# Training Engine
class TrainingConfigRequest(BaseModel):
    dataset: str
    algorithm: str
    epochs: int
    learning_rate: float
    max_depth: int
    split_train: int
    split_val: int
    split_test: int

@router.post("/train/start")
async def start_training(config: TrainingConfigRequest):
    try:
        return await get_training_engine().start_training(config.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/train/stop")
async def stop_training():
    await get_training_engine().stop_training()
    return {"status": "stopped"}

# Experiments
@router.get("/experiments")
async def list_experiments():
    return get_experiment_manager().get_all_experiments()

# Inference Engine Control (Optional)
@router.post("/inference/start")
async def start_inference():
    await get_inference_engine().start()
    return {"status": "started"}

@router.post("/inference/stop")
async def stop_inference():
    await get_inference_engine().stop()
    return {"status": "stopped"}
