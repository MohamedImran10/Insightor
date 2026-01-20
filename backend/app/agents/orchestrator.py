"""
Agent Orchestrator - Coordinates the workflow between agents
Manages: SearchAgent → ReaderAgent → MemoryAgent → SummarizerAgent → MemoryAgent
Clean flat architecture with no deep hierarchies
"""

from typing import List, Dict, Any, Optional
import asyncio
import logging
import os
from datetime import datetime

from app.agents.search_agent import SearchAgent, SearchResult
from app.agents.reader_agent import ReaderAgent
from app.agents.gemini_summarizer import GeminiSummarizer
from app.agents.memory_agent import MemoryAgent
from app.agents.embeddings import get_embedding_generator

# Use Pinecone, Weaviate for production, ChromaDB for development fallback
USE_PINECONE = os.getenv('USE_PINECONE', 'false').lower() == 'true'
USE_WEAVIATE = os.getenv('USE_WEAVIATE', 'false').lower() == 'true'

if USE_PINECONE:
    from app.agents.pinecone_memory import PineconeMemory
    def get_vector_memory():
        from app.config import get_settings
        settings = get_settings()
        return PineconeMemory(
            api_key=settings.pinecone_api_key,
            environment=settings.pinecone_environment
        )
elif USE_WEAVIATE:
    from app.agents.weaviate_memory import get_weaviate_memory as get_vector_memory
