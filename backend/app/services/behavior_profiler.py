from collections import deque
from typing import Dict
from app.schemas.router import ConnectedDevice

class BehaviorProfiler:

    def __init__(self, history_size: int = 120):
        # Maps MAC to deque of (tx_rate, rx_rate, connection_duration)
        self.device_history: Dict[str, deque] = {}
        self.history_size = history_size

    def _get_history(self, mac: str) -> deque:
        if mac not in self.device_history:
            self.device_history[mac] = deque(maxlen=self.history_size)
        return self.device_history[mac]

    def profile_device(self, device: ConnectedDevice) -> str:
        history = self._get_history(device.mac_address)
        history.append({
            "tx": device.tx_rate or 0.0,
            "rx": device.rx_rate or 0.0,
            "duration": device.connection_duration_seconds or 0
        })

        if len(history) < 5:
            # Need some baseline
            if device.device_type and "iot" in device.device_type.lower():
                return "IoT Device"
            return "Unknown"
            
        avg_rx = sum(h["rx"] for h in history) / len(history)
        avg_tx = sum(h["tx"] for h in history) / len(history)
        
        # High sustained RX -> Streaming
        if avg_rx > 15.0 and avg_tx < 2.0:
            return "Streaming"
            
        # Balanced TX/RX with high variance -> Gaming/Interactive
        if avg_rx > 2.0 and avg_tx > 1.0:
            return "Workstation/Gaming"
            
        # Low traffic, long duration -> IoT or Idle
        if avg_rx < 0.5 and avg_tx < 0.5:
            if history[-1]["duration"] > 3600:
                return "IoT (Idle)"
            return "Idle"
            
        return "Unknown"

behavior_profiler = BehaviorProfiler()

def get_behavior_profiler() -> BehaviorProfiler:
    return behavior_profiler
