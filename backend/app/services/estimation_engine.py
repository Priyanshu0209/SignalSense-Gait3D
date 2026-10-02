import math
from typing import Dict, Tuple, Optional
from datetime import datetime, timezone
from app.schemas.router import ConnectedDevice
from app.schemas.processing import DistanceClassification, MetricValue, MetricStatus
from app.services.confidence_engine import get_confidence_engine

class EstimationEngine:
    def __init__(self):
        self.mac_activity_history: Dict[str, float] = {}
        self.simulation_state: Dict[str, Dict[str, float]] = {}
        import random
        self.random = random

    def estimate_rssi(self, device: ConnectedDevice, real_rssi: Optional[int] = None) -> MetricValue[int]:
        if real_rssi is not None:
            return MetricValue(
                value=real_rssi,
                status=MetricStatus.REAL,
                confidence=get_confidence_engine().calculate_rssi_confidence("Hardware", True, 100.0),
                source="Device telemetry (Hardware)"
            )
            
        if device.mac_address not in self.simulation_state:
            self.simulation_state[device.mac_address] = {
                "distance": self.random.uniform(1.0, 20.0),
                "direction": self.random.uniform(0.0, 360.0)
            }
        else:
            state = self.simulation_state[device.mac_address]
            # Random walk
            state["distance"] += self.random.uniform(-1.0, 1.0)
            state["distance"] = max(0.5, min(35.0, state["distance"]))
            state["direction"] = (state["direction"] + self.random.uniform(-5.0, 5.0)) % 360
            
        sim_dist = self.simulation_state[device.mac_address]["distance"]
        tx_power_1m = -30
        n = 2.5
        # dist = 10 ^ ((tx_power - rssi) / 10n)
        # log10(dist) * 10n = tx_power - rssi
        # rssi = tx_power - log10(dist)*10n
        sim_rssi = tx_power_1m - (math.log10(sim_dist) * (10 * n))
        
        return MetricValue(
            value=int(sim_rssi),
            status=MetricStatus.ESTIMATED,
            confidence=10.0,
            source="SIMULATION (Random Walk)"
        )

    def estimate_distance(self, rssi_metric: MetricValue[int]) -> Tuple[MetricValue[float], DistanceClassification]:
        if rssi_metric.value is None:
            return (
                MetricValue(value=None, status=MetricStatus.UNKNOWN, confidence=0.0, source="No RSSI available"),
                DistanceClassification.UNKNOWN
            )
            
        tx_power_1m = -50.33  # Standard for 2.4/5GHz indoor Wi-Fi
        n = 2.5
        exponent = (tx_power_1m - rssi_metric.value) / (10 * n)
        distance_m = max(0.1, math.pow(10, exponent))
        
        if distance_m < 2.0:
            category = DistanceClassification.VERY_NEAR
        elif distance_m < 5.0:
            category = DistanceClassification.NEAR
        elif distance_m < 15.0:
            category = DistanceClassification.MEDIUM
        elif distance_m < 30.0:
            category = DistanceClassification.FAR
        else:
            category = DistanceClassification.VERY_FAR
            
        return (
            MetricValue(
                value=round(distance_m, 1),
                status=MetricStatus.ESTIMATED,
                confidence=10.0,
                source="SIMULATION (Random Walk)"
            ),
            category
        )

    def calculate_activity_score_and_direction(self, device: ConnectedDevice) -> Tuple[float, MetricValue[float], MetricValue[str]]:
        mac = device.mac_address
        
        # 1. Activity Estimation
        current_activity = 0.0
        activity_source = "Traffic Rate (Legacy)"
        
        rx_crc = getattr(device, 'rx_crc_per', None)
        tx_per = getattr(device, 'tx_per', None)
        false_cca = getattr(device, 'false_cca', None)
        
        if rx_crc is not None or tx_per is not None:
            activity_source = "Advanced PHY Metrics (PER/CRC)"
            if rx_crc: current_activity += min(50.0, rx_crc * 1.5)
            if tx_per: current_activity += min(30.0, tx_per * 1.5)
            if false_cca: current_activity += min(20.0, (false_cca / 100.0) * 10.0)
        elif device.tx_rate or device.rx_rate:
            total_rate = (device.tx_rate or 0) + (device.rx_rate or 0)
            current_activity = min(100.0, (total_rate / 500.0) * 100.0)
            
        prev_activity = self.mac_activity_history.get(mac, 0.0)
        smoothed_activity = (prev_activity * 0.7) + (current_activity * 0.3)
        self.mac_activity_history[mac] = smoothed_activity
        
        # 2. Direction Estimation
        direction_val = 0.0
        dir_source = "SIMULATION (Random Walk)"
        dir_conf = 10.0
        
        rssi0 = getattr(device, 'rssi_ant0', None)
        rssi1 = getattr(device, 'rssi_ant1', None)
        
        if rssi0 is not None and rssi1 is not None:
            # Simple heuristic Angle of Arrival based on RSSI delta
            diff = rssi0 - rssi1
            # Map difference roughly to angle: -10 to +10 dB difference -> -90 to 90 degrees
            direction_val = (diff * 9.0) % 360
            dir_source = "Dual Antenna RSSI Difference"
            dir_conf = 70.0
        else:
            direction_val = self.simulation_state.get(mac, {}).get("direction", 0.0)
            
        direction_metric = MetricValue(
            value=round(direction_val, 1),
            status=MetricStatus.ESTIMATED,
            confidence=dir_conf,
            source=dir_source
        )
        
        # 3. Movement State
        movement_state = "Stationary"
        if smoothed_activity > 60:
            movement_state = "Rapid Movement (Walking/Running)"
        elif smoothed_activity > 25:
            movement_state = "Moving (Gestures/Shifting)"
            
        movement_metric = MetricValue(
            value=movement_state,
            status=MetricStatus.ESTIMATED,
            confidence=60.0 if rx_crc else 10.0,
            source=activity_source
        )
        
        return smoothed_activity, direction_metric, movement_metric

estimation_engine = EstimationEngine()

def get_estimation_engine() -> EstimationEngine:
    return estimation_engine
