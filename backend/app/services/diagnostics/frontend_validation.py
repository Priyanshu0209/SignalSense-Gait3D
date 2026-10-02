import asyncio
import csv
import os
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger("signalsense.diagnostics.frontend")

class FrontendValidationService:

    def __init__(self, max_bytes: int = 50_000_000, backup_count: int = 5):
        self.queue = asyncio.Queue(maxsize=100000)
        self.log_dir = "logs/frontend"
        self.csv_file_path = os.path.join(self.log_dir, "frontend_validation.csv")
        self.json_file_path = os.path.join(self.log_dir, "frontend_validation.json")
        self._running = False
        self._worker_task = None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self.stats_lock = asyncio.Lock()
        self.stats = {
            "Total Validations": 0,
            "Passed Validations": 0,
            "Failed Validations": 0,
            "Missing Properties": 0,
            "Undefined Values": 0,
            "Null Values": 0,
            "Rendering Errors": 0,
            "Chart Errors": 0,
            "Timeline Errors": 0,
            "Component Frequencies": Counter(),
            "Property Frequencies": Counter()
        }
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        self.headers = [
            "Timestamp", "Component", "Discovery Scan ID", "Correlation ID",
            "MAC Address", "Property", "Expected", "Actual",
            "Validation Result", "Severity", "Render Time", "Thread"
        ]
        
        write_header = not os.path.exists(self.csv_file_path) or os.path.getsize(self.csv_file_path) == 0
        if write_header:
            with open(self.csv_file_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def _rotate_file_if_needed(self):
        if not os.path.exists(self.csv_file_path):
            return
            
        if os.path.getsize(self.csv_file_path) >= self.max_bytes:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = f"{self.csv_file_path}.{i}"
                dfn = f"{self.csv_file_path}.{i + 1}"
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
                    
            dfn = f"{self.csv_file_path}.1"
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.csv_file_path, dfn)
            
            self._init_csv()

    async def start(self):
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._flush_worker())

    async def stop(self):
        if self._running:
            self._running = False
            if self._worker_task:
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass

    async def _flush_worker(self):
        while self._running:
            try:
                batch = []
                while not self.queue.empty():
                    batch.append(self.queue.get_nowait())
                    
                if batch:
                    self._rotate_file_if_needed()
                    
                    with open(self.csv_file_path, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        for item in batch:
                            row = [item.get(k, "N/A") for k in self.headers]
                            writer.writerow(row)
                                
                    await self._update_json_stats(batch)
                        
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing frontend validation queue: {e}")
                await asyncio.sleep(1.0)
                
    async def _update_json_stats(self, batch: List[Dict[str, Any]]):
        async with self.stats_lock:
            for item in batch:
                self.stats["Total Validations"] += 1
                val_result = item.get("Validation Result", "")
                
                if val_result == "PASS":
                    self.stats["Passed Validations"] += 1
                else:
                    self.stats["Failed Validations"] += 1
                    
                if val_result == "MISSING_PROPERTY":
                    self.stats["Missing Properties"] += 1
                elif val_result == "UNDEFINED":
                    self.stats["Undefined Values"] += 1
                elif val_result == "NULL":
                    self.stats["Null Values"] += 1
                elif val_result == "RENDER_ERROR":
                    self.stats["Rendering Errors"] += 1
                elif val_result == "CHART_ERROR":
                    self.stats["Chart Errors"] += 1
                elif val_result == "TIMELINE_ERROR":
                    self.stats["Timeline Errors"] += 1
                    
                component = item.get("Component")
                if component and component != "N/A":
                    self.stats["Component Frequencies"][component] += 1
                    
                prop = item.get("Property")
                if prop and prop != "N/A":
                    self.stats["Property Frequencies"][prop] += 1
                    
            total_val = max(self.stats["Total Validations"], 1)
            top_component = self.stats["Component Frequencies"].most_common(1)
            top_property = self.stats["Property Frequencies"].most_common(1)
            
            output_stats = {
                "Total Validations": self.stats["Total Validations"],
                "Passed Validations": self.stats["Passed Validations"],
                "Failed Validations": self.stats["Failed Validations"],
                "Validation Success Rate": round((self.stats["Passed Validations"] / total_val) * 100, 2),
                "Missing Properties": self.stats["Missing Properties"],
                "Undefined Values": self.stats["Undefined Values"],
                "Null Values": self.stats["Null Values"],
                "Rendering Errors": self.stats["Rendering Errors"],
                "Chart Errors": self.stats["Chart Errors"],
                "Timeline Errors": self.stats["Timeline Errors"],
                "Most Failed Component": top_component[0][0] if top_component else "N/A",
                "Most Failed Property": top_property[0][0] if top_property else "N/A"
            }
            
            temp_json = self.json_file_path + ".tmp"
            with open(temp_json, 'w') as jf:
                json.dump(output_stats, jf, indent=2)
            os.replace(temp_json, self.json_file_path)

    def log_validation(self, data: Dict[str, Any]):
        try:
            self.queue.put_nowait(data)
        except asyncio.QueueFull:
            logger.error("Frontend validation queue full!")

frontend_validation_service = FrontendValidationService()

def get_frontend_validation_service() -> FrontendValidationService:
    return frontend_validation_service
