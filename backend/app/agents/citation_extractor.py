"""
CitationExtractor - Extracts and structures citations from research results
Builds proper citations with titles, URLs, dates, and domains
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class CitationExtractor:
    """
    Extracts structured citations from search results and research metadata
    Formats them for inclusion in final research output
    """
    
    def __init__(self):
        """Initialize CitationExtractor"""
        logger.info("📚 CitationExtractor initialized")
    
    def extract_citations(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract citations from search results
        
        Args:
            search_results: List of search result dictionaries from SearchAgent
        
        Returns:
            List of formatted citation objects
        """
        try:
            citations = []
            
            for i, result in enumerate(search_results, 1):
                citation = {
                    "id": i,
                    "title": result.get("title", "Unknown"),
                    "url": result.get("url", ""),
                    "domain": self._extract_domain(result.get("url", "")),
                    "snippet": result.get("snippet", "")[:200],
                    "published_date": self._extract_date(result.get("published_date", "")),
                    "fetch_status": result.get("fetch_status", "unknown")
                }
                citations.append(citation)
            
            logger.info(f"✅ Extracted {len(citations)} citations")
            return citations
        
        except Exception as e:
            logger.error(f"❌ Failed to extract citations: {str(e)}")
            return []
    
    def extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: Full URL string
        
        Returns:
            Domain name (e.g., "example.com")
        """
        try:
            if not url:
                return "Unknown"
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain if domain else "Unknown"
        except:
            return "Unknown"
    
    def _extract_domain(self, url: str) -> str:
        """Internal helper to extract domain"""
        return self.extract_domain(url)
    
    def _extract_date(self, date_string: str) -> Optional[str]:
        """
        Extract and normalize date string
        
        Args:
            date_string: Date in various formats
        
        Returns:
            ISO formatted date or None
        """
        try:
            if not date_string or date_string.lower() == "unknown":
                return None
            
            # Try to parse common formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.strptime(date_string[:10], "%Y-%m-%d")
                    return dt.isoformat()
                except:
                    pass
            
            return date_string  # Return as-is if can't parse
        
        except Exception as e:
            logger.warning(f"⚠️  Could not parse date '{date_string}': {str(e)}")
            return None
    
    def format_citations_for_display(self, citations: List[Dict[str, Any]]) -> str:
        """
        Format citations as human-readable text
        
        Args:
            citations: List of citation objects
        
        Returns:
            Formatted string for display
        """
        try:
            if not citations:
                return "No citations available"
            
            formatted = "## Sources\n\n"
            for cite in citations:
                formatted += f"[{cite['id']}] {cite['title']}\n"
                formatted += f"    URL: {cite['url']}\n"
                formatted += f"    Domain: {cite['domain']}\n"
                if cite.get('published_date'):
                    formatted += f"    Published: {cite['published_date']}\n"
                formatted += "\n"
            
            return formatted
        
        except Exception as e:
            logger.error(f"❌ Failed to format citations: {str(e)}")
            return "Error formatting citations"
    
    def build_in_text_citations(
        self,
        text: str,
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Add in-text citations to summary text
        (Advanced feature - marks where citations should appear)
        
        Args:
            text: Summary text
            citations: List of citation objects
        
        Returns:
            Text with citation markers
        """
        try:
            # This is a simple implementation - could be enhanced
            # with NLP to automatically detect citation needs
            if not citations or not text:
                return text
            
            # Add simple citation reference at end if any sources exist
            if len(citations) > 0:
                text += f"\n\n(Based on {len(citations)} sources)"
            
            return text
        
        except Exception as e:
            logger.error(f"❌ Failed to add in-text citations: {str(e)}")
            return text
    
    def dedup_citations(
        self,
        citations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate citations by URL
        
        Args:
            citations: List of citation objects
        
        Returns:
            Deduplicated list with re-indexed IDs
        """
        try:
            seen_urls = set()
            unique_citations = []
            
            for cite in citations:
                url = cite.get("url", "").lower()
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_citations.append(cite)
            
            # Re-index
            for i, cite in enumerate(unique_citations, 1):
                cite["id"] = i
            
            logger.info(f"✅ Deduplicated {len(citations)} → {len(unique_citations)} citations")
            return unique_citations
        
        except Exception as e:
            logger.error(f"❌ Failed to dedup citations: {str(e)}")
            return citations
