"""
Qwen API client for language model interactions.
"""

import requests
from typing import List, Optional, Dict, Any
import logging
from src.lib.config import get_config

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for Qwen language model API."""

    def __init__(self):
        """Initialize LLM client with API configuration."""
        config = get_config()
        self.api_base = config.qwen_api_base
        self.api_key = config.qwen_api_key
        self.model = "qwen3-max"

        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is required")

    def generate_completion(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion from a prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters for the API call

        Returns:
            Generated text response
        """
        url = f"{self.api_base}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Default parameters
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["temperature", "max_tokens"]:
                payload[key] = value

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            result = data["choices"][0]["message"]["content"]

            logger.info("Generated completion from LLM")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate completion: {e}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            raise

    def generate_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat completion from a conversation history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for the API call

        Returns:
            Generated text response
        """
        url = f"{self.api_base}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Default parameters
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["temperature", "max_tokens"]:
                payload[key] = value

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            result = data["choices"][0]["message"]["content"]

            logger.info("Generated chat completion from LLM")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate chat completion: {e}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            raise


# Global LLM client instance
llm_client = LLMClient()


def get_llm_client() -> LLMClient:
    """
    Get the global LLM client instance.

    Returns:
        LLMClient instance
    """
    return llm_client