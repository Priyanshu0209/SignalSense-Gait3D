import logging
from typing import Dict, Any

logger = logging.getLogger("signalsense.network_memory")

class NetworkMemory:

    def __init__(self):
        # In a full implementation, these would be backed by Time Series queries
        self.device_baselines: Dict[str, Dict[str, Any]] = {}
        
    def _initialize_baseline(self, mac_address: str):
        if mac_address not in self.device_baselines:
            self.device_baselines[mac_address] = {
                "avg_traffic_mbps": 0.0,
                "std_dev_traffic": 0.0,
                "typical_rssi": -60,
                "active_hours": set(),
                "sample_count": 0
            }
            
    def observe(self, mac_address: str, traffic: float, rssi: int, hour_of_day: int):

        self._initialize_baseline(mac_address)
        
        baseline = self.device_baselines[mac_address]
        n = baseline["sample_count"]
        
        # Incremental moving average calculation
        baseline["avg_traffic_mbps"] = (baseline["avg_traffic_mbps"] * n + traffic) / (n + 1)
        baseline["typical_rssi"] = int((baseline["typical_rssi"] * n + rssi) / (n + 1))
        baseline["active_hours"].add(hour_of_day)
        baseline["sample_count"] += 1
        
    def is_anomalous(self, mac_address: str, traffic: float, rssi: int, hour_of_day: int) -> bool:

        self._initialize_baseline(mac_address)
        baseline = self.device_baselines[mac_address]
        
        if baseline["sample_count"] < 100:
            return False # Not enough data to confidently flag an anomaly
            
        # Example dynamic threshold: traffic is 3x higher than historical average
        if traffic > (baseline["avg_traffic_mbps"] * 3) and baseline["avg_traffic_mbps"] > 1:
            return True
            
        # Device active at unusual hour
        if hour_of_day not in baseline["active_hours"]:
            return True
            
        return False

global_network_memory = NetworkMemory()

def get_network_memory() -> NetworkMemory:
    return global_network_memory
