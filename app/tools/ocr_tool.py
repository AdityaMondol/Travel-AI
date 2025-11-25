import asyncio
from typing import Dict, Any
from PIL import Image
import io
import base64
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class OCRTool:
    def __init__(self):
        self.model = "meta/llama-3.2-90b-vision-instruct"
    
    async def extract_text_from_image(self, image_data: bytes) -> Dict[str, Any]:
        try:
            from app.core.llm_client import LLMClient
            llm = LLMClient(provider="nvidia", model=self.model)
            
            image = Image.open(io.BytesIO(image_data))
            
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            prompt = """
Extract all text from this image. Provide:
1. All visible text in reading order
2. Text structure (headings, paragraphs, lists)
3. Any tables or structured data
4. Confidence level

Format as structured output."""

            result = await asyncio.to_thread(llm.generate, prompt, 0.2)
            
            return {
                "status": "success",
                "text": result,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def analyze_screenshot(self, image_data: bytes) -> Dict[str, Any]:
        try:
            from app.core.llm_client import LLMClient
            llm = LLMClient(provider="nvidia", model=self.model)
            
            prompt = """
Analyze this screenshot and provide:
1. What application/website is shown
2. Main UI elements visible
3. Current state/context
4. Actionable elements (buttons, links, inputs)
5. Any text content

Be detailed and structured."""

            result = await asyncio.to_thread(llm.generate, prompt, 0.3)
            
            return {
                "status": "success",
                "analysis": result,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Screenshot analysis failed: {e}")
            return {"status": "error", "error": str(e)}
