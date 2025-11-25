from typing import Dict, Any, List, Set, Optional
from datetime import datetime
import json
from pathlib import Path

class GraphNode:
    def __init__(self, id: str, type: str, data: Dict[str, Any]):
        self.id = id
        self.type = type
        self.data = data
        self.edges: Set[str] = set()
        self.created_at = datetime.now()

class GraphStore:
    def __init__(self, storage_path: str = ".cache/graph"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_node(self, id: str, type: str, data: Dict[str, Any]) -> GraphNode:
        node = GraphNode(id, type, data)
        self.nodes[id] = node
        return node
    
    def add_edge(self, from_id: str, to_id: str, relation: str, metadata: Dict[str, Any] = None):
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError("Both nodes must exist")
        
        self.nodes[from_id].edges.add(to_id)
        
        if from_id not in self.edges:
            self.edges[from_id] = []
        
        self.edges[from_id].append({
            "to": to_id,
            "relation": relation,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def get_node(self, id: str) -> Optional[GraphNode]:
        return self.nodes.get(id)
    
    def get_neighbors(self, id: str) -> List[GraphNode]:
        if id not in self.nodes:
            return []
        
        neighbor_ids = self.nodes[id].edges
        return [self.nodes[nid] for nid in neighbor_ids if nid in self.nodes]
    
    def query(self, node_type: str = None, filters: Dict[str, Any] = None) -> List[GraphNode]:
        results = []
        for node in self.nodes.values():
            if node_type and node.type != node_type:
                continue
            
            if filters:
                match = all(
                    node.data.get(k) == v 
                    for k, v in filters.items()
                )
                if not match:
                    continue
            
            results.append(node)
        
        return results
    
    def traverse(self, start_id: str, max_depth: int = 3) -> List[GraphNode]:
        if start_id not in self.nodes:
            return []
        
        visited = set()
        queue = [(start_id, 0)]
        result = []
        
        while queue:
            node_id, depth = queue.pop(0)
            
            if node_id in visited or depth > max_depth:
                continue
            
            visited.add(node_id)
            result.append(self.nodes[node_id])
            
            for neighbor_id in self.nodes[node_id].edges:
                if neighbor_id not in visited:
                    queue.append((neighbor_id, depth + 1))
        
        return result
    
    def save(self):
        data = {
            "nodes": {
                id: {
                    "type": node.type,
                    "data": node.data,
                    "edges": list(node.edges),
                    "created_at": node.created_at.isoformat()
                }
                for id, node in self.nodes.items()
            },
            "edges": self.edges
        }
        with open(self.storage_path / "graph.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        path = self.storage_path / "graph.json"
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
            
            for id, node_data in data["nodes"].items():
                node = GraphNode(id, node_data["type"], node_data["data"])
                node.edges = set(node_data["edges"])
                self.nodes[id] = node
            
            self.edges = data["edges"]
