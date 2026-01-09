"""
Pinecone Memory Implementation for Research Agent
Stores research chunks and topic memories using Pinecone vector database
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pinecone
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import hashlib
import logging

logger = logging.getLogger(__name__)

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
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=api_key)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Index names
        self.research_index_name = "research-chunks"
        self.topic_index_name = "topic-memories"
        
        # Initialize indexes
        self._initialize_indexes()
        
    def _initialize_indexes(self):
        """Initialize Pinecone indexes if they don't exist"""
        try:
            # List existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            # Create research chunks index
            if self.research_index_name not in existing_indexes:
                logger.info(f"Creating research index: {self.research_index_name}")
                self.pc.create_index(
                    name=self.research_index_name,
                    dimension=self.embedding_dim,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            # Create topic memories index  
            if self.topic_index_name not in existing_indexes:
                logger.info(f"Creating topic index: {self.topic_index_name}")
                self.pc.create_index(
                    name=self.topic_index_name,
                    dimension=self.embedding_dim,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws", 
                        region="us-east-1"
                    )
                )
                
            # Connect to indexes
            self.research_index = self.pc.Index(self.research_index_name)
            self.topic_index = self.pc.Index(self.topic_index_name)
            
            logger.info("Pinecone indexes initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone indexes: {e}")
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
                "content": content,
                "query": metadata.get("query", ""),
                "source": metadata.get("source", ""),
                "timestamp": metadata.get("timestamp", datetime.now().isoformat()),
                "type": "research_chunk"
            }
            
            # Store in Pinecone
            self.research_index.upsert([
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": pinecone_metadata
                }
            ])
            
            logger.info(f"Stored research chunk with ID: {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error storing research chunk: {e}")
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
            
            # Search in Pinecone
            results = self.research_index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True
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
            
            # Prepare metadata
            pinecone_metadata = {
                "topic": topic,
                "summary": summary,
                "related_queries": json.dumps(related_queries),
                "key_insights": json.dumps(key_insights),
                "timestamp": datetime.now().isoformat(),
                "type": "topic_memory"
            }
            
            # Store in Pinecone
            self.topic_index.upsert([
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": pinecone_metadata
                }
            ])
            
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
            
            # Search in Pinecone
            results = self.topic_index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True
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
            # Query all vectors in topic index (limited approach for free tier)
            results = self.topic_index.query(
                vector=[0] * self.embedding_dim,  # Dummy vector
                top_k=1000,  # Adjust based on your needs
                include_metadata=True
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
            research_stats = self.research_index.describe_index_stats()
            topic_stats = self.topic_index.describe_index_stats()
            
            return {
                "research_chunks": research_stats.total_vector_count,
                "topic_memories": topic_stats.total_vector_count,
                "embedding_dimension": self.embedding_dim,
                "embedding_model": self.embedding_model_name
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def clear_all_data(self):
        """Clear all data from both indexes (use with caution!)"""
        try:
            # Delete all vectors from both indexes
            self.research_index.delete(delete_all=True)
            self.topic_index.delete(delete_all=True)
            logger.info("Cleared all data from Pinecone indexes")
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            raise