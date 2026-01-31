"""
Pinecone Memory Implementation for Research Agent
Stores research chunks and topic memories using Pinecone vector database
Uses a single index with namespaces for free tier compatibility
Optimized for low-memory environments (Render free tier)
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
import hashlib
import logging
import time

logger = logging.getLogger(__name__)

# Global lazy-loaded embedding model
_embedding_model = None

def get_embedding_model():
    """Lazy load embedding model to save memory on startup"""
    global _embedding_model
    if _embedding_model is None:
        logger.info("🔄 Loading embedding model (lazy)...")
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Embedding model loaded")
    return _embedding_model

class PineconeMemory:
    def __init__(self, api_key: str, environment: str = "us-east-1", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize Pinecone memory with API credentials
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment (default: us-east-1)
            embedding_model: SentenceTransformer model for embeddings
        """
        self.api_key = api_key
        self.environment = environment
        self.embedding_model_name = embedding_model
        self._embedding_model = None  # Lazy loaded
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension (known value)
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=api_key)
        
        # Single index name (free tier allows only 1 index)
        self.index_name = "insightor"
        
        # Namespace names for different data types
        self.research_namespace = "research-chunks"
        self.topic_namespace = "topic-memories"
        
        # Initialize index (but don't load embedding model yet)
        self._initialize_index()
    
    @property
    def embedding_model(self):
        """Lazy load embedding model on first use"""
        if self._embedding_model is None:
            self._embedding_model = get_embedding_model()
        return self._embedding_model
        
    def _initialize_index(self):
        """Initialize Pinecone index if it doesn't exist"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # List existing indexes
                existing_indexes = [index.name for index in self.pc.list_indexes()]
                
                # Create main index if it doesn't exist
                if self.index_name not in existing_indexes:
                    logger.info(f"Creating Pinecone index: {self.index_name}")
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=self.embedding_dim,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                    # Wait for index to be ready (reduced for faster startup)
                    logger.info("Waiting for index to be ready...")
                    time.sleep(10)  # Reduced from 30 to 10 seconds
                
                # Connect to index
                self.index = self.pc.Index(self.index_name)
                logger.info(f"✅ Connected to Pinecone index: {self.index_name}")
                
                logger.info("Pinecone indexes initialized successfully")
                return  # Success, exit the retry loop
                
            except Exception as e:
                logger.error(f"Error initializing Pinecone indexes (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    raise
    
    def _generate_vector_id(self, content: str) -> str:
        """Generate a unique ID for content based on hash"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def store_research_chunk(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Store a research chunk in Pinecone
        
        Args:
            content: Text content to store
            metadata: Additional metadata (query, source, timestamp, etc.)
            
        Returns:
            vector_id: Unique identifier for the stored chunk
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Generate unique ID
            vector_id = self._generate_vector_id(content)
            
            # Prepare metadata (Pinecone has metadata size limits)
            pinecone_metadata = {
                "content": content[:1000],  # Limit content length
                "query": metadata.get("query", "")[:200],
                "source": metadata.get("source", "")[:500],
                "timestamp": metadata.get("timestamp", datetime.now().isoformat()),
                "type": "research_chunk"
            }
            
            # Store in Pinecone using namespace
            self.index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": pinecone_metadata
                    }
                ],
                namespace=self.research_namespace
            )
            
            logger.info(f"Stored research chunk with ID: {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error storing research chunk: {e}")
            raise
    
    def add_research_chunks(self, chunks: List[str], embeddings: List[List[float]], 
                           metadata_list: List[Dict[str, Any]], query: str) -> List[str]:
        """
        Add multiple research chunks to Pinecone (compatible with MemoryAgent interface)
        
        Args:
            chunks: List of text chunks
            embeddings: List of embeddings (ignored for Pinecone, we generate our own)
            metadata_list: List of metadata dicts
            query: Original research query
            
        Returns:
            List of stored chunk IDs
        """
        chunk_ids = []
        try:
            for i, chunk in enumerate(chunks):
                metadata = metadata_list[i] if i < len(metadata_list) else {}
                metadata["query"] = query
                chunk_id = self.store_research_chunk(chunk, metadata)
                chunk_ids.append(chunk_id)
            
            logger.info(f"✅ Added {len(chunk_ids)} research chunks to Pinecone")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Error adding research chunks: {e}")
            raise
    
    def search_research_chunks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant research chunks
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant chunks with content and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in Pinecone using namespace
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                namespace=self.research_namespace
            )
            
            # Format results
            chunks = []
            for match in results.matches:
                chunk = {
                    "content": match.metadata.get("content", ""),
                    "query": match.metadata.get("query", ""),
                    "source": match.metadata.get("source", ""),
                    "timestamp": match.metadata.get("timestamp", ""),
                    "score": float(match.score)
                }
                chunks.append(chunk)
            
            logger.info(f"Found {len(chunks)} research chunks for query: {query}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error searching research chunks: {e}")
            return []
    
    def store_topic_memory(self, topic: str, summary: str, related_queries: List[str], 
                          key_insights: List[str]) -> str:
        """
        Store topic memory in Pinecone
        
        Args:
            topic: Topic name
            summary: Summary of the topic
            related_queries: List of related queries
            key_insights: List of key insights
            
        Returns:
            vector_id: Unique identifier for the stored topic memory
        """
        try:
            # Create combined content for embedding
            content = f"Topic: {topic}\nSummary: {summary}\nInsights: {' '.join(key_insights)}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Generate unique ID
            vector_id = self._generate_vector_id(content)
            
            # Prepare metadata (limit sizes for Pinecone)
            pinecone_metadata = {
                "topic": topic[:200],
                "summary": summary[:1000],
                "related_queries": json.dumps(related_queries[:10]),
                "key_insights": json.dumps(key_insights[:10]),
                "timestamp": datetime.now().isoformat(),
                "type": "topic_memory"
            }
            
            # Store in Pinecone using namespace
            self.index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": pinecone_metadata
                    }
                ],
                namespace=self.topic_namespace
            )
            
            logger.info(f"Stored topic memory for: {topic}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error storing topic memory: {e}")
            raise
    
    def search_topic_memories(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant topic memories
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant topic memories
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in Pinecone using namespace
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                namespace=self.topic_namespace
            )
            
            # Format results
            memories = []
            for match in results.matches:
                memory = {
                    "topic": match.metadata.get("topic", ""),
                    "summary": match.metadata.get("summary", ""),
                    "related_queries": json.loads(match.metadata.get("related_queries", "[]")),
                    "key_insights": json.loads(match.metadata.get("key_insights", "[]")),
                    "timestamp": match.metadata.get("timestamp", ""),
                    "score": float(match.score)
                }
                memories.append(memory)
            
            logger.info(f"Found {len(memories)} topic memories for query: {query}")
            return memories
            
        except Exception as e:
            logger.error(f"Error searching topic memories: {e}")
            return []
    
    def get_all_topics(self) -> List[str]:
        """
        Get all stored topic names
        
        Returns:
            List of topic names
        """
        try:
            # Query all vectors in topic namespace (limited approach for free tier)
            results = self.index.query(
                vector=[0] * self.embedding_dim,  # Dummy vector
                top_k=1000,  # Adjust based on your needs
                include_metadata=True,
                namespace=self.topic_namespace
            )
            
            topics = []
            for match in results.matches:
                topic = match.metadata.get("topic", "")
                if topic and topic not in topics:
                    topics.append(topic)
            
            return topics
            
        except Exception as e:
            logger.error(f"Error getting all topics: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored data
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = self.index.describe_index_stats()
            
            # Get namespace-specific counts
            research_count = 0
            topic_count = 0
            if hasattr(stats, 'namespaces') and stats.namespaces:
                if self.research_namespace in stats.namespaces:
                    research_count = stats.namespaces[self.research_namespace].vector_count
                if self.topic_namespace in stats.namespaces:
                    topic_count = stats.namespaces[self.topic_namespace].vector_count
            
            return {
                "research_chunks": research_count,
                "topic_memories": topic_count,
                "total_vectors": stats.total_vector_count,
                "embedding_dimension": self.embedding_dim,
                "embedding_model": self.embedding_model_name
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def clear_all_data(self):
        """Clear all data from both namespaces (use with caution!)"""
        try:
            # Delete all vectors from both namespaces
            self.index.delete(delete_all=True, namespace=self.research_namespace)
            self.index.delete(delete_all=True, namespace=self.topic_namespace)
            logger.info("Cleared all data from Pinecone index")
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            raise
    
    def retrieve_similar_chunks(self, query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
        """
        Retrieve similar chunks using pre-computed embedding
        Compatible with ChromaDB interface
        
        Args:
            query_embedding: Pre-computed query embedding
            n_results: Number of results to return
            
        Returns:
            Dictionary with chunks and metadata
        """
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=n_results,
                include_metadata=True,
                namespace=self.research_namespace
            )
            
            chunks = []
            metadatas = []
            for match in results.matches:
                chunks.append(match.metadata.get("content", ""))
                metadatas.append(match.metadata)
            
            return {"chunks": chunks, "metadatas": metadatas}
            
        except Exception as e:
            logger.error(f"Error retrieving similar chunks: {e}")
            return {"chunks": [], "metadatas": []}