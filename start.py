#!/usr/bin/env python3
"""
Railway deployment startup script.
Handles PORT environment variable properly for uvicorn.
"""
import os
import uvicorn

if __name__ == "__main__":
    # Railway provides PORT as an environment variable
    # Default to 8000 for local development
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        workers=1,
        access_log=True
    )
