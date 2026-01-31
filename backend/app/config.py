from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # API Keys
    google_api_key: str
    tavily_api_key: str
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = True
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    # Agent Settings
    tavily_include_answer: bool = True
    tavily_include_raw_content: bool = True
    tavily_max_results: int = 5
    
    # Vector Database
    use_pinecone: bool = False  # Set to True to use Pinecone
    pinecone_api_key: Optional[str] = None  # Pinecone API key
    pinecone_environment: str = "us-east-1-aws"  # Pinecone environment
    
    use_weaviate: bool = False  # Set to True to use Weaviate instead of ChromaDB
    weaviate_url: str = "http://localhost:8085"  # Weaviate server URL
    
    # Firebase
    firebase_credentials_path: Optional[str] = None  # Path to serviceAccountKey.json
    firebase_credentials_json: Optional[str] = None  # JSON string for production deployment
    firebase_enabled: bool = False  # Enable Firebase auth
    firebase_project_id: Optional[str] = None  # Firebase project ID
    
    # Memory Settings
    chunk_size: int = 512
    chunk_overlap: int = 100
    embedding_model: str = "all-MiniLM-L6-v2"
    rag_context_max_chars: int = 15000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """Get application settings singleton (cached for performance)"""
    return settings
