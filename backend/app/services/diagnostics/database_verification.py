import asyncio
import csv
import os
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger("signalsense.diagnostics.database")

class DatabaseVerificationService:

    def __init__(self, max_bytes: int = 50_000_000, backup_count: int = 5):
        self.queue = asyncio.Queue(maxsize=100000)
        self.log_dir = "logs/database"
        self.csv_file_path = os.path.join(self.log_dir, "database_verification.csv")
        self.json_file_path = os.path.join(self.log_dir, "database_verification.json")
        self._running = False
        self._worker_task = None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self.stats_lock = asyncio.Lock()
        self.stats = {
            "Total Transactions": 0,
            "Successful Transactions": 0,
            "Failed Transactions": 0,
            "Null Overwrites": 0,
            "Unexpected Overwrites": 0,
            "Duplicate Rows": 0,
            "Rollback Count": 0,
            "Validation Success Rate": 100.0,
            "Modified Field Frequencies": Counter(),
            "Affected Device Frequencies": Counter()
        }
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        self.headers = [
            "Timestamp", "Discovery Scan ID", "Correlation ID", "Database Operation",
            "Table", "Primary Key", "MAC Address", "Field Name", "Value Before",
            "Value After", "Expected Value", "Validation Result", "Severity",
            "Execution Time", "Transaction ID", "Thread", "Exception"
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
                logger.error(f"Error flushing database verification queue: {e}")
                await asyncio.sleep(1.0)
                
    async def _update_json_stats(self, batch: List[Dict[str, Any]]):
        async with self.stats_lock:
            for item in batch:
                if item.get("Marker") == "TRANSACTION":
                    self.stats["Total Transactions"] += 1
                    if item.get("Success"):
                        self.stats["Successful Transactions"] += 1
                    else:
                        self.stats["Failed Transactions"] += 1
                    continue
                    
                val_result = item.get("Validation Result", "")
                if val_result == "NULL_OVERWRITE":
                    self.stats["Null Overwrites"] += 1
                elif val_result == "UNEXPECTED_OVERWRITE":
                    self.stats["Unexpected Overwrites"] += 1
                elif val_result == "DUPLICATE_ROW":
                    self.stats["Duplicate Rows"] += 1
                elif val_result == "ROLLBACK":
                    self.stats["Rollback Count"] += 1
                    
                field = item.get("Field Name")
                if field and field != "N/A":
                    self.stats["Modified Field Frequencies"][field] += 1
                    
                mac = item.get("MAC Address")
                if mac and mac != "N/A":
                    self.stats["Affected Device Frequencies"][mac] += 1
                    
            if self.stats["Total Transactions"] > 0:
                self.stats["Validation Success Rate"] = round(
                    (self.stats["Successful Transactions"] / self.stats["Total Transactions"]) * 100, 2
                )
                
            top_field = self.stats["Modified Field Frequencies"].most_common(1)
            top_device = self.stats["Affected Device Frequencies"].most_common(1)
            
            output_stats = {
                "Total Transactions": self.stats["Total Transactions"],
                "Successful Transactions": self.stats["Successful Transactions"],
                "Failed Transactions": self.stats["Failed Transactions"],
                "Null Overwrites": self.stats["Null Overwrites"],
                "Unexpected Overwrites": self.stats["Unexpected Overwrites"],
                "Duplicate Rows": self.stats["Duplicate Rows"],
                "Rollback Count": self.stats["Rollback Count"],
                "Validation Success Rate": self.stats["Validation Success Rate"],
                "Most Modified Field": top_field[0][0] if top_field else "N/A",
                "Most Affected Device": top_device[0][0] if top_device else "N/A"
            }
            
            temp_json = self.json_file_path + ".tmp"
            with open(temp_json, 'w') as jf:
                json.dump(output_stats, jf, indent=2)
            os.replace(temp_json, self.json_file_path)

    def log_verification(self, data: Dict[str, Any]):
        try:
            self.queue.put_nowait(data)
        except asyncio.QueueFull:
            logger.error("Database verification queue full!")
            
    def mark_transaction(self, success: bool = True):
        try:
            self.queue.put_nowait({"Marker": "TRANSACTION", "Success": success})
        except asyncio.QueueFull:
            pass

database_verification_service = DatabaseVerificationService()

def get_database_verification_service() -> DatabaseVerificationService:
    return database_verification_service
