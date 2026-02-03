"""
Pinecone-based History Manager
Stores user search history in Pinecone vector database (FREE tier compatible)
No billing required - uses existing Pinecone setup
"""
import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pinecone import Pinecone, ServerlessSpec

logger = logging.getLogger(__name__)

# History namespace in Pinecone
HISTORY_NAMESPACE = "user-history"

class PineconeHistoryManager:
    """Manages user search history in Pinecone (FREE - no billing required)"""
    
    def __init__(self, api_key: str = None, environment: str = "us-east-1"):
        """
        Initialize Pinecone history manager
        
        Args:
            api_key: Pinecone API key (uses env var if not provided)
            environment: Pinecone environment
        """
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment
        self.index_name = "insightor"
        self.namespace = HISTORY_NAMESPACE
        self.index = None
        self.embedding_dim = 384  # Same as other Pinecone data
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone connection"""
        try:
            if not self.api_key:
                logger.warning("⚠️ Pinecone API key not found - history disabled")
                return
            
            self.pc = Pinecone(api_key=self.api_key)
            self.index = self.pc.Index(self.index_name)
            logger.info(f"✅ Pinecone history manager initialized (namespace: {self.namespace})")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone history: {e}")
            self.index = None
    
    def _generate_id(self, user_id: str, query: str, timestamp: str) -> str:
        """Generate unique ID for history entry"""
        content = f"{user_id}_{query}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _create_dummy_embedding(self) -> List[float]:
        """Create a dummy embedding for history storage (not used for search)"""
        # Use small random-ish values instead of zeros for better Pinecone compatibility
        import random
        random.seed(42)  # Consistent seed for reproducibility
        return [random.uniform(-0.01, 0.01) for _ in range(self.embedding_dim)]
    
    async def save_search_history(
        self, 
        user_id: str, 
        query: str, 
        response: str, 
        sources: List[Dict[str, Any]],
        search_results: Optional[List[Dict]] = None,
        insights: Optional[List[str]] = None,
        memory_chunks: Optional[List[Dict]] = None
    ) -> bool:
        """
        Save a search query and response to Pinecone
        
        Args:
            user_id: User's unique ID
            query: Search query
            response: AI-generated response/summary
            sources: List of source URLs and titles
            search_results: Raw search results (optional)
            insights: Key insights (optional)
            memory_chunks: Related memory chunks (optional)
            
        Returns:
            bool: True if saved successfully
        """
        if not self.index or not user_id:
            logger.debug(f"History save skipped: index={bool(self.index)}, user_id={bool(user_id)}")
            return False
        
        try:
            timestamp = datetime.utcnow().isoformat()
            vector_id = self._generate_id(user_id, query, timestamp)
            
            # Process memory chunks to preserve structure while limiting size
            processed_chunks = []
            if memory_chunks:
                for chunk in memory_chunks[:3]:  # Only store first 3
                    if isinstance(chunk, str):
                        # If it's a string, create a minimal chunk object
                        processed_chunks.append({
                            "content": chunk[:300],  # Truncate content
                            "metadata": {},
                            "similarity": 0
                        })
                    elif isinstance(chunk, dict):
                        # If it's a dict, preserve structure
                        processed_chunks.append({
                            "content": str(chunk.get("content", ""))[:300],
                            "metadata": chunk.get("metadata", {}),
                            "similarity": chunk.get("similarity", 0)
                        })
            
            # Prepare metadata (Pinecone has 40KB limit per vector)
            # Truncate long fields to fit
            metadata = {
                "type": "search_history",
                "user_id": user_id,
                "query": query[:500],  # Limit query length
                "response": response[:3000],  # Limit response length
                "sources": json.dumps(sources[:10]),  # Limit sources
                "insights": json.dumps((insights or [])[:5]),  # Limit insights
                "memory_chunks": json.dumps(processed_chunks),  # Store processed chunks
                "timestamp": timestamp,
                "sources_count": len(sources),
            }
            
            # Create dummy embedding (history doesn't need semantic search)
            embedding = self._create_dummy_embedding()
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }],
                namespace=self.namespace
            )
            
            logger.info(f"✅ Saved search history for user {user_id[:8]}... (id: {vector_id[:12]}...)")
            return True
            
        except Exception as e:
            logger.debug(f"History save failed: {e}")
            return False
    
    async def get_search_history(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get user's search history
        
        Args:
            user_id: User's unique ID
            limit: Maximum number of entries to return
            
        Returns:
            List of history entries sorted by timestamp (newest first)
        """
        if not self.index or not user_id:
            return []
        
        try:
            # Query with dummy vector and filter by user_id
            # Pinecone filter syntax uses $eq for equality
            results = self.index.query(
                vector=self._create_dummy_embedding(),
                top_k=limit * 2,  # Get more to filter
                include_metadata=True,
                namespace=self.namespace,
                filter={
                    "$and": [
                        {"user_id": {"$eq": user_id}},
                        {"type": {"$eq": "search_history"}}
                    ]
                }
            )
            
            logger.info(f"📜 Pinecone query returned {len(results.matches)} matches for user {user_id[:8]}...")
            
            # Parse results
            history = []
            for match in results.matches:
                meta = match.metadata
                
                # Helper function to safely parse JSON
                def safe_json_parse(value, default=None):
                    if default is None:
                        default = []
                    if value is None or value == "":
                        return default
                    if isinstance(value, (list, dict)):
                        return value
                    if isinstance(value, str):
                        try:
                            return json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            logger.debug(f"Failed to parse JSON: {value}")
                            return default
                    return default
                
                entry = {
                    "id": match.id,
                    "query": meta.get("query", ""),
                    "response": meta.get("response", ""),
                    "sources": safe_json_parse(meta.get("sources")),
                    "insights": safe_json_parse(meta.get("insights")),
                    "memory_chunks": safe_json_parse(meta.get("memory_chunks")),
                    "search_results": safe_json_parse(meta.get("sources")),
                    "timestamp": meta.get("timestamp", ""),
                    "sources_count": meta.get("sources_count", 0),
                }
                
                logger.debug(f"Parsed history entry - Query: {entry['query'][:50]}..., Memory chunks: {len(entry['memory_chunks'])}")
                history.append(entry)
            
            # Sort by timestamp (newest first)
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            
            logger.info(f"Returning {len(history[:limit])} history entries")
            return history[:limit]
            
        except Exception as e:
            logger.debug(f"History fetch failed: {e}")
            return []
    
    async def delete_history_entry(self, user_id: str, entry_id: str) -> bool:
        """Delete a specific history entry"""
        if not self.index:
            return False
        
        try:
            self.index.delete(ids=[entry_id], namespace=self.namespace)
            logger.info(f"✅ Deleted history entry {entry_id}")
            return True
        except Exception as e:
            logger.debug(f"History delete failed: {e}")
            return False
    
    async def clear_user_history(self, user_id: str) -> bool:
        """Clear all history for a user"""
        if not self.index:
            return False
        
        try:
            # Get all user's history entries
            history = await self.get_search_history(user_id, limit=1000)
            
            if history:
                ids = [entry["id"] for entry in history]
                self.index.delete(ids=ids, namespace=self.namespace)
                logger.info(f"✅ Cleared {len(ids)} history entries for user {user_id[:8]}...")
            
            return True
        except Exception as e:
            logger.debug(f"History clear failed: {e}")
            return False


# Singleton instance
_history_manager = None

def get_pinecone_history_manager() -> PineconeHistoryManager:
    """Get or create singleton history manager"""
    global _history_manager
    if _history_manager is None:
        _history_manager = PineconeHistoryManager()
    return _history_manager
