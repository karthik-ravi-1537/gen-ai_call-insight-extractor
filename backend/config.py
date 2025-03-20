# config.py
import os
from typing import Dict, Any

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class BaseConfig:
    """Base configuration with common settings."""
    # API and service settings
    API_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Call Insight Extractor"
    DEBUG: bool = False

    # LLM settings
    LLM: str = os.getenv("LLM", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./call_insights.db")

    # Application settings
    MAX_TRANSCRIPT_LENGTH: int = 100000
    CORS_ORIGINS: list = [
        "*"  # Allow all origins for development; restrict in production
    ]


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG: bool = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG: bool = False
    # More restrictive CORS in production
    CORS_ORIGINS: list = [
        os.getenv("FRONTEND_URL", ""),
    ]


class TestConfig(BaseConfig):
    """Test configuration."""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test_call_insights.db"
    TESTING: bool = True


# Map environment names to config classes
config_by_name: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig,
}

# Get current environment or default to development
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

# Load the appropriate config
loaded_config = config_by_name[ENVIRONMENT]
