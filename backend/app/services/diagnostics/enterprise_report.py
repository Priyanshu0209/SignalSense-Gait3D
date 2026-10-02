import asyncio
import csv
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("signalsense.diagnostics.report")

class EnterpriseDiagnosticReport:

    def __init__(self, max_bytes: int = 50_000_000, backup_count: int = 5):
        self.queue = asyncio.Queue(maxsize=2000)
        self.log_dir = "logs/reports"
        self.csv_file_path = os.path.join(self.log_dir, "discovery_report.csv")
        self.json_file_path = os.path.join(self.log_dir, "discovery_report.json")
        self._running = False
        self._worker_task = None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        self.headers = [
            "Timestamp", "Discovery Scan ID", "Correlation ID",
            "Discovery Success Rate", "Telemetry Success Rate", "RSSI Success Rate",
            "Signal Quality Success Rate", "Database Success Rate", "REST Success Rate",
            "Frontend Success Rate", "Pipeline Success Rate",
            "Average Discovery Time", "Average Response Time",
            "Average RSSI", "Average Signal Quality", "Average Latency",
            "Total Devices", "Online Devices", "Offline Devices",
            "Total Missing Fields", "Missing Percentage",
            "Top Missing Field", "Top Failed Device", "Top Failed Layer",
            "Database Null Overwrites", "Database Rollbacks",
            "REST Null Fields", "REST Missing Fields",
            "Frontend Null Values", "Frontend Chart Errors", "Frontend Timeline Errors",
            "Overall Health Score", "Likely Root Cause",
            "Priority", "Suggested Investigation Layer", "Confidence Score"
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
                    
                    # Write CSV
                    with open(self.csv_file_path, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        for item in batch:
                            row = [item.get(k, "N/A") for k in self.headers]
                            writer.writerow(row)
                            
                    # Write JSON (last report is the latest)
                    latest = batch[-1]
                    temp_json = self.json_file_path + ".tmp"
                    with open(temp_json, 'w') as jf:
                        json.dump(latest, jf, indent=2)
                    os.replace(temp_json, self.json_file_path)
                        
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error flushing diagnostic report queue: {e}")
                await asyncio.sleep(1.0)

    def _safe_read_json(self, path: str) -> Dict[str, Any]:

        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    async def generate_report(self, scan_id: str, correlation_id: str, 
                               discovery_duration: float, total_devices: int,
                               online_devices: int, avg_rssi: float):

        # Read all module JSON stats
        summary_stats = self._safe_read_json("logs/discovery/latest_summary.json")
        missing_stats = self._safe_read_json("logs/discovery/missing_fields.json")
        db_stats = self._safe_read_json("logs/database/database_verification.json")
        rest_stats = self._safe_read_json("logs/api/rest_validation.json")
        fe_stats = self._safe_read_json("logs/frontend/frontend_validation.json")
        
        # Calculate success rates
        db_success = db_stats.get("Validation Success Rate", 100.0)
        rest_success = rest_stats.get("API Success Rate", 100.0)
        fe_success = fe_stats.get("Validation Success Rate", 100.0)
        missing_pct = missing_stats.get("Missing Percentage", 0.0)
        telemetry_success = round(100.0 - missing_pct, 2)
        
        # Pipeline success = average of all layers
        pipeline_success = round((db_success + rest_success + fe_success + telemetry_success) / 4, 2)
        
        # Health Score (0-100)
        health_score = round(pipeline_success * 0.7 + (100.0 if total_devices > 0 else 0.0) * 0.3, 1)
        
        # Root cause analysis
        top_missing = missing_stats.get("Most Missing Field", "N/A")
        top_failed_device = missing_stats.get("Most Affected Device", "N/A")
        top_failed_layer = missing_stats.get("Most Affected Layer", "N/A")
        
        # Determine likely root cause
        if missing_pct > 50:
            root_cause = f"Router adapter not providing {top_missing}"
            priority = "CRITICAL"
            suggested_layer = "Router Adapter"
            confidence = 90
        elif db_stats.get("Null Overwrites", 0) > 0:
            root_cause = f"Database NULL overwrites detected on {db_stats.get('Most Modified Field', 'unknown')}"
            priority = "HIGH"
            suggested_layer = "Database"
            confidence = 80
        elif rest_stats.get("Missing Fields", 0) > 0:
            root_cause = f"REST API serializing null {rest_stats.get('Most Missing Field', 'unknown')}"
            priority = "MEDIUM"
            suggested_layer = "REST API"
            confidence = 70
        elif fe_stats.get("Chart Errors", 0) > 0:
            root_cause = "Frontend chart rendering failures"
            priority = "MEDIUM"
            suggested_layer = "Frontend"
            confidence = 60
        else:
            root_cause = "No significant issues detected"
            priority = "LOW"
            suggested_layer = "None"
            confidence = 95
            
        report = {
            "Timestamp": datetime.now(timezone.utc).isoformat(),
            "Discovery Scan ID": scan_id,
            "Correlation ID": correlation_id,
            "Discovery Success Rate": 100.0 if total_devices > 0 else 0.0,
            "Telemetry Success Rate": telemetry_success,
            "RSSI Success Rate": round(100.0 - (summary_stats.get("RSSI Missing Count", 0) / max(total_devices, 1)) * 100, 2),
            "Signal Quality Success Rate": round(100.0 - (summary_stats.get("Signal Missing Count", 0) / max(total_devices, 1)) * 100, 2),
            "Database Success Rate": db_success,
            "REST Success Rate": rest_success,
            "Frontend Success Rate": fe_success,
            "Pipeline Success Rate": pipeline_success,
            "Average Discovery Time": discovery_duration,
            "Average Response Time": rest_stats.get("Average Response Time", 0.0),
            "Average RSSI": avg_rssi if avg_rssi != "N/A" else 0.0,
            "Average Signal Quality": "N/A",
            "Average Latency": "N/A",
            "Total Devices": total_devices,
            "Online Devices": online_devices,
            "Offline Devices": total_devices - online_devices,
            "Total Missing Fields": missing_stats.get("Total Missing Fields", 0),
            "Missing Percentage": missing_pct,
            "Top Missing Field": top_missing,
            "Top Failed Device": top_failed_device,
            "Top Failed Layer": top_failed_layer,
            "Database Null Overwrites": db_stats.get("Null Overwrites", 0),
            "Database Rollbacks": db_stats.get("Rollback Count", 0),
            "REST Null Fields": rest_stats.get("Null Fields", 0),
            "REST Missing Fields": rest_stats.get("Missing Fields", 0),
            "Frontend Null Values": fe_stats.get("Null Values", 0),
            "Frontend Chart Errors": fe_stats.get("Chart Errors", 0),
            "Frontend Timeline Errors": fe_stats.get("Timeline Errors", 0),
            "Overall Health Score": health_score,
            "Likely Root Cause": root_cause,
            "Priority": priority,
            "Suggested Investigation Layer": suggested_layer,
            "Confidence Score": confidence
        }
        
        try:
            self.queue.put_nowait(report)
        except asyncio.QueueFull:
            logger.error("Diagnostic report queue full!")

enterprise_diagnostic_report = EnterpriseDiagnosticReport()

def get_enterprise_diagnostic_report() -> EnterpriseDiagnosticReport:
    return enterprise_diagnostic_report
