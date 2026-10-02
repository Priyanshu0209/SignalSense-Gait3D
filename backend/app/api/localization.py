from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.services.localization.replay_engine import get_replay_engine
from app.services.localization.benchmark_engine import get_benchmark_engine
from app.services.localization.report_engine import get_report_engine

router = APIRouter()

class ReplayStartRequest(BaseModel):
    dataset: str

@router.post("/replay/load")
async def load_replay(req: ReplayStartRequest):
    try:
        await get_replay_engine().load_dataset(req.dataset)
        return {"status": "loaded"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/replay/play")
async def play_replay():
    await get_replay_engine().play()
    return {"status": "playing"}

@router.post("/replay/pause")
async def pause_replay():
    await get_replay_engine().pause()
    return {"status": "paused"}

@router.post("/replay/seek/{index}")
async def seek_replay(index: int):
    await get_replay_engine().seek(index)
    return {"status": "seeked"}

@router.post("/replay/speed/{speed}")
async def set_replay_speed(speed: float):
    await get_replay_engine().set_speed(speed)
    return {"status": "speed_set"}

class BenchmarkRequest(BaseModel):
    dataset: str
    model_ids: List[str]

@router.post("/benchmark/run")
async def run_benchmark(req: BenchmarkRequest):
    try:
        res = get_benchmark_engine().run_benchmark(req.dataset, req.model_ids)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/report/generate")
async def generate_report(req: dict):
    try:
        filepath = get_report_engine().generate_markdown_report(req)
        return {"status": "success", "file": filepath}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
