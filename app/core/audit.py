"""Tamper-proof audit logging system"""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
import asyncio
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class AuditEventType(str, Enum):
    """Audit event types"""
    AGENT_SPAWN = "agent_spawn"
    AGENT_ACTION = "agent_action"
    TOOL_EXECUTION = "tool_execution"
    DATA_ACCESS = "data_access"
    POLICY_VIOLATION = "policy_violation"
    HUMAN_APPROVAL = "human_approval"
    COST_THRESHOLD = "cost_threshold"
    SECURITY_EVENT = "security_event"
    MODEL_SWAP = "model_swap"
    CONFIG_CHANGE = "config_change"


class AuditLog:
    """Tamper-proof audit log with chain-of-custody"""
    
    def __init__(self):
        self.logs: list[Dict[str, Any]] = []
        self.chain_hash = "genesis"
    
    def _compute_hash(self, entry: Dict[str, Any]) -> str:
        """Compute SHA256 hash of entry"""
        entry_str = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(entry_str.encode()).hexdigest()
    
    async def log_event(
        self,
        event_type: AuditEventType,
        actor: str,
        resource: str,
        action: str,
        details: Dict[str, Any],
        result: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an audit event with chain-of-custody"""
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "actor": actor,
            "resource": resource,
            "action": action,
            "details": details,
            "result": result,
            "metadata": metadata or {},
            "previous_hash": self.chain_hash,
        }
        
        entry_hash = self._compute_hash(entry)
        entry["hash"] = entry_hash
        
        self.logs.append(entry)
        self.chain_hash = entry_hash
        
        logger.info(
            f"Audit: {event_type.value} by {actor} on {resource}",
            extra={"audit_hash": entry_hash, "result": result}
        )
        
        return entry_hash
    
    def verify_chain(self) -> bool:
        """Verify audit log chain integrity"""
        current_hash = "genesis"
        
        for entry in self.logs:
            if entry["previous_hash"] != current_hash:
                logger.error(f"Chain integrity violation at {entry['timestamp']}")
                return False
            
            stored_hash = entry.pop("hash")
            computed_hash = self._compute_hash(entry)
            entry["hash"] = stored_hash
            
            if stored_hash != computed_hash:
                logger.error(f"Entry hash mismatch at {entry['timestamp']}")
                return False
            
            current_hash = stored_hash
        
        return True
    
    def get_events(
        self,
        event_type: Optional[AuditEventType] = None,
        actor: Optional[str] = None,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """Query audit logs"""
        results = self.logs
        
        if event_type:
            results = [e for e in results if e["event_type"] == event_type.value]
        
        if actor:
            results = [e for e in results if e["actor"] == actor]
        
        return results[-limit:]
    
    def export_chain(self) -> Dict[str, Any]:
        """Export complete audit chain"""
        return {
            "chain_valid": self.verify_chain(),
            "total_entries": len(self.logs),
            "current_hash": self.chain_hash,
            "entries": self.logs
        }


# Global audit log instance
_audit_log: Optional[AuditLog] = None


def get_audit_log() -> AuditLog:
    """Get singleton audit log"""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log
