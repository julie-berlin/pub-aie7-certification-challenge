from typing import List
from .config_loader import config_loader


class AppSettings:
    """Application settings loaded from YAML config and environment variables"""
    
    def __init__(self):
        self._load_settings()
    
    def _load_settings(self):
        config_loader.load_all_configs()
        
        # API Settings
        app_config = config_loader.get_config("application")
        self.api_title = app_config["api"]["title"]
        self.api_version = app_config["api"]["version"] 
        self.api_description = app_config["api"]["description"]
        self.host = app_config["api"]["host"]
        self.port = app_config["api"]["port"]
        self.reload = app_config["api"]["reload"]
        
        # Security
        self.cors_origins = app_config["security"]["cors_origins"]
        
        # Environment
        self.environment = app_config["environment"]["name"]
        self.debug = app_config["environment"]["debug"]
        self.log_level = app_config["environment"]["log_level"]
        
        # AI Settings
        ai_config = config_loader.get_config("ai_models")
        self.openai_model = ai_config["openai"]["primary_model"]
        self.planning_model = ai_config["openai"]["planning_model"]
        self.embedding_model = ai_config["openai"]["embedding_model"]
        self.temperature = ai_config["openai"]["temperature"]
        self.max_tokens = ai_config["openai"]["max_tokens"]
        
        # Environment variables (required)
        self.openai_api_key = config_loader.get_env_or_config("OPENAI_API_KEY", "")
        self.tavily_api_key = config_loader.get_env_or_config("TAVILY_API_KEY", "")
        self.langchain_api_key = config_loader.get_env_or_config("LANGCHAIN_API_KEY", "")
        
        # LangSmith
        self.langchain_tracing = ai_config["langchain"]["tracing_enabled"]
        self.langchain_project = ai_config["langchain"]["project_name"]
        
        # Vector Database
        vector_config = config_loader.get_config("vector_database")
        self.qdrant_url = vector_config["qdrant"]["url"]
        self.collection_name = vector_config["qdrant"]["collection_name"]
        self.embedding_dimension = vector_config["qdrant"]["embedding_dimension"]
        self.retrieval_top_k = vector_config["retrieval"]["top_k"]
        
        # Data Processing
        data_config = config_loader.get_config("data_processing")
        self.data_directory = data_config["documents"]["data_directory"]
        self.ethics_pdf_filename = data_config["documents"]["ethics_pdf_filename"]
        self.chunk_size = data_config["text_splitting"]["chunk_size"]
        self.chunk_overlap = data_config["text_splitting"]["chunk_overlap"]
        
        # Agentic Workflow
        workflow_config = config_loader.get_config("agentic_workflow")
        self.parallel_search_enabled = workflow_config["parallel_search"]["enabled"]
        self.concurrent_searches = workflow_config["parallel_search"]["concurrent_searches"]
        self.planning_timeout = workflow_config["planning_agent"]["timeout_seconds"]


# Global settings instance
settings = AppSettings()