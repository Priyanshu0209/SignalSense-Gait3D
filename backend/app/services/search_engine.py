import logging
from typing import List, Dict, Any
from app.services.graph_database import get_graph_database, GraphNode

logger = logging.getLogger("signalsense.search_engine")

class SearchEngine:

    def __init__(self):
        self.graph = get_graph_database()
        
    def search(self, query_string: str) -> List[Dict[str, Any]]:

        results = []
        q = query_string.lower()
        
        # Simplified deterministic natural language parsing
        target_type = None
        if "iot" in q:
            target_type = "IoT"
        elif "router" in q:
            target_type = "Router"
            
        unstable_filter = "unstable" in q or "poor health" in q
        
        for node in self.graph.nodes.values():
            match = True
            if target_type and node.type.lower() != target_type.lower():
                match = False
            if unstable_filter and node.properties.get("health", "Good") not in ["Poor", "Critical"]:
                match = False
                
            if match:
                results.append({"id": node.id, "type": node.type, "properties": node.properties})
                
        return results

global_search_engine = SearchEngine()

def get_search_engine() -> SearchEngine:
    return global_search_engine
