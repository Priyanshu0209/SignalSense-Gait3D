import asyncio
import csv
import os
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger("signalsense.diagnostics.analyzer")

class MissingFieldAnalyzer:

    def __init__(self, max_bytes: int = 50_000_000, backup_count: int = 5):
        self.queue = asyncio.Queue(maxsize=100000)
        self.log_dir = "logs/discovery"
        self.csv_file_path = os.path.join(self.log_dir, "missing_fields.csv")
        self.json_file_path = os.path.join(self.log_dir, "missing_fields.json")
        self._running = False
        self._worker_task = None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # In-memory stats for JSON output
        self.stats_lock = asyncio.Lock()
        self.stats = {
            "Total Missing Fields": 0,
            "Total Devices Checked": 0,
            "Missing Percentage": 0.0,
            "Field Frequencies": Counter(),
            "Device Frequencies": Counter(),
            "Layer Frequencies": Counter(),
            "Severity Frequencies": Counter()
        }
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        self.headers = [
            "Timestamp", "Discovery Scan ID", "Correlation ID", "Router IP",
            "MAC Address", "Hostname", "Field Name", "Expected Type", "Actual Value",
            "Pipeline Layer", "Severity", "Recommendation", "Discovery Duration", "Adapter"
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
                            
                    # Update JSON safely
                    await self._update_json_stats(batch)
                        
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing missing fields queue: {e}")
                await asyncio.sleep(1.0)
                
    async def _update_json_stats(self, batch: List[Dict[str, Any]]):
        async with self.stats_lock:
            for item in batch:
                if item.get("Marker") == "DEVICE_CHECKED":
                    self.stats["Total Devices Checked"] += 1
                    continue
                    
                self.stats["Total Missing Fields"] += 1
                field = item.get("Field Name", "Unknown")
                mac = item.get("MAC Address", "Unknown")
                layer = item.get("Pipeline Layer", "Unknown")
                sev = item.get("Severity", "Unknown")
                
                self.stats["Field Frequencies"][field] += 1
                self.stats["Device Frequencies"][mac] += 1
                self.stats["Layer Frequencies"][layer] += 1
                self.stats["Severity Frequencies"][sev] += 1
                
            total_devs = max(self.stats["Total Devices Checked"], 1)
            # Assuming 19 required fields per device
            expected_total_fields = total_devs * 19
            if expected_total_fields > 0:
                self.stats["Missing Percentage"] = round(
                    (self.stats["Total Missing Fields"] / expected_total_fields) * 100, 2
                )
                
            top_field = self.stats["Field Frequencies"].most_common(1)
            top_device = self.stats["Device Frequencies"].most_common(1)
            top_layer = self.stats["Layer Frequencies"].most_common(1)
            
            output_stats = {
                "Total Missing Fields": self.stats["Total Missing Fields"],
                "Total Devices Checked": self.stats["Total Devices Checked"],
                "Missing Percentage": self.stats["Missing Percentage"],
                "Most Missing Field": top_field[0][0] if top_field else "N/A",
                "Most Affected Device": top_device[0][0] if top_device else "N/A",
                "Most Affected Layer": top_layer[0][0] if top_layer else "N/A",
                "Severity Distribution": dict(self.stats["Severity Frequencies"])
            }
            
            temp_json = self.json_file_path + ".tmp"
            with open(temp_json, 'w') as jf:
                json.dump(output_stats, jf, indent=2)
            os.replace(temp_json, self.json_file_path)

    def log_missing_field(self, field_data: Dict[str, Any]):

        try:
            self.queue.put_nowait(field_data)
        except asyncio.QueueFull:
            logger.error("Missing fields queue full! Dropping row.")
            
    def mark_device_checked(self):

        try:
            self.queue.put_nowait({"Marker": "DEVICE_CHECKED"})
        except asyncio.QueueFull:
            pass

missing_field_analyzer = MissingFieldAnalyzer()

def get_missing_field_analyzer() -> MissingFieldAnalyzer:
    return missing_field_analyzer
