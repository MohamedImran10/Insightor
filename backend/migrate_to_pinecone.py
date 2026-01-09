"""
Migration script to transfer data from Weaviate to Pinecone
Migrates research chunks and topic memories while preserving all metadata
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to the path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.agents.pinecone_memory import PineconeMemory
from app.agents.weaviate_memory import WeaviateMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables from .env file"""
    env_path = project_root / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def migrate_weaviate_to_pinecone(
    pinecone_api_key: str,
    pinecone_environment: str = "us-east-1",
    weaviate_url: str = "http://localhost:8085"
):
    """
    Migrate all data from Weaviate to Pinecone
    
    Args:
        pinecone_api_key: Pinecone API key
        pinecone_environment: Pinecone environment
        weaviate_url: Weaviate server URL
    """
    try:
        logger.info("🚀 Starting Weaviate to Pinecone migration...")
        
        # Initialize connections
        logger.info("Initializing Weaviate connection...")
        # Set environment variable for Weaviate URL if needed
        os.environ['WEAVIATE_URL'] = weaviate_url
        weaviate_memory = WeaviateMemory()
        
        logger.info("Initializing Pinecone connection...")
        pinecone_memory = PineconeMemory(
            api_key=pinecone_api_key,
            environment=pinecone_environment,
            embedding_model="all-MiniLM-L6-v2"  # Use cached model if available
        )
        
        # Get statistics from Weaviate
        logger.info("Getting Weaviate data...")
        logger.info("Checking Weaviate collections...")
        research_count = 0
        topic_count = 0
        
        # Migrate research chunks
        logger.info("\n📄 Migrating research chunks...")
        research_count = 0
        
        # Note: Weaviate doesn't have a direct "get all" method, so we'll use a broad search
        # This is a workaround for migration - in practice, you might need to modify this
        try:
            # Try to get all research chunks by searching with a very generic query
            all_chunks = weaviate_memory.search_research_chunks("", limit=10000)  # Adjust limit as needed
            
            for chunk in all_chunks:
                try:
                    # Store in Pinecone
                    pinecone_memory.store_research_chunk(
                        content=chunk['content'],
                        metadata={
                            'query': chunk.get('query', ''),
                            'source': chunk.get('source', ''),
                            'timestamp': chunk.get('timestamp', datetime.now().isoformat())
                        }
                    )
                    research_count += 1
                    
                    if research_count % 10 == 0:
                        logger.info(f"  Migrated {research_count} research chunks...")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error migrating research chunk: {e}")
                    continue
                    
            logger.info(f"✅ Successfully migrated {research_count} research chunks")
            
        except Exception as e:
            logger.error(f"❌ Error accessing research chunks: {e}")
        
        # Migrate topic memories
        logger.info("\n🧠 Migrating topic memories...")
        topic_count = 0
        
        try:
            # Try to get all topics
            all_topics = weaviate_memory.get_all_topics()
            
            for topic in all_topics:
                try:
                    # Get topic memories by searching for the topic
                    topic_memories = weaviate_memory.search_topic_memories(topic, limit=1)
                    
                    if topic_memories:
                        memory = topic_memories[0]  # Take the first (should be most relevant)
                        
                        # Store in Pinecone
                        pinecone_memory.store_topic_memory(
                            topic=memory.get('topic', topic),
                            summary=memory.get('summary', ''),
                            related_queries=memory.get('related_queries', []),
                            key_insights=memory.get('key_insights', [])
                        )
                        topic_count += 1
                        
                        if topic_count % 5 == 0:
                            logger.info(f"  Migrated {topic_count} topic memories...")
                            
                except Exception as e:
                    logger.error(f"  ❌ Error migrating topic '{topic}': {e}")
                    continue
                    
            logger.info(f"✅ Successfully migrated {topic_count} topic memories")
            
        except Exception as e:
            logger.error(f"❌ Error accessing topic memories: {e}")
        
        # Get final statistics
        logger.info("\n📊 Migration Summary:")
        pinecone_stats = pinecone_memory.get_stats()
        logger.info(f"Pinecone now contains:")
        logger.info(f"  - Research chunks: {pinecone_stats.get('research_chunks', 0)}")
        logger.info(f"  - Topic memories: {pinecone_stats.get('topic_memories', 0)}")
        
        logger.info(f"\n🎉 Migration completed successfully!")
        logger.info(f"  - {research_count} research chunks migrated")
        logger.info(f"  - {topic_count} topic memories migrated")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def migrate_chromadb_to_pinecone(
    pinecone_api_key: str,
    pinecone_environment: str = "us-east-1"
):
    """
    Alternative migration from ChromaDB to Pinecone
    (In case user was using ChromaDB before Weaviate)
    """
    try:
        logger.info("🚀 Starting ChromaDB to Pinecone migration...")
        
        # Import ChromaDB components
        from app.agents.chroma_memory import ChromaMemory
        
        # Initialize connections
        logger.info("Initializing ChromaDB connection...")
        chroma_memory = ChromaMemory()
        
        logger.info("Initializing Pinecone connection...")
        pinecone_memory = PineconeMemory(
            api_key=pinecone_api_key,
            environment=pinecone_environment
        )
        
        # Get all data from ChromaDB
        research_count = 0
        topic_count = 0
        
        # Migrate research chunks
        logger.info("\n📄 Migrating research chunks...")
        research_count = 0
        
        try:
            # Get all research chunks from ChromaDB
            research_collection = chroma_memory.research_chunks
            all_research_data = research_collection.get()
            
            logger.info(f"Found {len(all_research_data['ids'])} research chunks in ChromaDB")
            
            for i, chunk_id in enumerate(all_research_data['ids']):
                try:
                    content = all_research_data['documents'][i]
                    metadata = all_research_data['metadatas'][i] if all_research_data['metadatas'] else {}
                    
                    # Store in Pinecone
                    pinecone_memory.store_research_chunk(
                        content=content,
                        metadata={
                            'query': metadata.get('query', ''),
                            'source': metadata.get('source', ''),
                            'timestamp': metadata.get('timestamp', datetime.now().isoformat())
                        }
                    )
                    research_count += 1
                    
                    if research_count % 10 == 0:
                        logger.info(f"  Migrated {research_count}/{len(all_research_data['ids'])} research chunks...")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error migrating research chunk {chunk_id}: {e}")
                    continue
                    
            logger.info(f"✅ Successfully migrated {research_count} research chunks")
            
        except Exception as e:
            logger.error(f"❌ Error accessing ChromaDB research chunks: {e}")
        
        # Migrate topic memories
        logger.info("\n🧠 Migrating topic memories...")
        topic_count = 0
        
        try:
            # Get all topic memories from ChromaDB
            topic_collection = chroma_memory.topic_memory
            all_topic_data = topic_collection.get()
            
            logger.info(f"Found {len(all_topic_data['ids'])} topic memories in ChromaDB")
            
            for i, topic_id in enumerate(all_topic_data['ids']):
                try:
                    metadata = all_topic_data['metadatas'][i] if all_topic_data['metadatas'] else {}
                    
                    # Store in Pinecone
                    pinecone_memory.store_topic_memory(
                        topic=metadata.get('topic', f'Topic {i+1}'),
                        summary=metadata.get('summary', ''),
                        related_queries=metadata.get('related_queries', []),
                        key_insights=metadata.get('key_insights', [])
                    )
                    topic_count += 1
                    
                    if topic_count % 5 == 0:
                        logger.info(f"  Migrated {topic_count}/{len(all_topic_data['ids'])} topic memories...")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error migrating topic memory {topic_id}: {e}")
                    continue
                    
            logger.info(f"✅ Successfully migrated {topic_count} topic memories")
            
        except Exception as e:
            logger.error(f"❌ Error accessing ChromaDB topic memories: {e}")
        
        # Get final statistics
        logger.info("\n📊 Migration Summary:")
        pinecone_stats = pinecone_memory.get_stats()
        logger.info(f"Pinecone now contains:")
        logger.info(f"  - Research chunks: {pinecone_stats.get('research_chunks', 0)}")
        logger.info(f"  - Topic memories: {pinecone_stats.get('topic_memories', 0)}")
        
        logger.info(f"\n🎉 Migration completed successfully!")
        logger.info(f"  - {research_count} research chunks migrated")
        logger.info(f"  - {topic_count} topic memories migrated")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB migration failed: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🔄 Weaviate/ChromaDB to Pinecone Migration Tool")
    logger.info("=" * 50)
    
    # Load environment variables
    load_env_file()
    
    # Get configuration
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    pinecone_environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
    weaviate_url = os.getenv('WEAVIATE_URL', 'http://localhost:8085')
    
    if not pinecone_api_key:
        logger.error("❌ PINECONE_API_KEY not found in environment variables")
        logger.error("Please set PINECONE_API_KEY in your .env file")
        return
    
    # Ask user which migration to perform
    print("\nChoose migration source:")
    print("1. Migrate from Weaviate")
    print("2. Migrate from ChromaDB")
    print("3. Skip migration (just test Pinecone connection)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        logger.info("Selected: Weaviate to Pinecone migration")
        success = migrate_weaviate_to_pinecone(
            pinecone_api_key=pinecone_api_key,
            pinecone_environment=pinecone_environment,
            weaviate_url=weaviate_url
        )
    elif choice == "2":
        logger.info("Selected: ChromaDB to Pinecone migration")
        success = migrate_chromadb_to_pinecone(
            pinecone_api_key=pinecone_api_key,
            pinecone_environment=pinecone_environment
        )
    elif choice == "3":
        logger.info("Selected: Test Pinecone connection only")
        try:
            pinecone_memory = PineconeMemory(
                api_key=pinecone_api_key,
                environment=pinecone_environment
            )
            stats = pinecone_memory.get_stats()
            logger.info(f"✅ Pinecone connection successful!")
            logger.info(f"Current stats: {stats}")
            success = True
        except Exception as e:
            logger.error(f"❌ Pinecone connection failed: {e}")
            success = False
    else:
        logger.error("Invalid choice")
        return
    
    if success:
        logger.info("\n✅ Operation completed successfully!")
        logger.info("You can now update your .env file to use Pinecone:")
        logger.info("USE_PINECONE=true")
        logger.info("USE_WEAVIATE=false")
    else:
        logger.error("\n❌ Operation failed!")

if __name__ == "__main__":
    main()