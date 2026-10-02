from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from app.models.retention import AggregationResolution

class CursorPagination(BaseModel):
    cursor: Optional[str] = Field(default=None, description="Cursor token for the next/previous page")
    limit: int = Field(default=1000, le=10000, description="Maximum number of records to return per page")
    forward: bool = Field(default=True, description="Direction of pagination. True for forward, False for backward.")

class TimeSeriesQueryRequest(BaseModel):
    metrics: List[str] = Field(..., description="List of metric names to query (e.g. ['router_cpu', 'rssi'])")
    entity_id: Optional[str] = Field(default=None, description="Optional entity ID (like MAC address) to filter by")
    start_time: datetime = Field(..., description="Start of the time window")
    end_time: datetime = Field(..., description="End of the time window")
    resolution: Optional[AggregationResolution] = Field(default=None, description="Force a specific resolution. If None, the planner selects the optimal.")
    pagination: Optional[CursorPagination] = Field(default_factory=CursorPagination)
    downsample_target: Optional[int] = Field(default=None, description="Target number of points for downsampling (e.g. 500 for charts)")
    window_function: Optional[str] = Field(default=None, description="Optional window function (e.g. 'sma', 'ema', 'rolling_median')")
    window_size: Optional[int] = Field(default=5, description="Size of the sliding window if a window function is used")

class QueryDiagnostics(BaseModel):
    execution_time_ms: float = 0.0
    rows_scanned: int = 0
    rows_returned: int = 0
    resolution_used: str = ""
    cache_hit: bool = False
    downsampled: bool = False

class TimeSeriesQueryResponse(BaseModel):
    metric_name: str
    data: List[Dict[str, Any]]
    next_cursor: Optional[str] = None
    diagnostics: QueryDiagnostics
