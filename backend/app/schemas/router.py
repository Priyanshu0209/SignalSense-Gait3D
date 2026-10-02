from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class RouterCapabilities(BaseModel):
    supports_rssi: bool = False
    supports_clients: bool = False
    supports_cpu: bool = False
    supports_memory: bool = False
    supports_channels: bool = False
    supports_tx_rate: bool = False
    supports_rx_rate: bool = False
    supports_hostname: bool = False
    supports_vendor: bool = False
    supports_firmware: bool = False

class ConnectedDevice(BaseModel):
    mac_address: str
    ip_address: str
    hostname: Optional[str] = None
    rssi: Optional[int] = None
    signal_quality: Optional[int] = Field(None, ge=0, le=100)
    connection_state: str = "connected"
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    router_id: Optional[str] = "default_router"
    last_seen: datetime
    connection_duration_seconds: Optional[int] = None
    tx_rate: Optional[float] = None
    rx_rate: Optional[float] = None
    
    # Advanced Wi-Fi sensing parameters (Gait3D)
    rssi_ant0: Optional[int] = None
    rssi_ant1: Optional[int] = None
    tx_per: Optional[float] = None
    rx_crc_per: Optional[float] = None
    false_cca: Optional[int] = None
    tx_mcs: Optional[str] = None
    rx_mcs: Optional[str] = None

class RouterStatus(BaseModel):
    router_id: str = "default_router"
    router_name: str
    router_model: str
    vendor: str = "Generic"
    firmware_version: str
    gateway_ip: str = "192.168.1.1"
    mac_address: str = "00:00:00:00:00:00"
    
    # Phase 6 Multi-Site Topology
    location: Optional[str] = "Main Office"
    zone: Optional[str] = "Core"
    floor: Optional[str] = "1"
    building: Optional[str] = "HQ"
    connection_type: str = "Dynamic IP"
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    network_status: str
    internet_status: str
    uptime_seconds: int
    connected_devices_count: int
    timestamp: datetime
    capabilities: RouterCapabilities
    
    wan_ip: Optional[str] = None
    lan_ip: Optional[str] = None
    wifi_channel: Optional[int] = None
    frequency: Optional[str] = None
    bandwidth_mbps: Optional[float] = None
    packet_loss_percent: Optional[float] = None
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    dns_status: Optional[str] = None
    signal_quality: Optional[int] = None
    adapter_type: Optional[str] = None
    connection_status: Optional[str] = None
