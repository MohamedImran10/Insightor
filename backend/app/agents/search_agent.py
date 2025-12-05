"""
Search Agent - Orchestrates Tavily Search API queries
Retrieves search results and prepares data for Reader Agent
"""

import httpx
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SearchResult:
    """Data class for search results"""
    
    def __init__(self, title: str, url: str, snippet: str, published_date: str = ""):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.published_date = published_date
        self.cleaned_text = ""
        self.fetched_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "published_date": self.published_date,
            "cleaned_text": self.cleaned_text,
            "fetched_at": self.fetched_at
        }


class SearchAgent:
    """
    Agent responsible for performing web searches using Tavily API
    """
    
    def __init__(self, api_key: str, max_results: int = 5):
        """
        Initialize Search Agent
        
        Args:
            api_key: Tavily API key
            max_results: Maximum number of search results to fetch
        """
        self.api_key = api_key
        self.max_results = max_results
        self.base_url = "https://api.tavily.com/search"
    
    async def search(self, query: str) -> List[SearchResult]:
        """
        Execute a search query using Tavily API
        
        Args:
            query: User's research query
            
        Returns:
            List of SearchResult objects
        """
        try:
            logger.info(f"🔍 Initiating search for query: {query}")
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": self.max_results,
                "include_answer": True,
                "include_raw_content": True,
                "topic": "general"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
            
            logger.info(f"✅ Search completed. Found {len(data.get('results', []))} results")
            
            search_results = []
            for result in data.get("results", []):
                search_result = SearchResult(
                    title=result.get("title", "No title"),
                    url=result.get("url", ""),
                    snippet=result.get("snippet", ""),
                    published_date=result.get("published_date", "")
                )
                search_results.append(search_result)
            
            return search_results
            
        except httpx.RequestError as e:
            logger.error(f"❌ Search request failed: {str(e)}")
            raise Exception(f"Search API error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error in search: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
    
    
    async def validate_urls(self, urls: List[str]) -> List[str]:
        """
        Validate URLs are accessible before sending to Reader Agent
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of valid URLs
        """
        valid_urls = []
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for url in urls:
                try:
                    response = await client.head(url, follow_redirects=True)
                    if response.status_code < 400:
                        valid_urls.append(url)
                        logger.debug(f"✓ URL validated: {url}")
                    else:
                        logger.debug(f"✗ URL returned status {response.status_code}: {url}")
                except Exception as e:
                    logger.debug(f"✗ URL validation failed for {url}: {str(e)}")
        
        return valid_urls
