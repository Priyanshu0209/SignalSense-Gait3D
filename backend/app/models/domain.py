from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

def utcnow():
    return datetime.now(timezone.utc)

class RouterModel(Base):
    __tablename__ = "routers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    model = Column(String)
    firmware = Column(String)
    adapter_type = Column(String)
    created_at = Column(DateTime, default=utcnow)
    
class DeviceModel(Base):
    __tablename__ = "devices"
    mac_address = Column(String, primary_key=True, index=True)
    hostname = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    first_seen = Column(DateTime, default=utcnow)
    last_seen = Column(DateTime, default=utcnow)
    current_status = Column(String) # online, offline
    
    sessions = relationship("DeviceSessionModel", back_populates="device", cascade="all, delete-orphan")
    rssi_history = relationship("RSSIHistoryModel", back_populates="device", cascade="all, delete-orphan")
    metadata_history = relationship("DeviceMetadataHistoryModel", back_populates="device", cascade="all, delete-orphan")

class DeviceSessionModel(Base):
    __tablename__ = "device_sessions"
    id = Column(Integer, primary_key=True, index=True)
    mac_address = Column(String, ForeignKey("devices.mac_address"), index=True)
    connection_time = Column(DateTime, default=utcnow, index=True)
    disconnection_time = Column(DateTime, nullable=True)
    session_duration = Column(Integer, nullable=True) # in seconds
    
    device = relationship("DeviceModel", back_populates="sessions")

class DeviceMetadataHistoryModel(Base):
    __tablename__ = "device_metadata_history"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    mac_address = Column(String, ForeignKey("devices.mac_address"), index=True)
    field_name = Column(String, index=True) # e.g. "ip_address", "hostname", "manufacturer", "device_type"
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    
    device = relationship("DeviceModel", back_populates="metadata_history")

class RSSIHistoryModel(Base):
    __tablename__ = "rssi_history"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    mac_address = Column(String, ForeignKey("devices.mac_address"), index=True)
    raw_rssi = Column(Integer)
    filtered_rssi = Column(Integer, nullable=True)
    moving_average = Column(Float)
    signal_classification = Column(String)
    distance_classification = Column(String)
    trend = Column(String)
    stability_score = Column(Float)
    
    device = relationship("DeviceModel", back_populates="rssi_history")

class EventModel(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    event_type = Column(String, index=True) # DEVICE_CONNECTED, RSSI_CHANGED, etc.
    mac_address = Column(String, index=True, nullable=True) # Legacy backward compat
    entity_id = Column(String, index=True, nullable=True)
    severity = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=True)
    source_module = Column(String, index=True, nullable=True)
    correlation_id = Column(String, index=True, nullable=True)
    search_tags = Column(String, index=True, nullable=True)
    message = Column(Text, nullable=True)
    payload = Column(Text, nullable=True) # JSON payload

class AlertModel(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    alert_type = Column(String, index=True)
    severity = Column(String, index=True)
    resolved = Column(Boolean, default=False)
    message = Column(Text)

class SystemLogModel(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    level = Column(String, index=True)
    source = Column(String)
    message = Column(Text)

class SettingModel(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class RouterStatusHistoryModel(Base):
    __tablename__ = "router_status_history"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    uptime = Column(Integer, nullable=True)

class DiscoveryStatisticsModel(Base):
    __tablename__ = "discovery_statistics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    total_scans = Column(Integer)
    successful_scans = Column(Integer)
    failed_scans = Column(Integer)
    avg_scan_duration_ms = Column(Float)
    max_scan_duration_ms = Column(Float)
    reconnect_count = Column(Integer)
    dropped_events = Column(Integer)

class NetworkTopologySnapshotModel(Base):
    __tablename__ = "network_topology_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    node_count = Column(Integer)
    edge_count = Column(Integer, nullable=True)
    health_score = Column(Float, nullable=True)
    is_compressed = Column(Boolean, default=False)
    metadata_json = Column(Text, nullable=True)
    topology_data = Column(Text) # JSON or Base64 compressed representing nodes/edges

class TimeSeriesAggregateModel(Base):
    __tablename__ = "time_series_aggregates"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True) # Start of the bucket
    resolution = Column(String, index=True) # AggregationResolution string
    metric_name = Column(String, index=True)
    entity_id = Column(String, index=True, nullable=True) # MAC address or specific node id
    avg_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    sum_value = Column(Float, nullable=True)
    count = Column(Integer, default=0)

class AggregationCheckpointModel(Base):
    __tablename__ = "aggregation_checkpoints"
    id = Column(String, primary_key=True) # Composite key: {resolution}_{metric_name}_{entity_id_or_global}
    resolution = Column(String, index=True)
    metric_name = Column(String, index=True)
    entity_id = Column(String, index=True, nullable=True)
    last_aggregated_timestamp = Column(DateTime)

class TrendProfileModel(Base):
    __tablename__ = "trend_profiles"
    id = Column(String, primary_key=True) # Composite: {metric_name}_{entity_id}_{time_window}
    metric_name = Column(String, index=True)
    entity_id = Column(String, index=True, nullable=True)
    time_window = Column(String, index=True)
    
    current_value = Column(Float, nullable=True)
    previous_value = Column(Float, nullable=True)
    growth_rate = Column(Float, nullable=True)
    variance = Column(Float, nullable=True)
    std_dev = Column(Float, nullable=True)
    forecast_value = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    
    last_calculated = Column(DateTime, default=utcnow, onupdate=utcnow)

class DeviceSnapshotModel(Base):
    __tablename__ = "device_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    mac_address = Column(String, ForeignKey("devices.mac_address"), index=True)
    state_json = Column(Text) # Stores serialized ProcessedDeviceState
