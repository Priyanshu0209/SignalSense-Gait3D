from enum import Enum
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, Any
from datetime import datetime

class SignalClassification(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    WEAK = "Weak"
    CRITICAL = "Critical"
    DISCONNECTED = "Disconnected"
    UNKNOWN = "Unknown"

class DistanceClassification(str, Enum):
    VERY_NEAR = "Very Near"
    NEAR = "Near"
    MEDIUM = "Medium"
    FAR = "Far"
    VERY_FAR = "Very Far"
    DISCONNECTED = "Disconnected"
    UNKNOWN = "Unknown"

class SignalTrend(str, Enum):
    IMPROVING = "Improving"
    STABLE = "Stable"
    WEAKENING = "Weakening"
    RAPID_DROP = "Rapid Drop"
    FLUCTUATING = "Fluctuating"
    NONE = "None"

class AnimationState(BaseModel):
    color: str
    pulse_speed: str
    glow_intensity: str

class MetricStatus(str, Enum):
    REAL = "REAL"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"

T = TypeVar('T')

class MetricValue(BaseModel, Generic[T]):
    value: Optional[T] = None
    status: MetricStatus
    confidence: float  # 0.0 to 100.0
    source: str

class ProcessedDeviceState(BaseModel):
    mac_address: str
    ip_address: str
    hostname: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    router_id: str = "default_router"
    
    current_rssi: MetricValue[int]
    previous_rssi: Optional[int] = None
    moving_average_rssi: Optional[float] = None
    signal_quality: Optional[int] = None
    
    signal_classification: SignalClassification
    distance_classification: DistanceClassification
    signal_trend: SignalTrend
    stability_score: float # 0 to 100
    health_score: str = "Average"
    behavior_profile: str = "Unknown"
    ai_explanation: dict = None
    twin_mode: str = "REAL" # "REAL" or "SIMULATION"
    
    distance: MetricValue[float]
    direction: MetricValue[float]
    movement: MetricValue[str]
    activity_score: float = 0.0
    
    animation_state: AnimationState
    online_status: bool
    connection_duration: int
    last_seen: datetime
    tx_rate: Optional[float] = None
    rx_rate: Optional[float] = None
    
    # Advanced Wi-Fi sensing parameters
    rssi_ant0: Optional[int] = None
    rssi_ant1: Optional[int] = None
    tx_per: Optional[float] = None
    rx_crc_per: Optional[float] = None
    false_cca: Optional[int] = None
    tx_mcs: Optional[str] = None
    rx_mcs: Optional[str] = None
