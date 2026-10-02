import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.domain import TrendProfileModel, TimeSeriesAggregateModel
from app.services.math_utils import TimeSeriesMath

logger = logging.getLogger("signalsense.services.trend_analytics")

class TrendAnalyticsEngine:

    @staticmethod
    async def calculate_and_store_trend(
        metric_name: str, 
        time_window_days: int, 
        entity_id: Optional[str] = None
    ) -> Optional[TrendProfileModel]:

        async with AsyncSessionLocal() as session:
            now = datetime.now(timezone.utc)
            start_time = now - timedelta(days=time_window_days)
            
            # Fetch historical data
            stmt = select(TimeSeriesAggregateModel).filter(
                TimeSeriesAggregateModel.metric_name == metric_name,
                TimeSeriesAggregateModel.timestamp >= start_time,
                TimeSeriesAggregateModel.timestamp <= now
            )
            
            if entity_id:
                stmt = stmt.filter(TimeSeriesAggregateModel.entity_id == entity_id)
            else:
                stmt = stmt.filter(TimeSeriesAggregateModel.entity_id.is_(None))
                
            stmt = stmt.order_by(TimeSeriesAggregateModel.timestamp.asc())
            result = await session.execute(stmt)
            records = result.scalars().all()
            
            if not records:
                return None
                
            # Convert to math_utils format
            data_points = []
            for r in records:
                data_points.append({
                    "timestamp": r.timestamp,
                    "value": r.avg_value if r.avg_value is not None else 0.0
                })
                
            # Execute Pure Python Mathematics
            metrics = TimeSeriesMath.calculate_trend_metrics(data_points)
            if not metrics:
                return None
                
            # Persist the profile
            window_str = f"{time_window_days}d"
            profile_id = f"{metric_name}_{entity_id}_{window_str}" if entity_id else f"{metric_name}_global_{window_str}"
            
            profile = await session.get(TrendProfileModel, profile_id)
            if not profile:
                profile = TrendProfileModel(
                    id=profile_id,
                    metric_name=metric_name,
                    entity_id=entity_id,
                    time_window=window_str
                )
                session.add(profile)
                
            profile.current_value = metrics.get("current_value")
            profile.previous_value = metrics.get("previous_value")
            profile.growth_rate = metrics.get("growth_rate")
            profile.variance = metrics.get("variance")
            profile.std_dev = metrics.get("std_dev")
            profile.forecast_value = metrics.get("forecast_value")
            profile.anomaly_score = metrics.get("anomaly_score")
            
            await session.commit()
            return profile

    @staticmethod
    async def get_trend_profile(
        metric_name: str, 
        time_window_days: int, 
        entity_id: Optional[str] = None
    ) -> Optional[Dict]:

        window_str = f"{time_window_days}d"
        profile_id = f"{metric_name}_{entity_id}_{window_str}" if entity_id else f"{metric_name}_global_{window_str}"
        
        async with AsyncSessionLocal() as session:
            profile = await session.get(TrendProfileModel, profile_id)
            if profile:
                return {
                    "id": profile.id,
                    "metric_name": profile.metric_name,
                    "entity_id": profile.entity_id,
                    "time_window": profile.time_window,
                    "current_value": profile.current_value,
                    "previous_value": profile.previous_value,
                    "growth_rate": profile.growth_rate,
                    "variance": profile.variance,
                    "std_dev": profile.std_dev,
                    "forecast_value": profile.forecast_value,
                    "anomaly_score": profile.anomaly_score,
                    "last_calculated": profile.last_calculated.isoformat()
                }
        return None
