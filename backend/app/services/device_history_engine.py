import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy import func
from app.db.session import AsyncSessionLocal
from app.models.domain import DeviceModel, DeviceSessionModel, DeviceMetadataHistoryModel

logger = logging.getLogger("signalsense.services.device_history")

class DeviceHistoryEngine:

    @staticmethod
    async def get_device_lifecycle(mac_address: str) -> Optional[Dict[str, Any]]:

        async with AsyncSessionLocal() as session:
            device = await session.get(DeviceModel, mac_address)
            if not device:
                return None
                
            # Compute session metrics
            stmt = select(
                func.count(DeviceSessionModel.id).label("total_sessions"),
                func.sum(DeviceSessionModel.session_duration).label("total_duration"),
                func.avg(DeviceSessionModel.session_duration).label("avg_duration"),
                func.max(DeviceSessionModel.session_duration).label("max_duration")
            ).filter(
                DeviceSessionModel.mac_address == mac_address,
                DeviceSessionModel.session_duration.isnot(None)
            )
            
            result = await session.execute(stmt)
            metrics = result.one()
            
            total_sessions = metrics.total_sessions or 0
            total_duration = metrics.total_duration or 0
            avg_duration = int(metrics.avg_duration) if metrics.avg_duration else 0
            max_duration = metrics.max_duration or 0
            
            # Calculate availability %
            now = datetime.now(timezone.utc)
            if device.first_seen.tzinfo is None:
                first_seen = device.first_seen.replace(tzinfo=timezone.utc)
            else:
                first_seen = device.first_seen
                
            total_time_known = (now - first_seen).total_seconds()
            
            availability_percentage = 0.0
            if total_time_known > 0:
                availability_percentage = round((total_duration / total_time_known) * 100.0, 2)
                availability_percentage = min(availability_percentage, 100.0)
                
            return {
                "mac_address": device.mac_address,
                "first_seen": first_seen.isoformat(),
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "current_status": device.current_status,
                "online_sessions": total_sessions,
                "reconnect_count": max(0, total_sessions - 1),
                "session_duration_total": total_duration,
                "average_session_duration": avg_duration,
                "longest_session_duration": max_duration,
                "availability_percentage": availability_percentage
            }

    @staticmethod
    async def get_metadata_timeline(mac_address: str, limit: int = 100) -> List[Dict[str, Any]]:

        async with AsyncSessionLocal() as session:
            stmt = select(DeviceMetadataHistoryModel).filter(
                DeviceMetadataHistoryModel.mac_address == mac_address
            ).order_by(DeviceMetadataHistoryModel.timestamp.desc()).limit(limit)
            
            result = await session.execute(stmt)
            records = result.scalars().all()
            
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "field": r.field_name,
                    "old_value": r.old_value,
                    "new_value": r.new_value
                }
                for r in records
            ]

    @staticmethod
    async def get_session_history(mac_address: str, limit: int = 100) -> List[Dict[str, Any]]:

        async with AsyncSessionLocal() as session:
            stmt = select(DeviceSessionModel).filter(
                DeviceSessionModel.mac_address == mac_address
            ).order_by(DeviceSessionModel.connection_time.desc()).limit(limit)
            
            result = await session.execute(stmt)
            records = result.scalars().all()
            
            return [
                {
                    "connection_time": r.connection_time.isoformat(),
                    "disconnection_time": r.disconnection_time.isoformat() if r.disconnection_time else None,
                    "duration_seconds": r.session_duration
                }
                for r in records
            ]
