"""Configuration module for the RAG backend system."""

import os
import dotenv


def load_env():
    """Load environment variables from .env file."""
    dotenv.load_dotenv()


# Load environment variables when module is imported
load_env()