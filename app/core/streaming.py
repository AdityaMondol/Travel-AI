import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
import json
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class StreamingManager:
    def __init__(self, heartbeat_interval: int = 30):
        self.active_streams: Dict[str, asyncio.Queue] = {}
        self.stream_metadata: Dict[str, Dict[str, Any]] = {}
        self.heartbeat_interval = heartbeat_interval
    
    async def create_stream(self, stream_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.active_streams[stream_id] = queue
        self.stream_metadata[stream_id] = {
            "created_at": datetime.now().isoformat(),
            "last_event": datetime.now().isoformat(),
            "event_count": 0
        }
        return queue
    
    async def send_event(self, stream_id: str, event_type: str, data: Any):
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not found")
            return
        
        try:
            event = {
                "type": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            await self.active_streams[stream_id].put(event)
            self.stream_metadata[stream_id]["last_event"] = datetime.now().isoformat()
            self.stream_metadata[stream_id]["event_count"] += 1
        except Exception as e:
            logger.error(f"Error sending event to stream {stream_id}: {e}")
    
    async def _heartbeat_task(self, stream_id: str):
        """Send periodic heartbeat to keep connection alive"""
        try:
            while stream_id in self.active_streams:
                await asyncio.sleep(self.heartbeat_interval)
                if stream_id in self.active_streams:
                    await self.send_event(stream_id, "heartbeat", {"status": "alive"})
        except Exception as e:
            logger.error(f"Heartbeat error for stream {stream_id}: {e}")
    
    async def stream_generator(self, stream_id: str) -> AsyncGenerator[str, None]:
        if stream_id not in self.active_streams:
            queue = await self.create_stream(stream_id)
        else:
            queue = self.active_streams[stream_id]
        
        heartbeat_task = asyncio.create_task(self._heartbeat_task(stream_id))
        
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=120)
                    
                    if event.get("type") == "end":
                        break
                    
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    logger.warning(f"Stream {stream_id} timeout")
                    yield f"data: {json.dumps({'type': 'error', 'data': 'Stream timeout'})}\n\n"
                    break
        except Exception as e:
            logger.error(f"Stream generator error for {stream_id}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
        finally:
            heartbeat_task.cancel()
            try:
                await self.close_stream(stream_id)
            except:
                pass
    
    async def close_stream(self, stream_id: str):
        if stream_id in self.active_streams:
            try:
                await self.send_event(stream_id, "end", {})
            except:
                pass
            finally:
                if stream_id in self.active_streams:
                    del self.active_streams[stream_id]
                if stream_id in self.stream_metadata:
                    del self.stream_metadata[stream_id]
    
    def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        return self.stream_metadata.get(stream_id)
    
    def get_all_streams(self) -> Dict[str, Dict[str, Any]]:
        return self.stream_metadata.copy()
