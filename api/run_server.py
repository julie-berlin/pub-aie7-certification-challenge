#!/usr/bin/env python3
"""
FastAPI server startup script for Federal Ethics Chatbot
"""
import uvicorn
from app.main import app
from app.core.settings import settings
from app.utils.startup_utils import print_startup_info

if __name__ == "__main__":
    print_startup_info()
    
    print(f"🚀 Starting server...")
    print(f"🔗 URL: http://{settings.host}:{settings.port}")
    print(f"📚 Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )