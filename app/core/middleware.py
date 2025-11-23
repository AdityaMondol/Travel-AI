import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import setup_logger
from app.core.config import Config

logger = setup_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        self.requests = {
            ip: [t for t in reqs if current_time - t < self.window_seconds]
            for ip, reqs in self.requests.items()
        }
        
        self.requests = {ip: reqs for ip, reqs in self.requests.items() if reqs}
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip].append(current_time)
        
        if len(self.requests[client_ip]) > self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return Response(
                content='{"status": "error", "message": "Rate limit exceeded"}', 
                status_code=429, 
                media_type="application/json"
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - len(self.requests[client_ip]))
        return response

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request: {request.method} {request.url.path} - Time: {process_time:.4f}s")
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > self.max_size:
                return Response(
                    content='{"status": "error", "message": "Request too large"}',
                    status_code=413,
                    media_type="application/json"
                )
        return await call_next(request)

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
