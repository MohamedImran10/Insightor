"""
Migration Script: ChromaDB to Weaviate
Migrates existing research chunks and topic memory from ChromaDB to Weaviate
Run this script after setting up Weaviate to preserve your existing data
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.chroma_memory import ChromaMemory
from app.agents.weaviate_memory import WeaviateMemory
from app.agents.embeddings import EmbeddingGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_chroma_to_weaviate():
    """Migrate all data from ChromaDB to Weaviate"""
    
    logger.info("🚀 Starting ChromaDB → Weaviate migration...")
    
    # Initialize both databases
    logger.info("📦 Initializing ChromaDB...")
    chroma = ChromaMemory()
    
    logger.info("📦 Initializing Weaviate...")
    weaviate = WeaviateMemory()
    
    # Get ChromaDB stats
    chroma_stats = chroma.get_collection_stats()
    logger.info(f"📊 ChromaDB Stats: {chroma_stats}")
    
    chunks_count = chroma_stats.get("research_chunks", 0)
    memory_count = chroma_stats.get("topic_memory", 0)
    
    if chunks_count == 0 and memory_count == 0:
        logger.info("✅ No data to migrate. ChromaDB is empty.")
        return
    
    # Migrate research chunks
    if chunks_count > 0:
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 Migrating {chunks_count} research chunks...")
        logger.info(f"{'='*60}")
        
        try:
            # Get all chunks from ChromaDB
            all_chunks = chroma.research_chunks.get(include=['documents', 'metadatas', 'embeddings'])
            
            migrated = 0
            errors = 0
            
            for i, (doc, meta, emb) in enumerate(zip(
                all_chunks.get('documents', []),
                all_chunks.get('metadatas', []),
                all_chunks.get('embeddings', [])
            )):
                try:
                    # Store in Weaviate
                    weaviate.add_research_chunks(
                        chunks=[doc],
                        embeddings=[emb],
                        metadata_list=[meta],
                        query=meta.get('query', 'migrated')
                    )
                    migrated += 1
                    
                    if migrated % 50 == 0:
                        logger.info(f"  ✓ Migrated {migrated}/{chunks_count} chunks...")
                        
                except Exception as e:
                    errors += 1
                    logger.warning(f"  ⚠️  Failed to migrate chunk {i}: {str(e)}")
            
            logger.info(f"✅ Research chunks migration complete: {migrated} success, {errors} errors")
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate research chunks: {str(e)}")
    
    # Migrate topic memory
    if memory_count > 0:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧠 Migrating {memory_count} topic memories...")
        logger.info(f"{'='*60}")
        
        try:
            # Get all topic memories from ChromaDB
            all_memories = chroma.topic_memory.get(include=['documents', 'metadatas', 'embeddings'])
            
            migrated = 0
            errors = 0
            
            for i, (doc, meta, emb) in enumerate(zip(
                all_memories.get('documents', []),
                all_memories.get('metadatas', []),
                all_memories.get('embeddings', [])
            )):
                try:
                    # Store in Weaviate
                    weaviate.add_topic_memory(
                        query=meta.get('query', 'migrated'),
                        summary=doc,
                        embedding=emb,
                        insights=[],
                        key_findings=meta.get('key_findings', ''),
                        sources_count=meta.get('sources_count', 0)
                    )
                    migrated += 1
                    
                    if migrated % 10 == 0:
                        logger.info(f"  ✓ Migrated {migrated}/{memory_count} memories...")
                        
                except Exception as e:
                    errors += 1
                    logger.warning(f"  ⚠️  Failed to migrate memory {i}: {str(e)}")
            
            logger.info(f"✅ Topic memory migration complete: {migrated} success, {errors} errors")
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate topic memories: {str(e)}")
    
    # Verify migration
    logger.info(f"\n{'='*60}")
    logger.info("🔍 Verifying migration...")
    logger.info(f"{'='*60}")
    
    weaviate_stats = weaviate.get_collection_stats()
    logger.info(f"📊 Weaviate Stats after migration: {weaviate_stats}")
    
    logger.info("\n✅✅✅ Migration completed!")
    logger.info("💡 You can now set USE_WEAVIATE=true in your environment and restart the app.")


if __name__ == "__main__":
    migrate_chroma_to_weaviate()
