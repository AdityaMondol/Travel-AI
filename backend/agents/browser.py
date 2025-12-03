from typing import Dict, Any
from backend.agents.base import BaseAgent
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

class BrowserAgent(BaseAgent):
    def __init__(self, job_id: str):
        super().__init__("browser", job_id)
        self.allowed_domains = ["google.com", "wikipedia.org", "github.com"]

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        url = input_data.get("url")
        action = input_data.get("action", "read")
        
        self.log_activity("browser_action", {"url": url, "action": action})

        # Safety Check
        domain = url.split("/")[2] if "//" in url else url.split("/")[0]
        # Simple domain check (in production use robust parsing)
        if not any(d in domain for d in self.allowed_domains):
             # In a real system, request user approval here.
             # For now, we log and potentially block or proceed with caution.
             self.log_activity("domain_warning", {"domain": domain})

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=30000)
                
                if action == "read":
                    content = await page.content()
                    title = await page.title()
                    await browser.close()
                    return {"title": title, "content_length": len(content)}
                
                elif action == "screenshot":
                    path = f"artifacts/screenshot_{self.job_id}.png"
                    await page.screenshot(path=path)
                    await browser.close()
                    return {"path": path}
                
                await browser.close()
                return {"status": "success", "message": "Action completed"}
                
            except Exception as e:
                await browser.close()
                logger.error(f"Browser action failed: {e}")
                return {"status": "failed", "error": str(e)}
