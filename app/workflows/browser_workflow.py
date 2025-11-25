from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from app.core.llm_client import LLMClient
from app.tools.web_browser import WebBrowserTool
from app.tools.ocr_tool import OCRTool
from app.tools.computer_use import ComputerUseAgent
from app.core.logger import setup_logger
import asyncio

logger = setup_logger(__name__)

class BrowserState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    goal: str
    current_url: str
    screenshots: list
    actions_taken: list
    extracted_data: dict
    iteration: int

class BrowserInteractionAgent:
    def __init__(self):
        self.llm = LLMClient(provider="nvidia", model="meta/llama-3.2-90b-vision-instruct")
        self.browser = WebBrowserTool(headless=False)
        self.ocr = OCRTool()
        self.computer = ComputerUseAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(BrowserState)
        
        workflow.add_node("plan_actions", self.plan_actions)
        workflow.add_node("take_screenshot", self.take_screenshot)
        workflow.add_node("analyze_page", self.analyze_page)
        workflow.add_node("execute_action", self.execute_action)
        workflow.add_node("extract_data", self.extract_data)
        workflow.add_node("verify_goal", self.verify_goal)
        
        workflow.set_entry_point("plan_actions")
        
        workflow.add_edge("plan_actions", "take_screenshot")
        workflow.add_edge("take_screenshot", "analyze_page")
        workflow.add_edge("analyze_page", "execute_action")
        workflow.add_edge("execute_action", "extract_data")
        workflow.add_edge("extract_data", "verify_goal")
        
        workflow.add_conditional_edges(
            "verify_goal",
            self.should_continue,
            {
                "continue": "plan_actions",
                "end": END
            }
        )
        
        return workflow.compile()
    
    async def plan_actions(self, state: BrowserState) -> BrowserState:
        planning_prompt = f"""
Goal: {state['goal']}
Current URL: {state.get('current_url', 'Not started')}
Actions taken: {state.get('actions_taken', [])}
Iteration: {state.get('iteration', 0)}

Plan the next browser actions to achieve the goal.
Provide specific actions:
- navigate(url)
- click(selector)
- type(selector, text)
- scroll(amount)
- wait(seconds)

List 3-5 actions in order."""

        plan = await asyncio.to_thread(self.llm.generate, planning_prompt, 0.5)
        
        state["messages"].append(AIMessage(content=f"Action Plan:\n{plan}"))
        return state
    
    async def take_screenshot(self, state: BrowserState) -> BrowserState:
        screenshot = await self.computer.take_screenshot()
        
        state["screenshots"] = state.get("screenshots", []) + [screenshot]
        state["messages"].append(AIMessage(content="Screenshot captured"))
        return state
    
    async def analyze_page(self, state: BrowserState) -> BrowserState:
        screenshot = state["screenshots"][-1]
        
        import base64
        screenshot_bytes = base64.b64decode(screenshot)
        
        ocr_result = await self.ocr.analyze_screenshot(screenshot_bytes)
        
        analysis_prompt = f"""
Analyze this page for goal: {state['goal']}

OCR Analysis: {ocr_result.get('analysis', '')}

Identify:
1. Current page state
2. Available interactive elements
3. Next best action
4. Data to extract
5. Progress toward goal"""

        analysis = await asyncio.to_thread(self.llm.generate, analysis_prompt, 0.4)
        
        state["messages"].append(AIMessage(content=f"Page Analysis:\n{analysis}"))
        return state
    
    async def execute_action(self, state: BrowserState) -> BrowserState:
        plan = state["messages"][-2].content
        actions = self._parse_actions(plan)
        
        executed = []
        for action in actions[:3]:
            try:
                result = await self._execute_single_action(action)
                executed.append({"action": action, "result": result})
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Action failed: {action}, {e}")
                executed.append({"action": action, "error": str(e)})
        
        state["actions_taken"] = state.get("actions_taken", []) + executed
        state["messages"].append(AIMessage(content=f"Executed {len(executed)} actions"))
        return state
    
    async def extract_data(self, state: BrowserState) -> BrowserState:
        content = await self.browser.get_page_content()
        
        extraction_prompt = f"""
Extract relevant data for goal: {state['goal']}

Page content: {content[:3000]}

Extract structured data as JSON."""

        extracted = await asyncio.to_thread(self.llm.generate, extraction_prompt, 0.3)
        
        import json
        try:
            data = json.loads(extracted)
            state["extracted_data"] = {**state.get("extracted_data", {}), **data}
        except:
            state["extracted_data"] = state.get("extracted_data", {})
        
        state["messages"].append(AIMessage(content="Data extracted"))
        return state
    
    async def verify_goal(self, state: BrowserState) -> BrowserState:
        verification_prompt = f"""
Verify if goal is achieved:

Goal: {state['goal']}
Actions taken: {state['actions_taken']}
Extracted data: {state['extracted_data']}

Is the goal complete? (yes/no)
If no, what's missing?"""

        verification = await asyncio.to_thread(self.llm.generate, verification_prompt, 0.2)
        
        state["messages"].append(AIMessage(content=f"Verification:\n{verification}"))
        state["iteration"] = state.get("iteration", 0) + 1
        return state
    
    def should_continue(self, state: BrowserState) -> str:
        if state["iteration"] >= 10:
            return "end"
        
        last_message = state["messages"][-1].content.lower()
        if "yes" in last_message or "complete" in last_message:
            return "end"
        
        return "continue"
    
    def _parse_actions(self, text: str) -> list:
        actions = []
        for line in text.split('\n'):
            line = line.strip()
            if any(cmd in line.lower() for cmd in ['navigate', 'click', 'type', 'scroll', 'wait']):
                actions.append(line)
        return actions
    
    async def _execute_single_action(self, action: str) -> dict:
        action_lower = action.lower()
        
        if 'navigate' in action_lower:
            url = action.split('(')[1].split(')')[0].strip('\'"')
            return await self.browser.navigate(url)
        
        elif 'click' in action_lower:
            selector = action.split('(')[1].split(')')[0].strip('\'"')
            return await self.browser.click_element(selector)
        
        elif 'type' in action_lower:
            parts = action.split('(')[1].split(')')[0].split(',')
            selector = parts[0].strip('\'"')
            text = parts[1].strip('\'"') if len(parts) > 1 else ""
            return await self.browser.type_in_element(selector, text)
        
        elif 'scroll' in action_lower:
            amount = int(action.split('(')[1].split(')')[0])
            return await self.computer.scroll(amount)
        
        elif 'wait' in action_lower:
            seconds = float(action.split('(')[1].split(')')[0])
            await asyncio.sleep(seconds)
            return {"status": "waited"}
        
        return {"status": "unknown_action"}
    
    async def interact(self, goal: str, start_url: str = None) -> dict:
        initial_state = BrowserState(
            messages=[HumanMessage(content=goal)],
            goal=goal,
            current_url=start_url or "",
            screenshots=[],
            actions_taken=[],
            extracted_data={},
            iteration=0
        )
        
        try:
            if start_url:
                await self.browser.start()
                await self.browser.navigate(start_url)
            
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "status": "success",
                "extracted_data": final_state["extracted_data"],
                "actions_taken": len(final_state["actions_taken"]),
                "iterations": final_state["iteration"]
            }
        except Exception as e:
            logger.error(f"Browser workflow failed: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            await self.browser.close()
