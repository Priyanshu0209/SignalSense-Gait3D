import logging
from typing import List, AsyncGenerator
from sqlalchemy.future import select
from sqlalchemy import or_, desc, asc
from datetime import datetime
from app.db.session import AsyncSessionLocal
from app.models.domain import EventModel
from app.models.timeline import EventTimelineQueryRequest, EventTimelineResponse, PaginatedEventTimelineResponse

logger = logging.getLogger("signalsense.services.timeline")

class EventTimelineEngine:

    @staticmethod
    def add_event(type_name: str, message: str, mac_address: str = "", severity: str = "INFO", category: str = "GENERAL"):
        logger.info(f"[TIMELINE EVENT] [{type_name}] {message}")
        try:
            import asyncio
            from app.services.database_service import DatabaseService
            loop = asyncio.get_running_loop()
            loop.create_task(DatabaseService.save_event(event_type=type_name, mac_address=mac_address or "UNKNOWN", message=message, severity=severity, category=category))
        except Exception as e:
            logger.debug(f"Could not save timeline event to database asynchronously: {e}")

    @staticmethod
    def _build_query(request: EventTimelineQueryRequest):
        stmt = select(EventModel)
        
        if request.start_time:
            stmt = stmt.where(EventModel.timestamp >= request.start_time)
        if request.end_time:
            stmt = stmt.where(EventModel.timestamp <= request.end_time)
            
        if request.severities:
            stmt = stmt.where(EventModel.severity.in_(request.severities))
            
        if request.categories:
            stmt = stmt.where(EventModel.category.in_(request.categories))
            
        if request.source_modules:
            stmt = stmt.where(EventModel.source_module.in_(request.source_modules))
            
        if request.entity_id:
            # Check both explicit entity_id and legacy mac_address
            stmt = stmt.where(
                or_(
                    EventModel.entity_id == request.entity_id,
                    EventModel.mac_address == request.entity_id
                )
            )
            
        if request.correlation_id:
            stmt = stmt.where(EventModel.correlation_id == request.correlation_id)
            
        if request.search_query:
            search_term = f"%{request.search_query}%"
            stmt = stmt.where(
                or_(
                    EventModel.message.ilike(search_term),
                    EventModel.payload.ilike(search_term),
                    EventModel.search_tags.ilike(search_term)
                )
            )
            
        if request.pagination.cursor:
            cursor_dt = datetime.fromisoformat(request.pagination.cursor.replace('Z', '+00:00'))
            if request.pagination.forward:
                stmt = stmt.where(EventModel.timestamp > cursor_dt)
            else:
                stmt = stmt.where(EventModel.timestamp < cursor_dt)
                
        if request.pagination.forward:
            stmt = stmt.order_by(EventModel.timestamp.asc(), EventModel.id.asc())
        else:
            stmt = stmt.order_by(EventModel.timestamp.desc(), EventModel.id.desc())
            
        stmt = stmt.limit(request.pagination.limit)
        return stmt

    @staticmethod
    async def query_timeline(request: EventTimelineQueryRequest) -> PaginatedEventTimelineResponse:

        async with AsyncSessionLocal() as session:
            stmt = EventTimelineEngine._build_query(request)
            result = await session.execute(stmt)
            records = result.scalars().all()
            
            # If queried backwards, reverse to preserve chronological reading order
            if not request.pagination.forward:
                records.reverse()
                
            events = []
            for r in records:
                events.append(EventTimelineResponse(
                    id=r.id,
                    timestamp=r.timestamp,
                    event_type=r.event_type,
                    mac_address=r.mac_address,
                    entity_id=r.entity_id,
                    severity=r.severity,
                    category=r.category,
                    source_module=r.source_module,
                    correlation_id=r.correlation_id,
                    search_tags=r.search_tags,
                    message=r.message,
                    payload=r.payload
                ))
                
            next_cursor = None
            if len(events) == request.pagination.limit:
                last_dt = events[-1].timestamp if request.pagination.forward else events[0].timestamp
                next_cursor = last_dt.isoformat().replace('+00:00', 'Z')
                
            return PaginatedEventTimelineResponse(
                events=events,
                next_cursor=next_cursor,
                total_returned=len(events)
            )

    @staticmethod
    async def stream_events(request: EventTimelineQueryRequest) -> AsyncGenerator[EventTimelineResponse, None]:

        async with AsyncSessionLocal() as session:
            stmt = EventTimelineEngine._build_query(request)
            # Remove limit for complete streaming (or keep large chunks)
            stmt = stmt.limit(None)
            
            stream = await session.stream_scalars(stmt)
            async for r in stream:
                yield EventTimelineResponse(
                    id=r.id,
                    timestamp=r.timestamp,
                    event_type=r.event_type,
                    mac_address=r.mac_address,
                    entity_id=r.entity_id,
                    severity=r.severity,
                    category=r.category,
                    source_module=r.source_module,
                    correlation_id=r.correlation_id,
                    search_tags=r.search_tags,
                    message=r.message,
                    payload=r.payload
                )
