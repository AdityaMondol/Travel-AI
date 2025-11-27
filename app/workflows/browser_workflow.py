"""Browser automation workflow"""
from typing import Dict, Any, Optional
from app.core.llm_client import get_llm_client
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class BrowserInteractionAgent:
    """Browser automation with intelligent navigation"""
    
    async def interact(self, goal: str, start_url: Optional[str] = None) -> Dict[str, Any]:
        """Execute browser interaction workflow"""
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed")
            return {"status": "error", "reason": "Playwright not available"}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            try:
                # Step 1: Navigate to start URL
                if start_url:
                    await page.goto(start_url)
                    logger.info(f"Navigated to: {start_url}")
                
                # Step 2: Analyze page and plan actions
                page_content = await page.content()
                actions = await self._plan_actions(goal, page_content)
                
                # Step 3: Execute actions
                results = []
                for action in actions:
                    result = await self._execute_action(page, action)
                    results.append(result)
                
                # Step 4: Extract final result
                final_content = await page.content()
                
                return {
                    "goal": goal,
                    "actions_executed": len(results),
                    "results": results,
                    "final_url": page.url,
                    "status": "success"
                }
            
            finally:
                await browser.close()
    
    async def _plan_actions(self, goal: str, page_content: str) -> list[Dict[str, Any]]:
        """Plan browser actions using LLM"""
        llm = get_llm_client()
        
        prompt = f"""Analyze the following webpage and plan actions to achieve the goal.

Goal: {goal}

Page content (first 2000 chars):
{page_content[:2000]}

Plan specific actions like:
- click(selector)
- fill(selector, text)
- select(selector, value)
- wait(ms)
- screenshot()

Return as JSON array of actions."""
        
        response = await llm.generate(prompt, max_tokens=512)
        
        try:
            import json
            actions = json.loads(response)
            return actions if isinstance(actions, list) else []
        except:
            logger.warning("Failed to parse actions")
            return []
    
    async def _execute_action(self, page, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single browser action"""
        try:
            action_type = action.get("type", "").lower()
            
            if action_type == "click":
                selector = action.get("selector")
                await page.click(selector)
                return {"action": "click", "selector": selector, "status": "success"}
            
            elif action_type == "fill":
                selector = action.get("selector")
                text = action.get("text")
                await page.fill(selector, text)
                return {"action": "fill", "selector": selector, "status": "success"}
            
            elif action_type == "select":
                selector = action.get("selector")
                value = action.get("value")
                await page.select_option(selector, value)
                return {"action": "select", "selector": selector, "status": "success"}
            
            elif action_type == "wait":
                ms = action.get("ms", 1000)
                await page.wait_for_timeout(ms)
                return {"action": "wait", "ms": ms, "status": "success"}
            
            elif action_type == "screenshot":
                path = action.get("path", "screenshot.png")
                await page.screenshot(path=path)
                return {"action": "screenshot", "path": path, "status": "success"}
            
            else:
                return {"action": action_type, "status": "unknown"}
        
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return {"action": action.get("type"), "status": "error", "error": str(e)}
