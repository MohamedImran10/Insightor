"""
FollowupAgent - Generates follow-up questions from research summaries
Uses Gemini to create thoughtful next-step questions for deeper research
"""

import logging
import asyncio
from typing import List
import google.generativeai as genai

logger = logging.getLogger(__name__)


class FollowupAgent:
    """
    Generates follow-up questions based on research summary
    Helps users explore topics deeper with AI-suggested questions
    """
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize FollowupAgent with Gemini API
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        try:
            genai.configure(api_key=gemini_api_key)
            self.client = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("✅ FollowupAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize FollowupAgent: {str(e)}")
            raise
    
    async def generate_followups(
        self,
        summary: str,
        original_query: str,
        top_insights: List[str],
        sources: List[str] = None
    ) -> List[str]:
        """
        Generate follow-up questions based on research summary
        
        Args:
            summary: Executive summary or main findings
            original_query: Original research query
            top_insights: List of key insights extracted
            sources: Optional list of source URLs/titles
        
        Returns:
            List of 5-7 follow-up questions
        """
        try:
            insights_text = "\n".join([f"- {insight}" for insight in top_insights])
            sources_text = "\n".join([f"- {source}" for source in (sources or [])]) if sources else "N/A"
            
            prompt = f"""Based on this research summary, generate 5-7 high-quality follow-up questions that would help explore the topic deeper.

ORIGINAL QUERY: {original_query}

SUMMARY:
{summary[:1000]}

KEY INSIGHTS:
{insights_text}

SOURCES:
{sources_text}

Generate follow-up questions that:
1. Build on the insights discovered
2. Explore unexplored angles or subtopics
3. Are specific and actionable
4. Would lead to deeper understanding

Output ONLY the questions, one per line, starting with a number (e.g., "1. Question here?"). No explanations."""

            # Run Gemini call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(prompt)
            )
            
            # Parse response
            followups = []
            if response and response.text:
                lines = response.text.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and ("?" in line):
                        # Remove numbering
                        question = line.lstrip("0123456789.)- ").strip()
                        if question:
                            followups.append(question)
            
            logger.info(f"✅ Generated {len(followups)} follow-up questions")
            return followups
        
        except Exception as e:
            logger.error(f"❌ Failed to generate followups: {str(e)}")
            return []
