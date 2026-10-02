from typing import List, Optional
from app.sdk.plugins.base import BaseTelemetryPlugin
from app.schemas.router import ConnectedDevice, RouterStatus
from app.collectors.data_collector import get_data_collector

class DefaultRouterPlugin(BaseTelemetryPlugin):

    def __init__(self):
        self.collector = get_data_collector()
        
    @property
    def plugin_name(self) -> str:
        return "Netgear-R6220-Legacy"
        
    @property
    def supports_rssi(self) -> bool:
        return False
        
    @property
    def supports_aoa(self) -> bool:
        return False
        
    @property
    def supports_tof(self) -> bool:
        return False
        
    async def collect_router_status(self) -> Optional[RouterStatus]:
        return await self.collector.get_router_status()
        
    async def collect_devices(self) -> List[ConnectedDevice]:
        return await self.collector.get_connected_devices()
