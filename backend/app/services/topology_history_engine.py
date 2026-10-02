import json
import zlib
import base64
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.session import AsyncSessionLocal
from app.models.domain import NetworkTopologySnapshotModel
from app.models.topology import (
    TopologyHistoryQueryRequest,
    TopologySnapshotResponse,
    PaginatedTopologySnapshotResponse,
    TopologyDiffResponse,
    TopologyNode,
    TopologyEdge
)

logger = logging.getLogger("signalsense.services.topology")

class TopologyHistoryEngine:

    COMPRESSION_THRESHOLD_BYTES = 50 * 1024  # Compress if > 50KB

    @staticmethod
    def _compress_data(data: dict) -> (str, bool):

        json_str = json.dumps(data)
        if len(json_str.encode('utf-8')) > TopologyHistoryEngine.COMPRESSION_THRESHOLD_BYTES:
            compressed = zlib.compress(json_str.encode('utf-8'))
            b64_str = base64.b64encode(compressed).decode('utf-8')
            return b64_str, True
        return json_str, False

    @staticmethod
    def _decompress_data(data_str: str, is_compressed: bool) -> dict:
        if not data_str:
            return {"nodes": [], "edges": []}
            
        if is_compressed:
            compressed_bytes = base64.b64decode(data_str.encode('utf-8'))
            decompressed_bytes = zlib.decompress(compressed_bytes)
            return json.loads(decompressed_bytes.decode('utf-8'))
        return json.loads(data_str)

    @staticmethod
    async def save_snapshot(nodes: List[Dict], edges: List[Dict], health_score: float = None, metadata: dict = None):

        topology_dict = {"nodes": nodes, "edges": edges}
        data_str, is_compressed = TopologyHistoryEngine._compress_data(topology_dict)
        
        async with AsyncSessionLocal() as session:
            record = NetworkTopologySnapshotModel(
                node_count=len(nodes),
                edge_count=len(edges),
                health_score=health_score,
                is_compressed=is_compressed,
                metadata_json=json.dumps(metadata) if metadata else None,
                topology_data=data_str
            )
            session.add(record)
            await session.commit()
            
    @staticmethod
    async def get_snapshot_at(timestamp: datetime) -> Optional[TopologySnapshotResponse]:

        async with AsyncSessionLocal() as session:
            stmt = select(NetworkTopologySnapshotModel).where(
                NetworkTopologySnapshotModel.timestamp <= timestamp
            ).order_by(desc(NetworkTopologySnapshotModel.timestamp)).limit(1)
            
            result = await session.execute(stmt)
            record = result.scalars().first()
            
            if not record:
                return None
                
            raw_data = TopologyHistoryEngine._decompress_data(record.topology_data, record.is_compressed)
            
            nodes = [TopologyNode(**n) for n in raw_data.get("nodes", [])]
            edges = [TopologyEdge(**e) for e in raw_data.get("edges", [])]
            
            meta = json.loads(record.metadata_json) if record.metadata_json else None
            
            return TopologySnapshotResponse(
                id=record.id,
                timestamp=record.timestamp,
                node_count=record.node_count,
                edge_count=record.edge_count,
                health_score=record.health_score,
                metadata=meta,
                nodes=nodes,
                edges=edges
            )

    @staticmethod
    async def stream_playback(request: TopologyHistoryQueryRequest) -> AsyncGenerator[TopologySnapshotResponse, None]:

        async with AsyncSessionLocal() as session:
            stmt = select(NetworkTopologySnapshotModel)
            if request.start_time:
                stmt = stmt.where(NetworkTopologySnapshotModel.timestamp >= request.start_time)
            if request.end_time:
                stmt = stmt.where(NetworkTopologySnapshotModel.timestamp <= request.end_time)
                
            if request.pagination.cursor:
                cursor_dt = datetime.fromisoformat(request.pagination.cursor.replace('Z', '+00:00'))
                if request.pagination.forward:
                    stmt = stmt.where(NetworkTopologySnapshotModel.timestamp > cursor_dt)
                else:
                    stmt = stmt.where(NetworkTopologySnapshotModel.timestamp < cursor_dt)
                    
            if request.pagination.forward:
                stmt = stmt.order_by(NetworkTopologySnapshotModel.timestamp.asc())
            else:
                stmt = stmt.order_by(NetworkTopologySnapshotModel.timestamp.desc())
                
            if request.pagination.limit:
                stmt = stmt.limit(request.pagination.limit)
                
            stream = await session.stream_scalars(stmt)
            
            async for record in stream:
                raw_data = TopologyHistoryEngine._decompress_data(record.topology_data, record.is_compressed)
                meta = json.loads(record.metadata_json) if record.metadata_json else None
                
                yield TopologySnapshotResponse(
                    id=record.id,
                    timestamp=record.timestamp,
                    node_count=record.node_count,
                    edge_count=record.edge_count,
                    health_score=record.health_score,
                    metadata=meta,
                    nodes=[TopologyNode(**n) for n in raw_data.get("nodes", [])],
                    edges=[TopologyEdge(**e) for e in raw_data.get("edges", [])]
                )

    @staticmethod
    def compare_snapshots(snap_a: TopologySnapshotResponse, snap_b: TopologySnapshotResponse) -> TopologyDiffResponse:

        nodes_a = {n.id: n for n in snap_a.nodes}
        nodes_b = {n.id: n for n in snap_b.nodes}
        
        added_nodes = []
        removed_nodes = []
        modified_nodes = []
        
        for n_id, n in nodes_b.items():
            if n_id not in nodes_a:
                added_nodes.append(n)
            elif n.model_dump() != nodes_a[n_id].model_dump():
                modified_nodes.append(n)
                
        for n_id, n in nodes_a.items():
            if n_id not in nodes_b:
                removed_nodes.append(n)
                
        # Edge Diff using composite key (source_target)
        edges_a = {f"{e.source}_{e.target}": e for e in snap_a.edges}
        edges_b = {f"{e.source}_{e.target}": e for e in snap_b.edges}
        
        added_edges = []
        removed_edges = []
        modified_edges = []
        
        for e_id, e in edges_b.items():
            if e_id not in edges_a:
                added_edges.append(e)
            elif e.model_dump() != edges_a[e_id].model_dump():
                modified_edges.append(e)
                
        for e_id, e in edges_a.items():
            if e_id not in edges_b:
                removed_edges.append(e)
                
        return TopologyDiffResponse(
            timestamp_a=snap_a.timestamp,
            timestamp_b=snap_b.timestamp,
            nodes_added=added_nodes,
            nodes_removed=removed_nodes,
            nodes_modified=modified_nodes,
            edges_added=added_edges,
            edges_removed=removed_edges,
            edges_modified=modified_edges
        )
