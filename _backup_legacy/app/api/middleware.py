"""API middleware for auth, rate limiting, and monitoring"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from app.core.auth import get_auth_manager
from app.core.rate_limit import get_rate_limiter
from app.core.monitoring import get_metrics
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        public_paths = ['/api/health', '/api/test', '/']
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Extract token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid authorization"}
            )
        
        token = auth_header[7:]
        auth = get_auth_manager()
        user_id = auth.verify_token(token)
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token"}
            )
        
        request.state.user_id = user_id
        request.state.user = auth.get_user(user_id)
        
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        if not hasattr(request.state, 'user_id'):
            return await call_next(request)
        
        user_id = request.state.user_id
        rate_limiter = get_rate_limiter()
        
        allowed, info = rate_limiter.is_allowed(user_id)
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "details": info
                }
            )
        
        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Metrics collection middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        metrics = get_metrics()
        
        metrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            metrics = get_metrics()
            metrics.record_error(type(e).__name__)
            
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
