import logging
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

logger = logging.getLogger("signalsense.ai_investigator")

class AIInvestigator:

    def __init__(self):
        self.investigations: Dict[str, Dict[str, Any]] = {}
        
    def trigger_investigation(self, entity_id: str, anomaly_type: str, context: Dict[str, Any]) -> str:

        inv_id = str(uuid.uuid4())
        
        # Rule-based logic (mocked for architectural representation)
        possible_cause = "Unknown"
        suggested_fix = "Manual inspection required"
        confidence = 50.0
        
        if anomaly_type == "HIGH_TRAFFIC":
            possible_cause = "Device downloading large files or compromised by botnet."
            suggested_fix = "Apply bandwidth rate-limiting policy."
            confidence = 85.5
        elif anomaly_type == "RAPID_RSSI_DROP":
            possible_cause = "Device moved to edge of coverage or physical interference (e.g. microwave)."
            suggested_fix = "Check roaming logs. Recommend adding an AP in the dead zone."
            confidence = 90.0
            
        investigation = {
            "id": inv_id,
            "entity_id": entity_id,
            "anomaly_type": anomaly_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "timeline": [
                {"time": datetime.now(timezone.utc).isoformat(), "event": f"Anomaly {anomaly_type} detected"}
            ],
            "evidence": context,
            "possible_cause": possible_cause,
            "suggested_fix": suggested_fix,
            "confidence": confidence,
            "status": "OPEN"
        }
        
        self.investigations[inv_id] = investigation
        logger.info(f"Created AI Investigation {inv_id} for {entity_id}")
        return inv_id

global_investigator = AIInvestigator()

def get_ai_investigator() -> AIInvestigator:
    return global_investigator
