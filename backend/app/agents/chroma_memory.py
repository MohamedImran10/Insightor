"""
ChromaDB Manager - Persistent vector database for research memory
Maintains two collections: research_chunks (content vectors) and topic_memory (summary storage)
"""

import chromadb
from chromadb.config import Settings
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ChromaMemory:
    """
    Manages persistent vector storage using ChromaDB
    Provides RAG layer for research memory and retrieval
    """
    
    _instance = None
    
    def __new__(cls, db_path: str = "db/chroma"):
        """
        Singleton pattern - ensures only one ChromaDB client instance
        
        Args:
            db_path: Path to ChromaDB persistent storage
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "db/chroma"):
        """
        Initialize ChromaDB with persistent client
        
        Args:
            db_path: Directory to store ChromaDB data
        """
        if self._initialized:
            return
        
        try:
            logger.info(f"🗄️  Initializing ChromaDB at: {db_path}")
            
            # Create persistent client
            self.client = chromadb.PersistentClient(path=db_path)
            self.db_path = db_path
            
            # Initialize collections
            self.research_chunks = self._get_or_create_collection(
                name="research_chunks",
                metadata={"description": "Stores cleaned research content chunks with embeddings"}
            )
            
            self.topic_memory = self._get_or_create_collection(
                name="topic_memory",
                metadata={"description": "Stores final summaries and insights from research queries"}
            )
            
            self._initialized = True
            logger.info("✅ ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def _get_or_create_collection(self, name: str, metadata: Dict[str, Any] = None):
        """
        Get or create a ChromaDB collection
        
        Args:
            name: Collection name
            metadata: Collection metadata
            
        Returns:
            ChromaDB collection object
        """
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {}
            )
            logger.info(f"✓ Collection '{name}' ready")
            return collection
        except Exception as e:
            logger.error(f"❌ Failed to get/create collection '{name}': {str(e)}")
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
            chunk_ids = [f"chunk_{uuid.uuid4().hex[:12]}" for _ in chunks]
            
            # Add metadata to each
            enhanced_metadata = []
            for i, meta in enumerate(metadata_list):
                enhanced = {
                    **meta,
                    "query": query,
                    "chunk_index": i,
                    "added_at": datetime.now().isoformat()
                }
                enhanced_metadata.append(enhanced)
            
            # Add to ChromaDB
            self.research_chunks.add(
                ids=chunk_ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=enhanced_metadata
            )
            
            logger.info(f"✅ Added {len(chunks)} chunks to research_chunks collection")
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
            
            metadata = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "insights_count": len(insights),
                "sources_count": sources_count,
                "key_findings": key_findings[:500] if key_findings else "",  # Truncate for storage
            }
            
            # Add to topic memory
            self.topic_memory.add(
                ids=[memory_id],
                documents=[summary],
                embeddings=[embedding],
                metadatas=[metadata]
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
            where_filter = None
            if query_text:
                where_filter = {"query": {"$eq": query_text}}
            
            results = self.research_chunks.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
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
            results = self.topic_memory.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "summary": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
                    })
            
            logger.info(f"✅ Retrieved {len(formatted_results)} topic memories")
            return {"memories": formatted_results}
            
        except Exception as e:
            logger.error(f"❌ Error retrieving topic memory: {str(e)}")
            return {"memories": []}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about ChromaDB collections
        
        Returns:
            Dictionary with collection sizes and info
        """
        try:
            chunks_count = self.research_chunks.count()
            memory_count = self.topic_memory.count()
            
            stats = {
                "research_chunks": chunks_count,
                "topic_memory": memory_count,
                "total_entries": chunks_count + memory_count,
                "db_path": self.db_path
            }
            
            logger.info(f"📊 ChromaDB Stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {str(e)}")
            return {}
    
    def clear_collection(self, collection_name: str) -> bool:
        """
        Clear all data from a collection (use with caution!)
        
        Args:
            collection_name: "research_chunks" or "topic_memory"
            
        Returns:
            True if successful
        """
        try:
            collection = self.research_chunks if collection_name == "research_chunks" else self.topic_memory
            
            # Get all IDs and delete
            all_items = collection.get()
            if all_items["ids"]:
                collection.delete(ids=all_items["ids"])
                logger.warning(f"⚠️  Cleared {len(all_items['ids'])} items from {collection_name}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing collection: {str(e)}")
            return False


# Global singleton instance
chroma_memory = None


def get_chroma_memory(db_path: str = "db/chroma") -> ChromaMemory:
    """
    Get or create the global ChromaDB memory instance
    
    Args:
        db_path: Path to persistent storage
        
    Returns:
        ChromaMemory singleton
    """
    global chroma_memory
    if chroma_memory is None:
        chroma_memory = ChromaMemory(db_path)
    return chroma_memory
