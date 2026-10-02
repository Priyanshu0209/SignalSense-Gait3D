import logging
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
import uuid

logger = logging.getLogger("signalsense.graph")

class GraphNode(BaseModel):
    id: str
    type: str  # Router, Switch, AP, Client, Server, Service, Application, Edge Agent
    properties: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    target: str
    relationship: str  # Connected, Uses, DependsOn, RoamsTo, CommunicatesWith
    properties: Dict[str, Any] = Field(default_factory=dict)

class GraphDatabase:

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self._adjacency_list: Dict[str, Set[str]] = {}
        self._reverse_adjacency: Dict[str, Set[str]] = {}

    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node
        if node.id not in self._adjacency_list:
            self._adjacency_list[node.id] = set()
        if node.id not in self._reverse_adjacency:
            self._reverse_adjacency[node.id] = set()

    def add_edge(self, edge: GraphEdge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            # Nodes must exist before edges
            return False
            
        self.edges[edge.id] = edge
        self._adjacency_list[edge.source].add(edge.id)
        self._reverse_adjacency[edge.target].add(edge.id)
        return True
        
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)
        
    def get_edges_from(self, node_id: str) -> List[GraphEdge]:
        edge_ids = self._adjacency_list.get(node_id, set())
        return [self.edges[e_id] for e_id in edge_ids]
        
    def get_edges_to(self, node_id: str) -> List[GraphEdge]:
        edge_ids = self._reverse_adjacency.get(node_id, set())
        return [self.edges[e_id] for e_id in edge_ids]
        
    def query_relationships(self, source_id: str, relationship: str) -> List[GraphNode]:

        out_edges = self.get_edges_from(source_id)
        target_ids = [e.target for e in out_edges if e.relationship == relationship]
        return [self.nodes[t_id] for t_id in target_ids if t_id in self.nodes]

# Singleton instance
global_graph = GraphDatabase()

def get_graph_database() -> GraphDatabase:
    return global_graph
