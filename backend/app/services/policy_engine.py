import logging
from typing import Dict, Any, List
from app.schemas.processing import ProcessedDeviceState

logger = logging.getLogger("signalsense.policy_engine")

class PolicyEngine:

    def __init__(self):
        self.policies = {
            "Guest": {"max_bandwidth_mbps": 5.0, "blocked_ports": [22, 3389, 445]},
            "IoT": {"max_bandwidth_mbps": 1.0, "blocked_ports": [80, 443]},
            "Corporate": {"max_bandwidth_mbps": 1000.0, "blocked_ports": []}
        }
        
    def evaluate_compliance(self, state: ProcessedDeviceState) -> Dict[str, Any]:

        zone = "Unknown"
        if "iphone" in (state.hostname or "").lower() or "android" in (state.hostname or "").lower():
            zone = "Guest"
        elif "camera" in (state.hostname or "").lower() or "plug" in (state.hostname or "").lower():
            zone = "IoT"
        elif "macbook" in (state.hostname or "").lower() or "thinkpad" in (state.hostname or "").lower():
            zone = "Corporate"
            
        if zone not in self.policies:
            return {"compliant": True, "zone": zone, "violations": []}
            
        policy = self.policies[zone]
        violations = []
        
        # Example validation against traffic (mock logic)
        current_traffic = (state.tx_rate or 0.0) + (state.rx_rate or 0.0)
        if current_traffic > policy["max_bandwidth_mbps"]:
            violations.append(f"Bandwidth Exceeded: {current_traffic} > {policy['max_bandwidth_mbps']} Mbps")
            
        return {
            "compliant": len(violations) == 0,
            "zone": zone,
            "violations": violations
        }

global_policy_engine = PolicyEngine()

def get_policy_engine() -> PolicyEngine:
    return global_policy_engine
