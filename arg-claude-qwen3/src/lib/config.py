"""
Environment configuration management for the RAG backend system.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the RAG backend system."""

    def __init__(self):
        """Initialize configuration with default values."""
        # Database configuration
        self.database_url = os.getenv("DATABASE_URL", "bolt://127.0.0.1:7687")
        self.database_user = os.getenv("DATABASE_USER", "")
        self.database_password = os.getenv("DATABASE_PASSWORD", "")

        # Qwen API configuration
        self.qwen_api_base = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.qwen_api_key = os.getenv("QWEN_API_KEY")

        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE")

        # Performance configuration
        self.max_chunk_size = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"

    @property
    def is_debug(self) -> bool:
        """Check if running in debug mode."""
        return os.getenv("DEBUG", "").lower() in ("1", "true", "yes")

    def validate(self) -> None:
        """Validate required configuration values."""
        if not self.qwen_api_key:
            raise ValueError("QWEN_API_KEY is required")

        # Add more validation as needed


# Global configuration instance
config = Config()


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance
    """
    return config