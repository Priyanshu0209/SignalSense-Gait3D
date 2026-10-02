from abc import ABC, abstractmethod
from datetime import datetime
from app.models.retention import AggregationResolution

class IAnalyticsStorageEngine(ABC):

    @abstractmethod
    async def save_router_status(self, cpu_usage: float = None, memory_usage: float = None, uptime: int = None):
        pass
        
    @abstractmethod
    async def save_discovery_statistics(self, metrics: dict):
        pass
        
    @abstractmethod
    async def save_topology_snapshot(self, topology_data: dict, node_count: int, edge_count: int = None, health_score: float = None, is_compressed: bool = False, metadata_json: str = None, raw_data_str: str = None):
        pass
        
    @abstractmethod
    async def prune_records(self, resolution: AggregationResolution, threshold_days: int, chunk_size: int = 1000, dry_run: bool = False) -> dict:

        pass
        
    @abstractmethod
    async def get_aggregation_checkpoint(self, resolution: AggregationResolution, metric_name: str, entity_id: str = None) -> datetime:

        pass
        
    @abstractmethod
    async def save_time_series_aggregates(self, aggregates: list, new_checkpoint_time: datetime, resolution: AggregationResolution, metric_name: str, entity_id: str = None):

        pass
        
    @abstractmethod
    async def fetch_raw_data_for_aggregation(self, metric_name: str, start_time: datetime, end_time: datetime) -> list:

        pass
        
    @abstractmethod
    async def fetch_aggregated_data_for_rollup(self, source_resolution: AggregationResolution, metric_name: str, start_time: datetime, end_time: datetime) -> list:

        pass

    @abstractmethod
    async def stream_time_series_data(self, metric_name: str, resolution: AggregationResolution, start_time: datetime, end_time: datetime, entity_id: str = None, cursor: str = None, limit: int = 1000, forward: bool = True):

        pass
        
    # Phase 6: Query Engine
    @abstractmethod
    async def query_telemetry(self, query: str, filters: dict, time_range: tuple):

        pass
        
    # Phase 6: Stream Processing
    @abstractmethod
    async def process_stream_window(self, metric: str, window_size_seconds: int):

        pass
