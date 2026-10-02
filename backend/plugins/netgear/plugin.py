import asyncio
import logging
from typing import Dict, Any, Optional
from app.sdk.plugins.base import BasePlugin
from plugins.netgear.adapter import NetgearRouterAdapter

logger = logging.getLogger("signalsense.plugins.netgear")

class NetgearPlugin(BasePlugin):
    """
    Netgear Plugin complying with Part 11 SDK Specification.
    """
    def __init__(self, plugin_id: str, plugin_name: str, options: Optional[Dict[str, Any]] = None):
        super().__init__(plugin_id, plugin_name, options)
        self.host = self.options.get("host", "192.168.1.1")
        self.username = self.options.get("username", "admin")
        self.password = self.options.get("password", "password")
        self.adapter = NetgearRouterAdapter(self.host, self.username, self.password, self.options)
        
    async def start(self) -> bool:
        self._running = True
        logger.info(f"Starting {self.plugin_name}...")
        
        # Connect to adapter
        success = await self.adapter.connect()
        if not success:
            logger.error(f"{self.plugin_name} failed to authenticate.")
            return False
            
        await self.publish("plugin.started", {"status": "ONLINE"})
        
        # Start collection loop
        self._task = asyncio.create_task(self._collection_loop())
        return True
        
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        await self.adapter.disconnect()
        await self.publish("plugin.stopped", {"status": "OFFLINE"})
        logger.info(f"{self.plugin_name} stopped.")
        
    async def _collection_loop(self):
        while self._running:
            try:
                devices = await self.adapter.get_connected_devices()
                # Publish to Event Bus
                for dev in devices:
                    await self.publish("telemetry.device.discovered", dev.model_dump())
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await self.publish("plugin.failed", {"error": str(e)})
                
            await asyncio.sleep(self.options.get("poll_interval", 10))
