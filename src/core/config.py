"""Application configuration without pydantic-settings."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings using environment variables."""
    
    # Application settings
    APP_NAME: str = "Nha Trang Tourism Assistant API"
    APP_DESCRIPTION: str = "API for the Nha Trang Tourism Assistant chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # LLM Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    K_RESULTS: int = int(os.getenv("K_RESULTS", "2"))
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Search Settings
    DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "Nha Trang, Việt Nam")
    SEARCH_ENGINE: str = os.getenv("SEARCH_ENGINE", "google_maps")
    LANGUAGE: str = os.getenv("LANGUAGE", "vi")
    COUNTRY: str = os.getenv("COUNTRY", "vn")
    GOOGLE_DOMAIN: str = os.getenv("GOOGLE_DOMAIN", "google.com.vn")
    MAX_RESULTS: int = int(os.getenv("MAX_RESULTS", "2"))
    
    # Paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    PDF_PATH: str = os.getenv("PDF_PATH", "data/www-etrip4u-com-du-lich-thong-tin-tong-quat-ve-du-lich-nha-trang.pdf")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "faiss_index_openai_embeddings")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "logs")
    
    # Search API Keys (optional)
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        
        if not os.path.exists(cls.FAISS_INDEX_PATH):
            raise ValueError(f"FAISS index not found at: {cls.FAISS_INDEX_PATH}")
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (excluding sensitive data)."""
        print("=== Application Configuration ===")
        print(f"App Name: {cls.APP_NAME}")
        print(f"Version: {cls.APP_VERSION}")
        print(f"Debug: {cls.DEBUG}")
        print(f"Host: {cls.HOST}")
        print(f"Port: {cls.PORT}")
        print(f"LLM Model: {cls.LLM_MODEL}")
        print(f"Default Location: {cls.DEFAULT_LOCATION}")
        print(f"OpenAI API Key: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Missing'}")
        print(f"SerpAPI Key: {'✓ Set' if cls.SERPAPI_API_KEY else '✗ Missing'}")
        print("=" * 35)

# Global settings instance
settings = Settings()

# Validate on import (optional - remove if you prefer manual validation)
# settings.validate() 