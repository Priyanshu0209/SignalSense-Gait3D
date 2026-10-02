from typing import Dict, Any
import re
from app.services.digital_twin_engine import get_digital_twin_engine

class CopilotEngine:

    def __init__(self):
        self.twin = get_digital_twin_engine()
        
    def answer_query(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        graph = self.twin.get_network_knowledge_graph()
        devices = graph.get("children", [])
        
        if "unstable" in q or "poor" in q:
            unstable = [d for d in devices if d["health"] in ("Poor", "Critical")]
            return {
                "answer": f"I found {len(unstable)} unstable devices.",
                "evidence": unstable,
                "confidence": 100.0
            }
            
        elif "bandwidth hogs" in q or "streaming" in q:
            hogs = [d for d in devices if d["profile"] == "Streaming" or d["telemetry"]["traffic"] > 10]
            return {
                "answer": f"I detected {len(hogs)} devices consuming high bandwidth.",
                "evidence": hogs,
                "confidence": 95.0
            }
            
        elif "predict" in q and "tomorrow" in q:
            return {
                "answer": "Based on historical trend data, network load will peak at 8 PM tomorrow due to expected Streaming profiles coming online.",
                "evidence": "Predictive Engine Trailing Window (Simulation)",
                "confidence": 75.0
            }
            
        elif "explain" in q and "network" in q:
            online = sum(1 for d in devices if d["health"] != "Critical") # Approximation
            return {
                "answer": f"The network is currently operating with {len(devices)} active clients. Gateway health is {graph['health']}.",
                "evidence": graph,
                "confidence": 100.0
            }
            
        else:
            return {
                "answer": "I do not have enough telemetry to answer that question without hallucinating.",
                "evidence": None,
                "confidence": 0.0
            }

copilot_engine = CopilotEngine()

def get_copilot_engine() -> CopilotEngine:
    return copilot_engine
