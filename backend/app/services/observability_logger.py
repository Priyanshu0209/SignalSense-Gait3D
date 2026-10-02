import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

class ObservabilityLogger:

    def __init__(self):
        self.logger = logging.getLogger("SignalSense.Observability")
        self.logger.setLevel(logging.INFO)
        # Avoid duplicate handlers if instantiated multiple times
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)

    def log_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "metric",
            "name": metric_name,
            "value": value,
            "tags": tags or {}
        }
        self.logger.info(json.dumps(payload))

    def log_trace(self, trace_id: str, span_name: str, duration_ms: float, tags: Dict[str, str] = None) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "trace",
            "trace_id": trace_id,
            "span_name": span_name,
            "duration_ms": duration_ms,
            "tags": tags or {}
        }
        self.logger.info(json.dumps(payload))

    def log_event(self, event_name: str, data: Dict[str, Any]) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "event",
            "name": event_name,
            "data": data
        }
        self.logger.info(json.dumps(payload))

observability_logger = ObservabilityLogger()

def get_observability_logger() -> ObservabilityLogger:
    return observability_logger
