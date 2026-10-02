from typing import Dict, List, Any
from app.schemas.processing import ProcessedDeviceState
from app.services.device_state_manager import get_device_state_manager
from app.services.graph_database import get_graph_database, GraphNode, GraphEdge

class DigitalTwinEngine:

    def __init__(self):
        self.state_manager = get_device_state_manager()
        self.graph = get_graph_database()
        self.device_lifecycles: Dict[str, Dict[str, Any]] = {}
        
    def _update_lifecycle(self, device: ProcessedDeviceState):
        mac = device.mac_address
        if mac not in self.device_lifecycles:
            self.device_lifecycles[mac] = {
                "first_seen": device.last_seen,
                "connection_count": 1,
                "total_uptime_seconds": 0,
                "preferred_band": "2.4GHz", # Mock
                "historical_profiles": set()
            }
        else:
            self.device_lifecycles[mac]["total_uptime_seconds"] += 5 # Assuming 5s tick
            self.device_lifecycles[mac]["historical_profiles"].add(device.behavior_profile)
            
    def get_network_knowledge_graph(self) -> Dict[str, Any]:

        devices = self.state_manager.get_all_devices()
        
        # Upsert Gateways/Routers into Graph
        for d in devices:
            # Sync to Graph Database
            router_node = GraphNode(
                id=d.router_id,
                type="Router",
                properties={"health": "Good", "location": "HQ"}
            )
            self.graph.add_node(router_node)
            
            client_node = GraphNode(
                id=d.mac_address,
                type=d.device_type or "Client",
                properties={
                    "hostname": d.hostname,
                    "health": d.health_score,
                    "profile": d.behavior_profile,
                    "rssi": d.current_rssi.value
                }
            )
            self.graph.add_node(client_node)
            
            if d.online_status:
                self.graph.add_edge(GraphEdge(
                    source=d.mac_address,
                    target=d.router_id,
                    relationship="Connected"
                ))

        # Legacy return format for backwards compatibility with UI
        graph_dict = {
            "id": "GATEWAY",
            "type": "Router",
            "health": "Good",
            "children": []
        }
        
        for d in devices:
            self._update_lifecycle(d)
            if not d.online_status:
                continue
                
            node = {
                "id": d.mac_address,
                "hostname": d.hostname or d.mac_address,
                "type": d.device_type or "Unknown",
                "health": d.health_score,
                "profile": d.behavior_profile,
                "telemetry": {
                    "rssi": d.current_rssi.value,
                    "traffic": (d.tx_rate or 0) + (d.rx_rate or 0)
                }
            }
            graph_dict["children"].append(node)
            
        return graph_dict

digital_twin_engine = DigitalTwinEngine()

def get_digital_twin_engine() -> DigitalTwinEngine:
    return digital_twin_engine
