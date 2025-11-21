import secrets
import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login(request: Request):
    """
    Initiate Google OAuth login flow
    Returns the authorization URL for the client to redirect to
    """
    if not settings.GOOGLE_CLIENT_ID:
        return JSONResponse(
            status_code=501,
            content={
                "status": "error",
                "message": "Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
            }
        )
    
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Build authorization URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"state={state}"
    )
    
    return JSONResponse(content={
        "status": "success",
        "auth_url": auth_url,
        "message": "Redirect to auth_url to complete login"
    })

@router.get("/callback")
async def callback(request: Request):
    """Handle OAuth callback"""
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    
    if error:
        logger.warning(f"OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"Authorization failed: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    
    # Placeholder - implement token exchange in production
    logger.info("OAuth callback received")
    return RedirectResponse(url="/")

@router.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/")
    response.delete_cookie("user_email")
    response.delete_cookie("user_name")
    response.delete_cookie("user_picture")
    logger.info("User logged out")
    return response

@router.get("/user")
async def get_user(request: Request):
    """Get current user info from cookies"""
    user = {
        "email": request.cookies.get("user_email"),
        "name": request.cookies.get("user_name"),
        "picture": request.cookies.get("user_picture"),
        "authenticated": bool(request.cookies.get("user_email"))
    }
    return JSONResponse(content=user)
