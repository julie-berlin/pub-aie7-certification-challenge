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
from api.app.core.logging_config import configure_logging, get_logger
from api.app.utils.startup_utils import print_startup_info

# Configure logging
configure_logging()
logger = get_logger("app.startup")

if __name__ == "__main__":
    print_startup_info()
    
    logger.info("Starting FastAPI server from project root", extra={
        "host": settings.host,
        "port": settings.port,
        "docs_url": f"http://{settings.host}:{settings.port}/docs",
        "environment": settings.environment,
        "debug": settings.debug
    })
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )