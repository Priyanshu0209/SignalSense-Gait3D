from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import statistics

class PredictiveEngine:

    def __init__(self):
        self.device_traffic_history: Dict[str, List[float]] = {}
        self.device_rssi_history: Dict[str, List[float]] = {}

    def predict_device_state(self, mac_address: str, current_rssi: float, current_traffic: float) -> Optional[Dict[str, Any]]:

        # Maintain history
        if mac_address not in self.device_traffic_history:
            self.device_traffic_history[mac_address] = []
        if mac_address not in self.device_rssi_history:
            self.device_rssi_history[mac_address] = []
            
        t_hist = self.device_traffic_history[mac_address]
        r_hist = self.device_rssi_history[mac_address]
        
        t_hist.append(current_traffic)
        r_hist.append(current_rssi)
        
        # Keep last 30 readings
        if len(t_hist) > 30:
            t_hist.pop(0)
        if len(r_hist) > 30:
            r_hist.pop(0)
            
        if len(r_hist) < 10:
            return None
            
        # Predict Disconnect (RSSI dropping rapidly)
        recent_rssi_avg = sum(r_hist[-3:]) / 3
        old_rssi_avg = sum(r_hist[:3]) / 3
        rssi_drop_rate = old_rssi_avg - recent_rssi_avg
        
        if rssi_drop_rate > 15 and recent_rssi_avg < -75:
            return {
                "type": "disconnect",
                "severity": "WARNING",
                "message": "Device moving out of range. Disconnect predicted.",
                "confidence": 75.0
            }
            
        # Predict Bandwidth Saturation (Traffic consistently high and growing)
        recent_traffic_avg = sum(t_hist[-5:]) / 5
        if recent_traffic_avg > 800: # Arbitrary high Mbps threshold for heuristic
            return {
                "type": "saturation",
                "severity": "WARNING",
                "message": "Sustained high throughput. Bandwidth saturation predicted.",
                "confidence": 85.0
            }
            
        return None

predictive_engine = PredictiveEngine()

def get_predictive_engine() -> PredictiveEngine:
    return predictive_engine
