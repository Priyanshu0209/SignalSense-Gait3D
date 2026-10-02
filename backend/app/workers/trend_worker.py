import asyncio
import logging
from typing import List
from app.services.trend_analytics_engine import TrendAnalyticsEngine

logger = logging.getLogger("signalsense.workers.trend")

class TrendCalculationWorker:

    def __init__(self, check_interval_seconds: int = 900):
        self.check_interval = check_interval_seconds
        self._running = False
        self._task = None
        # Core metrics to trend globally
        self.metrics_to_trend = ["rssi", "latency", "device_count", "bandwidth", "packet_loss"]
        # Standard analytical windows
        self.windows = [1, 7, 30]

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._trend_loop())
        logger.info(f"TrendCalculationWorker started (interval {self.check_interval}s)")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("TrendCalculationWorker stopped")

    async def _trend_loop(self):
        while self._running:
            try:
                await self._recalculate_all_trends()
            except Exception as e:
                logger.error(f"Error in TrendCalculationWorker: {e}")
            
            # Sleep until next interval
            await asyncio.sleep(self.check_interval)

    async def _recalculate_all_trends(self):
        logger.debug("Starting background trend recalculation...")
        
        for metric in self.metrics_to_trend:
            for window in self.windows:
                # Recalculate Global Trends
                await TrendAnalyticsEngine.calculate_and_store_trend(metric, window, entity_id=None)
                
                # We could also pull a distinct list of MAC addresses and calculate per-device
                # For Enterprise scale (100K devices), we would queue these up into smaller batches
                # to prevent database locking. For now, we calculate global trends.
                
        logger.debug("Background trend recalculation complete.")
