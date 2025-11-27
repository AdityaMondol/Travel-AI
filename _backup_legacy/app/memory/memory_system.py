"""Memory system with vector and graph stores"""
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.logger import setup_logger
from app.core.database import SessionLocal, Memory

logger = setup_logger(__name__)

class MemorySystem:
    def __init__(self):
        self.db = SessionLocal()
        self.embeddings_cache = {}
    
    def store_memory(self, agent_id: Optional[str], session_id: Optional[str], 
                    memory_type: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """Store a memory entry"""
        try:
            memory_id = str(uuid.uuid4())
            memory = Memory(
                id=memory_id,
                agent_id=agent_id,
                session_id=session_id,
                type=memory_type,
                content=content,
                metadata=metadata or {}
            )
            self.db.add(memory)
            self.db.commit()
            logger.info(f"Stored memory {memory_id} of type {memory_type}")
            return memory_id
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            self.db.rollback()
            return None
    
    def recall_recent(self, session_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Recall recent memories"""
        try:
            query = self.db.query(Memory)
            if session_id:
                query = query.filter(Memory.session_id == session_id)
            
            memories = query.order_by(Memory.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": m.id,
                    "type": m.type,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                    "metadata": m.metadata
                }
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error recalling memories: {e}")
            return []
    
    def recall_by_type(self, memory_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recall memories by type"""
        try:
            memories = self.db.query(Memory).filter(
                Memory.type == memory_type
            ).order_by(Memory.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": m.id,
                    "type": m.type,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                    "metadata": m.metadata
                }
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error recalling memories by type: {e}")
            return []
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by content"""
        try:
            memories = self.db.query(Memory).filter(
                Memory.content.ilike(f"%{query}%")
            ).order_by(Memory.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": m.id,
                    "type": m.type,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                    "metadata": m.metadata
                }
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def get_agent_memory(self, agent_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all memories for an agent"""
        try:
            memories = self.db.query(Memory).filter(
                Memory.agent_id == agent_id
            ).order_by(Memory.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": m.id,
                    "type": m.type,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                    "metadata": m.metadata
                }
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error getting agent memory: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry"""
        try:
            self.db.query(Memory).filter(Memory.id == memory_id).delete()
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            self.db.rollback()
            return False
    
    def clear_session_memory(self, session_id: str) -> bool:
        """Clear all memories for a session"""
        try:
            self.db.query(Memory).filter(Memory.session_id == session_id).delete()
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error clearing session memory: {e}")
            self.db.rollback()
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            total = self.db.query(Memory).count()
            by_type = {}
            for memory_type in ["thought", "tool_use", "reflection", "conversation"]:
                count = self.db.query(Memory).filter(Memory.type == memory_type).count()
                if count > 0:
                    by_type[memory_type] = count
            
            return {
                "total_memories": total,
                "by_type": by_type
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"total_memories": 0, "by_type": {}}
