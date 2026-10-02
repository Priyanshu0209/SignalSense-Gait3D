from typing import Dict, Any

class ConfidenceEngine:

    @staticmethod
    def calculate_rssi_confidence(source: str, is_real: bool, signal_stability: float) -> float:
        if is_real:
            # Hardware-reported RSSI is highly confident, influenced slightly by stability
            return min(100.0, 90.0 + (signal_stability / 10.0))
        else:
            # Heuristics based on traffic
            return 45.0

    @staticmethod
    def calculate_distance_confidence(rssi_confidence: float, is_real: bool) -> float:
        if is_real:
            # Distance derived from real RSSI is decent, but still an estimation (Path Loss)
            return min(85.0, rssi_confidence * 0.9)
        else:
            # Distance derived from fake RSSI is very low confidence
            return 30.0

    @staticmethod
    def calculate_direction_confidence(has_aoa_hardware: bool) -> float:
        if has_aoa_hardware:
            return 95.0
        return 0.0

    @staticmethod
    def calculate_movement_confidence(source: str) -> float:
        if "hardware" in source.lower():
            return 90.0
        elif "anomaly" in source.lower() or "fluctuation" in source.lower():
            return 40.0
        return 0.0

    @staticmethod
    def calculate_health_score(rssi_value: int, drop_rate: float, reconnects: int) -> str:

        score = 100
        
        # Deduct based on RSSI
        if rssi_value < -80:
            score -= 30
        elif rssi_value < -70:
            score -= 15
        elif rssi_value < -60:
            score -= 5
            
        # Deduct based on drops/reconnects
        score -= (reconnects * 10)
        score -= (drop_rate * 50)
        
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 50:
            return "Average"
        elif score >= 30:
            return "Poor"
        return "Critical"

confidence_engine = ConfidenceEngine()

def get_confidence_engine() -> ConfidenceEngine:
    return confidence_engine
