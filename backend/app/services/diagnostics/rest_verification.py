import asyncio
import csv
import os
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger("signalsense.diagnostics.rest")

class RESTVerificationService:

    def __init__(self, max_bytes: int = 50_000_000, backup_count: int = 5):
        self.queue = asyncio.Queue(maxsize=100000)
        self.log_dir = "logs/api"
        self.csv_file_path = os.path.join(self.log_dir, "rest_validation.csv")
        self.json_file_path = os.path.join(self.log_dir, "rest_validation.json")
        self._running = False
        self._worker_task = None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self.stats_lock = asyncio.Lock()
        self.stats = {
            "Total Validations": 0,
            "Passed Validations": 0,
            "Failed Validations": 0,
            "Missing Fields": 0,
            "Null Fields": 0,
            "Type Mismatches": 0,
            "Serialization Errors": 0,
            "Total Requests": 0,
            "Total Payload Bytes": 0,
            "Total Response Time Ms": 0.0,
            "Field Frequencies": Counter(),
            "Endpoint Frequencies": Counter()
        }
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        self.headers = [
            "Timestamp", "Endpoint", "HTTP Method", "Status Code",
            "Discovery Scan ID", "Correlation ID", "MAC Address", "Field",
            "Expected Type", "Actual Type", "Expected Value", "Actual Value",
            "Validation Result", "Severity", "Payload Size", "Serialization Time",
            "Response Time", "Thread"
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
                            if "Marker" not in item:
                                row = [item.get(k, "N/A") for k in self.headers]
                                writer.writerow(row)
                                
                    await self._update_json_stats(batch)
                        
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing REST validation queue: {e}")
                await asyncio.sleep(1.0)
                
    async def _update_json_stats(self, batch: List[Dict[str, Any]]):
        async with self.stats_lock:
            for item in batch:
                if item.get("Marker") == "REQUEST":
                    self.stats["Total Requests"] += 1
                    self.stats["Total Payload Bytes"] += item.get("Payload Size", 0)
                    self.stats["Total Response Time Ms"] += item.get("Response Time", 0.0)
                    continue
                    
                self.stats["Total Validations"] += 1
                val_result = item.get("Validation Result", "")
                
                if val_result == "PASS":
                    self.stats["Passed Validations"] += 1
                else:
                    self.stats["Failed Validations"] += 1
                    
                if val_result == "MISSING":
                    self.stats["Missing Fields"] += 1
                elif val_result == "NULL":
                    self.stats["Null Fields"] += 1
                elif val_result == "TYPE_MISMATCH":
                    self.stats["Type Mismatches"] += 1
                elif val_result == "SERIALIZATION_ERROR":
                    self.stats["Serialization Errors"] += 1
                    
                field = item.get("Field")
                if field and field != "N/A":
                    self.stats["Field Frequencies"][field] += 1
                    
                endpoint = item.get("Endpoint")
                if endpoint and endpoint != "N/A":
                    self.stats["Endpoint Frequencies"][endpoint] += 1
                    
            total_val = max(self.stats["Total Validations"], 1)
            total_req = max(self.stats["Total Requests"], 1)
            
            top_field = self.stats["Field Frequencies"].most_common(1)
            top_endpoint = self.stats["Endpoint Frequencies"].most_common(1)
            
            output_stats = {
                "Total Validations": self.stats["Total Validations"],
                "Passed Validations": self.stats["Passed Validations"],
                "Failed Validations": self.stats["Failed Validations"],
                "API Success Rate": round((self.stats["Passed Validations"] / total_val) * 100, 2),
                "Serialization Success Rate": round(((total_val - self.stats["Serialization Errors"]) / total_val) * 100, 2),
                "Missing Fields": self.stats["Missing Fields"],
                "Null Fields": self.stats["Null Fields"],
                "Type Mismatches": self.stats["Type Mismatches"],
                "Serialization Errors": self.stats["Serialization Errors"],
                "Total Requests": self.stats["Total Requests"],
                "Average Payload Size": round(self.stats["Total Payload Bytes"] / total_req, 2),
                "Average Response Time": round(self.stats["Total Response Time Ms"] / total_req, 2),
                "Most Missing Field": top_field[0][0] if top_field else "N/A",
                "Most Affected Endpoint": top_endpoint[0][0] if top_endpoint else "N/A"
            }
            
            temp_json = self.json_file_path + ".tmp"
            with open(temp_json, 'w') as jf:
                json.dump(output_stats, jf, indent=2)
            os.replace(temp_json, self.json_file_path)

    def log_validation(self, data: Dict[str, Any]):
        try:
            self.queue.put_nowait(data)
        except asyncio.QueueFull:
            logger.error("REST validation queue full!")
            
    def mark_request(self, payload_size: int = 0, response_time: float = 0.0):
        try:
            self.queue.put_nowait({
                "Marker": "REQUEST",
                "Payload Size": payload_size,
                "Response Time": response_time
            })
        except asyncio.QueueFull:
            pass

rest_verification_service = RESTVerificationService()

def get_rest_verification_service() -> RESTVerificationService:
    return rest_verification_service
