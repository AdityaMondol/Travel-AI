import time
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.start_time = datetime.now()
    
    def start_timer(self, operation: str) -> float:
        """Start timing an operation"""
        return time.time()
    
    def end_timer(self, operation: str, start_time: float) -> float:
        """End timing and record metric"""
        elapsed = time.time() - start_time
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(elapsed)
        logger.info(f"Operation '{operation}' took {elapsed:.3f}s")
        return elapsed
    
    def get_average(self, operation: str) -> Optional[float]:
        """Get average time for operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return None
        return sum(self.metrics[operation]) / len(self.metrics[operation])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        for op, times in self.metrics.items():
            if times:
                stats[op] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "total": sum(times)
                }
        return {
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "operations": stats
        }
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.start_time = datetime.now()
