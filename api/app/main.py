import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .core.settings import settings
from .core.logging_config import configure_logging, get_logger
from .routers.chat_router import router as chat_router
from .routers.document_router import router as document_router

# Configure logging first
configure_logging()
logger = get_logger("app.main")

# Load environment variables
load_dotenv(".env.local")

# Set up LangSmith tracing
if settings.langchain_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing).lower()
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key

# Create FastAPI application
logger.info("Initializing FastAPI application", extra={
    "title": settings.api_title,
    "version": settings.api_version,
    "environment": settings.environment
})

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(document_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Federal Ethics Compliance Chatbot API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )