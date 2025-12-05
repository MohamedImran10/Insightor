"""
Models for API requests and responses
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResearchRequest(BaseModel):
    """Request model for research endpoint"""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the latest developments in artificial intelligence?"
            }
        }


class SearchResultItem(BaseModel):
    """Individual search result item"""
    title: str
    url: str
    snippet: str
    cleaned_text: Optional[str] = None
    published_date: Optional[str] = None
    fetch_status: str = "success"


class ResearchResponse(BaseModel):
    """Response model for research endpoint"""
    query: str
    status: str
    timestamp: str
    execution_time_seconds: float
    search_results: List[SearchResultItem]
    final_summary: str
    detailed_analysis: Optional[str] = None
    key_findings: Optional[str] = None
    top_insights: List[str]
    recommendations: Optional[str] = None
    sources_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "status": "success",
                "timestamp": "2024-12-04T10:30:00",
                "execution_time_seconds": 12.5,
                "search_results": [
                    {
                        "title": "Machine Learning Basics",
                        "url": "https://example.com",
                        "snippet": "Machine learning is a subset of AI...",
                        "cleaned_text": "Full article content here...",
                        "fetch_status": "success"
                    }
                ],
                "final_summary": "Machine learning is...",
                "top_insights": ["Insight 1", "Insight 2"],
                "sources_count": 5
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    agents_ready: Dict[str, bool]


class ErrorResponse(BaseModel):
    """Error response model"""
    query: Optional[str] = None
    status: str = "error"
    error: str
    timestamp: str


class Citation(BaseModel):
    """Citation model"""
    id: int
    title: str
    url: str
    domain: str
    snippet: str
    published_date: Optional[str] = None
    fetch_status: str = "unknown"


class RetrievedChunk(BaseModel):
    """Retrieved memory chunk"""
    id: str
    text: str
    similarity: float
    metadata: Dict[str, Any]


class ResearchHistoryItem(BaseModel):
    """Single research history item"""
    id: str
    query: str
    timestamp: str
    summary_preview: str
    insights_count: int
    sources_count: int
    similarity_to_current: Optional[float] = None


class ExtendedResearchResponse(ResearchResponse):
    """Extended research response with Phase-3 features"""
    citations: List[Citation] = []
    followup_questions: List[str] = []
    related_topics: List[str] = []
    retrieved_memory: List[RetrievedChunk] = []
    new_chunks_stored: int = 0
    time_taken: float = 0.0


class UserInfo(BaseModel):
    """User information from Firebase token"""
    uid: str
    email: str
    name: Optional[str] = None
    email_verified: bool = False


class ResearchHistoryResponse(BaseModel):
    """Research history response"""
    history: List[ResearchHistoryItem]
    total_count: int
    page: int
    limit: int


class TopicGraphNode(BaseModel):
    """Topic graph node"""
    id: str
    query: str
    timestamp: str
    related_topics: List[str] = []
    edges_count: int = 0


class TopicGraphResponse(BaseModel):
    """Topic graph response"""
    nodes: List[TopicGraphNode]
    edges: List[Dict[str, str]]
    node_count: int
    edge_count: int
