"""
Leonore AI - Multi-Agent AI Assistant System
Production-ready FastAPI implementation with NVIDIA NIM
"""

import json
import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from app.core.logger import setup_logger
from app.core.config import Config
from app.agents.orchestrator import OrchestratorAgent
from app.core.streaming import StreamingManager

logger = setup_logger(__name__)

class LeonoreAI:
    def __init__(self):
        try:
            self.orchestrator = OrchestratorAgent()
            logger.info("Orchestrator initialized")
        except Exception as e:
            logger.error(f"Orchestrator init error: {e}")
            raise
        
        self.streaming = StreamingManager()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.memory_store: Dict[str, list] = {}
        logger.info("Leonore AI initialized")
    
    async def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process a message and return response"""
        try:
            # Initialize session memory if needed
            if session_id not in self.memory_store:
                self.memory_store[session_id] = []
            
            # Store user message
            self.memory_store[session_id].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Execute with orchestrator
            result = await self.orchestrator.execute(message, {})
            
            # Store assistant response
            self.memory_store[session_id].append({
                "role": "assistant",
                "content": json.dumps(result),
                "timestamp": datetime.now().isoformat()
            })
            
            return result
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
    
    async def stream_response(self, stream_id: str, session_id: str, message: str):
        """Stream response with real-time updates"""
        try:
            await self.streaming.send_event(stream_id, "start", {"session_id": session_id})
            
            if message.lower().startswith("research:"):
                query = message[9:].strip()
                await self.streaming.send_event(stream_id, "status", {"status": "Researching..."})
                result = await self.process_message(session_id, f"Research: {query}")
            elif message.lower().startswith("code:"):
                task = message[5:].strip()
                await self.streaming.send_event(stream_id, "status", {"status": "Generating code..."})
                result = await self.process_message(session_id, f"Code: {task}")
            elif message.lower().startswith("browse:"):
                goal = message[7:].strip()
                await self.streaming.send_event(stream_id, "status", {"status": "Browsing..."})
                result = await self.process_message(session_id, f"Browse: {goal}")
            else:
                result = await self.process_message(session_id, message)
            
            # Stream the response
            synthesis = result.get("synthesis", "")
            if synthesis:
                # Send in chunks
                for i in range(0, len(synthesis), 50):
                    chunk = synthesis[i:i+50]
                    await self.streaming.send_event(stream_id, "chunk", chunk)
                    await asyncio.sleep(0.01)
            else:
                # Send full result if no synthesis
                await self.streaming.send_event(stream_id, "chunk", str(result))
            
            await self.streaming.send_event(stream_id, "complete", result)
        except Exception as e:
            logger.error(f"Stream error: {e}")
            await self.streaming.send_event(stream_id, "error", {"error": str(e)})
        finally:
            await self.streaming.close_stream(stream_id)

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router

app = FastAPI(
    title="Leonore AI",
    description="Multi-Agent AI Assistant System powered by NVIDIA NIM",
    version="1.0.0",
    docs_url="/api/docs"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files
try:
    app.mount("/css", StaticFiles(directory="static/css"), name="css")
    app.mount("/js", StaticFiles(directory="static/js"), name="js")
except:
    pass

# Initialize Leonore
leonore = LeonoreAI()

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/favicon.svg")
async def favicon():
    return FileResponse("static/favicon.svg")

# Include API routes
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
