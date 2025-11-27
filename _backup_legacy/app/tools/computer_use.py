import asyncio
from typing import Dict, Any, Optional
import pyautogui
from PIL import ImageGrab
import io
import base64
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class ComputerUseAgent:
    def __init__(self):
        self.screen_size = pyautogui.size()
        pyautogui.FAILSAFE = True
    
    async def take_screenshot(self) -> str:
        screenshot = await asyncio.to_thread(ImageGrab.grab)
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    async def move_mouse(self, x: int, y: int, duration: float = 0.5):
        await asyncio.to_thread(pyautogui.moveTo, x, y, duration)
        return {"status": "success", "position": (x, y)}
    
    async def click(self, x: int = None, y: int = None, button: str = "left"):
        if x and y:
            await asyncio.to_thread(pyautogui.click, x, y, button=button)
        else:
            await asyncio.to_thread(pyautogui.click, button=button)
        return {"status": "success", "action": "click"}
    
    async def type_text(self, text: str, interval: float = 0.05):
        await asyncio.to_thread(pyautogui.write, text, interval)
        return {"status": "success", "text": text}
    
    async def press_key(self, key: str):
        await asyncio.to_thread(pyautogui.press, key)
        return {"status": "success", "key": key}
    
    async def hotkey(self, *keys):
        await asyncio.to_thread(pyautogui.hotkey, *keys)
        return {"status": "success", "keys": keys}
    
    async def scroll(self, clicks: int):
        await asyncio.to_thread(pyautogui.scroll, clicks)
        return {"status": "success", "scroll": clicks}
    
    def get_screen_info(self) -> Dict[str, Any]:
        return {
            "width": self.screen_size.width,
            "height": self.screen_size.height,
            "position": pyautogui.position()
        }
