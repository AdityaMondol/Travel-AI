"""Unified memory system with vector and graph stores"""
from typing import Dict, List, Any, Optional
from app.core.vector_store import get_vector_store
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class MemorySystem:
    """Unified memory with semantic and relational storage"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.graph_data: Dict[str, List[Dict[str, Any]]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    async def store_memory(
        self,
        content: str,
        memory_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store memory in vector store"""
        meta = metadata or {}
        meta["type"] = memory_type
        
        try:
            ids = await self.vector_store.add([content], [meta])
            memory_id = ids[0] if ids else None
            
            if memory_id:
                self.metadata[memory_id] = meta
                logger.info(f"Memory stored: {memory_id}")
            
            return memory_id
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return None
    
    async def retrieve_memory(
        self,
        query: str,
        k: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories"""
        try:
            results = await self.vector_store.search(query, k=k)
            
            if memory_type:
                results = [
                    r for r in results
                    if r.get("metadata", {}).get("type") == memory_type
                ]
            
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {e}")
            return []
    
    def add_relation(self, from_id: str, to_id: str, relation_type: str):
        """Add relationship between memories"""
        if from_id not in self.graph_data:
            self.graph_data[from_id] = []
        
        self.graph_data[from_id].append({
            "to": to_id,
            "type": relation_type,
        })
    
    def get_relations(self, memory_id: str) -> List[Dict[str, Any]]:
        """Get relations for memory"""
        return self.graph_data.get(memory_id, [])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_memories": len(self.metadata),
            "total_relations": sum(len(v) for v in self.graph_data.values()),
            "memory_types": list(set(
                m.get("type", "unknown") for m in self.metadata.values()
            )),
        }


# Global memory instance
_memory_system: Optional[MemorySystem] = None


def get_memory_system() -> MemorySystem:
    """Get memory system"""
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system
