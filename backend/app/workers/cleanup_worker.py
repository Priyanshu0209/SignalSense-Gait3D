import asyncio
import logging
import time
from datetime import datetime
from typing import Dict
from app.core.config import settings
from app.adapters.analytics.interface import IAnalyticsStorageEngine
from app.models.retention import RetentionPolicy, CleanupMetrics, AggregationResolution

logger = logging.getLogger("signalsense.workers.cleanup")

class CleanupSchedulerWorker:

    def __init__(self, engine: IAnalyticsStorageEngine, policy: RetentionPolicy = None):
        self.engine = engine
        self.policy = policy or RetentionPolicy()
        self.metrics = CleanupMetrics()
        
        self._running = False
        self._paused = False
        self._cleanup_task = None
        self._cleanup_lock = asyncio.Lock()
        
    async def start(self):
        if self._running:
            return
        logger.info("Starting Cleanup Scheduler Worker...")
        self._running = True
        self._cleanup_task = asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        if not self._running:
            return
        logger.info("Stopping Cleanup Scheduler Worker...")
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
    def pause(self):
        self._paused = True
        logger.info("Cleanup Scheduler paused.")
        
    def resume(self):
        self._paused = False
        logger.info("Cleanup Scheduler resumed.")
        
    async def execute_cleanup(self, dry_run: bool = False) -> CleanupMetrics:

        if self._cleanup_lock.locked():
            logger.warning("Cleanup rejected: A cleanup job is already in progress.")
            return self.metrics
            
        async with self._cleanup_lock:
            if not dry_run:
                self.metrics.last_cleanup_time = datetime.now()
            
            start_time = time.time()
            total_deleted = 0
            total_bytes = 0
            
            for resolution, threshold in self.policy.thresholds.items():
                if threshold is None:
                    continue # Infinite retention
                    
                logger.info(f"Processing retention policy for {resolution.value} (threshold: {threshold} days)")
                
                # We chunk until no more records are deleted for this resolution
                while True:
                    if self._paused and not dry_run:
                        await asyncio.sleep(1)
                        continue
                        
                    try:
                        # With exponential backoff retry for SQLite "database is locked" errors
                        result = await self._execute_with_retry(
                            self.engine.prune_records,
                            resolution=resolution,
                            threshold_days=threshold,
                            chunk_size=settings.CLEANUP_BATCH_SIZE,
                            dry_run=dry_run
                        )
                        
                        deleted_chunk = result.get("deleted", 0)
                        bytes_chunk = result.get("estimated_bytes", 0)
                        
                        total_deleted += deleted_chunk
                        total_bytes += bytes_chunk
                        
                        # If dry run, or if the chunk didn't fill the batch size, we're done with this resolution
                        if dry_run or deleted_chunk < settings.CLEANUP_BATCH_SIZE:
                            break
                            
                        # Brief yield to allow other coroutines (REST API, etc.) to process
                        await asyncio.sleep(0.01)
                        
                    except Exception as e:
                        logger.error(f"Cleanup failure for {resolution.value}: {e}")
                        if not dry_run:
                            self.metrics.cleanup_failures += 1
                        break
                        
            duration = time.time() - start_time
            
            # If it's not a dry run, record metrics permanently
            if not dry_run:
                self.metrics.cleanup_duration_ms = duration * 1000
                self.metrics.rows_deleted += total_deleted
                self.metrics.estimated_reclaimed_storage_bytes += total_bytes
                logger.info(f"Cleanup completed in {duration:.2f}s. Deleted {total_deleted} rows.")
                return self.metrics
            else:
                # Return dry-run mock metrics
                mock_metrics = CleanupMetrics(
                    cleanup_duration_ms=duration * 1000,
                    rows_deleted=total_deleted,
                    estimated_reclaimed_storage_bytes=total_bytes
                )
                return mock_metrics
                
    async def _execute_with_retry(self, coro_func, *args, **kwargs):

        max_retries = 5
        base_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                # Catch generic exceptions - in SQLAlchemy this is typically OperationalError
                if attempt == max_retries - 1:
                    raise
                
                self.metrics.cleanup_retries += 1
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Database operation failed, retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(delay)
                
    async def _scheduler_loop(self):
        while self._running:
            try:
                if not self._paused:
                    await self.execute_cleanup(dry_run=False)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                
            # Wait for next cycle
            try:
                await asyncio.sleep(settings.CLEANUP_INTERVAL_HOURS * 3600)
            except asyncio.CancelledError:
                break
