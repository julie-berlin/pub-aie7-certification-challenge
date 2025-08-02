#!/usr/bin/env python3
"""
Start FastAPI backend from project root
"""
import sys
import os
sys.path.append('api')

import uvicorn
from api.app.main import app
from api.app.core.settings import settings
from api.app.utils.startup_utils import print_startup_info

if __name__ == "__main__":
    print_startup_info()
    
    print(f"🚀 Starting server from project root...")
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