else:
    from app.agents.chroma_memory import get_chroma_memory as get_vector_memory

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """
    Orchestrates complete research workflow with memory integration
    Pipeline: Search → Read → Store Memory → Retrieve Memory → Summarize → Save Summary
    """
    
    def __init__(self, tavily_key: str, gemini_key: str):
        """
        Initialize the orchestrator with all agents
        
        Args:
            tavily_key: Tavily API key
            gemini_key: Google Gemini API key
        """
        self.search_agent = SearchAgent(api_key=tavily_key, max_results=5)
        self.reader_agent = ReaderAgent(timeout=10)
        self.gemini_summarizer = GeminiSummarizer(api_key=gemini_key)
        
        # RAG components - uses Pinecone, Weaviate (production) or ChromaDB (development)
        if USE_PINECONE:
            self.embedder = None  # Pinecone handles embeddings internally
        else:
            self.embedder = get_embedding_generator()
        self.vector_memory = get_vector_memory()
        # Keep chroma_memory alias for backward compatibility
        self.chroma_memory = self.vector_memory
        self.memory_agent = MemoryAgent(
            embedder=self.embedder,
            vector_memory=self.vector_memory,
            chunk_size=1000,
            overlap=100
        )
        
        backend = "Pinecone" if USE_PINECONE else ("Weaviate" if USE_WEAVIATE else "ChromaDB")
        logger.info(f"🚀 Research Orchestrator initialized with {backend} (SearchAgent → ReaderAgent → MemoryAgent → SummarizerAgent)")
    
    async def execute_research(self, query: str) -> Dict[str, Any]:
        """
        Execute complete research pipeline with RAG
        
        Args:
            query: User's research query
            
        Returns:
            Complete research result with search, summary, and memory
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"🎯 Starting research for query: {query}")
            logger.info(f"{'='*80}\n")
            
            # Step 1: Search
            logger.info("Step 1/5: 🔍 Running Search Agent...")
            search_results = await self.search_agent.search(query)
            
            if not search_results:
                logger.warning("⚠ No search results found")
                return self._create_error_response(query, "No search results found")
            
            logger.info(f"✅ Found {len(search_results)} search results\n")
            
            # Step 2: Read and Clean Content
            logger.info("Step 2/5: 📖 Running Reader Agent...")
            urls = [result.url for result in search_results]
            reader_results = await self.reader_agent.process_urls(urls)
            
            # Merge reader results with search results
            enriched_results = self._merge_results(search_results, reader_results)
            
            logger.info(f"✅ Processed {len(enriched_results)} URLs\n")
            
            # Step 3: Store new content in memory and retrieve relevant context
            logger.info("Step 3/5: 💾 Memory Agent - Storing new content...")
            self.memory_agent.write_chunks(query, enriched_results)
            
            logger.info("Step 3.5/5: 🔍 Memory Agent - Retrieving relevant context...")
            relevant_chunks = self.memory_agent.query_memory(query, n_results=5)
            past_memories = self.memory_agent.query_topic_memory(query, n_results=3)
            rag_context = self.memory_agent.format_memory_context(relevant_chunks, past_memories)
            logger.info(f"✅ Retrieved {len(relevant_chunks)} chunks and {len(past_memories)} past research summaries\n")
            
            # Step 4: Summarize with Gemini (with RAG context)
            logger.info("Step 4/5: 🧠 Summarizer Agent - Generating Summary...")
            
            summary_result = await self.gemini_summarizer.summarize_research(
                query,
                enriched_results,
                rag_context=rag_context if rag_context.strip() else None
            )
            
            logger.info(f"✅ Summary generated\n")
            
            # Step 5: Store final summary in topic memory
            logger.info("Step 5/5: 💾 Memory Agent - Storing summary...")
            self.memory_agent.write_summary_memory(
                query=query,
                summary=summary_result.get("executive_summary", ""),
                insights=summary_result.get("top_insights", []),
                key_findings=summary_result.get("key_findings", ""),
                sources_count=summary_result.get("sources_count", 0)
            )
            logger.info(f"✅ Summary stored in memory\n")
            
            # Compile final response
            final_response = self._compile_response(
                query,
                enriched_results,
                summary_result,
                start_time,
                relevant_chunks,
                past_memories
            )
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Research execution failed: {str(e)}")
            return self._create_error_response(query, str(e))
    
    def _merge_results(self, search_results: List[SearchResult], reader_results: List[Dict]) -> List[Dict[str, Any]]:
        """
        Merge search results with cleaned content from reader agent
        
        Args:
            search_results: Results from search agent
            reader_results: Results from reader agent
            
        Returns:
            Merged results list
        """
        merged = []
        
        # Create a dict for quick lookup
        reader_dict = {r["url"]: r for r in reader_results}
        
        for search_result in search_results:
            reader_data = reader_dict.get(search_result.url, {})
            
            merged_item = {
                "title": search_result.title,
                "url": search_result.url,
                "snippet": search_result.snippet,
                "published_date": search_result.published_date,
                "cleaned_text": reader_data.get("cleaned_text", search_result.snippet),
                "fetch_status": reader_data.get("status", "not_attempted")
            }
            merged.append(merged_item)
        
        return merged
    
    def _compile_response(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        summary_result: Dict[str, Any],
        start_time: datetime,
        relevant_chunks: List[Dict[str, Any]] = None,
        past_memories: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compile the final response with memory context
        
        Args:
            query: Original query
            search_results: Merged search and reader results
            summary_result: Gemini summary result
            start_time: Start time of research
            relevant_chunks: Retrieved content chunks from memory
            past_memories: Retrieved past research summaries
            
        Returns:
            Final response dictionary
        """
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"⏱️  Total execution time: {elapsed_time:.2f}s\n")
        
        return {
            "query": query,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": elapsed_time,
            "search_results": search_results,
            "final_summary": summary_result.get("executive_summary", ""),
            "detailed_analysis": summary_result.get("detailed_analysis", ""),
            "key_findings": summary_result.get("key_findings", ""),
            "top_insights": summary_result.get("top_insights", []),
            "recommendations": summary_result.get("recommendations", ""),
            "sources_count": summary_result.get("sources_count", len(search_results)),
            "full_summary": summary_result.get("full_summary", ""),
            "relevant_memory_chunks": relevant_chunks or [],
            "past_research_memories": past_memories or [],
            "metrics": {}
        }
    
    def _create_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """
        Create an error response
        
        Args:
            query: Original query
            error: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            "query": query,
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "search_results": [],
            "final_summary": "",
            "top_insights": [],
            "sources_count": 0,
            "relevant_memory_chunks": [],
            "past_research_memories": []
        }
    
    async def validate_pipeline(self) -> Dict[str, bool]:
        """
        Validate that all agents are properly initialized
        
        Returns:
            Dictionary with validation results
        """
        try:
            return {
                "search_agent": self.search_agent is not None,
                "reader_agent": self.reader_agent is not None,
                "gemini_summarizer": self.gemini_summarizer is not None,
                "memory_agent": self.memory_agent is not None,
                "pipeline_ready": all([
                    self.search_agent,
                    self.reader_agent,
                    self.gemini_summarizer,
                    self.memory_agent
                ])
            }
        except Exception as e:
            logger.error(f"Pipeline validation failed: {str(e)}")
            return {
                "search_agent": False,
                "reader_agent": False,
                "gemini_summarizer": False,
                "memory_agent": False,
                "pipeline_ready": False
            }
