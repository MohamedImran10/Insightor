"""
Gemini LLM Summarizer - Uses Google's Gemini API for intelligent summarization
Integrated with RAG layer for memory-augmented generation
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class GeminiSummarizer:
    """
    Uses Google Gemini 2.5 Flash for summarization and insights extraction
    With RAG integration for context-aware generation
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        """
        Initialize Gemini Summarizer
        
        Args:
            api_key: Google API key for Gemini
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    async def summarize_research(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        rag_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary from search results with RAG context
        
        Args:
            query: Original research query
            search_results: List of search results with cleaned content
            rag_context: Optional retrieved context from ChromaDB memory
            
        Returns:
            Dictionary with summary and insights
        """
        try:
            logger.info(f"🧠 Generating summary with Gemini for query: {query}")
            
            # Prepare content for summarization
            content_summary = self._prepare_content_for_summarization(search_results)
            
            # Create prompt for Gemini (with optional RAG context)
            prompt = self._create_summarization_prompt(query, content_summary, rag_context)
            
            # Call Gemini (run in executor to avoid blocking event loop)
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.client.generate_content(prompt))
            summary_text = response.text
            
            logger.info("✅ Summary generated successfully")
            
            # Parse and structure the response
            result = self._parse_summary_response(summary_text, search_results)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in summarization: {str(e)}")
            raise Exception(f"Summarization failed: {str(e)}")
    
    def _prepare_content_for_summarization(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Prepare search results for Gemini by combining relevant content
        
        Args:
            search_results: List of search results
            
        Returns:
            Combined text for summarization
        """
        content_parts = []
        
        for i, result in enumerate(search_results, 1):
            if result.get("cleaned_text"):
                content_parts.append(f"Source {i}: {result.get('title', 'Untitled')}")
                content_parts.append(f"URL: {result.get('url', '')}")
                content_parts.append(f"Snippet: {result.get('snippet', '')}")
                content_parts.append(f"Content: {result.get('cleaned_text', '')}")
                content_parts.append("\n" + "="*80 + "\n")
        
        return "\n".join(content_parts)
    
    def _create_summarization_prompt(
        self,
        query: str,
        content: str,
        rag_context: Optional[str] = None
    ) -> str:
        """
        Create a structured prompt for Gemini with optional RAG context
        
        Args:
            query: Original research query
            content: Combined new content to summarize
            rag_context: Optional retrieved context from ChromaDB memory
            
        Returns:
            Formatted prompt
        """
        rag_section = ""
        if rag_context and rag_context.strip():
            rag_section = f"""
RETRIEVED MEMORY CONTEXT (From previous research):
{rag_context}

---

"""
        
        prompt = f"""You are an expert AI research assistant. Your task is to analyze the provided research materials and create a comprehensive summary.

{rag_section}RESEARCH QUERY: {query}

NEW RESEARCH MATERIALS:
{content}

Please provide:

1. **EXECUTIVE SUMMARY** (2-3 sentences): A concise overview answering the research query. If memory context is available, note any new information or confirmations.
2. **KEY FINDINGS** (3-5 bullet points): Main insights and discoveries from the research, including new developments not mentioned in past research
3. **DETAILED ANALYSIS** (1-2 paragraphs): In-depth explanation of findings, with comparison to historical context if available
4. **TOP INSIGHTS** (3-5 items): Most important takeaways and novel discoveries
5. **RECOMMENDATIONS** (2-3 items): Suggested next steps or actions based on findings
6. **SOURCES USED**: Which sources were most relevant (list by title)

Format your response as clear sections with headers. Be specific, factual, and cite information from the sources when possible.
"""
        return prompt
    
    def _clean_markdown_symbols(self, text: str) -> str:
        """
        Remove markdown formatting symbols from text comprehensively
        
        Args:
            text: Text with potential markdown symbols
            
        Returns:
            Cleaned text without markdown
        """
        if not text:
            return text
        
        text = text.strip()
        
        # Remove all ** (bold markdown)
        while '**' in text:
            text = text.replace('**', '')
        
        # Remove all __ (alternate bold)
        while '__' in text:
            text = text.replace('__', '')
        
        # Remove all ~~ (strikethrough)
        while '~~' in text:
            text = text.replace('~~', '')
        
        # Remove leading/trailing asterisks
        text = text.strip('*')
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _parse_summary_response(self, response_text: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse Gemini response and structure it
        
        Args:
            response_text: Response from Gemini
            search_results: Original search results for reference
            
        Returns:
            Structured summary dictionary
        """
        # Extract sections using simple parsing
        sections = {}
        current_section = "full_response"
        current_content = []
        
        # Keywords to look for in headers
        header_keywords = {
            'EXECUTIVE': 'executive_summary',
            'KEY FINDINGS': 'key_findings',
            'DETAILED': 'detailed_analysis',
            'TOP INSIGHTS': 'top_insights',
            'RECOMMENDATIONS': 'recommendations',
            'SOURCES': 'sources_used'
        }
        
        for line in response_text.split('\n'):
            # Check if this line is a header
            is_header = False
            for keyword, section_name in header_keywords.items():
                if keyword in line.upper():
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_name
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Don't forget the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Extract insights
        top_insights = self._extract_top_insights(sections)
        
        # Use full_response as fallback for executive_summary if not found
        executive_summary = sections.get("executive_summary", "").strip()
        if not executive_summary:
            executive_summary = sections.get("full_response", response_text[:500]).strip()
        
        # Clean markdown from all sections
        executive_summary = self._clean_markdown_symbols(executive_summary)
        key_findings = self._clean_markdown_symbols(sections.get("key_findings", ""))
        detailed_analysis = self._clean_markdown_symbols(sections.get("detailed_analysis", ""))
        recommendations = self._clean_markdown_symbols(sections.get("recommendations", ""))
        
        return {
            "full_summary": response_text,
            "executive_summary": executive_summary,
            "key_findings": key_findings,
            "detailed_analysis": detailed_analysis,
            "top_insights": top_insights,
            "recommendations": recommendations,
            "sources_count": len([r for r in search_results if r.get("cleaned_text")])
        }
    
    def _extract_top_insights(self, sections: Dict[str, str]) -> List[str]:
        """
        Extract key insights from parsed sections
        
        Args:
            sections: Parsed response sections
            
        Returns:
            List of top insights (cleaned of all markdown)
        """
        insights = []
        
        # Try to extract from TOP INSIGHTS section
        top_insights_text = sections.get("top_insights", "")
        if top_insights_text:
            # Split by bullet points or numbering
            lines = top_insights_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 5:  # Minimum length check
                    # Remove all ** markdown symbols first
                    cleaned = line.replace('**', '')
                    # Remove bullet points, numbers, and other markdown symbols
                    cleaned = cleaned.lstrip('- •*0123456789.). ')
                    # Remove any remaining asterisks at start/end
                    cleaned = cleaned.strip('* ')
                    # Final cleanup of multiple spaces
                    cleaned = ' '.join(cleaned.split())
                    
                    if cleaned and len(cleaned) > 5:
                        insights.append(cleaned[:300])
        
        # If we didn't get enough, extract from KEY FINDINGS
        if len(insights) < 3:
            key_findings = sections.get("key_findings", "")
            if key_findings:
                lines = key_findings.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 5 and len(insights) < 5:
                        cleaned = line.replace('**', '')
                        cleaned = cleaned.lstrip('- •*0123456789.). ')
                        cleaned = cleaned.strip('* ')
                        cleaned = ' '.join(cleaned.split())
                        
                        if cleaned and len(cleaned) > 5:
                            insights.append(cleaned[:300])
        
        # If still not enough, extract from executive summary
        if len(insights) < 2:
            exec_summary = sections.get("executive_summary", "")
            if exec_summary:
                # Split by sentences and take first few meaningful ones
                sentences = [s.strip() for s in exec_summary.split('.') if s.strip() and len(s.strip()) > 20]
                for sentence in sentences[:3]:
                    if sentence and len(insights) < 5:
                        # Clean all markdown symbols
                        cleaned_sentence = sentence.replace('**', '')
                        cleaned_sentence = cleaned_sentence.strip('* ')
                        cleaned_sentence = ' '.join(cleaned_sentence.split())
                        
                        if cleaned_sentence:
                            insights.append(cleaned_sentence + '.')
        
        return insights[:5]  # Return top 5 insights
    
    async def generate_follow_up_questions(self, query: str, summary: str) -> List[str]:
        """
        Generate follow-up research questions based on the summary
        
        Args:
            query: Original research query
            summary: Generated summary
            
        Returns:
            List of follow-up questions
        """
        try:
            prompt = f"""Based on this research query and summary, generate 3-5 thoughtful follow-up questions for deeper research:

ORIGINAL QUERY: {query}

SUMMARY: {summary}

Provide only the questions, one per line, without numbering or bullet points. Make them specific and actionable."""
            
            response = self.client.generate_content(prompt)
            questions = [q.strip() for q in response.text.split('\n') if q.strip()]
            
            return questions[:5]
            
        except Exception as e:
            logger.warning(f"Could not generate follow-up questions: {str(e)}")
            return []
    
    async def extract_key_metrics(self, content: str) -> Dict[str, Any]:
        """
        Extract key metrics and statistics from content
        
        Args:
            content: Text content to analyze
            
        Returns:
            Dictionary of extracted metrics
        """
        try:
            prompt = f"""Extract any key metrics, statistics, numbers, percentages, or measurements from this content:

{content}

Format as JSON with metric name as key and value. Example: {{"Market Size": "$50 billion", "Growth Rate": "23% annually"}}
"""
            
            response = self.client.generate_content(prompt)
            
            # Try to parse as JSON
            try:
                metrics = json.loads(response.text)
                return metrics
            except:
                return {"raw_metrics": response.text}
                
        except Exception as e:
            logger.warning(f"Could not extract metrics: {str(e)}")
            return {}
