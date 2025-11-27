import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from app.core.logger import setup_logger
from app.core.config import Config

logger = setup_logger(__name__)

class TelemetryCollector:
    def __init__(self, telemetry_file: str = "telemetry.json"):
        self.telemetry_file = telemetry_file
        self.enabled = Config.ENABLE_TELEMETRY
        self.events: list = []
        self.session_start = datetime.now()
        self.error_count = 0
        self.request_count = 0
    
    def record_event(self, event_type: str, data: Dict[str, Any] = None) -> bool:
        if not self.enabled:
            return False
        try:
            event = {
                "type": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data or {}
            }
            self.events.append(event)
            return True
        except Exception as e:
            logger.error(f"Failed to record event: {e}")
            return False
    
    def record_request(self, model: str, tokens: int, latency: float) -> bool:
        if not self.enabled:
            return False
        self.request_count += 1
        return self.record_event("request", {
            "model": model,
            "tokens": tokens,
            "latency": latency
        })
    
    def record_error(self, error_type: str, message: str) -> bool:
        if not self.enabled:
            return False
        self.error_count += 1
        return self.record_event("error", {
            "error_type": error_type,
            "message": message
        })
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "session_start": self.session_start.isoformat(),
            "total_events": len(self.events),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "uptime_seconds": (datetime.now() - self.session_start).total_seconds()
        }
    
    def clear_telemetry(self) -> bool:
        self.events.clear()
        self.error_count = 0
        self.request_count = 0
        return True

class AnalyticsEngine:
    def __init__(self, analytics_file: str = "analytics.json"):
        self.analytics_file = analytics_file
        self.enabled = Config.ENABLE_ANALYTICS
        self.data: Dict[str, Any] = {
            "destinations": {},
            "languages": {},
            "total_requests": 0
        }
        self.load_analytics()
    
    def load_analytics(self) -> bool:
        if not Path(self.analytics_file).exists():
            return False
        try:
            with open(self.analytics_file, 'r') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Failed to load analytics: {e}")
            return False
    
    def save_analytics(self) -> bool:
        if not self.enabled:
            return False
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save analytics: {e}")
            return False
    
    def track_destination(self, destination: str) -> bool:
        if not self.enabled:
            return False
        try:
            if destination not in self.data["destinations"]:
                self.data["destinations"][destination] = 0
            self.data["destinations"][destination] += 1
            self.data["total_requests"] += 1
            self.save_analytics()
            return True
        except Exception as e:
            logger.error(f"Failed to track destination: {e}")
            return False
    
    def track_language(self, language: str) -> bool:
        if not self.enabled:
            return False
        try:
            if language not in self.data["languages"]:
                self.data["languages"][language] = 0
            self.data["languages"][language] += 1
            self.save_analytics()
            return True
        except Exception as e:
            logger.error(f"Failed to track language: {e}")
            return False
    
    def get_popular_destinations(self, limit: int = 10) -> list:
        sorted_dests = sorted(
            self.data["destinations"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [dest for dest, count in sorted_dests[:limit]]
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        return {
            "total_destinations": len(self.data["destinations"]),
            "total_languages": len(self.data["languages"]),
            "total_requests": self.data["total_requests"],
            "popular_destinations": self.get_popular_destinations(5),
            "languages_used": list(self.data["languages"].keys())
        }
