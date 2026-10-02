from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from app.events.bus import get_telemetry_bus, TelemetryEvent

router = APIRouter()

class TelemetryPayload(BaseModel):
    source_id: str
    topic: str
    data: Dict[str, Any]

@router.post("/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):

    try:
        bus = get_telemetry_bus()
        event = TelemetryEvent(
            topic=payload.topic,
            source_id=payload.source_id,
            payload=payload.data
        )
        await bus.publish(event)
        return {"status": "accepted", "event_id": event.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
