import os
import json
from datetime import datetime

class DatasetService:
    def __init__(self):
        self.datasets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "datasets"))
        os.makedirs(self.datasets_dir, exist_ok=True)

    def get_all_datasets(self):
        datasets = []
        for filename in os.listdir(self.datasets_dir):
            if filename.endswith(".csv"):
                filepath = os.path.join(self.datasets_dir, filename)
                meta_path = filepath.replace(".csv", "_metadata.json")
                
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                
                # Default mock stats if metadata is missing
                metadata = {
                    "Session Name": filename.split(".")[0],
                    "Number of Samples": 0,
                    "Number of Devices": 0,
                    "Environment": "Unknown",
                    "Total Duration": "0s",
                    "Start Time": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                }
                
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r") as f:
                            meta_content = json.load(f)
                            metadata.update(meta_content)
                    except Exception:
                        pass
                
                # Mock Quality Score for UI visualization purposes
                quality_score = min(100, max(50, int(metadata.get("Number of Samples", 0) / 100)))

                datasets.append({
                    "filename": filename,
                    "name": metadata.get("Session Name"),
                    "size_mb": round(size_mb, 2),
                    "samples": metadata.get("Number of Samples"),
                    "devices": metadata.get("Number of Devices"),
                    "environment": metadata.get("Environment"),
                    "duration": metadata.get("Total Duration"),
                    "created_at": metadata.get("Start Time"),
                    "quality_score": quality_score
                })
        return sorted(datasets, key=lambda x: x["created_at"], reverse=True)

    def delete_dataset(self, filename: str) -> bool:
        if not filename.endswith(".csv"):
            return False
            
        filepath = os.path.join(self.datasets_dir, filename)
        meta_path = filepath.replace(".csv", "_metadata.json")
        
        deleted = False
        if os.path.exists(filepath):
            os.remove(filepath)
            deleted = True
            
        if os.path.exists(meta_path):
            os.remove(meta_path)
            
        return deleted

dataset_service = DatasetService()

def get_dataset_service() -> DatasetService:
    return dataset_service
