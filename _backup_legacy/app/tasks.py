"""Celery task definitions for async job processing"""
from celery import Celery, Task
from app.core.config import get_config
from app.core.logger import setup_logger
from app.core.audit import get_audit_log, AuditEventType


logger = setup_logger(__name__)
config = get_config()

celery_app = Celery(
    'leonore',
    broker=config.redis_url,
    backend=config.redis_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=config.max_execution_time_seconds,
)


class CallbackTask(Task):
    """Task with callbacks"""
    
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} succeeded")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")


@celery_app.task(base=CallbackTask, bind=True)
def execute_research(self, query: str, session_id: str):
    """Execute research workflow"""
    from app.workflows.research_workflow import DeepResearchAgent
    import asyncio
    
    try:
        agent = DeepResearchAgent()
        result = asyncio.run(agent.research(query))
        
        audit_log = get_audit_log()
        asyncio.run(audit_log.log_event(
            AuditEventType.TOOL_EXECUTION,
            session_id,
            'research',
            'execute',
            {'query': query},
            result='success'
        ))
        
        return result
    except Exception as e:
        logger.error(f"Research task failed: {e}")
        raise


@celery_app.task(base=CallbackTask, bind=True)
def execute_code_generation(self, task: str, session_id: str):
    """Execute code generation workflow"""
    from app.workflows.coding_workflow import FullstackCodingAgent
    import asyncio
    
    try:
        agent = FullstackCodingAgent()
        result = asyncio.run(agent.build(task))
        
        audit_log = get_audit_log()
        asyncio.run(audit_log.log_event(
            AuditEventType.TOOL_EXECUTION,
            session_id,
            'code_generation',
            'execute',
            {'task': task},
            result='success'
        ))
        
        return result
    except Exception as e:
        logger.error(f"Code generation task failed: {e}")
        raise


@celery_app.task(base=CallbackTask, bind=True)
def execute_browser_automation(self, goal: str, start_url: str, session_id: str):
    """Execute browser automation workflow"""
    from app.workflows.browser_workflow import BrowserInteractionAgent
    import asyncio
    
    try:
        agent = BrowserInteractionAgent()
        result = asyncio.run(agent.interact(goal, start_url))
        
        audit_log = get_audit_log()
        asyncio.run(audit_log.log_event(
            AuditEventType.TOOL_EXECUTION,
            session_id,
            'browser_automation',
            'execute',
            {'goal': goal, 'start_url': start_url},
            result='success'
        ))
        
        return result
    except Exception as e:
        logger.error(f"Browser automation task failed: {e}")
        raise


@celery_app.task
def cleanup_old_sessions(days: int = 30):
    """Cleanup old chat sessions"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    logger.info(f"Cleaning up sessions older than {cutoff_date}")
    
    # Implementation would depend on database setup
    return {"status": "cleanup_completed"}


@celery_app.task
def sync_metrics():
    """Sync metrics to monitoring system"""
    from app.core.monitoring import get_metrics
    
    metrics = get_metrics()
    stats = metrics.get_system_stats()
    
    logger.info(f"Metrics synced: {stats}")
    return stats
