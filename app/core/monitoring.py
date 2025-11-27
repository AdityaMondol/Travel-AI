"""Prometheus monitoring and observability"""
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from typing import Dict, Any
import time
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class MetricsCollector:
    """Prometheus metrics collection"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Request metrics
        self.request_count = Counter(
            "leonore_requests_total",
            "Total requests",
            ["method", "endpoint", "status"],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            "leonore_request_duration_seconds",
            "Request duration",
            ["method", "endpoint"],
            registry=self.registry
        )
        
        # Agent metrics
        self.agent_count = Gauge(
            "leonore_agents_active",
            "Active agents",
            registry=self.registry
        )
        
        self.agent_actions = Counter(
            "leonore_agent_actions_total",
            "Agent actions",
            ["agent_type", "action"],
            registry=self.registry
        )
        
        # LLM metrics
        self.llm_tokens = Counter(
            "leonore_llm_tokens_total",
            "LLM tokens used",
            ["model"],
            registry=self.registry
        )
        
        self.llm_cost = Gauge(
            "leonore_llm_cost_usd",
            "LLM cost in USD",
            registry=self.registry
        )
        
        # Error metrics
        self.errors = Counter(
            "leonore_errors_total",
            "Total errors",
            ["error_type"],
            registry=self.registry
        )
        
        # Safety metrics
        self.policy_violations = Counter(
            "leonore_policy_violations_total",
            "Policy violations",
            ["violation_type"],
            registry=self.registry
        )
        
        # Resource metrics
        self.memory_usage = Gauge(
            "leonore_memory_usage_bytes",
            "Memory usage",
            registry=self.registry
        )
        
        self.gpu_memory = Gauge(
            "leonore_gpu_memory_bytes",
            "GPU memory usage",
            registry=self.registry
        )
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request"""
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_agent_action(self, agent_type: str, action: str):
        """Record agent action"""
        self.agent_actions.labels(agent_type=agent_type, action=action).inc()
    
    def record_llm_usage(self, model: str, tokens: int, cost: float):
        """Record LLM usage"""
        self.llm_tokens.labels(model=model).inc(tokens)
        self.llm_cost.set(cost)
    
    def record_error(self, error_type: str):
        """Record error"""
        self.errors.labels(error_type=error_type).inc()
    
    def record_policy_violation(self, violation_type: str):
        """Record policy violation"""
        self.policy_violations.labels(violation_type=violation_type).inc()
    
    def set_active_agents(self, count: int):
        """Set active agent count"""
        self.agent_count.set(count)
    
    def set_memory_usage(self, bytes: int):
        """Set memory usage"""
        self.memory_usage.set(bytes)
    
    def set_gpu_memory(self, bytes: int):
        """Set GPU memory usage"""
        self.gpu_memory.set(bytes)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        import psutil
        
        process = psutil.Process()
        
        return {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(interval=0.1),
            "num_threads": process.num_threads(),
            "open_files": len(process.open_files()),
        }
    
    def get_endpoint_stats(self, endpoint: str, minutes: int = 5) -> Dict[str, Any]:
        """Get endpoint statistics"""
        # This would integrate with Prometheus query API
        return {
            "endpoint": endpoint,
            "period_minutes": minutes,
            "requests": 0,
            "avg_duration_ms": 0,
            "error_rate": 0.0,
        }


# Global metrics instance
_metrics: MetricsCollector = None


def get_metrics() -> MetricsCollector:
    """Get metrics collector"""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics


class MetricsMiddleware:
    """FastAPI middleware for metrics collection"""
    
    def __init__(self, app):
        self.app = app
        self.metrics = get_metrics()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                duration = time.time() - start_time
                
                method = scope["method"]
                path = scope["path"]
                
                self.metrics.record_request(method, path, status, duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
