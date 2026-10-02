from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
from app.events.bus import get_telemetry_bus, TelemetryEvent

class BasePlugin(ABC):

    def __init__(self, plugin_id: str, plugin_name: str, options: Optional[Dict[str, Any]] = None):
        self.plugin_id = plugin_id
        self.plugin_name = plugin_name
        self.options = options or {}
        self.bus = get_telemetry_bus()
        self._running = False
        self._task = None
        
    @abstractmethod
    async def start(self) -> bool:

        pass
        
    @abstractmethod
    async def stop(self):

        pass
        
    async def publish(self, topic: str, payload: Dict[str, Any]):

        event = TelemetryEvent(
            topic=topic,
            source_id=self.plugin_id,
            payload=payload
        )
        await self.bus.publish(event)
