from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from app.services.research.research_manager import get_research_manager
from app.services.research.publication_engine import get_publication_engine
from app.services.research.validation_engine import get_validation_engine

router = APIRouter()

@router.get("/experiments")
async def list_experiments():
    return get_research_manager().get_all_experiments()

@router.get("/experiments/{exp_id}")
async def get_experiment(exp_id: str):
    exp = get_research_manager().get_experiment(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp

@router.get("/notebook/{exp_id}")
async def get_notebook(exp_id: str):
    return {"content": get_research_manager().get_note(exp_id)}

class NoteRequest(BaseModel):
    content: str

@router.post("/notebook/{exp_id}")
async def update_notebook(exp_id: str, req: NoteRequest):
    success = get_research_manager().update_note(exp_id, req.content)
    if not success:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"status": "success"}

@router.get("/provenance")
async def get_provenance():
    return get_research_manager().get_all_provenance()

class PublicationRequest(BaseModel):
    experiment_id: str
    title: str
    abstract: str

@router.post("/publications/generate")
async def generate_publication(req: PublicationRequest):
    try:
        filepath = get_publication_engine().generate_report(req.experiment_id, req.title, req.abstract)
        return {"status": "success", "file": filepath}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/validate")
async def run_validation():
    return get_validation_engine().run_diagnostics()
