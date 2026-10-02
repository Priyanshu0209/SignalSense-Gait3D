import asyncio
import csv
import json
import os
import time
from datetime import datetime, timezone
import logging
import aiofiles
from app.services.research.research_manager import get_research_manager

logger = logging.getLogger("signalsense.dataset_writer")

class DatasetWriter:
    def __init__(self):
        self.output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "datasets"))
        self.session_id = None
        self.csv_path = None
        self.metadata_path = None
        self._csv_file = None
        self._csv_writer = None
        self.is_running = False
        
        # Ensure output dir exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Async queue for non-blocking writes
        self.queue = asyncio.Queue()
        self.writer_task = None
        
        # Headers defined by requirements
        self.headers = [
            "Timestamp", "Session ID", "Device Name", "MAC Address",
            "Ground Truth Distance", "Ground Truth Direction", "Orientation",
            "LOS", "Environment", "RSSI", "Noise", "SNR", "Channel", "Frequency",
            "Bandwidth", "Signal Quality", "Tx Rate", "Rx Rate", "Collector Device", "Router", "Temperature"
        ]

    async def start_session(self, session_name: str, environment: str, collector_device: str):
        if self.is_running:
            logger.warning("Session already running. Stop it first.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in session_name if c.isalnum() or c in ('_', '-')).strip()
        
        self.session_id = f"dataset_{safe_name}_{timestamp}" if safe_name else f"dataset_{timestamp}"
        self.csv_path = os.path.join(self.output_dir, f"{self.session_id}.csv")
        self.metadata_path = os.path.join(self.output_dir, f"{self.session_id}_metadata.json")
        
        # Initialize CSV file with headers
        async with aiofiles.open(self.csv_path, mode='w', newline='') as f:
            # We use a synchronous writer via string formatting or just raw string joining for async
            header_str = ",".join(self.headers) + "\n"
            await f.write(header_str)
            
        self.is_running = True
        self.writer_task = asyncio.create_task(self._process_queue())
        logger.info(f"Dataset session {self.session_id} started. Writing to {self.csv_path}")

    async def enqueue_sample(self, sample: dict):
        if not self.is_running:
            return
        await self.queue.put(sample)

    async def _process_queue(self):
        while self.is_running or not self.queue.empty():
            try:
                sample = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                try:
                    async with aiofiles.open(self.csv_path, mode='a', newline='') as f:
                        row = [str(sample.get(h, "")) for h in self.headers]
                        # Minimal escaping for CSV
                        escaped_row = []
                        for cell in row:
                            if "," in cell or '"' in cell or "\n" in cell:
                                escaped = cell.replace('"', '""')
                                escaped_row.append(f'"{escaped}"')
                            else:
                                escaped_row.append(cell)
                                
                        await f.write(",".join(escaped_row) + "\n")
                except Exception as e:
                    logger.error(f"Failed to write sample to CSV: {e}")
                finally:
                    self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dataset writer loop: {e}")

    async def stop_session(self, metadata: dict):
        if not self.is_running:
            return
            
        self.is_running = False
        if self.writer_task:
            try:
                # Wait for remaining items in the queue to be written
                await asyncio.wait_for(self.queue.join(), timeout=10.0)
                self.writer_task.cancel()
                await self.writer_task
            except Exception as e:
                pass
                
        # Write metadata
        if self.metadata_path:
            try:
                async with aiofiles.open(self.metadata_path, mode='w') as f:
                    await f.write(json.dumps(metadata, indent=4))
            except Exception as e:
                logger.error(f"Failed to write dataset metadata: {e}")
                
        logger.info(f"Dataset session {self.session_id} stopped.")
        self.session_id = None
        self.csv_path = None
        self.metadata_path = None

dataset_writer = DatasetWriter()

def get_dataset_writer() -> DatasetWriter:
    return dataset_writer
