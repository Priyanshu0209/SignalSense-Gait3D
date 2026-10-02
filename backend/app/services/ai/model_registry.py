import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

class ModelMetadata(BaseModel):
    id: str
    name: str
    algorithm: str
    training_date: str
    dataset: str
    accuracy: float
    version: str
    status: str # "Active", "Inactive"
    filepath: Optional[str] = None

import os
import json

class ModelRegistry:
    def __init__(self):
        self.models: Dict[str, ModelMetadata] = {}
        self.active_model_id: Optional[str] = None
        self.registry_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "models", "registry.json"))
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        
        self._load_registry()
        
        # Fallback if empty
        if not self.models:
            self._add_mock_model()

    def _load_registry(self):
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                    for k, v in data.get("models", {}).items():
                        self.models[k] = ModelMetadata(**v)
                    self.active_model_id = data.get("active_model_id")
            except Exception as e:
                print(f"Failed to load registry: {e}")

    def _save_registry(self):
        try:
            data = {
                "models": {k: v.model_dump() for k, v in self.models.items()},
                "active_model_id": self.active_model_id
            }
            with open(self.registry_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save registry: {e}")

    def _add_mock_model(self):
        mid = str(uuid.uuid4())
        self.models[mid] = ModelMetadata(
            id=mid,
            name="Baseline_RF_Model",
            algorithm="Random Forest",
            training_date=datetime.now(timezone.utc).isoformat(),
            dataset="dataset_office_room_A",
            accuracy=92.4,
            version="v1.0.0",
            status="Active"
        )
        self.active_model_id = mid
        self._save_registry()

    def register_model(self, metadata: ModelMetadata):
        self.models[metadata.id] = metadata
        self._save_registry()

    def get_all_models(self) -> List[ModelMetadata]:
        return list(self.models.values())

    def get_active_model(self) -> Optional[ModelMetadata]:
        if self.active_model_id:
            return self.models.get(self.active_model_id)
        return None

    def activate_model(self, model_id: str):
        if model_id in self.models:
            # Deactivate current
            if self.active_model_id and self.active_model_id in self.models:
                self.models[self.active_model_id].status = "Inactive"
            # Activate new
            self.models[model_id].status = "Active"
            self.active_model_id = model_id
            self._save_registry()
            return True
        return False

    def delete_model(self, model_id: str):
        if model_id in self.models:
            if self.active_model_id == model_id:
                self.active_model_id = None
            del self.models[model_id]
            self._save_registry()
            return True
        return False

model_registry = ModelRegistry()

def get_model_registry() -> ModelRegistry:
    return model_registry
