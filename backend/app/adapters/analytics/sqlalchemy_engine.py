import json
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.future import select
from sqlalchemy import delete, func
from app.db.session import AsyncSessionLocal
from app.models.domain import (
    RouterStatusHistoryModel,
    DiscoveryStatisticsModel,
    NetworkTopologySnapshotModel,
    RSSIHistoryModel,
    EventModel,
    DeviceSessionModel,
    TimeSeriesAggregateModel,
    AggregationCheckpointModel
)
from app.models.retention import AggregationResolution
from app.adapters.analytics.interface import IAnalyticsStorageEngine

logger = logging.getLogger("signalsense.adapters.analytics.sqlalchemy")

class SQLAlchemyAnalyticsEngine(IAnalyticsStorageEngine):

    async def save_router_status(self, cpu_usage: float = None, memory_usage: float = None, uptime: int = None):
        async with AsyncSessionLocal() as session:
            try:
                record = RouterStatusHistoryModel(
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    uptime=uptime
                )
                session.add(record)
                await session.commit()
            except Exception as e:
                logger.error(f"Error saving router status history via SQLAlchemy: {e}")
                await session.rollback()

    async def save_discovery_statistics(self, metrics: dict):
        async with AsyncSessionLocal() as session:
            try:
                record = DiscoveryStatisticsModel(
                    total_scans=metrics.get("total_scans", 0),
                    successful_scans=metrics.get("successful_scans", 0),
                    failed_scans=metrics.get("failed_scans", 0),
                    avg_scan_duration_ms=metrics.get("avg_scan_duration_ms", 0.0),
                    max_scan_duration_ms=metrics.get("max_scan_duration_ms", 0.0),
                    reconnect_count=metrics.get("reconnect_count", 0),
                    dropped_events=metrics.get("dropped_events", 0)
                )
                session.add(record)
                await session.commit()
            except Exception as e:
                logger.error(f"Error saving discovery statistics via SQLAlchemy: {e}")
                await session.rollback()

    async def save_topology_snapshot(self, topology_data: dict, node_count: int, edge_count: int = None, health_score: float = None, is_compressed: bool = False, metadata_json: str = None, raw_data_str: str = None):
        async with AsyncSessionLocal() as session:
            try:
                # If raw_data_str is provided (e.g. pre-compressed base64), use it. Otherwise dump the dict.
                final_data = raw_data_str if raw_data_str else json.dumps(topology_data)
                
                record = NetworkTopologySnapshotModel(
                    node_count=node_count,
                    edge_count=edge_count,
                    health_score=health_score,
                    is_compressed=is_compressed,
                    metadata_json=metadata_json,
                    topology_data=final_data
                )
                session.add(record)
                await session.commit()
            except Exception as e:
                logger.error(f"Error saving topology snapshot via SQLAlchemy: {e}")
                await session.rollback()

    async def prune_records(self, resolution: AggregationResolution, threshold_days: int, chunk_size: int = 1000, dry_run: bool = False) -> dict:
        threshold = datetime.now(timezone.utc) - timedelta(days=threshold_days)
        result_metrics = {"deleted": 0, "estimated_bytes": 0}
        
        # Determine models based on resolution
        if resolution == AggregationResolution.RAW:
            models_to_prune = [
                (RouterStatusHistoryModel, RouterStatusHistoryModel.timestamp),
                (DiscoveryStatisticsModel, DiscoveryStatisticsModel.timestamp),
                (NetworkTopologySnapshotModel, NetworkTopologySnapshotModel.timestamp),
                (RSSIHistoryModel, RSSIHistoryModel.timestamp),
                (EventModel, EventModel.timestamp),
                (DeviceSessionModel, DeviceSessionModel.connection_time)
            ]
        else:
            # Placeholder for aggregated tables
            return result_metrics

        async with AsyncSessionLocal() as session:
            for model_cls, time_col in models_to_prune:
                try:
                    if dry_run:
                        stmt = select(func.count()).select_from(model_cls).where(time_col < threshold)
                        count = await session.scalar(stmt)
                        result_metrics["deleted"] += (count or 0)
                        # Rough estimate: ~200 bytes per row
                        result_metrics["estimated_bytes"] += (count or 0) * 200
                    else:
                        # SQLite workaround for chunked deletes: select IDs first, then delete them
                        # This works universally across dialects
                        stmt_ids = select(model_cls.id).where(time_col < threshold).limit(chunk_size)
                        ids_to_delete = (await session.execute(stmt_ids)).scalars().all()
                        
                        if ids_to_delete:
                            stmt_del = delete(model_cls).where(model_cls.id.in_(ids_to_delete))
                            res = await session.execute(stmt_del)
                            result_metrics["deleted"] += res.rowcount
                            await session.commit()
                except Exception as e:
                    logger.error(f"Error pruning records for {model_cls.__name__}: {e}")
                    await session.rollback()
                    
        return result_metrics

    async def get_aggregation_checkpoint(self, resolution: AggregationResolution, metric_name: str, entity_id: str = None) -> datetime:
        checkpoint_id = f"{resolution.value}_{metric_name}_{entity_id or 'GLOBAL'}"
        async with AsyncSessionLocal() as session:
            stmt = select(AggregationCheckpointModel).where(AggregationCheckpointModel.id == checkpoint_id)
            result = await session.execute(stmt)
            checkpoint = result.scalars().first()
            if checkpoint:
                return checkpoint.last_aggregated_timestamp
            return None

    async def save_time_series_aggregates(self, aggregates: list, new_checkpoint_time: datetime, resolution: AggregationResolution, metric_name: str, entity_id: str = None):
        checkpoint_id = f"{resolution.value}_{metric_name}_{entity_id or 'GLOBAL'}"
        async with AsyncSessionLocal() as session:
            try:
                # Save aggregates
                for agg in aggregates:
                    record = TimeSeriesAggregateModel(**agg)
                    session.add(record)
                    
                # Update checkpoint
                stmt = select(AggregationCheckpointModel).where(AggregationCheckpointModel.id == checkpoint_id)
                result = await session.execute(stmt)
                checkpoint = result.scalars().first()
                if checkpoint:
                    checkpoint.last_aggregated_timestamp = new_checkpoint_time
                else:
                    checkpoint = AggregationCheckpointModel(
                        id=checkpoint_id,
                        resolution=resolution.value,
                        metric_name=metric_name,
                        entity_id=entity_id,
                        last_aggregated_timestamp=new_checkpoint_time
                    )
                    session.add(checkpoint)
                    
                await session.commit()
            except Exception as e:
                logger.error(f"Error saving time series aggregates: {e}")
                await session.rollback()

    async def fetch_raw_data_for_aggregation(self, metric_name: str, start_time: datetime, end_time: datetime) -> list:
        async with AsyncSessionLocal() as session:
            results = []
            if metric_name == "router_cpu":
                stmt = select(RouterStatusHistoryModel).where(
                    RouterStatusHistoryModel.timestamp >= start_time,
                    RouterStatusHistoryModel.timestamp < end_time
                )
                for row in (await session.execute(stmt)).scalars().all():
                    if row.cpu_usage is not None:
                        results.append({"timestamp": row.timestamp, "value": row.cpu_usage, "entity_id": None})
            elif metric_name == "rssi":
                stmt = select(RSSIHistoryModel).where(
                    RSSIHistoryModel.timestamp >= start_time,
                    RSSIHistoryModel.timestamp < end_time
                )
                for row in (await session.execute(stmt)).scalars().all():
                    if row.raw_rssi is not None:
                        results.append({"timestamp": row.timestamp, "value": row.raw_rssi, "entity_id": row.mac_address})
            return results

    async def fetch_aggregated_data_for_rollup(self, source_resolution: AggregationResolution, metric_name: str, start_time: datetime, end_time: datetime) -> list:
        async with AsyncSessionLocal() as session:
            stmt = select(TimeSeriesAggregateModel).where(
                TimeSeriesAggregateModel.resolution == source_resolution.value,
                TimeSeriesAggregateModel.metric_name == metric_name,
                TimeSeriesAggregateModel.timestamp >= start_time,
                TimeSeriesAggregateModel.timestamp < end_time
            )
            results = []
            for row in (await session.execute(stmt)).scalars().all():
                results.append({
                    "timestamp": row.timestamp,
                    "avg_value": row.avg_value,
                    "min_value": row.min_value,
                    "max_value": row.max_value,
                    "sum_value": row.sum_value,
                    "count": row.count,
                    "entity_id": row.entity_id
                })
            return results

    async def stream_time_series_data(self, metric_name: str, resolution: AggregationResolution, start_time: datetime, end_time: datetime, entity_id: str = None, cursor: str = None, limit: int = 1000, forward: bool = True):
        # We need to construct a robust cursor based query
        async with AsyncSessionLocal() as session:
            if resolution == AggregationResolution.RAW:
                if metric_name == "router_cpu":
                    model = RouterStatusHistoryModel
                    value_col = RouterStatusHistoryModel.cpu_usage
                    entity_col = None
                elif metric_name == "rssi":
                    model = RSSIHistoryModel
                    value_col = RSSIHistoryModel.raw_rssi
                    entity_col = RSSIHistoryModel.mac_address
                else:
                    return # Unknown metric
                    
                stmt = select(model).where(model.timestamp >= start_time, model.timestamp < end_time)
                if entity_id and entity_col is not None:
                    stmt = stmt.where(entity_col == entity_id)
            else:
                stmt = select(TimeSeriesAggregateModel).where(
                    TimeSeriesAggregateModel.resolution == resolution.value,
                    TimeSeriesAggregateModel.metric_name == metric_name,
                    TimeSeriesAggregateModel.timestamp >= start_time,
                    TimeSeriesAggregateModel.timestamp < end_time
                )
                if entity_id:
                    stmt = stmt.where(TimeSeriesAggregateModel.entity_id == entity_id)

            if cursor:
                cursor_dt = datetime.fromisoformat(cursor.replace('Z', '+00:00'))
                if forward:
                    stmt = stmt.where(model.timestamp > cursor_dt) if resolution == AggregationResolution.RAW else stmt.where(TimeSeriesAggregateModel.timestamp > cursor_dt)
                else:
                    stmt = stmt.where(model.timestamp < cursor_dt) if resolution == AggregationResolution.RAW else stmt.where(TimeSeriesAggregateModel.timestamp < cursor_dt)

            if forward:
                stmt = stmt.order_by(model.timestamp.asc()) if resolution == AggregationResolution.RAW else stmt.order_by(TimeSeriesAggregateModel.timestamp.asc())
            else:
                stmt = stmt.order_by(model.timestamp.desc()) if resolution == AggregationResolution.RAW else stmt.order_by(TimeSeriesAggregateModel.timestamp.desc())
                
            stmt = stmt.limit(limit)
            
            # Use stream_scalars to prevent fully loading into memory (supported in SQLAlchemy async)
            result = await session.stream_scalars(stmt)
            async for row in result:
                if resolution == AggregationResolution.RAW:
                    val = getattr(row, value_col.name) if hasattr(value_col, 'name') else getattr(row, value_col.key)
                    ent = getattr(row, entity_col.key) if entity_col is not None else None
                    yield {
                        "timestamp": row.timestamp,
                        "value": val,
                        "entity_id": ent
                    }
                else:
                    yield {
                        "timestamp": row.timestamp,
                        "avg_value": row.avg_value,
                        "min_value": row.min_value,
                        "max_value": row.max_value,
                        "sum_value": row.sum_value,
                        "count": row.count,
                        "entity_id": row.entity_id
                    }

    async def query_telemetry(self, query: str, filters: dict, time_range: tuple):

        pass
        
    async def process_stream_window(self, metric: str, window_size_seconds: int):

        pass
