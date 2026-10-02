from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class AggregationResolution(str, Enum):
    RAW = "RAW"
    MINUTE_1 = "MINUTE_1"
    MINUTE_5 = "MINUTE_5"
    MINUTE_15 = "MINUTE_15"
    MINUTE_30 = "MINUTE_30"
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class RetentionPolicy(BaseModel):

    thresholds: Dict[AggregationResolution, Optional[int]] = {
        AggregationResolution.RAW: 7,
        AggregationResolution.MINUTE_1: 30,
        AggregationResolution.MINUTE_5: 90,
        AggregationResolution.MINUTE_15: 90,
        AggregationResolution.MINUTE_30: 180,
        AggregationResolution.HOURLY: 180,
        AggregationResolution.DAILY: 1825,
        AggregationResolution.WEEKLY: 1825,
        AggregationResolution.MONTHLY: 3650,
        AggregationResolution.YEARLY: None
    }

class CleanupMetrics(BaseModel):
    last_cleanup_time: Optional[datetime] = None
    cleanup_duration_ms: float = 0.0
    rows_deleted: int = 0
    rows_scanned: int = 0
    estimated_reclaimed_storage_bytes: int = 0
    cleanup_failures: int = 0
    cleanup_retries: int = 0
