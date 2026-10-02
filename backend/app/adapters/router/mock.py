import asyncio
import random
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.adapters.router.base import RouterAdapter
from app.schemas.router import RouterStatus, ConnectedDevice, RouterCapabilities

class MockRouterAdapter(RouterAdapter):

    def __init__(self, host: str, username: str, password: str, options: Dict[str, Any] = None):
        super().__init__(host, username, password, options)
        self.is_connected = False
        self.start_time = datetime.now(timezone.utc)
        self._mock_devices = self._generate_mock_devices()
    def _generate_mock_devices(self) -> List[dict]:
        return [
            {
                "mac_address": "0E:41:49:3E:D3:01",
                "ip_address": "192.168.1.3",
                "hostname": "MOTO-G84-5G",
                "device_type": "Smartphone",
                "manufacturer": "Motorola",
                "base_rssi": -65
            },
            {
                "mac_address": "B4:8C:9D:64:EB:47",
                "ip_address": "192.168.1.5",
                "hostname": "PRIYANSHU",
                "device_type": "Laptop",
                "manufacturer": "Unknown",
                "base_rssi": -50
            },
            {
                "mac_address": "46:BD:A7:A6:4D:6A",
                "ip_address": "192.168.1.6",
                "hostname": "IPAD",
                "device_type": "Tablet",
                "manufacturer": "Apple",
                "base_rssi": -72
            },
            {
                "mac_address": "D6:5E:95:9D:9E:06",
                "ip_address": "192.168.1.4",
                "hostname": "SHRISTI-S-F41",
                "device_type": "Smartphone",
                "manufacturer": "Samsung",
                "base_rssi": -60
            }
        ]

    async def connect(self) -> bool:
        await asyncio.sleep(0.5)
        self.is_connected = True
        return True

    async def disconnect(self) -> None:
        self.is_connected = False

    def get_capabilities(self) -> RouterCapabilities:
        return RouterCapabilities(
            supports_rssi=True,
            supports_clients=True,
            supports_cpu=True,
            supports_memory=True,
            supports_channels=True,
            supports_tx_rate=True,
            supports_rx_rate=True,
            supports_hostname=True,
            supports_vendor=True,
            supports_firmware=True
        )

    async def get_status(self) -> RouterStatus:
        if not self.is_connected:
            raise ConnectionError("Router is not connected")
            
        now = datetime.now(timezone.utc)
        uptime = int((now - self.start_time).total_seconds())
        
        return RouterStatus(
            router_name="MockRouter-AX3000",
            router_model="MOCK-AX",
            vendor="Cisco (Mock)",
            firmware_version="v2.1.mock",
            gateway_ip="192.168.1.1",
            mac_address="AA:BB:CC:DD:EE:FF",
            connection_type="Fiber",
            cpu_usage=random.uniform(5.0, 30.0),
            memory_usage=random.uniform(40.0, 60.0),
            network_status="online",
            internet_status="connected",
            uptime_seconds=uptime,
            connected_devices_count=len(self._mock_devices),
            timestamp=now,
            wan_ip="203.0.113.45",
            lan_ip="192.168.1.1",
            wifi_channel=6,
            frequency="5GHz",
            bandwidth_mbps=1000.0,
            packet_loss_percent=random.uniform(0.0, 0.5),
            latency_ms=random.uniform(2.0, 15.0),
            jitter_ms=random.uniform(0.5, 3.0),
            dns_status="healthy",
            signal_quality=98,
            adapter_type="Mock Adapter",
            connection_status="Connected",
            capabilities=self.get_capabilities()
        )

    async def get_connected_devices(self) -> List[ConnectedDevice]:
        if not self.is_connected:
            raise ConnectionError("Router is not connected")
            
        devices = []
        now = datetime.now(timezone.utc)
        
        for d in self._mock_devices:
            # Smooth RSSI random walk
            step = random.choice([-2, -1, 0, 1, 2])
            d["base_rssi"] += step
            # Cap RSSI between -90 and -30
            d["base_rssi"] = max(-90, min(-30, d["base_rssi"]))
            current_rssi = d["base_rssi"]
            
            # Map RSSI to quality percentage roughly (-90 -> 0%, -30 -> 100%)
            quality = max(0, min(100, int((current_rssi + 90) * (100 / 60))))
            
            devices.append(ConnectedDevice(
                mac_address=d["mac_address"],
                ip_address=d["ip_address"],
                hostname=d["hostname"],
                rssi=current_rssi,
                signal_quality=quality,
                connection_state="connected",
                device_type=d["device_type"],
                manufacturer=d["manufacturer"],
                last_seen=now,
                connection_duration_seconds=int((now - self.start_time).total_seconds()),
                tx_rate=random.uniform(10.0, 300.0),
                rx_rate=random.uniform(10.0, 300.0)
            ))
            
        try:
            from app.services.diagnostics.raw_response_logger import get_raw_response_logger
            logger_service = get_raw_response_logger()
            logger_service.log_response(
                router_ip="192.168.1.1",
                gateway="192.168.1.1",
                response_time_ms=10.0,
                discovery_duration_ms=15.0,
                error_status=None,
                raw_payload=self._mock_devices
            )
        except ImportError:
            pass
            
        return devices
