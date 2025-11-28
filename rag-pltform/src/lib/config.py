"""
Configuration management module.
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    def __init__(self):
        """Initialize configuration."""
        self._load_environment_variables()

    def _load_environment_variables(self) -> None:
        """Load environment variables."""
        # Qwen Configuration
        self.QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")

        # Memgraph Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "bolt://127.0.0.1:7687")
        self.DATABASE_USER = os.getenv("DATABASE_USER", "")
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")

    @property
    def qwen_api_key(self) -> str:
        """Get Qwen API key."""
        return self.QWEN_API_KEY

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.DATABASE_URL

    @property
    def database_user(self) -> str:
        """Get database user."""
        return self.DATABASE_USER

    @property
    def database_password(self) -> str:
        """Get database password."""
        return self.DATABASE_PASSWORD

    def validate(self) -> None:
        """Validate required configuration."""
        missing_vars = []

        if not self.QWEN_API_KEY:
            missing_vars.append("QWEN_API_KEY")

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Global configuration instance
config = Config()