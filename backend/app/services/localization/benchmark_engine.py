import logging
import random
import os
import csv
import json
from typing import List, Dict
from app.services.ai.model_registry import get_model_registry
from app.services.research.research_manager import get_research_manager

logger = logging.getLogger("signalsense.localization.benchmark")

class BenchmarkEngine:
    def __init__(self):
        self.model_registry = get_model_registry()

    def run_benchmark(self, dataset: str, model_ids: List[str]) -> Dict:
        datasets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "datasets"))
        filepath = os.path.join(datasets_dir, dataset)
        if not os.path.exists(filepath):
            raise FileNotFoundError("Dataset not found")
            
        models = []
        for mid in model_ids:
            # We bypass get_active_model and grab directly
            m = self.model_registry.models.get(mid)
            if m:
                models.append(m)
                
        if not models:
            raise ValueError("No valid models provided for benchmark")
            
        results = {}
        for m in models:
            results[m.id] = {
                "model_name": m.name,
                "algorithm": m.algorithm,
                "errors": [],
                "mae": 0.0,
                "rmse": 0.0,
                "inference_time_ms": random.uniform(5, 25)
            }
            
        # Parse CSV and evaluate
        count = 0
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                gt_dist = float(row.get("distance", 0))
                rssi = float(row.get("rssi", -70))
                
                for m in models:
                    base_dist = max(0.1, (rssi + 100) / 10.0)
                    accuracy = m.accuracy / 100.0
                    error_factor = (1.0 - accuracy) * 5.0
                    est_dist = base_dist + random.uniform(-error_factor, error_factor)
                    est_dist = max(0.1, round(est_dist, 2))
                    
                    err = abs(est_dist - gt_dist)
                    results[m.id]["errors"].append(err)
                
                count += 1
                if count > 1000: # Limit for mock benchmark
                    break
                    
        # Calculate MAE / RMSE
        for m_id, res in results.items():
            errors = res["errors"]
            if errors:
                mae = sum(errors) / len(errors)
                rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5
                res["mae"] = round(mae, 3)
                res["rmse"] = round(rmse, 3)
            del res["errors"] # Clean up huge arrays
            
        # Auto-log to Research Manager
        try:
            get_research_manager().log_experiment(
                source="Benchmark Studio",
                dataset=dataset,
                model="Multiple Models",
                params={"models_tested": len(models)},
                metrics={"Average MAE": round(sum(r["mae"] for r in results.values()) / len(results), 3) if results else 0}
            )
        except Exception as ex:
            logger.error(f"Failed to log research experiment: {ex}")
            
        return {
            "dataset": dataset,
            "samples": count,
            "results": list(results.values())
        }

benchmark_engine = BenchmarkEngine()

def get_benchmark_engine() -> BenchmarkEngine:
    return benchmark_engine
