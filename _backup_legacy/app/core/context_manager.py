from typing import List, Dict, Any
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class InfiniteContextManager:
    def __init__(self, max_tokens: int = 128000):
        self.max_tokens = max_tokens
        self.context_window: List[Dict[str, Any]] = []
        self.summarized_history: List[str] = []
        self.current_tokens = 0
    
    def add_message(self, role: str, content: str, tokens: int = None):
        if tokens is None:
            tokens = len(content.split()) * 1.3
        
        message = {
            "role": role,
            "content": content,
            "tokens": tokens,
            "timestamp": datetime.now().isoformat()
        }
        
        self.context_window.append(message)
        self.current_tokens += tokens
        
        if self.current_tokens > self.max_tokens * 0.8:
            self._compress_context()
    
    async def _compress_context(self):
        if len(self.context_window) < 10:
            return
        
        to_summarize = self.context_window[:len(self.context_window)//2]
        
        summary_text = "\n".join([
            f"{msg['role']}: {msg['content'][:200]}..."
            for msg in to_summarize
        ])
        
        from app.core.llm_client import LLMClient
        llm = LLMClient(provider="nvidia", model="meta/llama-3.1-70b-instruct")
        
        summary_prompt = f"""
Summarize this conversation history concisely while preserving key information:

{summary_text}

Provide a dense summary that captures:
- Main topics discussed
- Key decisions made
- Important context
- Action items

Keep it under 500 words."""

        import asyncio
        summary = await asyncio.to_thread(llm.generate, summary_prompt, 0.3)
        
        self.summarized_history.append(summary)
        
        self.context_window = self.context_window[len(to_summarize):]
        self.current_tokens = sum(msg["tokens"] for msg in self.context_window)
        
        logger.info(f"Compressed context: {len(to_summarize)} messages -> summary")
    
    def get_context(self) -> str:
        context_parts = []
        
        if self.summarized_history:
            context_parts.append("Previous conversation summary:")
            context_parts.extend(self.summarized_history)
            context_parts.append("\nCurrent conversation:")
        
        for msg in self.context_window:
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        self.context_window = []
        self.summarized_history = []
        self.current_tokens = 0
