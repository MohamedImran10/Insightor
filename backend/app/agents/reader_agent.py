"""
Reader Agent - Fetches and cleans content from URLs
Uses BeautifulSoup for content extraction and cleaning
"""

import httpx
from typing import Optional, List
import logging
from bs4 import BeautifulSoup
import re
import html2text

logger = logging.getLogger(__name__)


class ReaderAgent:
    """
    Agent responsible for fetching and cleaning content from URLs
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize Reader Agent
        
        Args:
            timeout: Timeout for HTTP requests in seconds
        """
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """
        Fetch raw HTML content from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            Raw HTML content or None if fetch fails
        """
        try:
            logger.debug(f"📥 Fetching content from: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    follow_redirects=True
                )
                response.raise_for_status()
                
                logger.debug(f"✓ Successfully fetched: {url} ({len(response.text)} chars)")
                return response.text
                
        except httpx.RequestError as e:
            logger.warning(f"⚠ Failed to fetch {url}: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"⚠ Unexpected error fetching {url}: {str(e)}")
            return None
    
    def clean_content(self, raw_html: str) -> Optional[str]:
        """
        Clean and extract main content from HTML using BeautifulSoup
        
        Args:
            raw_html: Raw HTML content
            
        Returns:
            Cleaned text content
        """
        try:
            # Use BeautifulSoup for content extraction
            cleaned = self._extract_with_beautifulsoup(raw_html)
            
            if cleaned and len(cleaned) > 50:
                logger.debug(f"✓ Content cleaned: {len(cleaned)} chars extracted")
                return cleaned
            else:
                logger.debug(f"⚠ Content extraction returned too little text")
                return None
                
        except Exception as e:
            logger.warning(f"⚠ Error during content cleaning: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Additional text cleaning
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        # Limit to first 5000 characters for performance
        text = text[:5000]
        
        return text.strip()
    
    def _extract_with_beautifulsoup(self, raw_html: str) -> Optional[str]:
        """
        Extract content using BeautifulSoup
        
        Args:
            raw_html: Raw HTML content
            
        Returns:
            Extracted text or None
        """
        try:
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            # Remove script and style tags
            for tag in soup(['script', 'style', 'meta', 'link', 'noscript']):
                tag.decompose()
            
            # Try to find main content areas
            main_content = None
            
            # Look for common main content containers
            for selector in ['main', 'article', '[role="main"]', '.content', '.article']:
                try:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break
                except:
                    pass
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.find('body') or soup
            
            # Extract paragraphs and headers
            content_parts = []
            
            for tag in main_content.find_all(['h1', 'h2', 'h3', 'p', 'li']):
                text = tag.get_text(strip=True)
                if text and len(text) > 10:
                    content_parts.append(text)
            
            if content_parts:
                combined_text = ' '.join(content_parts)
                return self._clean_text(combined_text)
            else:
                # Fallback: get all text
                text = soup.get_text(separator=' ')
                return self._clean_text(text) if text else None
                
        except Exception as e:
            logger.warning(f"⚠ BeautifulSoup extraction failed: {str(e)}")
            return None
    
    def _fallback_extraction(self, raw_html: str) -> Optional[str]:
        """
        Fallback content extraction using basic text extraction
        
        Args:
            raw_html: Raw HTML content
            
        Returns:
            Extracted text or None
        """
        try:
            # Convert HTML to markdown then to text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            
            text = h.handle(raw_html)
            cleaned = self._clean_text(text)
            
            if len(cleaned) > 100:
                logger.debug(f"✓ Fallback extraction successful: {len(cleaned)} chars")
                return cleaned
            else:
                logger.debug(f"⚠ Fallback extraction returned too little text")
                return None
                
        except Exception as e:
            logger.warning(f"⚠ Fallback extraction failed: {str(e)}")
            return None
    
    async def process_urls(self, urls: List[str]) -> List[dict]:
        """
        Process multiple URLs concurrently
        
        Args:
            urls: List of URLs to process
            
        Returns:
            List of dicts with URL and cleaned content
        """
        results = []
        
        for url in urls:
            try:
                raw_content = await self.fetch_content(url)
                if raw_content:
                    cleaned = self.clean_content(raw_content)
                    results.append({
                        "url": url,
                        "cleaned_text": cleaned,
                        "status": "success"
                    })
                else:
                    results.append({
                        "url": url,
                        "cleaned_text": None,
                        "status": "fetch_failed"
                    })
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                results.append({
                    "url": url,
                    "cleaned_text": None,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def extract_key_sentences(self, text: str, num_sentences: int = 3) -> List[str]:
        """
        Extract key sentences from cleaned text
        
        Args:
            text: Cleaned text content
            num_sentences: Number of sentences to extract
            
        Returns:
            List of key sentences
        """
        if not text:
            return []
        
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Return first N sentences as key insights
        return sentences[:num_sentences]
