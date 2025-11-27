from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, AppError):
        logger.error(f"AppError: {exc.message} - {exc.details}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "details": exc.details
            }
        )
    
    if isinstance(exc, HTTPException):
        logger.warning(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail
            }
        )
        
    logger.exception(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal Server Error",
            "details": str(exc) if "development" in str(request.url) else "An unexpected error occurred."
        }
    )
