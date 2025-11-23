"""
REST API Server for Cerebras AI Agent Army
Production-ready FastAPI implementation
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from app.core.logger import setup_logger
from app.core.config import Config
from app.core.llm_client import LLMClient
from app.core.file_manager import FileManager
from app.services.orchestrator import create_travel_plan
from app.services.html_generator import PremiumHTMLGenerator as HTMLGenerator
from app.core.telemetry import TelemetryCollector, AnalyticsEngine

logger = setup_logger(__name__)

class APIServer:
    def __init__(self):
        try:
            self.llm_client = LLMClient()
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.llm_client = None
        self.telemetry = TelemetryCollector()
        self.analytics = AnalyticsEngine()
    
    def generate_travel_guide(self, destination: str, language: str = "en") -> Dict[str, Any]:
        """Generate travel guide for destination"""
        try:
            logger.info(f"API: Generating guide for {destination}")
            
            self.telemetry.record_event("api_request", {
                "destination": destination,
                "language": language
            })
            
            travel_data = create_travel_plan(destination, language, self.llm_client)
            
            self.analytics.track_destination(destination)
            self.analytics.track_language(language)
            
            return {
                "status": "success",
                "destination": destination,
                "data": travel_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"API error: {e}")
            self.telemetry.record_error("api_error", str(e))
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_html_guide(self, destination: str, language: str = "en") -> Dict[str, Any]:
        """Get HTML version of travel guide"""
        try:
            travel_data = create_travel_plan(destination, language, self.llm_client)
            html = HTMLGenerator.generate(travel_data)
            
            return {
                "status": "success",
                "html": html,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"HTML generation error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get system analytics"""
        return {
            "status": "success",
            "analytics": self.analytics.get_analytics_summary(),
            "telemetry": self.telemetry.get_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages"""
        return {
            "status": "success",
            "languages": Config.SUPPORTED_LANGUAGES,
            "count": len(Config.SUPPORTED_LANGUAGES)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "Cerebras AI Agent Army",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }

# FastAPI Integration (optional)
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    
    from app.core.exceptions import global_exception_handler
    from app.core.middleware import (
        RateLimitMiddleware,
        TimingMiddleware,
        SecurityHeadersMiddleware,
        RequestSizeLimitMiddleware,
        CorrelationIdMiddleware
    )
    from app.core.config import settings
    from app.core.auth import router as auth_router

    app = FastAPI(
        title="TravelAI - AI Agent Army API",
        description="Production-grade travel guide generation API powered by multi-agent AI",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Global exception handler
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Add middleware in order (last added is executed first)
    # CORS should be last to add headers to all responses
    allowed_origins = getattr(settings, 'ALLOWED_ORIGINS', '*')
    if isinstance(allowed_origins, str):
        if allowed_origins == '*':
            origins = ['*']
        else:
            origins = [origin.strip() for origin in allowed_origins.split(',')]
    else:
        origins = allowed_origins if allowed_origins else ['*']
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
    )
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Request size limit (10MB)
    app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)
    
    # Rate limiting
    app.add_middleware(
        RateLimitMiddleware, 
        max_requests=settings.RATE_LIMIT_REQUESTS, 
        window_seconds=settings.RATE_LIMIT_WINDOW
    )
    
    # Correlation ID for distributed tracing
    app.add_middleware(CorrelationIdMiddleware)
    
    # Timing middleware
    app.add_middleware(TimingMiddleware)
    
    # Include routers
    app.include_router(auth_router)
    
    # Serve static files from root directory
    app.mount("/css", StaticFiles(directory="static/css"), name="css")
    app.mount("/js", StaticFiles(directory="static/js"), name="js")
    
    # Serve individual root-level files
    from fastapi.responses import FileResponse
    
    @app.get("/favicon.ico")
    async def favicon():
        return FileResponse("static/favicon.svg", media_type="image/svg+xml")
    
    @app.get("/favicon.svg")
    async def favicon_svg():
        return FileResponse("static/favicon.svg", media_type="image/svg+xml")
    
    @app.get("/manifest.json")
    async def manifest():
        return FileResponse("static/manifest.json", media_type="application/json")
        
    @app.get("/icon-144x144.png")
    async def icon_144():
        # Serve SVG as fallback for now to prevent 404
        return FileResponse("static/favicon.svg", media_type="image/svg+xml")
    
    @app.get("/service-worker.js")
    async def service_worker():
        return FileResponse("static/service-worker.js", media_type="application/javascript")
    
    @app.get("/offline.html")
    async def offline():
        return FileResponse("static/offline.html", media_type="text/html")
        
    @app.get("/index.html")
    async def index_file():
        return FileResponse("static/index.html", media_type="text/html")

    @app.get("/robots.txt")
    async def robots():
        return FileResponse("static/robots.txt", media_type="text/plain")
    
    @app.get("/sitemap.xml")
    async def sitemap():
        return FileResponse("static/sitemap.xml", media_type="application/xml")
    
    from pydantic import BaseModel
    
    class GenerateRequest(BaseModel):
        destination: str
        language: str = "en"
    
    api_server = APIServer()
    
    @app.get("/")
    async def read_root():
        return HTMLResponse(content=open("static/index.html", "r").read())
    
    @app.get("/health")
    async def health():
        return api_server.health_check()
    
    @app.get("/api/languages")
    async def get_languages():
        return api_server.get_supported_languages()

    @app.get("/api/stream")
    async def stream_travel_plan(destination: str, mother_tongue: str = "en"):
        from app.services.orchestrator_langgraph import LangGraphOrchestrator
        
        async def event_generator():
            orchestrator = LangGraphOrchestrator()
            try:
                async for event in orchestrator.run_stream(destination, mother_tongue):
                    yield event
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    @app.post("/api/generate")
    async def generate_guide(request: GenerateRequest):
        from app.services.orchestrator_langgraph import create_travel_plan_langgraph
        try:
            result = await create_travel_plan_langgraph(request.destination, request.language)
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            return {
                "status": "success",
                "destination": request.destination,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Generate error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/guide/html")
    async def get_html(destination: str, language: str = "en"):
        result = api_server.get_html_guide(destination, language)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return HTMLResponse(content=result["html"])
    
    @app.get("/api/analytics")
    async def get_analytics():
        return api_server.get_analytics()
    
    @app.get("/api/recommendations")
    async def get_recommendations(
        destination: str,
        travel_style: str = "balanced",
        budget_level: str = "moderate"
    ):
        from app.services.recommendation_engine import RecommendationEngine
        try:
            recommendations = RecommendationEngine.get_recommendations(
                destination, travel_style, budget_level
            )
            return {
                "status": "success",
                "destination": destination,
                "recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"Recommendations error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/export")
    async def export_guide(request: GenerateRequest, format: str = "html"):
        from app.services.export_service import ExportService
        try:
            result = api_server.generate_travel_guide(request.destination, request.language)
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            
            if format == "json":
                export_result = ExportService.export_json(result["data"], request.destination)
                if export_result["status"] == "success":
                    return FileResponse(
                        export_result["filename"],
                        media_type="application/json",
                        filename=f"{request.destination}_guide.json"
                    )
            elif format == "markdown":
                export_result = ExportService.export_markdown(result["data"], request.destination)
                if export_result["status"] == "success":
                    return FileResponse(
                        export_result["filename"],
                        media_type="text/markdown",
                        filename=f"{request.destination}_guide.md"
                    )
            elif format == "html":
                export_result = ExportService.export_html(result["data"], request.destination)
                if export_result["status"] == "success":
                    return FileResponse(
                        export_result["filename"],
                        media_type="text/html",
                        filename=f"{request.destination}_guide.html"
                    )
            
            raise HTTPException(status_code=400, detail="Invalid export format")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Export error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/export/download")
    async def download_export(filename: str, format: str = "html"):
        try:
            filepath = f"output/{filename}"
            if not Path(filepath).exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            media_type = "text/html" if format == "html" else "application/json" if format == "json" else "text/markdown"
            return FileResponse(
                filepath,
                media_type=media_type,
                filename=f"{filename}.{format}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Download error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
                    "json": json_file,
                    "markdown": md_file,
                    "html": html_file
                }
            }
        except Exception as e:
            logger.error(f"Export error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/search")
    async def search_places(
        destination: str,
        query: str,
        limit: int = 10
    ):
        from app.services.search_service import SearchService
        try:
            result = api_server.generate_travel_guide(destination)
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            
            places = result.get("data", {}).get("places", {}).get("places", [])
            search_results = SearchService.search_places(places, query, limit)
            
            return {
                "status": "success",
                "query": query,
                "results": search_results,
                "count": len(search_results)
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/performance")
    async def get_performance_stats():
        from app.core.performance_monitor import PerformanceMonitor
        monitor = PerformanceMonitor()
        return {
            "status": "success",
            "performance": monitor.get_stats()
        }
    
    @app.post("/api/favorites/add")
    async def add_favorite(destination: str, item_id: str, item_type: str = "place"):
        from app.services.favorites_service import FavoritesService
        try:
            favorites = FavoritesService()
            result = favorites.add_favorite("user_1", item_id, item_type, {"destination": destination})
            return {
                "status": "success" if result else "already_favorited",
                "message": "Added to favorites" if result else "Already in favorites"
            }
        except Exception as e:
            logger.error(f"Favorites error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/itinerary/create")
    async def create_itinerary(request: GenerateRequest):
        from app.services.itinerary_builder import ItineraryBuilder
        try:
            itinerary = ItineraryBuilder.create_itinerary(
                request.destination,
                duration_days=3,
                travel_style="balanced"
            )
            return {
                "status": "success",
                "itinerary": itinerary
            }
        except Exception as e:
            logger.error(f"Itinerary creation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/notifications")
    async def get_notifications():
        from app.core.notification_service import NotificationService
        try:
            service = NotificationService()
            notifications = service.get_notifications()
            return {
                "status": "success",
                "notifications": notifications,
                "count": len(notifications)
            }
        except Exception as e:
            logger.error(f"Notifications error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

except ImportError:
    logger.warning("FastAPI not installed. API server not available.")
