"""
Embeddings Module - Handles semantic vector generation using Sentence-Transformers
Converts text into dense vectors for similarity search and RAG retrieval
Optimized for low-memory environments with lazy loading
"""

import logging
import os
from typing import List, Union

logger = logging.getLogger(__name__)

# Check if we're in a memory-constrained environment (Render free tier)
MEMORY_SAFE_MODE = (
    os.environ.get('RENDER_MEMORY_SAFE', 'false').lower() == 'true' or
    os.environ.get('MEMORY_SAFE_MODE', 'false').lower() == 'true'
)


class EmbeddingGenerator:
    """
    Generates embeddings using Sentence-Transformers all-MiniLM-L6-v2 model
    Optimized for semantic search and RAG applications
    Uses lazy loading to reduce memory footprint on startup
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Singleton pattern - ensures only one model instance in memory
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._model = None
        return cls._instance
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator with Sentence-Transformers model
        
        Args:
            model_name: HuggingFace model identifier (default: all-MiniLM-L6-v2)
                       - Lightweight (22M parameters)
                       - Fast inference
                       - 384-dimensional embeddings
                       - Good for semantic search
        """
        if self._initialized:
            return
        
        self.model_name = model_name
        self.embedding_dim = 384
        self._initialized = True
        logger.info(f"📦 Embedding generator initialized (model will load on first use)")
    
    @property
    def model(self):
        """Lazy load the model on first use"""
        if MEMORY_SAFE_MODE:
            logger.warning("⚠️ Memory safe mode - skipping model load")
            return None
        if self._model is None:
            try:
                logger.info(f"🔧 Loading embedding model: {self.model_name}")
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"✅ Embedding model loaded successfully (dim={self.embedding_dim})")
            except Exception as e:
                logger.error(f"❌ Failed to load embedding model: {str(e)}")
                raise
        return self._model
    
    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> Union[List[float], List[List[float]], None]:
        """
        Encode text(s) into embeddings
        
        Args:
            texts: Single text string or list of text strings
            normalize: Whether to normalize embeddings (default: True for cosine similarity)
            
        Returns:
            Single embedding list or list of embeddings, or None in memory safe mode
        """
        if MEMORY_SAFE_MODE:
            logger.info("Memory safe mode: Returning None for embeddings")
            return None
            
        try:
            if isinstance(texts, str):
                # Single text
                embedding = self.model.encode(texts, normalize_embeddings=normalize)
                return embedding.tolist()
            else:
                # Batch of texts
                embeddings = self.model.encode(texts, normalize_embeddings=normalize, show_progress_bar=False)
                return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Error encoding text: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Efficiently embed multiple text chunks in batches
        
        Args:
            chunks: List of text chunks to embed
            batch_size: Number of texts to process at once (default: 32)
            
        Returns:
            List of embeddings, or empty list in memory safe mode
        """
        if MEMORY_SAFE_MODE:
            logger.info("Memory safe mode: Returning empty list for embed_chunks")
            return []
            
        try:
            logger.info(f"📦 Encoding {len(chunks)} chunks in batches of {batch_size}")
            embeddings = self.model.encode(chunks, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
            logger.info(f"✅ Encoded {len(chunks)} chunks successfully")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Error embedding chunks: {str(e)}")
            raise
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        import numpy as np
        
        e1 = np.array(embedding1)
        e2 = np.array(embedding2)
        
        # Cosine similarity (since embeddings are normalized)
        similarity = np.dot(e1, e2)
        return float(similarity)


# Global singleton instance
embedding_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """
    Get or create the global embedding generator instance
    
    Returns:
        EmbeddingGenerator singleton
    """
    global embedding_generator
    if embedding_generator is None:
        embedding_generator = EmbeddingGenerator()
    return embedding_generator
