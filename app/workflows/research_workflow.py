"""Deep research workflow with RAG"""
from typing import Dict, Any, List
from app.core.llm_client import get_llm_client
from app.core.vector_store import get_vector_store
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class DeepResearchAgent:
    """Deep research with web scraping, PDF parsing, and RAG"""
    
    async def research(self, query: str) -> Dict[str, Any]:
        """Execute deep research workflow"""
        
        # Step 1: Web scraping
        sources = await self._scrape_sources(query)
        
        # Step 2: Parse and embed
        documents = await self._parse_documents(sources)
        
        # Step 3: RAG retrieval
        relevant_docs = await self._retrieve_relevant(query, documents)
        
        # Step 4: Generate report
        report = await self._generate_report(query, relevant_docs)
        
        return {
            "query": query,
            "sources_found": len(sources),
            "documents_processed": len(documents),
            "report": report,
            "citations": self._extract_citations(relevant_docs)
        }
    
    async def _scrape_sources(self, query: str) -> List[Dict[str, str]]:
        """Scrape web sources"""
        from duckduckgo_search import DDGS
        
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=10)
            
            sources = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                }
                for r in results
            ]
            
            logger.info(f"Scraped {len(sources)} sources for: {query}")
            return sources
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return []
    
    async def _parse_documents(self, sources: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Parse and extract text from sources"""
        documents = []
        
        for source in sources:
            doc = {
                "title": source["title"],
                "url": source["url"],
                "content": source["snippet"],
                "metadata": {
                    "source": "web",
                    "url": source["url"]
                }
            }
            documents.append(doc)
        
        return documents
    
    async def _retrieve_relevant(
        self,
        query: str,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using RAG"""
        vector_store = get_vector_store()
        
        # Add documents to vector store
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        try:
            await vector_store.add(texts, metadatas)
        except Exception as e:
            logger.warning(f"Vector store error: {e}")
        
        # Search for relevant documents
        try:
            results = await vector_store.search(query, k=5)
            return results
        except Exception as e:
            logger.warning(f"Search error: {e}")
            return documents[:5]
    
    async def _generate_report(
        self,
        query: str,
        relevant_docs: List[Dict[str, Any]]
    ) -> str:
        """Generate structured research report"""
        llm = get_llm_client()
        
        context = "\n".join([
            f"- {doc.get('text', str(doc))}"
            for doc in relevant_docs[:5]
        ])
        
        prompt = f"""Based on the following research:

Query: {query}

Sources:
{context}

Generate a comprehensive research report with:
1. Executive Summary
2. Key Findings
3. Analysis
4. Recommendations
5. Sources"""
        
        report = await llm.generate(prompt, max_tokens=2048)
        return report
    
    def _extract_citations(self, docs: List[Dict[str, Any]]) -> List[str]:
        """Extract citations from documents"""
        citations = []
        for doc in docs:
            if "metadata" in doc and "url" in doc["metadata"]:
                citations.append(doc["metadata"]["url"])
        return citations
