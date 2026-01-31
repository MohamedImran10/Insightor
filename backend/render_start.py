#!/usr/bin/env python3
"""
Render-optimized startup script
Binds to port immediately, initializes components lazily
Memory optimized for Render free tier (512MB limit)
"""
import os
import sys
import gc
from pathlib import Path

# Memory optimization for Render free tier
os.environ['MALLOC_TRIM_THRESHOLD_'] = '65536'
os.environ['PYTHONMALLOC'] = 'malloc'

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Force garbage collection before starting
    gc.collect()
    
    import uvicorn
    
    # Render provides PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting on {host}:{port}", flush=True)
    print(f"📊 Environment: PORT={port}", flush=True)
    print(f"📊 USE_PINECONE={os.environ.get('USE_PINECONE', 'not set')}", flush=True)
    print(f"💾 Memory optimization enabled for Render free tier", flush=True)
    
    # Use workers=1 and no reload for production
    # limit_max_requests helps with memory leaks
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        workers=1,
        timeout_keep_alive=60,
        limit_concurrency=5,
        limit_max_requests=100  # Restart worker after 100 requests to free memory
    )
