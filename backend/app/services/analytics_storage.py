import logging
from typing import Dict, Any
from app.adapters.analytics.interface import IAnalyticsStorageEngine
from app.workers.cleanup_worker import CleanupSchedulerWorker
from app.workers.aggregation_worker import AggregationSchedulerWorker

logger = logging.getLogger("signalsense.services.analytics")

class AnalyticsStorageService:
    def __init__(self, engine: IAnalyticsStorageEngine):

        self.engine = engine
        self.cleanup_worker = CleanupSchedulerWorker(engine=self.engine)
        self.aggregation_worker = AggregationSchedulerWorker(engine=self.engine)
        
    async def save_router_status(self, cpu_usage: float = None, memory_usage: float = None, uptime: int = None):
        await self.engine.save_router_status(cpu_usage, memory_usage, uptime)
                
    async def save_discovery_statistics(self, metrics: dict):
        await self.engine.save_discovery_statistics(metrics)
                
    async def save_topology_snapshot(self, topology_data: dict, node_count: int):
        await self.engine.save_topology_snapshot(topology_data, node_count)
                
    async def start_background_tasks(self):
        await self.cleanup_worker.start()
        await self.aggregation_worker.start()
        
    async def stop_background_tasks(self):
        await self.cleanup_worker.stop()
        await self.aggregation_worker.stop()
        
    async def trigger_manual_cleanup(self, dry_run: bool = False) -> Dict[str, Any]:

        metrics = await self.cleanup_worker.execute_cleanup(dry_run=dry_run)
        return metrics.model_dump()
        
    def get_cleanup_status(self) -> Dict[str, Any]:

        return {
            "is_running": self.cleanup_worker._running,
            "is_paused": self.cleanup_worker._paused,
            "is_locked": self.cleanup_worker._cleanup_lock.locked(),
            "metrics": self.cleanup_worker.metrics.model_dump()
        }

_analytics_storage_service = None

def get_analytics_storage_service() -> AnalyticsStorageService:
    global _analytics_storage_service
    if _analytics_storage_service is None:
        from app.adapters.analytics.factory import get_analytics_engine
        engine = get_analytics_engine()
        _analytics_storage_service = AnalyticsStorageService(engine)
    return _analytics_storage_service
