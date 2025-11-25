from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from app.core.llm_client import LLMClient
from app.tools.web_browser import WebBrowserTool
from app.core.logger import setup_logger
import asyncio

logger = setup_logger(__name__)

class ResearchState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    search_results: list
    scraped_content: list
    analysis: str
    final_report: str
    iteration: int

class DeepResearchAgent:
    def __init__(self):
        self.llm = LLMClient(provider="nvidia", model="meta/llama-3.1-405b-instruct")
        self.browser = WebBrowserTool(headless=True)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(ResearchState)
        
        workflow.add_node("plan_research", self.plan_research)
        workflow.add_node("web_search", self.web_search)
        workflow.add_node("scrape_content", self.scrape_content)
        workflow.add_node("analyze_content", self.analyze_content)
        workflow.add_node("synthesize_report", self.synthesize_report)
        workflow.add_node("critique_report", self.critique_report)
        
        workflow.set_entry_point("plan_research")
        
        workflow.add_edge("plan_research", "web_search")
        workflow.add_edge("web_search", "scrape_content")
        workflow.add_edge("scrape_content", "analyze_content")
        workflow.add_edge("analyze_content", "synthesize_report")
        workflow.add_edge("synthesize_report", "critique_report")
        
        workflow.add_conditional_edges(
            "critique_report",
            self.should_continue,
            {
                "continue": "plan_research",
                "end": END
            }
        )
        
        return workflow.compile()
    
    async def plan_research(self, state: ResearchState) -> ResearchState:
        query = state["query"]
        iteration = state.get("iteration", 0)
        
        planning_prompt = f"""
Research Query: {query}
Iteration: {iteration}

Create a detailed research plan:
1. Key questions to answer
2. Search queries to execute
3. Types of sources needed
4. Analysis approach

Previous findings: {state.get('analysis', 'None')}

Provide 5-7 specific search queries."""

        plan = await asyncio.to_thread(self.llm.generate, planning_prompt, 0.7)
        
        state["messages"].append(AIMessage(content=f"Research Plan:\n{plan}"))
        return state
    
    async def web_search(self, state: ResearchState) -> ResearchState:
        from duckduckgo_search import DDGS
        
        queries = self._extract_queries(state["messages"][-1].content)
        
        results = []
        async with DDGS() as ddgs:
            for query in queries[:5]:
                try:
                    search_results = list(ddgs.text(query, max_results=5))
                    results.extend(search_results)
                except Exception as e:
                    logger.error(f"Search failed for {query}: {e}")
        
        state["search_results"] = results
        state["messages"].append(AIMessage(content=f"Found {len(results)} sources"))
        return state
    
    async def scrape_content(self, state: ResearchState) -> ResearchState:
        scraped = []
        
        for result in state["search_results"][:10]:
            try:
                url = result.get("href") or result.get("link")
                if not url:
                    continue
                
                await self.browser.navigate(url)
                await asyncio.sleep(2)
                
                content = await self.browser.get_page_content()
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                
                scraped.append({
                    "url": url,
                    "title": result.get("title", ""),
                    "content": text[:5000]
                })
                
            except Exception as e:
                logger.error(f"Scraping failed for {url}: {e}")
        
        state["scraped_content"] = scraped
        state["messages"].append(AIMessage(content=f"Scraped {len(scraped)} pages"))
        return state
    
    async def analyze_content(self, state: ResearchState) -> ResearchState:
        content_summary = "\n\n".join([
            f"Source: {item['title']}\nURL: {item['url']}\n{item['content'][:1000]}"
            for item in state["scraped_content"]
        ])
        
        analysis_prompt = f"""
Analyze this research content for query: {state['query']}

Content:
{content_summary}

Provide:
1. Key findings and insights
2. Data points and statistics
3. Expert opinions
4. Contradictions or gaps
5. Credibility assessment

Be thorough and critical."""

        analysis = await asyncio.to_thread(self.llm.generate, analysis_prompt, 0.5)
        
        state["analysis"] = analysis
        state["messages"].append(AIMessage(content=f"Analysis complete"))
        return state
    
    async def synthesize_report(self, state: ResearchState) -> ResearchState:
        synthesis_prompt = f"""
Create a comprehensive research report for: {state['query']}

Analysis: {state['analysis']}

Structure:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Data & Evidence
5. Conclusions
6. Sources

Make it authoritative, well-structured, and actionable."""

        report = await asyncio.to_thread(self.llm.generate, synthesis_prompt, 0.6)
        
        state["final_report"] = report
        state["messages"].append(AIMessage(content="Report synthesized"))
        return state
    
    async def critique_report(self, state: ResearchState) -> ResearchState:
        critique_prompt = f"""
Critically evaluate this research report:

{state['final_report']}

Assess:
1. Completeness (0-10)
2. Accuracy (0-10)
3. Depth (0-10)
4. Missing information
5. Need for additional research

If score < 8 on any dimension, recommend specific improvements."""

        critique = await asyncio.to_thread(self.llm.generate, critique_prompt, 0.3)
        
        state["messages"].append(AIMessage(content=f"Critique:\n{critique}"))
        state["iteration"] = state.get("iteration", 0) + 1
        
        return state
    
    def should_continue(self, state: ResearchState) -> str:
        if state["iteration"] >= 3:
            return "end"
        
        last_message = state["messages"][-1].content
        if "score" in last_message.lower():
            scores = [int(s) for s in last_message.split() if s.isdigit()]
            if scores and min(scores) < 8:
                return "continue"
        
        return "end"
    
    def _extract_queries(self, text: str) -> list:
        lines = text.split('\n')
        queries = []
        for line in lines:
            if any(line.strip().startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '*']):
                query = line.strip().lstrip('0123456789.-* ')
                if len(query) > 10:
                    queries.append(query)
        return queries[:7]
    
    async def research(self, query: str) -> dict:
        initial_state = ResearchState(
            messages=[HumanMessage(content=query)],
            query=query,
            search_results=[],
            scraped_content=[],
            analysis="",
            final_report="",
            iteration=0
        )
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            return {
                "status": "success",
                "report": final_state["final_report"],
                "analysis": final_state["analysis"],
                "sources": len(final_state["scraped_content"]),
                "iterations": final_state["iteration"]
            }
        except Exception as e:
            logger.error(f"Research workflow failed: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            await self.browser.close()
