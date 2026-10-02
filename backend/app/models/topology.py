from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from app.models.query import CursorPagination

class TopologyHistoryQueryRequest(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pagination: Optional[CursorPagination] = Field(default_factory=CursorPagination)

class TopologyNode(BaseModel):
    id: str
    type: str
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TopologyEdge(BaseModel):
    source: str
    target: str
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TopologySnapshotResponse(BaseModel):
    id: int
    timestamp: datetime
    node_count: int
    edge_count: Optional[int] = None
    health_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    nodes: List[TopologyNode]
    edges: List[TopologyEdge]

class PaginatedTopologySnapshotResponse(BaseModel):
    snapshots: List[TopologySnapshotResponse]
    next_cursor: Optional[str] = None
    total_returned: int

class TopologyDiffResponse(BaseModel):
    timestamp_a: datetime
    timestamp_b: datetime
    nodes_added: List[TopologyNode]
    nodes_removed: List[TopologyNode]
    nodes_modified: List[TopologyNode]
    edges_added: List[TopologyEdge]
    edges_removed: List[TopologyEdge]
    edges_modified: List[TopologyEdge]
