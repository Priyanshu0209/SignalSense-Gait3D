import asyncio
import csv
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("signalsense.diagnostics.summary")

class DiscoverySummaryLogger:

    def __init__(self, max_bytes: int = 50_000_000, backup_count: int = 5):
        self.queue = asyncio.Queue(maxsize=2000)
        self.log_dir = "logs/discovery"
        self.csv_file_path = os.path.join(self.log_dir, "discovery_summary.csv")
        self.json_file_path = os.path.join(self.log_dir, "latest_summary.json")
        self._running = False
        self._worker_task = None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        self.headers = [
            "Timestamp", "Discovery Scan ID", "Correlation ID", "Router IP", "Gateway",
            "Discovery Duration (ms)", "Router Response Time (ms)", "Processing Time (ms)", 
            "Database Time (ms)", "API Time (ms)", "Frontend Time (ms)", "Total Devices", 
            "Online Devices", "Offline Devices", "New Devices", "Disconnected Devices", 
            "Updated Devices", "Metadata Changes", "Average RSSI", "Minimum RSSI", 
            "Maximum RSSI", "Average Signal Quality", "Average Latency", "Average Upload", 
            "Average Download", "RSSI Missing Count", "Signal Missing Count", 
            "Hostname Missing Count", "Manufacturer Missing Count", "Vendor Missing Count", 
            "Frequency Missing Count", "Channel Missing Count", "Firmware Missing Count", 
            "Model Missing Count", "CPU Missing Count", "RAM Missing Count", 
            "Warnings", "Errors", "Validation Result"
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
                    
                    # Write to CSV
                    with open(self.csv_file_path, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        for item in batch:
                            row = [item.get(k, "N/A") for k in self.headers]
                            writer.writerow(row)
                            
                    # Write latest item to JSON atomically
                    latest_item = batch[-1]
                    temp_json = self.json_file_path + ".tmp"
                    with open(temp_json, 'w') as jf:
                        json.dump(latest_item, jf, indent=2)
                    os.replace(temp_json, self.json_file_path)
                        
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing discovery summary queue: {e}")
                await asyncio.sleep(1.0)
                
    def log_summary(self, summary_data: Dict[str, Any]):

        try:
            self.queue.put_nowait(summary_data)
        except asyncio.QueueFull:
            logger.error("Discovery summary queue full! Dropping summary.")

discovery_summary_logger = DiscoverySummaryLogger()

def get_discovery_summary_logger() -> DiscoverySummaryLogger:
    return discovery_summary_logger
