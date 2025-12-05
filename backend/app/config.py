from pydantic_settings import BaseSettings
from typing import Optional


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
    
    # Qdrant Cloud
    qdrant_url: str = "http://localhost:6333"  # Default local, override with cloud URL
    qdrant_api_key: str = ""  # Required for cloud
    
    # Firebase
    firebase_credentials_path: Optional[str] = None  # Path to serviceAccountKey.json
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
