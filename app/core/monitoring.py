"""Monitoring and metrics collection"""
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class MetricsCollector:
    """Collect and track system metrics"""
    
    def __init__(self):
        self.request_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.agent_metrics = {}
        self.start_time = datetime.now()
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record API request metrics"""
        self.request_times[endpoint].append({
            "duration": duration,
            "status": status_code,
            "timestamp": datetime.now().isoformat()
        })
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1
    
    def record_agent_metric(self, agent_id: str, metric_name: str, value: Any):
        """Record agent-specific metrics"""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = {}
        
        self.agent_metrics[agent_id][metric_name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_endpoint_stats(self, endpoint: str, minutes: int = 5) -> Dict[str, Any]:
        """Get statistics for an endpoint"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        requests = [
            r for r in self.request_times.get(endpoint, [])
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]
        
        if not requests:
            return {
                "endpoint": endpoint,
                "requests": 0,
                "avg_duration": 0,
                "error_rate": 0
            }
        
        durations = [r["duration"] for r in requests]
        errors = sum(1 for r in requests if r["status"] >= 400)
        
        return {
            "endpoint": endpoint,
            "requests": len(requests),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "error_rate": errors / len(requests),
            "errors": errors
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        uptime = datetime.now() - self.start_time
        
        total_requests = sum(len(v) for v in self.request_times.values())
        total_errors = sum(self.error_counts.values())
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 0,
            "endpoints": len(self.request_times),
            "agents": len(self.agent_metrics),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a specific agent"""
        return self.agent_metrics.get(agent_id, {})
    
    def cleanup_old_data(self, hours: int = 24):
        """Remove metrics older than specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for endpoint in self.request_times:
            self.request_times[endpoint] = [
                r for r in self.request_times[endpoint]
                if datetime.fromisoformat(r["timestamp"]) > cutoff
            ]

# Global metrics collector
metrics = MetricsCollector()

def get_metrics() -> MetricsCollector:
    """Get global metrics collector"""
    return metrics
