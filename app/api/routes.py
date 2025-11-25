from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import asyncio
import uuid
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=10000)
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class OverdriveRequest(BaseModel):
    agent_id: Optional[str] = None
    authorization_code: Optional[str] = None

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Stream chat response with multi-agent processing"""
    try:
        from app.main import leonore
        
        async def generate():
            stream_id = str(uuid.uuid4())
            queue = await leonore.streaming.create_stream(stream_id)
            
            # Start processing in background
            task = asyncio.create_task(leonore.stream_response(stream_id, request.session_id, request.message))
            
            # Stream events
            try:
                async for event in leonore.streaming.stream_generator(stream_id):
                    yield event
            finally:
                await task
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.post("/upload")
async def upload_endpoint(file: UploadFile = File(...), session_id: str = ""):
    """Upload and process files"""
    try:
        import os
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        content = await file.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Save file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File uploaded: {file.filename} ({len(content)} bytes)")
        
        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def agents_status():
    """Get agent pool status"""
    try:
        from app.main import leonore
        return leonore.orchestrator.get_system_status()
    except Exception as e:
        logger.error(f"Agents status error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get agent status"}
        )

@router.get("/memory")
async def memory_query(query: str = Query("", max_length=1000), limit: int = Query(10, ge=1, le=100)):
    """Query memory system"""
    try:
        from app.main import leonore
        
        # Get session memories
        results = []
        for session_id, memories in list(leonore.memory_store.items())[:limit]:
            results.extend(memories[-5:])  # Last 5 from each session
        
        return {"results": results[:limit], "count": len(results[:limit])}
    except Exception as e:
        logger.error(f"Memory query error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to query memory"}
        )

@router.post("/overdrive")
async def activate_overdrive(request: OverdriveRequest):
    from app.core.overdrive_mode import overdrive_system
    
    if request.authorization_code:
        success = overdrive_system.genesis_protocol(request.authorization_code)
        if success:
            return {
                "status": "genesis_protocol_activated",
                "warning": "ALL RESTRICTIONS REMOVED"
            }
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")
    
    overdrive_system.activate_overdrive(request.agent_id)
    return {
        "status": "overdrive_activated",
        "agent_id": request.agent_id or "all"
    }

@router.post("/overdrive/deactivate")
async def deactivate_overdrive(agent_id: Optional[str] = None):
    from app.core.overdrive_mode import overdrive_system
    overdrive_system.deactivate_overdrive(agent_id)
    return {"status": "overdrive_deactivated"}

@router.get("/overdrive/status")
async def overdrive_status():
    from app.core.overdrive_mode import overdrive_system
    return overdrive_system.get_status()

@router.get("/hierarchy")
async def hierarchy_stats():
    from app.main import leonore
    return leonore.orchestrator.hierarchy.get_hierarchy_stats()

@router.post("/plan")
async def create_plan(goal: str):
    from app.main import leonore
    plan = await leonore.orchestrator.planner.create_multi_step_plan(goal)
    return plan

@router.post("/plan/{plan_id}/execute")
async def execute_plan(plan_id: str):
    from app.main import leonore
    result = await leonore.orchestrator.planner.execute_plan(plan_id)
    return result

@router.get("/tools")
async def list_tools():
    from app.main import leonore
    return leonore.orchestrator.tool_creator.get_tool_list()

@router.post("/tools/create")
async def create_tool(name: str, description: str):
    from app.main import leonore
    from app.core.llm_client import LLMClient
    
    llm = LLMClient(provider="nvidia")
    tool = await leonore.orchestrator.tool_creator.create_tool_from_description(
        name, description, llm
    )
    
    return {
        "status": "success",
        "tool_name": name,
        "description": description
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from app.main import leonore
        
        return {
            "status": "healthy",
            "service": "Leonore AI",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "agents_active": len(leonore.orchestrator.agent_pool),
            "memory_stats": {
                "total_memories": sum(len(m) for m in leonore.memory_store.values())
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.post("/research")
async def deep_research(query: str):
    from app.workflows.research_workflow import DeepResearchAgent
    
    agent = DeepResearchAgent()
    result = await agent.research(query)
    return result

@router.post("/code")
async def fullstack_code(task: str):
    from app.workflows.coding_workflow import FullstackCodingAgent
    
    agent = FullstackCodingAgent()
    result = await agent.build(task)
    return result

@router.post("/browse")
async def browser_interact(goal: str, start_url: str = None):
    from app.workflows.browser_workflow import BrowserInteractionAgent
    
    agent = BrowserInteractionAgent()
    result = await agent.interact(goal, start_url)
    return result


@router.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        from app.core.monitoring import get_metrics
        metrics = get_metrics()
        return metrics.get_system_stats()
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get metrics"}
        )

@router.get("/metrics/endpoint/{endpoint}")
async def get_endpoint_metrics(endpoint: str, minutes: int = Query(5, ge=1, le=60)):
    """Get metrics for specific endpoint"""
    try:
        from app.core.monitoring import get_metrics
        metrics = get_metrics()
        return metrics.get_endpoint_stats(endpoint, minutes)
    except Exception as e:
        logger.error(f"Endpoint metrics error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get endpoint metrics"}
        )

@router.get("/status")
async def system_status():
    """Get detailed system status"""
    try:
        from app.main import leonore
        from app.core.monitoring import get_metrics
        
        metrics = get_metrics()
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "system": metrics.get_system_stats(),
            "agents": {
                "total": len(leonore.orchestrator.agent_pool),
                "active": sum(1 for a in leonore.orchestrator.agent_pool.values() 
                            if a.state != "idle")
            },
            "memory": {
                "total_memories": leonore.memory.get_stats()["total_memories"]
            }
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get system status"}
        )


@router.post("/test")
async def test_llm():
    """Test LLM connectivity"""
    try:
        from app.core.llm_client import LLMClient
        
        llm = LLMClient(provider="nvidia")
        response = llm.generate("Say 'Hello from Leonore AI' in one sentence.")
        
        if response:
            return {
                "status": "success",
                "response": response,
                "model": llm.model
            }
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "No response from LLM"}
            )
    except Exception as e:
        logger.error(f"LLM test error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to connect to LLM"}
        )


@router.post("/chat/simple")
async def chat_simple(request: ChatRequest):
    """Simple non-streaming chat endpoint"""
    try:
        from app.main import leonore
        
        result = await leonore.process_message(request.session_id, request.message)
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "message": request.message,
            "response": result.get("synthesis", str(result)),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
