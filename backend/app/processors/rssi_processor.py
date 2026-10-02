from collections import deque
import statistics
from typing import List
from app.schemas.router import ConnectedDevice
from app.schemas.processing import (
    SignalClassification, DistanceClassification, 
    SignalTrend, AnimationState, ProcessedDeviceState, MetricValue, MetricStatus
)

class RSSIProcessor:

    def __init__(self, moving_avg_window: int = 15):
        self.moving_avg_window = moving_avg_window
        self._history = {} # type: dict[str, deque]
        
    def _get_history(self, mac_address: str) -> deque:
        if mac_address not in self._history:
            self._history[mac_address] = deque(maxlen=self.moving_avg_window)
        return self._history[mac_address]

    def _classify_signal_and_distance(self, rssi: float) -> tuple[SignalClassification, AnimationState]:
        if rssi > -45:
            return (
                SignalClassification.EXCELLENT,
                AnimationState(color="Green", pulse_speed="Slow", glow_intensity="High")
            )
        elif -60 <= rssi <= -45:
            return (
                SignalClassification.GOOD,
                AnimationState(color="Yellow", pulse_speed="Medium", glow_intensity="Medium")
            )
        elif -75 <= rssi <= -61:
            return (
                SignalClassification.WEAK,
                AnimationState(color="Orange", pulse_speed="Fast", glow_intensity="Lower")
            )
        else:
            return (
                SignalClassification.CRITICAL,
                AnimationState(color="Red", pulse_speed="Rapid", glow_intensity="Strong Alert")
            )

    def _detect_trend(self, history: list[int]) -> SignalTrend:
        if len(history) < 3:
            return SignalTrend.STABLE
            
        recent = history[-1]
        oldest = history[0]
        diff = recent - oldest
        
        if diff <= -10:
            return SignalTrend.RAPID_DROP
        elif diff <= -3:
            return SignalTrend.WEAKENING
        elif diff >= 3:
            return SignalTrend.IMPROVING
            
        std_dev = statistics.stdev(history) if len(history) > 1 else 0
        if std_dev > 5:
            return SignalTrend.FLUCTUATING
            
        return SignalTrend.STABLE

    def _calculate_stability_score(self, history: list[int]) -> float:
        if len(history) < 2:
            return 100.0
            
        std_dev = statistics.stdev(history)
        score = max(0.0, 100.0 - (std_dev * (100.0 / 15.0)))
        return min(100.0, score)

    def process(self, raw_device: ConnectedDevice) -> ProcessedDeviceState:
        from app.services.estimation_engine import get_estimation_engine
        from app.services.confidence_engine import get_confidence_engine
        from app.services.predictive_engine import get_predictive_engine
        from app.services.behavior_profiler import get_behavior_profiler
        from app.services.anomaly_detector import get_anomaly_detector
        from app.services.ai_analyst import get_ai_analyst
        
        estimator = get_estimation_engine()
        conf_engine = get_confidence_engine()
        pred_engine = get_predictive_engine()
        behavior = get_behavior_profiler()
        anomaly = get_anomaly_detector()
        ai = get_ai_analyst()
        
        # Estimate RSSI (if missing)
        rssi_metric = estimator.estimate_rssi(raw_device, raw_device.rssi)
        
        # Estimate distance from RSSI
        distance_metric, dist_class = estimator.estimate_distance(rssi_metric)
        
        # Estimate Activity and Direction
        activity, dir_metric, mov_metric = estimator.calculate_activity_score_and_direction(raw_device)

        history_q = self._get_history(raw_device.mac_address)
        previous_rssi = history_q[-1] if len(history_q) > 0 else None
        
        # Use working_rssi for history and filtering
        working_rssi = rssi_metric.value
        history_q.append(working_rssi)
        
        # --- BASIC MOVEMENT LOGIC (Option A) ---
        if len(history_q) >= 3:
            std_dev = statistics.stdev(history_q)
            if std_dev > 2.0:
                mov_state = "Moving"
            else:
                mov_state = "Stationary"
                
            mov_metric = MetricValue(
                value=mov_state,
                status=MetricStatus.REAL,
                confidence=95.0,
                source="RSSI Variance Analysis"
            )
        # ---------------------------------------
            
        history_list = list(history_q)
        moving_average_rssi = sum(history_list) / len(history_list) if history_list else None
        
        trend = self._detect_trend(history_list)
        stability = self._calculate_stability_score(history_list)
        
        if moving_average_rssi is not None:
            sig_class, anim_state = self._classify_signal_and_distance(moving_average_rssi)
        else:
            sig_class = SignalClassification.UNKNOWN
            anim_state = AnimationState(color="Gray", pulse_speed="None", glow_intensity="None")
        
        # Override animation state based on activity to create blinking effect
        if activity > 75:
            anim_state.pulse_speed = "Rapid"
            anim_state.glow_intensity = "High"
        elif activity > 40:
            anim_state.pulse_speed = "Fast"
        elif activity < 10:
            anim_state.pulse_speed = "Slow"
            
        # Calculate Health Score
        health = conf_engine.calculate_health_score(
            rssi_value=working_rssi if working_rssi else -90,
            drop_rate=0.0, # Placeholder until we track drops per device here
            reconnects=0   # Placeholder
        )
        
        # Run Predictive Engine
        traffic = (raw_device.tx_rate or 0) + (raw_device.rx_rate or 0)
        prediction = pred_engine.predict_device_state(raw_device.mac_address, working_rssi if working_rssi else -90, traffic)
        
        # Profile Behavior & Detect Anomalies
        profile = behavior.profile_device(raw_device)
        anomalies = anomaly.detect_anomalies(raw_device.mac_address, raw_device.rx_rate or 0, raw_device.tx_rate or 0, working_rssi if working_rssi else -90)
        
        # AI Analyst Generation
        explanation = ai.generate_explanation(profile, anomalies, health)
        
        if prediction:
            # We will send this to the Event Timeline Engine to show on the dashboard
            from app.services.event_timeline_engine import EventTimelineEngine
            # Just add it as a global event for now
            EventTimelineEngine.add_event(
                type_name=prediction["severity"].lower(),
                message=f"[PREDICTED] {raw_device.hostname or raw_device.mac_address}: {prediction['message']}"
            )
            
        for a in anomalies:
            from app.services.event_timeline_engine import EventTimelineEngine
            EventTimelineEngine.add_event(
                type_name=a["severity"].lower(),
                message=f"[ANOMALY] {raw_device.hostname or raw_device.mac_address}: {a['description']}"
            )
        
        from app.services.diagnostics.diagnostics_logger import get_diagnostics_logger
        logger_service = get_diagnostics_logger()
        logger_service.log_processor_layer(
            raw_device.mac_address,
            working_rssi,
            f"Moving Average: {moving_average_rssi:.2f}" if moving_average_rssi else ""
        )
        
        return ProcessedDeviceState(
            mac_address=raw_device.mac_address,
            ip_address=raw_device.ip_address,
            hostname=raw_device.hostname,
            device_type=raw_device.device_type,
            manufacturer=raw_device.manufacturer,
            
            current_rssi=rssi_metric,
            previous_rssi=previous_rssi,
            moving_average_rssi=moving_average_rssi,
            signal_quality=raw_device.signal_quality,
            
            signal_classification=sig_class,
            distance_classification=dist_class,
            signal_trend=trend,
            stability_score=stability,
            health_score=health,
            behavior_profile=profile,
            ai_explanation=explanation,
            
            distance=distance_metric,
            direction=dir_metric,
            movement=mov_metric,
            activity_score=activity,
            
            animation_state=anim_state,
            online_status=True,
            connection_duration=raw_device.connection_duration_seconds or 0,
            last_seen=raw_device.last_seen,
            tx_rate=raw_device.tx_rate,
            rx_rate=raw_device.rx_rate,
            rssi_ant0=getattr(raw_device, 'rssi_ant0', None),
            rssi_ant1=getattr(raw_device, 'rssi_ant1', None),
            tx_per=getattr(raw_device, 'tx_per', None),
            rx_crc_per=getattr(raw_device, 'rx_crc_per', None),
            false_cca=getattr(raw_device, 'false_cca', None),
            tx_mcs=getattr(raw_device, 'tx_mcs', None),
            rx_mcs=getattr(raw_device, 'rx_mcs', None)
        )
