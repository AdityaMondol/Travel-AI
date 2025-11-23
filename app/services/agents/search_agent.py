from typing import Any, Dict, List
from langchain.tools import Tool
from duckduckgo_search import DDGS
from app.core.logger import setup_logger
from app.services.agents.base_agent import BaseAgent

logger = setup_logger(__name__)

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SearchAgent",
            description="Powerful search agent using DuckDuckGo for real-time information"
        )
        self.ddgs = DDGS()
        self._setup_tools()
    
    def _setup_tools(self):
        search_tool = Tool(
            name="web_search",
            func=self._web_search,
            description="Search the web for information about destinations, attractions, and travel tips"
        )
        self.add_tool(search_tool)
    
    def _web_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        try:
            results = self.ddgs.text(query, max_results=max_results)
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination", "")
        
        try:
            attractions_query = f"best attractions and places to visit in {destination}"
            attractions = self._web_search(attractions_query, max_results=5)
            
            restaurants_query = f"best restaurants and local food in {destination}"
            restaurants = self._web_search(restaurants_query, max_results=5)
            
            tips_query = f"travel tips and recommendations for {destination}"
            tips = self._web_search(tips_query, max_results=3)
            
            return {
                "search_results": {
                    "attractions": attractions,
                    "restaurants": restaurants,
                    "travel_tips": tips
                }
            }
        except Exception as e:
            logger.error(f"Search agent execution error: {e}")
            return {"search_results": {}}
