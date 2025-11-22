#!/usr/bin/env python3
import os
import sys
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.core.config import Config
from app.core.llm_client import LLMClient
from app.core.logger import setup_logger
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

class Orchestrator:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.agents = {
            "places": PlacesAgent(self.llm_client),
            "weather": WeatherAgent(self.llm_client),
            "food": CulinaryAgent(self.llm_client),
            "culture": CulturalAgent(self.llm_client),
            "budget": BudgetAgent(self.llm_client),
            "transport": TransportAgent(self.llm_client),
            "safety": SafetyAgent(self.llm_client),
            "history": HistoryAgent(self.llm_client),
            "adventure": AdventureAgent(self.llm_client),
            "shopping": ShoppingAgent(self.llm_client),
            "nightlife": NightlifeAgent(self.llm_client),
            "photography": PhotographyAgent(self.llm_client),
            "events": EventsAgent(self.llm_client),
            "translation": TranslationAgent(self.llm_client),
            "visa": VisaAgent(self.llm_client),
            "itinerary": ItineraryAgent(self.llm_client)
        }

    def run(self, destination: str, mother_tongue: str = "en", progress_callback=None) -> Dict[str, Any]:
        # ... (existing run implementation) ...
        # For backward compatibility, we can keep run() or just wrap run_stream
        # But since run() uses threading, let's keep it as is for now or refactor it to use run_stream logic if possible.
        # Actually, let's just add run_stream as a separate method that yields events.
        
        context = {
            "destination": destination,
            "mother_tongue": mother_tongue,
            "generated_at": datetime.now().isoformat(),
            "session_id": str(uuid.uuid4()),
            "agents_active": []
        }

        # Phase 1: Independent Agents (Parallel)
        phase1_agents = [
            "places", "weather", "food", "culture", "budget", "transport", "safety",
            "history", "adventure", "shopping", "nightlife", "photography", "events", "translation", "visa"
        ]
        
        with ThreadPoolExecutor(max_workers=len(phase1_agents)) as executor:
            future_to_agent = {
                executor.submit(self._run_agent, name, context, progress_callback): name 
                for name in phase1_agents
            }
            
            for future in as_completed(future_to_agent):
                name = future_to_agent[future]
                try:
                    result = future.result()
                    context.update(result)
                    context["agents_active"].append(name)
                except Exception as e:
                    logger.error(f"Agent {name} failed: {e}")

        # Phase 2: Dependent Agents (Sequential)
        if progress_callback:
            progress_callback("[ItineraryAgent] Starting...")
        
        try:
            itinerary_result = self.agents["itinerary"].execute(context)
            context.update(itinerary_result)
            context["agents_active"].append("itinerary")
            if progress_callback:
                progress_callback("[ItineraryAgent] Completed")
        except Exception as e:
            logger.error(f"Agent itinerary failed: {e}")

        return context

    async def run_stream(self, destination: str, mother_tongue: str = "en"):
        """
        Async generator for SSE.
        """
        context = {
            "destination": destination,
            "mother_tongue": mother_tongue,
            "generated_at": datetime.now().isoformat(),
            "session_id": str(uuid.uuid4()),
            "agents_active": []
        }
        
        yield f"data: {json.dumps({'type': 'start', 'message': 'Orchestrator started'})}\n\n"

        phase1_agents = [
            "places", "weather", "food", "culture", "budget", "transport", "safety",
            "history", "adventure", "shopping", "nightlife", "photography", "events", "translation", "visa"
        ]
        
        # We can't easily use ThreadPoolExecutor with async generator yielding.
        # So we'll run them and yield as they complete, but we need a way to bridge threads to async.
        # Or we just run them sequentially for the stream (easier but slower) OR use asyncio.to_thread.
        
        import asyncio
        
        loop = asyncio.get_event_loop()
        
        # Helper to run agent and return name + result
        async def run_agent_async(name):
            try:
                agent = self.agents[name]
                # Run in thread to not block loop
                res = await loop.run_in_executor(None, agent.execute, context)
                return name, res, None
            except Exception as e:
                return name, None, str(e)

        # Start all phase 1 agents
        tasks = [run_agent_async(name) for name in phase1_agents]
        
        # Notify that all agents are starting
        for name in phase1_agents:
             yield f"data: {json.dumps({'type': 'agent_start', 'agent': name})}\n\n"
        
        # Process as they complete
        for future in asyncio.as_completed(tasks):
            name, result, error = await future
            
            if error:
                logger.error(f"Agent {name} failed: {error}")
                yield f"data: {json.dumps({'type': 'agent_error', 'agent': name, 'error': error})}\n\n"
            else:
                context.update(result)
                context["agents_active"].append(name)
                yield f"data: {json.dumps({'type': 'agent_complete', 'agent': name})}\n\n"

        # Phase 2
        yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'itinerary'})}\n\n"
        try:
            agent = self.agents["itinerary"]
            result = await loop.run_in_executor(None, agent.execute, context)
            context.update(result)
            context["agents_active"].append("itinerary")
            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': 'itinerary'})}\n\n"
        except Exception as e:
            logger.error(f"Agent itinerary failed: {e}")
            yield f"data: {json.dumps({'type': 'agent_error', 'agent': 'itinerary', 'error': str(e)})}\n\n"
            
        # Send the complete event with context data
        yield f"data: {json.dumps({'type': 'complete', 'context': context})}\n\n"

    def _run_agent(self, name: str, context: Dict[str, Any], progress_callback) -> Dict[str, Any]:
        agent = self.agents[name]
        if progress_callback:
            progress_callback(f"[{agent.name}] Starting...")
        
        result = agent.execute(context)
        
        if progress_callback:
            progress_callback(f"[{agent.name}] Completed")
        
        return result

def create_travel_plan(destination: str, mother_tongue: str = "en", llm_client: LLMClient = None, progress_callback=None) -> Dict[str, Any]:
    orchestrator = Orchestrator(llm_client)
    return orchestrator.run(destination, mother_tongue, progress_callback)

if __name__ == "__main__":
    # Simple CLI test
    if len(sys.argv) > 1:
        dest = sys.argv[1]
        print(f"Generating plan for {dest}...")
        plan = create_travel_plan(dest, progress_callback=print)
        print(json.dumps(plan, indent=2))
    else:
        print("Usage: python main.py <destination>")
