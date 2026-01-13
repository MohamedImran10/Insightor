#!/usr/bin/env python3
"""
Entry point for running the FastAPI backend server
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        import uvicorn
        from app.config import settings
        
        # Cloud Run injects PORT environment variable, use it if available
        port = int(os.environ.get("PORT", settings.backend_port))
        host = os.environ.get("HOST", settings.backend_host)
        
        logger.info("🚀 Starting Insightor Backend")
        logger.info(f"🌐 Server will run on http://{host}:{port}")
        logger.info(f"📚 API Docs available at http://{host}:{port}/docs")
        
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,  # Disable reload in production
            log_level="info"
        )
    except KeyError as e:
        logger.error(f"❌ Missing environment variable: {str(e)}")
        logger.error("Please set up your .env file using .env.example as a template")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}", exc_info=True)
        sys.exit(1)
