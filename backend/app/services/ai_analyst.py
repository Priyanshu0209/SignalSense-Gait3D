from typing import List, Dict

class AIAnalyst:

    def generate_explanation(self, behavior_profile: str, anomalies: List[Dict], device_health: str) -> Dict:

        if not anomalies and device_health in ["Excellent", "Good"]:
            return {
                "message": f"Device is operating nominally as a {behavior_profile} profile.",
                "reasoning": "Telemetry falls within historical moving averages.",
                "evidence": f"Health is {device_health}. Zero active anomalies.",
                "confidence": 99.0,
                "root_cause": None
            }
            
        explanations = []
        root_causes = []
        
        for anomaly in anomalies:
            if anomaly["type"] == "TrafficSpike":
                msg = f"Bandwidth utilization spiked abnormally."
                if behavior_profile == "Streaming":
                    msg = "High bandwidth utilization detected, consistent with a sudden Video Stream or Download."
                    cause = "Background download or High-Res streaming initiated."
                elif behavior_profile == "IoT (Idle)":
                    msg = "Unexpected massive traffic from an IoT device. Potential compromise or firmware update."
                    cause = "IoT Firmware OTA Update or Botnet activity."
                else:
                    cause = "Large file transfer or software update."
                    
                explanations.append(msg)
                root_causes.append({
                    "issue": "Traffic Anomaly",
                    "possible_causes": [cause, "Network Congestion"],
                    "impact": "May degrade local network performance for other clients.",
                    "actions": ["Monitor bandwidth", "Apply QoS shaping if persistent"]
                })
                
            elif anomaly["type"] == "SignalDrop":
                explanations.append("The wireless signal degraded drastically in a short timeframe.")
                root_causes.append({
                    "issue": "Structural Degradation",
                    "possible_causes": ["Physical movement to a deadzone", "Interference (Microwave/Bluetooth)", "Obstruction (Doors closed)"],
                    "impact": "High packet loss, likely disconnects.",
                    "actions": ["Relocate device", "Check for RF interference"]
                })
                
        return {
            "message": " ".join(explanations) if explanations else f"Device health is {device_health}.",
            "reasoning": "Detected deviations from adaptive baselines.",
            "evidence": ", ".join([a["description"] for a in anomalies]) if anomalies else "Heuristic analysis",
            "confidence": 90.0 if anomalies else 75.0,
            "root_cause": root_causes[0] if root_causes else None
        }

ai_analyst = AIAnalyst()

def get_ai_analyst() -> AIAnalyst:
    return ai_analyst
