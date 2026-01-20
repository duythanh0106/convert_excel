#!/usr/bin/env python3
"""
Universal File Converter - Entry Point
Version 3.0.0

This is the main entry point for running the FastAPI application.
The actual application code is in the app/ folder.
"""

import os
import sys

# Add the app directory to the path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Import and run the FastAPI app from app/main.py
from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    reload = os.getenv("APP_RELOAD", "true").lower() == "true"
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║   Universal File Converter v3.0.0        ║
    ║   UrBox Guideline Template System       ║
    ║                                          ║
    ║   ��� Starting server...                  ║
    ║   ��� http://{host}:{port}             ║
    ╚══════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
