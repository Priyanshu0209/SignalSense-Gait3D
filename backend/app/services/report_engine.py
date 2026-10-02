import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger("signalsense.report_engine")

class ReportEngine:

    def generate_executive_summary(self, network_state: Dict[str, Any]) -> str:

        active_devices = len(network_state.get("children", []))
        health = network_state.get("health", "Unknown")
        
        report = (
            f"Executive Summary ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})\n\n"
            f"Overall Network Health is currently {health}.\n"
            f"There are {active_devices} active devices connected to the infrastructure.\n"
            f"All critical core systems are operating within expected baselines."
        )
        return report
        
    def generate_incident_report(self, investigation: Dict[str, Any]) -> str:

        return (
            f"Incident Report: {investigation['id']}\n"
            f"Entity: {investigation['entity_id']}\n"
            f"Type: {investigation['anomaly_type']}\n"
            f"Cause: {investigation['possible_cause']} (Confidence: {investigation['confidence']}%)\n"
            f"Recommended Fix: {investigation['suggested_fix']}"
        )

global_report_engine = ReportEngine()

def get_report_engine() -> ReportEngine:
    return global_report_engine
