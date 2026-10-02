from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from app.models.query import CursorPagination

class EventTimelineQueryRequest(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    severities: Optional[List[str]] = Field(default=None, description="e.g. ['INFO', 'ERROR']")
    categories: Optional[List[str]] = Field(default=None, description="e.g. ['DEVICE', 'SYSTEM']")
    source_modules: Optional[List[str]] = Field(default=None)
    entity_id: Optional[str] = Field(default=None)
    correlation_id: Optional[str] = Field(default=None)
    search_query: Optional[str] = Field(default=None, description="Text to search within message, payload, or tags")
    pagination: Optional[CursorPagination] = Field(default_factory=CursorPagination)

class EventTimelineResponse(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    mac_address: Optional[str] = None
    entity_id: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    source_module: Optional[str] = None
    correlation_id: Optional[str] = None
    search_tags: Optional[str] = None
    message: Optional[str] = None
    payload: Optional[str] = None

class PaginatedEventTimelineResponse(BaseModel):
    events: List[EventTimelineResponse]
    next_cursor: Optional[str] = None
    total_returned: int
