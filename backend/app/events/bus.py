import asyncio
import logging
from typing import Callable, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

logger = logging.getLogger("signalsense.events.bus")

class TelemetryEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    source_id: str  # Plugin ID or Router ID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any]

class TelemetryEventBus:

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[TelemetryEvent], Any]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self._running = False
        self._task = None
        
    def subscribe(self, topic: str, callback: Callable[[TelemetryEvent], Any]):

        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
        logger.info(f"Subscribed to topic: {topic}")
        
    async def publish(self, event: TelemetryEvent):

        try:
            await self._queue.put(event)
        except asyncio.QueueFull:
            logger.warning(f"Event bus queue full! Dropping event from {event.source_id}")
            
    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("Telemetry Event Bus started.")
        
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Telemetry Event Bus stopped.")
        
    async def _process_events(self):
        while self._running:
            try:
                event: TelemetryEvent = await self._queue.get()
                
                # Deliver to specific topic subscribers
                if event.topic in self._subscribers:
                    for callback in self._subscribers[event.topic]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            logger.error(f"Error in subscriber for {event.topic}: {e}")
                            
                # Deliver to wildcard subscribers
                if "*" in self._subscribers:
                    for callback in self._subscribers["*"]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            logger.error(f"Error in wildcard subscriber: {e}")
                            
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event bus queue: {e}")
                await asyncio.sleep(0.1)

# Global singleton
telemetry_bus = TelemetryEventBus()

def get_telemetry_bus() -> TelemetryEventBus:
    return telemetry_bus
