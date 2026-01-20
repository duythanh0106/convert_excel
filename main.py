import os
import sys

app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

from app.main import app

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    reload = os.getenv("APP_RELOAD", "true").lower() == "true"
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║   Universal File Converter v3.0.0        ║
    ║   UrBox Guideline Template System       ║
    ║                                          ║
    ║   * Starting server...                   ║
    ║   * http://{host}:{port}                 ║
    ╚══════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
