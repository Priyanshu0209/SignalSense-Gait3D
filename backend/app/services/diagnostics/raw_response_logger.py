import asyncio
import csv
import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("signalsense.diagnostics.raw")

class RawResponseLogger:

    def __init__(self):
        self.queue = asyncio.Queue(maxsize=1000)
        self.log_dir = "logs/router/raw"
        self.csv_index_path = os.path.join(self.log_dir, "index.csv")
        self._running = False
        self._worker_task = None
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create CSV header if not exists
        if not os.path.exists(self.csv_index_path):
            with open(self.csv_index_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", 
                    "router_ip", 
                    "gateway", 
                    "response_time_ms", 
                    "discovery_duration_ms", 
                    "error_status",
                    "file_reference"
                ])
                
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
                    # Write to index.csv
                    with open(self.csv_index_path, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        for item in batch:
                            # Unpack item
                            (timestamp_str, router_ip, gateway, response_time, duration, error, file_ref, raw_payload) = item
                            
                            # Write index row
                            writer.writerow([
                                timestamp_str, router_ip, gateway, response_time, duration, error, file_ref
                            ])
                            
                            # Dump JSON/String payload exactly as received
                            payload_path = os.path.join(self.log_dir, file_ref)
                            with open(payload_path, 'w') as pf:
                                if isinstance(raw_payload, (dict, list)):
                                    json.dump(raw_payload, pf, indent=2)
                                else:
                                    pf.write(str(raw_payload))
                                    
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing raw response queue: {e}")
                await asyncio.sleep(1.0)
                
    def log_response(
        self,
        router_ip: str,
        gateway: str,
        response_time_ms: float,
        discovery_duration_ms: float,
        error_status: Optional[str],
        raw_payload: any
    ):

        now = datetime.now(timezone.utc)
        timestamp_str = now.isoformat()
        
        # File naming pattern: 2026-07-21T103322_192.168.1.1_raw.json
        clean_time = now.strftime("%Y%m%dT%H%M%S")
        clean_ip = router_ip.replace(".", "_").replace(":", "_")
        file_ref = f"{clean_time}_{clean_ip}_raw.json" if isinstance(raw_payload, (dict, list)) else f"{clean_time}_{clean_ip}_raw.txt"
        
        row = (
            timestamp_str,
            router_ip,
            gateway,
            f"{response_time_ms:.2f}",
            f"{discovery_duration_ms:.2f}",
            error_status or "None",
            file_ref,
            raw_payload
        )
        
        try:
            self.queue.put_nowait(row)
        except asyncio.QueueFull:
            logger.error("Raw response queue full! Dropping pristine payload capture.")

raw_response_logger = RawResponseLogger()

def get_raw_response_logger() -> RawResponseLogger:
    return raw_response_logger
