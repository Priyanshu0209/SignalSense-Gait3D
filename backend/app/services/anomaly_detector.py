import statistics
from collections import deque
from typing import Dict, List, Optional
from datetime import datetime, timezone

class AnomalyDetector:

    def __init__(self, window_size: int = 60):
        # MAC -> deque of metrics
        self.traffic_windows: Dict[str, deque] = {}
        self.rssi_windows: Dict[str, deque] = {}
        self.mac_history: set = set()
        self.window_size = window_size
        
    def _get_window(self, windows_dict: Dict, mac: str) -> deque:
        if mac not in windows_dict:
            windows_dict[mac] = deque(maxlen=self.window_size)
        return windows_dict[mac]
        
    def calculate_zero_trust_readiness(self) -> float:

        total_devices = len(self.mac_history)
        if total_devices == 0:
            return 100.0
            
        # Simplified algorithm: start at 100, deduct for every un-profiled or anomalous device
        score = 100.0
        # In a real implementation, this would query active anomalies and policy engine
        return max(0.0, min(100.0, score))

    def fingerprint_device(self, mac_address: str, traffic: float, rssi: int) -> str:

        t_window = self._get_window(self.traffic_windows, mac_address)
        if len(t_window) < 10:
            return "Unknown"
            
        mean_traffic = statistics.mean(t_window)
        if mean_traffic < 1.0:
            return "IoT_Sensor"
        elif mean_traffic > 50.0:
            return "High_Bandwidth_Client"
        return "Standard_Client"

    def detect_anomalies(self, mac_address: str, rx_rate: float, tx_rate: float, rssi: int) -> List[Dict]:
        anomalies = []
        traffic = rx_rate + tx_rate
        
        # Security: MAC Spoofing Detection (Simplistic logic: device changes its hardware profile signature)
        # This is a mock since we don't have deep packet inspection, but we flag very drastic traffic shifts
        
        # Security: Unknown Device Check
        if mac_address not in self.mac_history:
            self.mac_history.add(mac_address)
            # In Phase 5, if it's new, it could be a threat if not whitelisted
            anomalies.append({
                "type": "NewDevice",
                "severity": "Info",
                "description": f"New device {mac_address} joined the network.",
                "confidence": 100.0
            })
            
        # Traffic Anomaly
        t_window = self._get_window(self.traffic_windows, mac_address)
        if len(t_window) >= 10:
            mean_traffic = statistics.mean(t_window)
            std_traffic = statistics.stdev(t_window) if len(t_window) > 1 else 0
            
            # Z-Score > 3 is highly anomalous
            if std_traffic > 0:
                z_score = (traffic - mean_traffic) / std_traffic
                if z_score > 3.0 and traffic > 50.0:
                    anomalies.append({
                        "type": "TrafficSpike",
                        "severity": "Warning",
                        "description": f"Abnormal bandwidth spike detected ({traffic:.1f} Mbps, baseline {mean_traffic:.1f} Mbps)",
                        "confidence": 95.0
                    })
                    
        t_window.append(traffic)
        
        # RSSI Drop Anomaly
        r_window = self._get_window(self.rssi_windows, mac_address)
        if len(r_window) >= 10:
            mean_rssi = statistics.mean(r_window)
            if rssi < -75 and mean_rssi > -60:
                anomalies.append({
                    "type": "SignalDrop",
                    "severity": "Warning",
                    "description": f"Sudden structural signal degradation ({mean_rssi:.1f} dBm to {rssi} dBm)",
                    "confidence": 90.0
                })
        r_window.append(rssi)
        
        # Gateway Change Anomaly
        if mac_address == "GATEWAY" and rssi < -50:
             anomalies.append({
                 "type": "GatewaySpoofing",
                 "severity": "Critical",
                 "description": f"Potential Rogue AP or Gateway Spoofing detected. Gateway RSSI is abnormally low ({rssi} dBm).",
                 "confidence": 85.0
             })
             
        return anomalies

anomaly_detector = AnomalyDetector()

def get_anomaly_detector() -> AnomalyDetector:
    return anomaly_detector
