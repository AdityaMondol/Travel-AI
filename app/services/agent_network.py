from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage
from app.core.logger import setup_logger
from app.services.agents.search_agent import SearchAgent
from app.services.agents.places_agent import PlacesAgent
from app.services.agents.weather_agent import WeatherAgent
from app.services.agents.itinerary_agent import ItineraryAgent
from app.services.agents.culinary_agent import CulinaryAgent
from app.services.agents.cultural_agent import CulturalAgent
from app.services.agents.logistics_agents import BudgetAgent, TransportAgent, SafetyAgent
from app.services.agents.history_agent import HistoryAgent
from app.services.agents.adventure_agent import AdventureAgent
from app.services.agents.shopping_agent import ShoppingAgent
from app.services.agents.nightlife_agent import NightlifeAgent
from app.services.agents.photography_agent import PhotographyAgent
from app.services.agents.events_agent import EventsAgent
from app.services.agents.translation_agent import TranslationAgent
from app.services.agents.visa_agent import VisaAgent

logger = setup_logger(__name__)

class AgentNetwork:
    def __init__(self):
        self.agents = {
            "search": SearchAgent(),
            "places": PlacesAgent(None),
            "weather": WeatherAgent(None),
            "food": CulinaryAgent(None),
            "culture": CulturalAgent(None),
            "budget": BudgetAgent(None),
            "transport": TransportAgent(None),
            "safety": SafetyAgent(None),
            "history": HistoryAgent(None),
            "adventure": AdventureAgent(None),
            "shopping": ShoppingAgent(None),
            "nightlife": NightlifeAgent(None),
            "photography": PhotographyAgent(None),
            "events": EventsAgent(None),
            "translation": TranslationAgent(None),
            "visa": VisaAgent(None),
            "itinerary": ItineraryAgent(None)
        }
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(dict)
        
        for agent_name in self.agents.keys():
            workflow.add_node(agent_name, self._create_agent_node(agent_name))
        
        workflow.set_entry_point("search")
        
        workflow.add_edge("search", "places")
        workflow.add_edge("places", "weather")
        workflow.add_edge("weather", "food")
        workflow.add_edge("food", "culture")
        workflow.add_edge("culture", "budget")
        workflow.add_edge("budget", "transport")
        workflow.add_edge("transport", "safety")
        workflow.add_edge("safety", "history")
        workflow.add_edge("history", "adventure")
        workflow.add_edge("adventure", "shopping")
        workflow.add_edge("shopping", "nightlife")
        workflow.add_edge("nightlife", "photography")
        workflow.add_edge("photography", "events")
        workflow.add_edge("events", "translation")
        workflow.add_edge("translation", "visa")
        workflow.add_edge("visa", "itinerary")
        workflow.add_edge("itinerary", END)
        
        return workflow.compile()
    
    def _create_agent_node(self, agent_name: str):
        def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
            try:
                agent = self.agents[agent_name]
                result = agent.execute(state)
                state.update(result)
                logger.info(f"Agent {agent_name} completed successfully")
                return state
            except Exception as e:
                logger.error(f"Agent {agent_name} error: {e}")
                return state
        
        return agent_node
    
    async def run(self, destination: str, language: str = "en") -> Dict[str, Any]:
        initial_state = {
            "destination": destination,
            "language": language,
            "agents_active": []
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            logger.error(f"Agent network execution error: {e}")
            return initial_state
    
    async def run_stream(self, destination: str, language: str = "en"):
        initial_state = {
            "destination": destination,
            "language": language,
            "agents_active": []
        }
        
        try:
            for output in self.graph.stream(initial_state):
                for agent_name, state in output.items():
                    yield {
                        "type": "agent_complete",
                        "agent": agent_name,
                        "state": state
                    }
        except Exception as e:
            logger.error(f"Agent network stream error: {e}")
            yield {
                "type": "error",
                "message": str(e)
            }
