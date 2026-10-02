import asyncio
import logging
from app.sdk.plugins.base import BasePlugin

logger = logging.getLogger("signalsense.plugins.csi")

class CSIProvider(BasePlugin):

    def __init__(self, plugin_id: str, options: dict = None):
        super().__init__(plugin_id, "CSI Provider", options)
        
    async def start(self) -> bool:
        self._running = True
        return True
        
    async def stop(self):
        self._running = False
