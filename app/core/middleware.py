import time
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
        
        # Clean up old requests for all IPs
        self.requests = {
            ip: [t for t in reqs if current_time - t < self.window_seconds]
            for ip, reqs in self.requests.items()
        }
        
        # Remove empty entries
        self.requests = {ip: reqs for ip, reqs in self.requests.items() if reqs}
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Check rate limit
        if len(self.requests[client_ip]) > self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}: {len(self.requests[client_ip])} requests")
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
    """
    Adds comprehensive security headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable built-in XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS - Force HTTPS (only in production with HTTPS)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Referrer Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy - Restrict browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Content Security Policy - Prevent XSS attacks
        # Note: This is a basic CSP, adjust based on your needs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.tailwindcss.com https://unpkg.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Limits the size of incoming requests to prevent DoS attacks.
    """
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header
        content_length = request.headers.get("Content-Length")
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                logger.warning(f"Request size {content_length} exceeds limit {self.max_size}")
                return Response(
                    content='{"status": "error", "message": "Request too large"}',
                    status_code=413,
                    media_type="application/json"
                )
        
        response = await call_next(request)
        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Adds a correlation ID to each request for distributed tracing.
    """
    async def dispatch(self, request: Request, call_next):
        import uuid
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Add to request state for use in logging
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response

