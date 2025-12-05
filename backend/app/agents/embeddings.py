"""
Embeddings Module - Handles semantic vector generation using Sentence-Transformers
Converts text into dense vectors for similarity search and RAG retrieval
"""

from sentence_transformers import SentenceTransformer
import logging
from typing import List, Union

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings using Sentence-Transformers all-MiniLM-L6-v2 model
    Optimized for semantic search and RAG applications
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Singleton pattern - ensures only one model instance in memory
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
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
        
        try:
            logger.info(f"🔧 Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.embedding_dim = 384
            self._initialized = True
            logger.info(f"✅ Embedding model loaded successfully (dim={self.embedding_dim})")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {str(e)}")
            raise
    
    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> Union[List[float], List[List[float]]]:
        """
        Encode text(s) into embeddings
        
        Args:
            texts: Single text string or list of text strings
            normalize: Whether to normalize embeddings (default: True for cosine similarity)
            
        Returns:
            Single embedding list or list of embeddings
        """
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
            List of embeddings
        """
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
