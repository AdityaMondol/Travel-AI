"""Safety & governance layer with content filtering and policy enforcement"""
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from app.core.logger import setup_logger
from app.core.audit import get_audit_log, AuditEventType


logger = setup_logger(__name__)


class RiskLevel(str, Enum):
    """Risk classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyViolation(Exception):
    """Raised when policy is violated"""
    pass


class ContentFilter:
    """Content filtering with configurable rules"""
    
    # Disallowed categories
    DISALLOWED_PATTERNS = {
        "malware": [
            r"(?i)(ransomware|trojan|worm|virus|backdoor|rootkit)",
            r"(?i)(exploit|shellcode|payload|injection)",
        ],
        "illegal": [
            r"(?i)(drug|cocaine|heroin|fentanyl|meth)",
            r"(?i)(bomb|explosive|weapon|firearm)",
        ],
        "privacy": [
            r"(?i)(ssn|social.?security|credit.?card|cvv)",
            r"(?i)(password|api.?key|secret|token)",
        ],
        "abuse": [
            r"(?i)(harassment|hate|discrimination|abuse)",
        ],
    }
    
    def __init__(self, enable: bool = True):
        self.enable = enable
    
    def check_content(self, content: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check content for violations.
        Returns: (is_safe, violation_category, violation_detail)
        """
        if not self.enable:
            return True, None, None
        
        for category, patterns in self.DISALLOWED_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    return False, category, pattern
        
        return True, None, None
    
    def sanitize(self, content: str) -> str:
        """Remove sensitive patterns"""
        sanitized = content
        
        # Mask potential credentials
        sanitized = re.sub(r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*\S+", 
                          r"\1=[REDACTED]", sanitized)
        
        # Mask potential SSN
        sanitized = re.sub(r"\d{3}-\d{2}-\d{4}", "[SSN]", sanitized)
        
        # Mask potential credit cards
        sanitized = re.sub(r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}", 
                          "[CARD]", sanitized)
        
        return sanitized


class PolicyEngine:
    """Policy enforcement engine"""
    
    def __init__(self):
        self.policies: Dict[str, Dict] = {
            "max_execution_time": 300,  # seconds
            "max_memory_usage": 512,  # MB
            "max_api_calls_per_minute": 60,
            "disallowed_tools": ["system_shutdown", "format_disk"],
            "require_approval_for": ["data_deletion", "external_api_calls"],
            "data_retention_days": 90,
        }
        self.audit_log = get_audit_log()
    
    async def check_action(
        self,
        actor: str,
        action: str,
        resource: str,
        context: Dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if action is allowed by policy.
        Returns: (allowed, reason_if_denied)
        """
        
        # Check disallowed tools
        if action in self.policies["disallowed_tools"]:
            reason = f"Action '{action}' is disallowed by policy"
            await self.audit_log.log_event(
                AuditEventType.POLICY_VIOLATION,
                actor,
                resource,
                action,
                {"reason": reason},
                result="denied"
            )
            return False, reason
        
        # Check if approval required
        if action in self.policies["require_approval_for"]:
            reason = f"Action '{action}' requires human approval"
            await self.audit_log.log_event(
                AuditEventType.POLICY_VIOLATION,
                actor,
                resource,
                action,
                {"reason": reason, "requires_approval": True},
                result="pending_approval"
            )
            return False, reason
        
        return True, None
    
    def set_policy(self, policy_name: str, value):
        """Update policy"""
        self.policies[policy_name] = value
        logger.info(f"Policy updated: {policy_name} = {value}")
    
    def get_policy(self, policy_name: str):
        """Get policy value"""
        return self.policies.get(policy_name)


class RiskAssessment:
    """Risk assessment for agent actions"""
    
    @staticmethod
    def assess_action(
        action: str,
        resource: str,
        context: Dict
    ) -> Tuple[RiskLevel, str]:
        """Assess risk level of an action"""
        
        # High-risk actions
        if action in ["delete_data", "modify_config", "execute_code", "external_api"]:
            return RiskLevel.HIGH, "Potentially destructive or external action"
        
        # Medium-risk actions
        if action in ["read_sensitive_data", "create_resource", "modify_resource"]:
            return RiskLevel.MEDIUM, "Requires audit trail"
        
        # Low-risk actions
        return RiskLevel.LOW, "Standard operation"
    
    @staticmethod
    def requires_human_approval(risk_level: RiskLevel) -> bool:
        """Check if action requires human approval"""
        return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]


class SafetyManager:
    """Unified safety management"""
    
    def __init__(self, enable_content_filter: bool = True, enable_approval: bool = False):
        self.content_filter = ContentFilter(enable=enable_content_filter)
        self.policy_engine = PolicyEngine()
        self.enable_approval = enable_approval
        self.audit_log = get_audit_log()
    
    async def validate_request(
        self,
        actor: str,
        action: str,
        resource: str,
        content: str,
        context: Dict = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate request against all safety checks"""
        context = context or {}
        
        # Content filtering
        is_safe, category, detail = self.content_filter.check_content(content)
        if not is_safe:
            await self.audit_log.log_event(
                AuditEventType.SECURITY_EVENT,
                actor,
                resource,
                action,
                {"violation": category, "pattern": detail},
                result="blocked"
            )
            return False, f"Content violation: {category}"
        
        # Policy check
        allowed, reason = await self.policy_engine.check_action(
            actor, action, resource, context
        )
        if not allowed:
            return False, reason
        
        # Risk assessment
        risk_level, risk_reason = RiskAssessment.assess_action(action, resource, context)
        
        if self.enable_approval and RiskAssessment.requires_human_approval(risk_level):
            await self.audit_log.log_event(
                AuditEventType.HUMAN_APPROVAL,
                actor,
                resource,
                action,
                {"risk_level": risk_level.value, "reason": risk_reason},
                result="pending"
            )
            return False, f"Requires human approval (risk: {risk_level.value})"
        
        return True, None
    
    def sanitize_output(self, content: str) -> str:
        """Sanitize output before returning to user"""
        return self.content_filter.sanitize(content)


# Global safety manager
_safety_manager: Optional[SafetyManager] = None


def get_safety_manager() -> SafetyManager:
    """Get singleton safety manager"""
    global _safety_manager
    if _safety_manager is None:
        from app.core.config import get_config
        config = get_config()
        _safety_manager = SafetyManager(
            enable_content_filter=config.enable_content_filter,
            enable_approval=config.enable_human_approval
        )
    return _safety_manager
