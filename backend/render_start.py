#!/usr/bin/env python3
"""
Render-optimized startup script
Binds to port immediately, initializes components lazily
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    
    # Render provides PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting on {host}:{port}", flush=True)
    print(f"📊 Environment: PORT={port}", flush=True)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
            workers=1,
            timeout_keep_alive=30
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
