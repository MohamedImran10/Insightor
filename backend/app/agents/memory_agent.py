"""
MemoryAgent - Handles text chunking, embedding, and persistent memory operations
Responsible for storing and retrieving research content from Pinecone, Weaviate (or ChromaDB fallback)
Supports ChromaDB (local), Weaviate, and Pinecone (production) backends
"""

import logging
import os
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Determine which backend to use based on environment
USE_PINECONE = os.getenv('USE_PINECONE', 'false').lower() == 'true'
USE_WEAVIATE = os.getenv('USE_WEAVIATE', 'false').lower() == 'true'


class MemoryAgent:
    """
    Manages chunking, embedding, and retrieval of research content
    Interfaces with Pinecone, Weaviate (production) or ChromaDB (development) for persistent memory storage
    """
    
    def __init__(self, embedder, vector_memory, chunk_size: int = 1000, overlap: int = 100):
        """
        Initialize MemoryAgent
        
        Args:
            embedder: EmbeddingGenerator instance for encoding text (or None if using Pinecone internal embeddings)
            vector_memory: PineconeMemory, WeaviateMemory or ChromaMemory instance for database operations
            chunk_size: Size of text chunks (default: 1000 chars)
            overlap: Overlap between chunks for context preservation (default: 100 chars)
        """
        self.embedder = embedder
        self.vector_memory = vector_memory
        # Keep chroma_memory alias for backward compatibility
        self.chroma_memory = vector_memory
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Determine backend type
        if USE_PINECONE:
            backend = "Pinecone"
        elif USE_WEAVIATE:
            backend = "Weaviate"
        else:
            backend = "ChromaDB"
            
        logger.info(f"🧠 MemoryAgent initialized with {backend} (chunk_size={chunk_size}, overlap={overlap})")

    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or len(text) < self.chunk_size:
            return [text] if text else []
        
        chunks = []
        step = self.chunk_size - self.overlap
        
        for i in range(0, len(text), step):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        logger.info(f"✂️  Chunked text into {len(chunks)} pieces (size={self.chunk_size}, overlap={self.overlap})")
        return chunks
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (None if using Pinecone which handles embeddings internally)
        """
        try:
            # Skip embedding if using Pinecone (handles embeddings internally)
            if USE_PINECONE:
                return None
            
            embedding = self.embedder.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"❌ Error embedding text: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple chunks
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of embedding vectors (None if using Pinecone which handles embeddings internally)
        """
        try:
            if not chunks:
                return []
            
            # Skip embedding if using Pinecone (handles embeddings internally)
            if USE_PINECONE:
                return None
            
            embeddings = self.embedder.embed_chunks(chunks)
            logger.info(f"🔢 Embedded {len(chunks)} chunks")
            return embeddings
        except Exception as e:
            logger.error(f"❌ Error embedding chunks: {str(e)}")
            raise
    
    def write_chunks(
        self,
        query: str,
        search_results: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Process search results, chunk them, embed them, and store in ChromaDB
        
        Args:
            query: Original research query
            search_results: List of search results with cleaned_text
            
        Returns:
            List of stored chunk IDs
        """
        try:
            logger.info(f"📝 Processing search results for storage...")
            
            all_chunks = []
            all_embeddings = []
            all_metadata = []
            
            for result in search_results:
                cleaned_text = result.get("cleaned_text", "")
                if not cleaned_text:
                    continue
                
                # Chunk the content
                chunks = self.chunk_text(cleaned_text)
                
                # Embed the chunks
                embeddings = self.embed_chunks(chunks)
                
                # Prepare metadata
                for i, chunk in enumerate(chunks):
                    metadata = {
                        "title": result.get("title", "Unknown"),
                        "url": result.get("url", ""),
                        "source_domain": result.get("url", "").split("/")[2] if result.get("url") else "",
                        "chunk_index": i,
                        "query": query
                    }
                    all_metadata.append(metadata)
                
                all_chunks.extend(chunks)
                # Only extend embeddings if not using Pinecone (which handles embeddings internally)
                if embeddings is not None:
                    all_embeddings.extend(embeddings)
            
            # Store in vector database (Weaviate or ChromaDB)
            if all_chunks:
                chunk_ids = self.vector_memory.add_research_chunks(
                    chunks=all_chunks,
                    embeddings=all_embeddings,
                    metadata_list=all_metadata,
                    query=query
                )
                logger.info(f"✅ Stored {len(all_chunks)} chunks with IDs")
                return chunk_ids
            else:
                logger.warning("⚠️  No content to store")
                return []
            
        except Exception as e:
            logger.error(f"❌ Error writing chunks: {str(e)}")
            raise
    
    def query_memory(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search ChromaDB for relevant content chunks
        
        Args:
            query: Query text to search for
            n_results: Number of results to retrieve
            
        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        try:
            logger.info(f"🔍 Querying memory for similar chunks (n={n_results})")
            
            # Embed query (returns None for Pinecone which handles internally)
            query_embedding = self.embed_text(query)
            
            # Retrieve similar chunks - pass query for Pinecone which may need to generate embedding
            results = self.vector_memory.retrieve_similar_chunks(
                query_embedding=query_embedding,
                query=query,  # Pass query text for Pinecone fallback
                n_results=n_results
            )
            
            chunks = results.get("chunks", [])
            logger.info(f"✅ Retrieved {len(chunks)} relevant chunks")
            
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Error querying memory: {str(e)}")
            return []
    
    def query_topic_memory(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for past research summaries by topic similarity
        
        Args:
            query: Query text
            n_results: Number of past summaries to retrieve
            
        Returns:
            List of relevant past research summaries
        """
        try:
            logger.info(f"📚 Querying topic memory for related research (n={n_results})")
            
            # Embed query
            query_embedding = self.embed_text(query)
            
            # Retrieve similar memories
            results = self.vector_memory.retrieve_topic_memory(
                query_embedding=query_embedding,
                n_results=n_results
            )
            
            memories = results.get("memories", [])
            logger.info(f"✅ Retrieved {len(memories)} related past research summaries")
            
            return memories
            
        except Exception as e:
            logger.error(f"❌ Error querying topic memory: {str(e)}")
            return []
    
    def write_summary_memory(
        self,
        query: str,
        summary: str,
        insights: List[str],
        key_findings: str = "",
        sources_count: int = 0
    ) -> str:
        """
        Store final research summary in topic memory
        
        Args:
            query: Original research query
            summary: Executive summary text
            insights: List of key insights
            key_findings: Key findings text
            sources_count: Number of sources used
            
        Returns:
            Memory ID
        """
        try:
            logger.info(f"💾 Storing summary in topic memory...")
            
            # Embed summary
            summary_embedding = self.embed_text(summary)
            
            # Store in topic memory
            memory_id = self.vector_memory.add_topic_memory(
                query=query,
                summary=summary,
                embedding=summary_embedding,
                insights=insights,
                key_findings=key_findings,
                sources_count=sources_count
            )
            
            logger.info(f"✅ Summary stored with ID: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Error writing summary memory: {str(e)}")
            raise
    
    def format_memory_context(
        self,
        relevant_chunks: List[Dict[str, Any]],
        past_memories: List[Dict[str, Any]]
    ) -> str:
        """
        Format retrieved memory into text for LLM prompt
        
        Args:
            relevant_chunks: Retrieved content chunks
            past_memories: Retrieved past research summaries
            
        Returns:
            Formatted context string
        """
        try:
            context_parts = []
            
            # Add relevant chunks
            if relevant_chunks:
                context_parts.append("## RELEVANT MEMORY CHUNKS FROM PAST RESEARCH:\n")
                for i, chunk in enumerate(relevant_chunks, 1):
                    similarity = chunk.get("similarity", 0)
                    source = chunk.get("metadata", {}).get("title", "Unknown Source")
                    url = chunk.get("metadata", {}).get("url", "")
                    
                    context_parts.append(f"### Memory {i} (Relevance: {similarity:.2%}) - {source}")
                    if url:
                        context_parts.append(f"Source: {url}")
                    context_parts.append(chunk["content"][:500])  # Truncate for readability
                    context_parts.append("")
            
            # Add past memories
            if past_memories:
                context_parts.append("\n## RELATED PAST RESEARCH SUMMARIES:\n")
                for i, memory in enumerate(past_memories, 1):
                    meta = memory.get("metadata", {})
                    similarity = memory.get("similarity", 0)
                    past_query = meta.get("query", "Unknown Query")
                    
                    context_parts.append(f"### Past Research {i} (Relevance: {similarity:.2%})")
                    context_parts.append(f"Query: {past_query}")
                    context_parts.append(f"Summary: {memory['summary'][:400]}")
                    context_parts.append("")
            
            formatted = "\n".join(context_parts)
            logger.info(f"✓ Formatted memory context: {len(formatted)} characters")
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting memory context: {str(e)}")
            return ""
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored memory
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            stats = self.vector_memory.get_collection_stats()
            logger.info(f"📊 Memory stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting memory stats: {str(e)}")
            return {}
