import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from app.core.config import settings
from app.adapters.analytics.interface import IAnalyticsStorageEngine
from app.models.retention import AggregationResolution

logger = logging.getLogger("signalsense.workers.aggregation")

# Define the hierarchical rollup paths.
# source_resolution -> (target_resolution, window_minutes)
ROLLUP_HIERARCHY = {
    AggregationResolution.RAW: (AggregationResolution.MINUTE_1, 1),
    AggregationResolution.MINUTE_1: (AggregationResolution.MINUTE_5, 5),
    AggregationResolution.MINUTE_5: (AggregationResolution.MINUTE_15, 15),
    AggregationResolution.MINUTE_15: (AggregationResolution.MINUTE_30, 30),
    AggregationResolution.MINUTE_30: (AggregationResolution.HOURLY, 60),
    AggregationResolution.HOURLY: (AggregationResolution.DAILY, 1440),
    AggregationResolution.DAILY: (AggregationResolution.WEEKLY, 10080),
    AggregationResolution.WEEKLY: (AggregationResolution.MONTHLY, 43200),
    AggregationResolution.MONTHLY: (AggregationResolution.YEARLY, 525600)
}

METRICS_TO_AGGREGATE = ["router_cpu", "rssi"]

class AggregationSchedulerWorker:

    def __init__(self, engine: IAnalyticsStorageEngine):
        self.engine = engine
        self._running = False
        self._paused = False
        self._task = None
        self._lock = asyncio.Lock()
        
    async def start(self):
        if self._running:
            return
        logger.info("Starting Aggregation Scheduler Worker...")
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        if not self._running:
            return
        logger.info("Stopping Aggregation Scheduler Worker...")
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
                
    def pause(self):
        self._paused = True
        logger.info("Aggregation Scheduler paused.")
        
    def resume(self):
        self._paused = False
        logger.info("Aggregation Scheduler resumed.")
        
    async def _scheduler_loop(self):
        # Initial sleep to let other services start
        await asyncio.sleep(5)
        
        while self._running:
            try:
                if not self._paused:
                    await self.execute_aggregation()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in aggregation scheduler loop: {e}")
                
            # Run every minute
            try:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
                
    def _truncate_to_window(self, dt: datetime, window_minutes: int) -> datetime:

        # Simple truncation for minutes/hours/days (works well for multiples of 60)
        # Note: This is a simplified boundary logic
        total_minutes = dt.hour * 60 + dt.minute
        window_start_minute = (total_minutes // window_minutes) * window_minutes
        
        # Adjust day if window > 1440, etc. (Simplified for this exercise)
        # For full accuracy across months/years, standard libraries like dateutil are preferred.
        # But for minute/hour/daily it's trivial.
        if window_minutes >= 1440:
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif window_minutes >= 60:
            hour = window_start_minute // 60
            return dt.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            minute = window_start_minute % 60
            return dt.replace(minute=minute, second=0, microsecond=0)

    def _aggregate_data(self, data: List[Dict[str, Any]], target_resolution: str, metric_name: str, window_start: datetime) -> List[Dict[str, Any]]:
        if not data:
            return []
            
        # Group by entity_id
        grouped = {}
        for item in data:
            entity_id = item.get("entity_id")
            if entity_id not in grouped:
                grouped[entity_id] = []
            grouped[entity_id].append(item)
            
        results = []
        for entity_id, items in grouped.items():
            count = len(items)
            
            # If rolling up from raw, it's just 'value', if from aggregate, it has 'sum_value' etc.
            if "value" in items[0]:
                values = [x["value"] for x in items]
                sum_val = sum(values)
                min_val = min(values)
                max_val = max(values)
                avg_val = sum_val / count if count > 0 else 0
                actual_count = count
            else:
                sum_val = sum(x["sum_value"] for x in items)
                min_val = min(x["min_value"] for x in items)
                max_val = max(x["max_value"] for x in items)
                actual_count = sum(x["count"] for x in items)
                avg_val = sum_val / actual_count if actual_count > 0 else 0
                
            results.append({
                "timestamp": window_start,
                "resolution": target_resolution.value,
                "metric_name": metric_name,
                "entity_id": entity_id,
                "avg_value": avg_val,
                "min_value": min_val,
                "max_value": max_val,
                "sum_value": sum_val,
                "count": actual_count
            })
            
        return results

    async def execute_aggregation(self):

        if self._lock.locked():
            return
            
        async with self._lock:
            now = datetime.now(timezone.utc)
            
            for metric in METRICS_TO_AGGREGATE:
                for source_res, (target_res, window_mins) in ROLLUP_HIERARCHY.items():
                    # 1. Get checkpoint
                    ckpt = await self.engine.get_aggregation_checkpoint(target_res, metric)
                    
                    if not ckpt:
                        # Fallback for new metrics: start from 1 day ago or earliest
                        ckpt = now - timedelta(days=1)
                        ckpt = self._truncate_to_window(ckpt, window_mins)
                    elif ckpt.tzinfo is None:
                        ckpt = ckpt.replace(tzinfo=timezone.utc)
                    
                    # 2. Determine target window
                    window_end = ckpt + timedelta(minutes=window_mins)
                    
                    # If the window_end is in the future, we can't aggregate this window yet
                    if window_end > now:
                        continue
                        
                    # We can process multiple windows in batches to catch up, but we'll do 1 window per loop for safety
                    
                    # 3. Fetch data
                    if source_res == AggregationResolution.RAW:
                        data = await self.engine.fetch_raw_data_for_aggregation(metric, ckpt, window_end)
                    else:
                        data = await self.engine.fetch_aggregated_data_for_rollup(source_res, metric, ckpt, window_end)
                        
                    # 4. Compute Aggregate
                    if data:
                        aggregates = self._aggregate_data(data, target_res, metric, ckpt)
                        # 5. Save and bump checkpoint
                        await self.engine.save_time_series_aggregates(aggregates, window_end, target_res, metric)
                    else:
                        # Bump checkpoint even if no data exists so we don't get stuck
                        await self.engine.save_time_series_aggregates([], window_end, target_res, metric)
                    
                    # Yield to event loop
                    await asyncio.sleep(0.01)
