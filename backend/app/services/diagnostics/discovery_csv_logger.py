import asyncio
import csv
import os
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Any

logger = logging.getLogger("signalsense.diagnostics.discovery")

class DiscoveryCSVLogger:

    def __init__(self, max_bytes: int = 50_000_000, backup_count: int = 5):
        self.queue = asyncio.Queue(maxsize=10000)
        self.log_dir = "logs/discovery"
        self.csv_file_path = os.path.join(self.log_dir, "device_scan.csv")
        self._running = False
        self._worker_task = None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        self.headers = [
            "Timestamp", "Discovery Scan ID", "Correlation ID", "Router IP", "Gateway",
            "MAC Address", "IP Address", "Hostname", "Manufacturer", "Vendor",
            "RSSI", "Signal Quality", "Upload Mbps", "Download Mbps", "Frequency",
            "Channel", "Latency", "Connection Status", "Online Duration", 
            "Discovery Duration", "Response Time", "Device Type", "Firmware", 
            "Model", "Missing Fields", "Warnings", "Errors", "Adapter Name", "Payload Source",
            "RSSI Ant0", "RSSI Ant1", "Tx PER", "Rx CRC PER", "False CCA", "Tx MCS", "Rx MCS"
        ]
        
        # Write header if file doesn't exist or is empty
        write_header = not os.path.exists(self.csv_file_path) or os.path.getsize(self.csv_file_path) == 0
        if write_header:
            with open(self.csv_file_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def _rotate_file_if_needed(self):

        if not os.path.exists(self.csv_file_path):
            return
            
        if os.path.getsize(self.csv_file_path) >= self.max_bytes:
            # Rotate backups
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
            
            # Re-init empty file with headers
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
                        writer.writerows(batch)
                        
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing discovery CSV queue: {e}")
                await asyncio.sleep(1.0)
                
    def log_device(self, row_data: List[Any]):

        try:
            self.queue.put_nowait(row_data)
        except asyncio.QueueFull:
            logger.error("Discovery CSV queue full! Dropping row.")

discovery_csv_logger = DiscoveryCSVLogger()

def get_discovery_csv_logger() -> DiscoveryCSVLogger:
    return discovery_csv_logger
