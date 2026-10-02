from fastapi import APIRouter, Query
from typing import List, Any
import json
from datetime import datetime, timezone, timedelta
from app.db.session import AsyncSessionLocal
from app.models.domain import DeviceSnapshotModel
from sqlalchemy.future import select

router = APIRouter()

@router.get("/snapshots")
async def get_snapshots(
    start_time: str = Query(..., description="ISO 8601 start time"),
    end_time: str = Query(..., description="ISO 8601 end time")
) -> List[Any]:

    try:
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    except ValueError:
        return []

    async with AsyncSessionLocal() as session:
        stmt = select(DeviceSnapshotModel).filter(
            DeviceSnapshotModel.timestamp >= start_dt,
            DeviceSnapshotModel.timestamp <= end_dt
        ).order_by(DeviceSnapshotModel.timestamp.asc()).limit(500)
        
        result = await session.execute(stmt)
        records = result.scalars().all()
        
        snapshots = []
        for r in records:
            try:
                state = json.loads(r.state_json)
                snapshots.append({
                    "timestamp": r.timestamp.isoformat(),
                    "state": state
                })
            except:
                pass
                
        return snapshots
