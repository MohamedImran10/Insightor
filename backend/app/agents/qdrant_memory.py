"""
QdrantMemory - Cloud-based vector database integration
Manages user-scoped research chunks and topic memory in Qdrant Cloud
"""

import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class QdrantMemory:
    """
    Async Qdrant Cloud client for persistent multi-user vector storage
    Maintains user-scoped collections for research memory
    """
    
    def __init__(self, qdrant_url: str, qdrant_api_key: str, vector_size: int = 384):
        """
        Initialize async Qdrant client
        
        Args:
            qdrant_url: Qdrant Cloud instance URL
            qdrant_api_key: Qdrant API key for authentication
            vector_size: Embedding dimension (default: 384 for all-MiniLM-L6-v2)
        """
        self.client = AsyncQdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30.0
        )
        self.vector_size = vector_size
        self.research_chunks_collection = "research_chunks"
        self.topic_memory_collection = "topic_memory"
        logger.info(f"🔗 Qdrant client initialized (url={qdrant_url}, vector_size={vector_size})")
    
    async def ensure_collections(self):
        """
        Create collections if they don't exist
        Called on app startup
        """
        try:
            # Check research_chunks collection
            try:
                await self.client.get_collection(self.research_chunks_collection)
                logger.info(f"✓ Collection '{self.research_chunks_collection}' exists")
            except:
                logger.info(f"📦 Creating collection '{self.research_chunks_collection}'")
                await self.client.create_collection(
                    collection_name=self.research_chunks_collection,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Collection '{self.research_chunks_collection}' created")
            
            # Check topic_memory collection
            try:
                await self.client.get_collection(self.topic_memory_collection)
                logger.info(f"✓ Collection '{self.topic_memory_collection}' exists")
            except:
                logger.info(f"📦 Creating collection '{self.topic_memory_collection}'")
                await self.client.create_collection(
                    collection_name=self.topic_memory_collection,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Collection '{self.topic_memory_collection}' created")
        
        except Exception as e:
            logger.error(f"❌ Failed to ensure collections: {str(e)}")
            raise
    
    async def store_chunks(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        user_id: str,
        query: str,
        metadata_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Store research chunks in Qdrant (user-scoped)
        
        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
            user_id: User ID for scoping
            query: Original search query
            metadata_list: List of metadata dicts for each chunk
        
        Returns:
            List of point IDs stored
        """
        try:
            if not chunks or not embeddings:
                logger.warning("No chunks to store")
                return []
            
            points = []
            point_ids = []
            
            for i, (chunk_text, embedding, metadata) in enumerate(zip(chunks, embeddings, metadata_list)):
                point_id = str(uuid.uuid4())
                point_ids.append(point_id)
                
                # Add user_id to metadata for filtering
                payload = {
                    "user_id": user_id,
                    "query": query,
                    "text": chunk_text,
                    "chunk_index": i,
                    "timestamp": datetime.now().isoformat(),
                    **metadata  # Merge with existing metadata
                }
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)
            
            # Batch upsert
            await self.client.upsert(
                collection_name=self.research_chunks_collection,
                points=points
            )
            
            logger.info(f"✅ Stored {len(chunks)} chunks for user {user_id[:8]}... (query: {query[:30]}...)")
            return point_ids
        
        except Exception as e:
            logger.error(f"❌ Failed to store chunks: {str(e)}")
            raise
    
    async def retrieve_relevant(
        self,
        query_embedding: List[float],
        user_id: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve most relevant chunks for user (user-scoped search)
        
        Args:
            query_embedding: Query embedding vector
            user_id: User ID to filter results
            top_k: Number of results to return
        
        Returns:
            Dictionary with retrieved chunks and metadata
        """
        try:
            # Search with user_id filter
            search_results = await self.client.search(
                collection_name=self.research_chunks_collection,
                query_vector=query_embedding,
                query_filter={
                    "must": [
                        {
                            "key": "user_id",
                            "match": {"value": user_id}
                        }
                    ]
                },
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            formatted_chunks = []
            for result in search_results:
                formatted_chunks.append({
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "similarity": result.score,
                    "metadata": {
                        "query": result.payload.get("query"),
                        "chunk_index": result.payload.get("chunk_index"),
                        "timestamp": result.payload.get("timestamp"),
                        "source_url": result.payload.get("source_url"),
                        "domain": result.payload.get("domain")
                    }
                })
            
            logger.info(f"✅ Retrieved {len(formatted_chunks)} relevant chunks for user {user_id[:8]}...")
            return {"chunks": formatted_chunks, "count": len(formatted_chunks)}
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve chunks: {str(e)}")
            return {"chunks": [], "count": 0, "error": str(e)}
    
    async def store_topic_memory(
        self,
        summary_text: str,
        embedding: List[float],
        user_id: str,
        query: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Store final research summary in topic_memory (user-scoped)
        
        Args:
            summary_text: Final summary text
            embedding: Summary embedding vector
            user_id: User ID for scoping
            query: Original research query
            metadata: Additional metadata (insights_count, sources_count, etc.)
        
        Returns:
            Point ID
        """
        try:
            point_id = str(uuid.uuid4())
            
            payload = {
                "user_id": user_id,
                "query": query,
                "text": summary_text,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
            
            await self.client.upsert(
                collection_name=self.topic_memory_collection,
                points=[point]
            )
            
            logger.info(f"✅ Stored summary for user {user_id[:8]}... (query: {query[:30]}...)")
            return point_id
        
        except Exception as e:
            logger.error(f"❌ Failed to store topic memory: {str(e)}")
            raise
    
    async def retrieve_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve research history for user (all stored summaries)
        
        Args:
            user_id: User ID to filter
            limit: Number of results
            offset: Pagination offset
        
        Returns:
            Dictionary with user's research history
        """
        try:
            # Search all topic_memory entries for this user
            search_results = await self.client.scroll(
                collection_name=self.topic_memory_collection,
                limit=limit,
                offset=offset,
                query_filter={
                    "must": [
                        {
                            "key": "user_id",
                            "match": {"value": user_id}
                        }
                    ]
                },
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            history = []
            for result in search_results[0]:  # scroll returns (points, next_page_offset)
                history.append({
                    "id": result.id,
                    "query": result.payload.get("query"),
                    "timestamp": result.payload.get("timestamp"),
                    "text_preview": result.payload.get("text", "")[:200],
                    "insights_count": result.payload.get("insights_count", 0),
                    "sources_count": result.payload.get("sources_count", 0)
                })
            
            logger.info(f"✅ Retrieved {len(history)} history entries for user {user_id[:8]}...")
            return {"history": history, "count": len(history)}
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve history: {str(e)}")
            return {"history": [], "count": 0, "error": str(e)}
    
    async def delete_summary(self, user_id: str, summary_id: str) -> bool:
        """
        Delete one summary by ID (with user ownership check)
        
        Args:
            user_id: User ID for authorization
            summary_id: Summary point ID to delete
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Get point to verify ownership
            point = await self.client.retrieve(
                collection_name=self.topic_memory_collection,
                ids=[summary_id],
                with_payload=True
            )
            
            if not point or point[0].payload.get("user_id") != user_id:
                logger.warning(f"⚠️  Unauthorized delete attempt or point not found")
                return False
            
            # Delete
            await self.client.delete(
                collection_name=self.topic_memory_collection,
                points_selector=[summary_id]
            )
            
            logger.info(f"✅ Deleted summary {summary_id[:8]}... for user {user_id[:8]}...")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete summary: {str(e)}")
            return False
    
    async def delete_user_data(self, user_id: str) -> bool:
        """
        Delete ALL data for a user (chunks + summaries)
        
        Args:
            user_id: User ID to delete
        
        Returns:
            True if successful
        """
        try:
            # Delete from research_chunks
            await self.client.delete(
                collection_name=self.research_chunks_collection,
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "user_id",
                                "match": {"value": user_id}
                            }
                        ]
                    }
                }
            )
            
            # Delete from topic_memory
            await self.client.delete(
                collection_name=self.topic_memory_collection,
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "user_id",
                                "match": {"value": user_id}
                            }
                        ]
                    }
                }
            )
            
            logger.info(f"✅ Deleted all data for user {user_id[:8]}...")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete user data: {str(e)}")
            return False
    
    async def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get collection statistics
        
        Args:
            user_id: If provided, get stats for this user only
        
        Returns:
            Dictionary with stats
        """
        try:
            chunks_info = await self.client.get_collection(self.research_chunks_collection)
            memory_info = await self.client.get_collection(self.topic_memory_collection)
            
            stats = {
                "research_chunks_total": chunks_info.points_count,
                "topic_memory_total": memory_info.points_count,
                "vector_size": self.vector_size,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"📊 Stats: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {str(e)}")
            return {"error": str(e)}
