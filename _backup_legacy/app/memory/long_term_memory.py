from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.memory.vector_store import VectorStore
from app.memory.graph_store import GraphStore
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class LongTermMemory:
    def __init__(self):
        self.vector_store = VectorStore()
        self.graph_store = GraphStore()
        self.episodic_memory: List[Dict[str, Any]] = []
        self.semantic_memory: Dict[str, Any] = {}
        self.procedural_memory: Dict[str, Any] = {}
    
    def store_episode(self, event: Dict[str, Any]):
        self.episodic_memory.append({
            "timestamp": datetime.now().isoformat(),
            "event": event
        })
        
        text = f"{event.get('type', 'event')}: {event.get('description', '')}"
        self.vector_store.add(text, metadata=event)
        
        if len(self.episodic_memory) > 1000:
            self.episodic_memory = self.episodic_memory[-1000:]
    
    def store_knowledge(self, key: str, value: Any, category: str = "general"):
        if category not in self.semantic_memory:
            self.semantic_memory[category] = {}
        
        self.semantic_memory[category][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.graph_store.add_node(key, category, {"value": value})
    
    def store_procedure(self, name: str, steps: List[str], metadata: Dict[str, Any] = None):
        self.procedural_memory[name] = {
            "steps": steps,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "usage_count": 0
        }
    
    def recall_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.vector_store.search(query, top_k)
    
    def recall_knowledge(self, key: str, category: str = None) -> Optional[Any]:
        if category:
            return self.semantic_memory.get(category, {}).get(key)
        
        for cat_data in self.semantic_memory.values():
            if key in cat_data:
                return cat_data[key]
        return None
    
    def recall_procedure(self, name: str) -> Optional[Dict[str, Any]]:
        proc = self.procedural_memory.get(name)
        if proc:
            proc["usage_count"] += 1
        return proc
    
    def get_recent_episodes(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            ep for ep in self.episodic_memory
            if datetime.fromisoformat(ep["timestamp"]) > cutoff
        ]
    
    def consolidate(self):
        logger.info("Consolidating long-term memory")
        self.vector_store.save()
        self.graph_store.save()
    
    def load(self):
        self.vector_store.load()
        self.graph_store.load()
