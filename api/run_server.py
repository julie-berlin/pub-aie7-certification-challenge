#!/usr/bin/env python3
"""
FastAPI server startup script for Federal Ethics Chatbot
"""
import uvicorn
from app.main import app
from app.core.settings import settings
from app.core.logging_config import configure_logging, get_logger
from app.utils.startup_utils import print_startup_info

# Configure logging
configure_logging()
logger = get_logger("app.startup")

if __name__ == "__main__":
    print_startup_info()
    
    logger.info("Starting FastAPI server", extra={
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