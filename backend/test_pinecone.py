"""
Simple Pinecone test script
Quick test to verify Pinecone connection and basic operations
"""

import os
import sys
from pathlib import Path

# Add the project root to the path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def load_env_file():
    """Load environment variables from .env file"""
    env_path = project_root / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value

def test_pinecone():
    """Test Pinecone connection"""
    print("🔍 Testing Pinecone connection...")
    
    # Load environment variables
    load_env_file()
    
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    pinecone_environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
    
    if not pinecone_api_key:
        print("❌ PINECONE_API_KEY not found in .env file")
        return False
    
    try:
        from app.agents.pinecone_memory import PineconeMemory
        
        print(f"✅ Connecting to Pinecone environment: {pinecone_environment}")
        
        # Initialize with minimal setup
        memory = PineconeMemory(
            api_key=pinecone_api_key,
            environment=pinecone_environment
        )
        
        # Test basic functionality
        print("✅ Pinecone connection successful!")
        
        # Get stats
        stats = memory.get_stats()
        print(f"📊 Pinecone Stats:")
        print(f"  - Research chunks: {stats.get('research_chunks', 0)}")
        print(f"  - Topic memories: {stats.get('topic_memories', 0)}")
        
        # Test storing a simple chunk
        test_id = memory.store_research_chunk(
            content="Test migration content",
            metadata={
                'query': 'test query',
                'source': 'migration test',
                'timestamp': '2026-01-09T20:00:00'
            }
        )
        print(f"✅ Test chunk stored with ID: {test_id}")
        
        # Test search
        results = memory.search_research_chunks("test migration", limit=1)
        print(f"✅ Search test successful - found {len(results)} results")
        
        print("\n🎉 Pinecone is working correctly!")
        print("Your application is ready to use Pinecone as the vector database.")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pinecone()
    if success:
        print("\n✅ Next step: Test your application with docker-compose up --build")
    else:
        print("\n❌ Please check your Pinecone API key and try again")