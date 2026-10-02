import asyncio
import csv
import os
import logging
from datetime import datetime, timezone
from typing import Optional, Any

logger = logging.getLogger("signalsense.diagnostics")

class DiagnosticsLogger:

    def __init__(self):
        self.queue = asyncio.Queue(maxsize=5000)
        self.csv_file_path = "logs/pipeline/rssi_pipeline_trace.csv"
        self._running = False
        self._worker_task = None
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
        
        # Create CSV header if not exists
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", 
                    "pipeline_layer", 
                    "mac_address", 
                    "rssi_value", 
                    "status", 
                    "additional_info"
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
                    with open(self.csv_file_path, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(batch)
                        
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing diagnostics queue: {e}")
                await asyncio.sleep(1.0)
                
    def _enqueue_log(self, layer: str, mac_address: str, rssi: Optional[Any], info: str = ""):
        now = datetime.now(timezone.utc).isoformat()
        
        status = "OK"
        if rssi is None or rssi == "N/A" or rssi == "":
            status = "MISSING"
            logger.warning(f"[Diagnostics] RSSI Missing at {layer} for {mac_address}!")
            
        row = [now, layer, mac_address, str(rssi), status, info]
        
        try:
            self.queue.put_nowait(row)
        except asyncio.QueueFull:
            logger.error("Diagnostics queue full! Dropping diagnostic trace.")

    # Specific Layer Tracking
    
    def log_router_layer(self, mac_address: str, rssi: Optional[Any], info: str = ""):
        self._enqueue_log("1_ROUTER_ADAPTER", mac_address, rssi, info)
        
    def log_processor_layer(self, mac_address: str, rssi: Optional[Any], info: str = ""):
        self._enqueue_log("2_PROCESSOR", mac_address, rssi, info)
        
    def log_state_manager_layer(self, mac_address: str, rssi: Optional[Any], info: str = ""):
        self._enqueue_log("3_STATE_MANAGER", mac_address, rssi, info)
        
    def log_database_layer(self, mac_address: str, rssi: Optional[Any], info: str = ""):
        self._enqueue_log("4_DATABASE", mac_address, rssi, info)
        
    def log_api_layer(self, mac_address: str, rssi: Optional[Any], info: str = ""):
        self._enqueue_log("5_REST_API", mac_address, rssi, info)

diagnostics_logger = DiagnosticsLogger()

def get_diagnostics_logger() -> DiagnosticsLogger:
    return diagnostics_logger
