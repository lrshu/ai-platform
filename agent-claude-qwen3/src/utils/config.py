"""
Configuration management utilities.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_config():
    """
    Get configuration from environment variables.
    """
    return {
        'QWEN_API_BASE': os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
        'QWEN_API_KEY': os.getenv('QWEN_API_KEY'),
        'MCP_SERVER': os.getenv('MCP_SERVER', 'http://127.0.0.1:9012/mcp'),
        'LANGSMITH_API_KEY': os.getenv('LANGSMITH_API_KEY'),
        'LANGSMITH_PROJECT': os.getenv('LANGSMITH_PROJECT', 'employee-onboarding'),
        'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///./onboarding.db'),
    }

def get_required_config(key):
    """
    Get a required configuration value or raise an exception if not found.
    """
    config = get_config()
    value = config.get(key)
    if not value:
        raise ValueError(f"Required configuration '{key}' not found in environment")
    return value