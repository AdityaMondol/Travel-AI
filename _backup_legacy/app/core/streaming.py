"""Server-sent events streaming for real-time updates"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class StreamingManager:
    """Manage SSE streams for real-time communication"""
    
    def __init__(self):
        self.streams: Dict[str, asyncio.Queue] = {}
    
    async def create_stream(self, stream_id: str) -> asyncio.Queue:
        """Create new stream"""
        queue = asyncio.Queue()
        self.streams[stream_id] = queue
        logger.info(f"Stream created: {stream_id}")
        return queue
    
    async def send_event(self, stream_id: str, event_type: str, data: Any):
        """Send event to stream"""
        if stream_id not in self.streams:
            return
        
        event = {
            "type": event_type,
            "data": data,
        }
        
        await self.streams[stream_id].put(event)
    
    async def stream_generator(self, stream_id: str) -> AsyncGenerator[str, None]:
        """Generate SSE formatted stream"""
        if stream_id not in self.streams:
            return
        
        queue = self.streams[stream_id]
        
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            await self.close_stream(stream_id)
    
    async def close_stream(self, stream_id: str):
        """Close stream"""
        if stream_id in self.streams:
            del self.streams[stream_id]
            logger.info(f"Stream closed: {stream_id}")
