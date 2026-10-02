from typing import Dict, List, Any
import uuid
from datetime import datetime, timezone

class ExperimentManager:
    def __init__(self):
        self.experiments: Dict[str, Any] = {}

    def create_experiment(self, dataset: str, algorithm: str, params: dict):
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"
        self.experiments[exp_id] = {
            "id": exp_id,
            "dataset": dataset,
            "algorithm": algorithm,
            "parameters": params,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "status": "Running",
            "metrics": {},
            "logs": []
        }
        return exp_id

    def update_experiment(self, exp_id: str, metrics: dict, status: str = "Completed"):
        if exp_id in self.experiments:
            self.experiments[exp_id]["metrics"] = metrics
            self.experiments[exp_id]["status"] = status
            if status in ["Completed", "Failed", "Stopped"]:
                self.experiments[exp_id]["end_time"] = datetime.now(timezone.utc).isoformat()

    def get_all_experiments(self) -> List[Any]:
        return list(self.experiments.values())

experiment_manager = ExperimentManager()

def get_experiment_manager() -> ExperimentManager:
    return experiment_manager
