import logging
import statistics
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone

from .time_series_collector import get_gait_time_series_collector
from .signal_filter_engine import get_signal_filter_engine

logger = logging.getLogger("signalsense.gait3d.activity")

class MotionActivityEngine:

    def __init__(self):
        self.collector = get_gait_time_series_collector()
        self.filter_engine = get_signal_filter_engine()
        self.history_log: List[Dict[str, Any]] = []

    def evaluate_device_activity(self, mac_address: str, window_seconds: float = 6.0) -> Dict[str, Any]:

        samples = self.collector.get_recent_window(mac_address, duration_sec=window_seconds)
        if len(samples) < 15:
            return {
                "mac_address": mac_address,
                "activity": "Unknown",
                "confidence_pct": 0,
                "anomaly_detected": False,
                "features": {"variance": 0, "range_dbm": 0, "zero_crossings": 0, "dominant_freq_hz": 0},
                "class_probabilities": {"Still": 16, "Standing": 17, "Sitting": 17, "Walking": 17, "Running": 16, "Falling": 17},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        raw_rssi = [s["raw_rssi"] for s in samples]
        # Smooth and filter
        filtered = self.filter_engine.apply_butterworth_lowpass(raw_rssi, cutoff_hz=3.5, sample_rate_hz=self.collector.sample_rate_hz)
        fft_res = self.filter_engine.compute_fft(filtered, sample_rate_hz=self.collector.sample_rate_hz)
        
        # 1. Feature Extraction
        mean_val = statistics.mean(filtered)
        variance = statistics.variance(filtered) if len(filtered) > 1 else 0.0
        range_dbm = max(filtered) - min(filtered)
        dom_freq = fft_res["dominant_frequency_hz"]
        entropy = fft_res["spectral_entropy"]
        
        # Zero-Crossing Rate of mean-subtracted signal
        centered = [v - mean_val for v in filtered]
        zero_crossings = sum(1 for i in range(1, len(centered)) if (centered[i-1] >= 0 and centered[i] < 0) or (centered[i-1] < 0 and centered[i] >= 0))
        zcr_rate = zero_crossings / float(len(centered))
        
        # 2. Activity Classification Logic & Probabilities
        activity = "Still"
        confidence = 85
        anomaly = False
        probs = {"Still": 10, "Standing": 15, "Sitting": 15, "Walking": 20, "Running": 20, "Falling": 20}
        
        if variance > 10.0 and range_dbm > 10.0 and zcr_rate > 0.3:
            activity = "Falling"
            confidence = 94
            anomaly = True
            probs = {"Still": 2, "Standing": 5, "Sitting": 5, "Walking": 8, "Running": 15, "Falling": 65}
        elif dom_freq >= 2.1 and range_dbm >= 5.5:
            activity = "Running"
            confidence = 91
            probs = {"Still": 2, "Standing": 5, "Sitting": 3, "Walking": 18, "Running": 70, "Falling": 2}
        elif dom_freq >= 1.1 and dom_freq < 2.1 and range_dbm >= 2.5:
            activity = "Walking"
            confidence = 93
            probs = {"Still": 4, "Standing": 8, "Sitting": 6, "Walking": 72, "Running": 8, "Falling": 2}
        elif variance >= 0.5 and variance < 2.0 and dom_freq < 1.1:
            activity = "Sitting"
            confidence = 84
            probs = {"Still": 15, "Standing": 20, "Sitting": 52, "Walking": 8, "Running": 3, "Falling": 2}
        elif variance >= 0.15 and variance < 0.5:
            activity = "Standing"
            confidence = 88
            probs = {"Still": 22, "Standing": 62, "Sitting": 10, "Walking": 4, "Running": 1, "Falling": 1}
        else:
            activity = "Still"
            confidence = 92
            probs = {"Still": 78, "Standing": 12, "Sitting": 6, "Walking": 2, "Running": 1, "Falling": 1}

        # Override with explicit simulated ground truth if active in collector
        if self.collector.simulation_enabled and mac_address in self.collector.sim_params:
            sim_act = self.collector.sim_params[mac_address].get("activity", activity)
            if sim_act != "Unknown":
                activity = sim_act
                confidence = 96
                for k in probs:
                    probs[k] = 5 if k != activity else 75

        result = {
            "mac_address": mac_address,
            "device_name": samples[-1]["device_name"],
            "activity": activity,
            "confidence_pct": confidence,
            "anomaly_detected": anomaly,
            "features": {
                "variance": round(variance, 3),
                "range_dbm": round(range_dbm, 2),
                "zero_crossing_rate": round(zcr_rate, 3),
                "dominant_freq_hz": dom_freq,
                "spectral_entropy": entropy
            },
            "class_probabilities": probs,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self._record_history(result)
        return result

    def get_network_activity_summary(self) -> List[Dict[str, Any]]:

        macs = self.collector.get_all_macs()
        results = []
        for mac in macs:
            results.append(self.evaluate_device_activity(mac))
        return results

    def _record_history(self, record: Dict[str, Any]):
        self.history_log.insert(0, {
            "id": f"act-{len(self.history_log)+1}",
            "mac_address": record["mac_address"],
            "device_name": record["device_name"],
            "activity": record["activity"],
            "confidence": record["confidence_pct"],
            "anomaly": record["anomaly_detected"],
            "timestamp": record["timestamp"]
        })
        if len(self.history_log) > 100:
            self.history_log.pop()

    def get_activity_history(self) -> List[Dict[str, Any]]:
        return self.history_log[:50]

activity_engine_singleton = MotionActivityEngine()

def get_motion_activity_engine() -> MotionActivityEngine:
    return activity_engine_singleton
