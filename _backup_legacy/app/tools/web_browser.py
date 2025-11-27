import asyncio
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class WebBrowserTool:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
    
    async def start(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = await asyncio.to_thread(webdriver.Chrome, options=options)
        return {"status": "started"}
    
    async def navigate(self, url: str):
        if not self.driver:
            await self.start()
        await asyncio.to_thread(self.driver.get, url)
        return {"status": "navigated", "url": url}
    
    async def get_page_content(self) -> str:
        if not self.driver:
            return ""
        return await asyncio.to_thread(lambda: self.driver.page_source)
    
    async def find_element(self, selector: str, by: str = "css") -> Optional[Any]:
        if not self.driver:
            return None
        
        by_type = By.CSS_SELECTOR if by == "css" else By.XPATH
        try:
            element = await asyncio.to_thread(
                self.driver.find_element, by_type, selector
            )
            return element
        except:
            return None
    
    async def click_element(self, selector: str):
        element = await self.find_element(selector)
        if element:
            await asyncio.to_thread(element.click)
            return {"status": "clicked"}
        return {"status": "not_found"}
    
    async def type_in_element(self, selector: str, text: str):
        element = await self.find_element(selector)
        if element:
            await asyncio.to_thread(element.send_keys, text)
            return {"status": "typed"}
        return {"status": "not_found"}
    
    async def screenshot(self) -> bytes:
        if not self.driver:
            return b""
        return await asyncio.to_thread(self.driver.get_screenshot_as_png)
    
    async def close(self):
        if self.driver:
            await asyncio.to_thread(self.driver.quit)
            self.driver = None
        return {"status": "closed"}
