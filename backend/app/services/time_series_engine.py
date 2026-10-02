import asyncio
import time
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, AsyncGenerator
from app.models.query import TimeSeriesQueryRequest, TimeSeriesQueryResponse, QueryDiagnostics
from app.models.retention import AggregationResolution
from app.adapters.analytics.interface import IAnalyticsStorageEngine
from app.core.cache import QueryCache
from app.services.math_utils import TimeSeriesMath
import logging

logger = logging.getLogger("signalsense.services.time_series")

class QueryPlanner:
    @staticmethod
    def select_optimal_resolution(start_time: datetime, end_time: datetime) -> AggregationResolution:
        delta = end_time - start_time
        hours = delta.total_seconds() / 3600
        days = hours / 24

        if hours <= 6:
            return AggregationResolution.RAW
        elif hours <= 24:
            return AggregationResolution.MINUTE_1
        elif days <= 3:
            return AggregationResolution.MINUTE_5
        elif days <= 7:
            return AggregationResolution.MINUTE_15
        elif days <= 30:
            return AggregationResolution.HOURLY
        elif days <= 365:
            return AggregationResolution.DAILY
        elif days <= 1825: # 5 years
            return AggregationResolution.WEEKLY
        else:
            return AggregationResolution.MONTHLY

class TimeSeriesEngine:

    def __init__(self, engine: IAnalyticsStorageEngine, cache: QueryCache):
        self.engine = engine
        self.cache = cache

    def _generate_cache_key(self, metric: str, request: TimeSeriesQueryRequest) -> str:
        # Create a deterministic hash for the cache key
        data = {
            "metric": metric,
            "entity": request.entity_id,
            "start": request.start_time.isoformat(),
            "end": request.end_time.isoformat(),
            "res": request.resolution.value if request.resolution else "AUTO",
            "ds": request.downsample_target,
            "win_fn": request.window_function,
            "win_size": request.window_size,
            "limit": request.pagination.limit,
            "cursor": request.pagination.cursor,
            "forward": request.pagination.forward
        }
        encoded = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()

    async def execute_query(self, request: TimeSeriesQueryRequest) -> List[TimeSeriesQueryResponse]:

        resolution = request.resolution or QueryPlanner.select_optimal_resolution(request.start_time, request.end_time)
        
        # Parallel execution of multiple metrics
        tasks = []
        for metric in request.metrics:
            tasks.append(self._execute_single_metric(metric, resolution, request))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Error querying metric {request.metrics[i]}: {res}")
                # We could append an error response, but for now we skip or return empty
                # We will return an empty list with 0 diagnostics to ensure API stability
                final_results.append(
                    TimeSeriesQueryResponse(
                        metric_name=request.metrics[i],
                        data=[],
                        diagnostics=QueryDiagnostics()
                    )
                )
            else:
                final_results.append(res)
                
        return final_results

    async def _execute_single_metric(self, metric: str, resolution: AggregationResolution, request: TimeSeriesQueryRequest) -> TimeSeriesQueryResponse:
        start_ts = time.time()
        
        cache_key = self._generate_cache_key(metric, request)
        cached_response = await self.cache.get(cache_key)
        
        if cached_response:
            # Update execution time for diagnostics even if cached
            cached_response.diagnostics.execution_time_ms = round((time.time() - start_ts) * 1000, 2)
            cached_response.diagnostics.cache_hit = True
            return cached_response

        # 1. Stream data from DB
        data = []
        stream = self.engine.stream_time_series_data(
            metric_name=metric,
            resolution=resolution,
            start_time=request.start_time,
            end_time=request.end_time,
            entity_id=request.entity_id,
            cursor=request.pagination.cursor,
            limit=request.pagination.limit,
            forward=request.pagination.forward
        )
        
        rows_scanned = 0
        async for row in stream:
            data.append(row)
            rows_scanned += 1
            
        # Reverse if fetched backward to return chronological order
        if not request.pagination.forward:
            data.reverse()
            
        # Determine next cursor
        next_cursor = None
        if len(data) == request.pagination.limit:
            # The next cursor is the timestamp of the last element returned
            last_dt = data[-1]["timestamp"] if request.pagination.forward else data[0]["timestamp"]
            next_cursor = last_dt.isoformat().replace('+00:00', 'Z')
            
        # 2. Apply window functions
        if request.window_function and len(data) > 0:
            data = TimeSeriesMath.apply_window_function(data, request.window_function, request.window_size)
            
        # 3. Apply Downsampling
        downsampled = False
        if request.downsample_target and len(data) > request.downsample_target:
            data = TimeSeriesMath.lttb_downsample(data, request.downsample_target)
            downsampled = True

        execution_time_ms = round((time.time() - start_ts) * 1000, 2)
        
        diagnostics = QueryDiagnostics(
            execution_time_ms=execution_time_ms,
            rows_scanned=rows_scanned,
            rows_returned=len(data),
            resolution_used=resolution.value,
            cache_hit=False,
            downsampled=downsampled
        )
        
        response = TimeSeriesQueryResponse(
            metric_name=metric,
            data=data,
            next_cursor=next_cursor,
            diagnostics=diagnostics
        )
        
        # Save to cache (default TTL 60 seconds)
        await self.cache.set(cache_key, response)
        
        return response
