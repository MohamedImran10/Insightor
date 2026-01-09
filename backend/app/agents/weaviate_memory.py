"""
WeaviateMemory - Production-ready vector database for research memory
Replaces ChromaDB with Weaviate for scalable, unlimited storage
Maintains two collections: ResearchChunk (content vectors) and TopicMemory (summary storage)
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter, MetadataQuery
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import os

logger = logging.getLogger(__name__)


class WeaviateMemory:
    """
    Manages persistent vector storage using Weaviate
    Provides RAG layer for research memory and retrieval
    Production-ready with unlimited storage capabilities
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Singleton pattern - ensures only one Weaviate client instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize Weaviate client and collections
        Supports both local Docker and Weaviate Cloud
        """
        if self._initialized:
            return
        
        try:
            logger.info("🗄️  Initializing Weaviate...")
            
            # Get configuration from environment
            weaviate_url = os.getenv('WEAVIATE_URL', 'http://localhost:8085')
            api_key = os.getenv('WEAVIATE_API_KEY')
            
            # Connect to Weaviate
            if api_key:
                # Cloud connection
                logger.info(f"Connecting to Weaviate Cloud: {weaviate_url}")
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=weaviate_url,
                    auth_credentials=weaviate.auth.AuthApiKey(api_key)
                )
            else:
                # Local Docker connection
                logger.info(f"Connecting to local Weaviate: {weaviate_url}")
                host = weaviate_url.replace('http://', '').replace('https://', '').split(':')[0]
                port = int(weaviate_url.split(':')[-1]) if ':' in weaviate_url else 8080
                self.client = weaviate.connect_to_local(host=host, port=port)
            
            # Create collections
            self._create_collections()
            
            self._initialized = True
            logger.info("✅ Weaviate initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Weaviate: {str(e)}")
            raise
    
    def _create_collections(self):
        """Create Weaviate collections if they don't exist"""
        try:
            # Create ResearchChunk collection
            if not self.client.collections.exists("ResearchChunk"):
                self.client.collections.create(
                    name="ResearchChunk",
                    description="Stores cleaned research content chunks with embeddings",
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                        Property(name="query", data_type=DataType.TEXT),
                        Property(name="title", data_type=DataType.TEXT),
                        Property(name="url", data_type=DataType.TEXT),
                        Property(name="source_domain", data_type=DataType.TEXT),
                        Property(name="chunk_index", data_type=DataType.INT),
                        Property(name="added_at", data_type=DataType.TEXT),
                        Property(name="chunk_id", data_type=DataType.TEXT),
                    ]
                )
                logger.info("✓ Collection 'ResearchChunk' created")
            else:
                logger.info("✓ Collection 'ResearchChunk' ready")
            
            # Create TopicMemory collection
            if not self.client.collections.exists("TopicMemory"):
                self.client.collections.create(
                    name="TopicMemory",
                    description="Stores final summaries and insights from research queries",
                    properties=[
                        Property(name="summary", data_type=DataType.TEXT),
                        Property(name="query", data_type=DataType.TEXT),
                        Property(name="timestamp", data_type=DataType.TEXT),
                        Property(name="insights_count", data_type=DataType.INT),
                        Property(name="sources_count", data_type=DataType.INT),
                        Property(name="key_findings", data_type=DataType.TEXT),
                        Property(name="memory_id", data_type=DataType.TEXT),
                    ]
                )
                logger.info("✓ Collection 'TopicMemory' created")
            else:
                logger.info("✓ Collection 'TopicMemory' ready")
            
            # Get collection references
            self.research_chunks = self.client.collections.get("ResearchChunk")
            self.topic_memory = self.client.collections.get("TopicMemory")
            
        except Exception as e:
            logger.error(f"❌ Failed to create collections: {str(e)}")
            raise
    
    def add_research_chunks(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata_list: List[Dict[str, Any]],
        query: str
    ) -> List[str]:
        """
        Add research content chunks to the vector store
        
        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata_list: List of metadata dicts for each chunk
            query: Original research query
            
        Returns:
            List of chunk IDs
        """
        try:
            chunk_ids = []
            
            for i, (chunk, embedding, meta) in enumerate(zip(chunks, embeddings, metadata_list)):
                chunk_id = f"chunk_{uuid.uuid4().hex[:12]}"
                
                properties = {
                    "content": chunk,
                    "query": query,
                    "title": meta.get("title", "Unknown"),
                    "url": meta.get("url", ""),
                    "source_domain": meta.get("source_domain", ""),
                    "chunk_index": meta.get("chunk_index", i),
                    "added_at": datetime.now().isoformat(),
                    "chunk_id": chunk_id,
                }
                
                self.research_chunks.data.insert(
                    properties=properties,
                    vector=embedding
                )
                
                chunk_ids.append(chunk_id)
            
            logger.info(f"✅ Added {len(chunks)} chunks to ResearchChunk collection")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"❌ Error adding research chunks: {str(e)}")
            raise
    
    def add_topic_memory(
        self,
        query: str,
        summary: str,
        embedding: List[float],
        insights: List[str],
        key_findings: str = "",
        sources_count: int = 0
    ) -> str:
        """
        Store final research summary in topic memory
        
        Args:
            query: Original research query
            summary: Executive summary text
            embedding: Summary embedding vector
            insights: List of key insights
            key_findings: Key findings text
            sources_count: Number of sources used
            
        Returns:
            Memory ID
        """
        try:
            memory_id = f"memory_{uuid.uuid4().hex[:12]}"
            
            properties = {
                "summary": summary,
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "insights_count": len(insights),
                "sources_count": sources_count,
                "key_findings": key_findings[:500] if key_findings else "",
                "memory_id": memory_id,
            }
            
            self.topic_memory.data.insert(
                properties=properties,
                vector=embedding
            )
            
            logger.info(f"✅ Added topic memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Error adding topic memory: {str(e)}")
            raise
    
    def retrieve_similar_chunks(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        query_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve most similar research chunks using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return (default: 5)
            query_text: Optional text query for filtering
            
        Returns:
            Dictionary with retrieved chunks and metadata
        """
        try:
            # Build query with optional filter
            query_builder = self.research_chunks.query.near_vector(
                near_vector=query_embedding,
                limit=n_results,
                return_metadata=MetadataQuery(distance=True)
            )
            
            # Add filter if query_text provided
            if query_text:
                query_builder = self.research_chunks.query.near_vector(
                    near_vector=query_embedding,
                    limit=n_results,
                    filters=Filter.by_property("query").equal(query_text),
                    return_metadata=MetadataQuery(distance=True)
                )
            
            results = query_builder
            
            # Format results
            formatted_results = []
            for obj in results.objects:
                distance = obj.metadata.distance if obj.metadata and obj.metadata.distance else 0
                similarity = 1 - distance  # Convert distance to similarity
                
                formatted_results.append({
                    "content": obj.properties.get("content", ""),
                    "metadata": {
                        "title": obj.properties.get("title", "Unknown"),
                        "url": obj.properties.get("url", ""),
                        "source_domain": obj.properties.get("source_domain", ""),
                        "query": obj.properties.get("query", ""),
                        "chunk_index": obj.properties.get("chunk_index", 0),
                    },
                    "similarity": similarity
                })
            
            logger.info(f"✅ Retrieved {len(formatted_results)} similar chunks")
            return {"chunks": formatted_results}
            
        except Exception as e:
            logger.error(f"❌ Error retrieving chunks: {str(e)}")
            return {"chunks": []}
    
    def retrieve_topic_memory(
        self,
        query_embedding: List[float],
        n_results: int = 3
    ) -> Dict[str, Any]:
        """
        Retrieve past research summaries by topic similarity
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of past summaries to retrieve (default: 3)
            
        Returns:
            Dictionary with retrieved memories
        """
        try:
            results = self.topic_memory.query.near_vector(
                near_vector=query_embedding,
                limit=n_results,
                return_metadata=MetadataQuery(distance=True)
            )
            
            # Format results
            formatted_results = []
            for obj in results.objects:
                distance = obj.metadata.distance if obj.metadata and obj.metadata.distance else 0
                similarity = 1 - distance
                
                formatted_results.append({
                    "summary": obj.properties.get("summary", ""),
                    "metadata": {
                        "query": obj.properties.get("query", ""),
                        "timestamp": obj.properties.get("timestamp", ""),
                        "insights_count": obj.properties.get("insights_count", 0),
                        "sources_count": obj.properties.get("sources_count", 0),
                        "key_findings": obj.properties.get("key_findings", ""),
                    },
                    "similarity": similarity
                })
            
            logger.info(f"✅ Retrieved {len(formatted_results)} topic memories")
            return {"memories": formatted_results}
            
        except Exception as e:
            logger.error(f"❌ Error retrieving topic memory: {str(e)}")
            return {"memories": []}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about Weaviate collections
        
        Returns:
            Dictionary with collection sizes and info
        """
        try:
            # Get counts using aggregate
            chunks_response = self.research_chunks.aggregate.over_all(total_count=True)
            memory_response = self.topic_memory.aggregate.over_all(total_count=True)
            
            chunks_count = chunks_response.total_count if chunks_response else 0
            memory_count = memory_response.total_count if memory_response else 0
            
            stats = {
                "research_chunks": chunks_count,
                "topic_memory": memory_count,
                "total_entries": chunks_count + memory_count,
                "db_type": "weaviate",
                "unlimited_storage": True
            }
            
            logger.info(f"📊 Weaviate Stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {str(e)}")
            return {"error": str(e)}
    
    def clear_collection(self, collection_name: str) -> bool:
        """
        Clear all data from a collection (use with caution!)
        
        Args:
            collection_name: "ResearchChunk" or "TopicMemory"
            
        Returns:
            True if successful
        """
        try:
            if collection_name == "ResearchChunk":
                self.client.collections.delete("ResearchChunk")
                self._create_collections()
                logger.warning("⚠️  Cleared ResearchChunk collection")
            elif collection_name == "TopicMemory":
                self.client.collections.delete("TopicMemory")
                self._create_collections()
                logger.warning("⚠️  Cleared TopicMemory collection")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing collection: {str(e)}")
            return False
    
    def close(self):
        """Close the Weaviate connection"""
        try:
            if self.client:
                self.client.close()
                logger.info("✅ Weaviate connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Weaviate: {str(e)}")


# Global singleton instance
weaviate_memory = None


def get_weaviate_memory() -> WeaviateMemory:
    """
    Get or create the global Weaviate memory instance
    
    Returns:
        WeaviateMemory singleton
    """
    global weaviate_memory
    if weaviate_memory is None:
        weaviate_memory = WeaviateMemory()
    return weaviate_memory
