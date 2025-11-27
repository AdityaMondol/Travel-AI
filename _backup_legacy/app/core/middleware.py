"""Middleware for request validation, error handling, and monitoring"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import uuid
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests"""
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling"""
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled error in {request.url.path}: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": getattr(request.state, "request_id", None),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting"""
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_times = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        if client_ip not in self.request_times:
            self.request_times[client_ip] = []
        
        # Clean old requests (older than 1 minute)
        self.request_times[client_ip] = [
            t for t in self.request_times[client_ip] 
            if current_time - t < 60
        ]
        
        if len(self.request_times[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": 60
                }
            )
        
        self.request_times[client_ip].append(current_time)
        response = await call_next(request)
        return response

class ValidationMiddleware(BaseHTTPMiddleware):
    """Validate request content"""
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            if request.headers.get("content-type") == "application/json":
                try:
                    await request.json()
                except Exception as e:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Invalid JSON",
                            "detail": str(e)
                        }
                    )
        
        response = await call_next(request)
        return response
