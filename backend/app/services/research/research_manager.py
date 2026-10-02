import uuid
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any

class ResearchManager:
    def __init__(self):
        self.experiments: Dict[str, Any] = {}
        self.notes: Dict[str, str] = {}
        self.provenance: Dict[str, Any] = {}

    def log_experiment(self, source: str, dataset: str, model: str, params: dict, metrics: dict):

        exp_id = f"R-{uuid.uuid4().hex[:8].upper()}"
        
        experiment = {
            "id": exp_id,
            "name": f"Auto-Experiment ({source})",
            "source": source,
            "dataset": dataset,
            "model": model,
            "parameters": params,
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "Logged",
            "tags": [source]
        }
        
        self.experiments[exp_id] = experiment
        self.notes[exp_id] = f"# Research Notes for {exp_id}\n\nAuto-generated on {experiment['timestamp']}."
        
        # Mock Provenance Generation
        self.provenance[dataset] = {
            "dataset_version": "v1.0",
            "collection_date": experiment['timestamp'],
            "collector": "Auto-System",
            "csv_hash": f"sha256-{uuid.uuid4().hex}",
            "related_experiments": [exp_id]
        }
        
        return exp_id

    def get_all_experiments(self) -> List[Any]:
        return list(self.experiments.values())
        
    def get_experiment(self, exp_id: str) -> Any:
        return self.experiments.get(exp_id)

    def get_note(self, exp_id: str) -> str:
        return self.notes.get(exp_id, "")

    def update_note(self, exp_id: str, content: str):
        self.notes[exp_id] = content
        return True

    def get_all_provenance(self) -> Dict[str, Any]:
        return self.provenance

research_manager = ResearchManager()

def get_research_manager() -> ResearchManager:
    return research_manager
