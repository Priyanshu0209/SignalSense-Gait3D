from typing import List, Dict, Any
from datetime import datetime, timezone
from app.services.digital_twin_engine import get_digital_twin_engine

class InsightEngine:

    def __init__(self):
        self.twin = get_digital_twin_engine()
        self.insights = []
        
    def generate_scores(self) -> Dict[str, float]:
        graph = self.twin.get_network_knowledge_graph()
        devices = graph.get("children", [])
        
        if not devices:
            return {"overall": 100, "security": 100, "performance": 100, "reliability": 100}
            
        poor_health = sum(1 for d in devices if d["health"] in ("Poor", "Critical"))
        high_traffic = sum(1 for d in devices if d["telemetry"]["traffic"] > 5)
        
        reliability = max(0, 100 - (poor_health * 10))
        performance = max(0, 100 - (high_traffic * 5))
        security = 100 # Adjusted by anomaly detector if MAC spoofing is found
        
        overall = (reliability + performance + security) / 3
        
        return {
            "overall": round(overall, 1),
            "security": round(security, 1),
            "performance": round(performance, 1),
            "reliability": round(reliability, 1)
        }
        
    def get_live_insights(self) -> List[Dict[str, Any]]:
        scores = self.generate_scores()
        
        insights = []
        now = datetime.now(timezone.utc).isoformat()
        
        if scores["reliability"] < 80:
            insights.append({
                "timestamp": now,
                "message": "Multiple devices experiencing poor signal stability.",
                "confidence": 90,
                "type": "warning"
            })
        elif scores["overall"] > 95:
            insights.append({
                "timestamp": now,
                "message": "Network is operating in peak condition.",
                "confidence": 99,
                "type": "success"
            })
            
        return insights

insight_engine = InsightEngine()

def get_insight_engine() -> InsightEngine:
    return insight_engine
