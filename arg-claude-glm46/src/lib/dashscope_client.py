"""DashScope API clients for embedding and LLM services."""

import os
import requests
from typing import List, Dict, Any
import json
from functools import lru_cache
import hashlib


class DashScopeEmbeddingClient:
    """Client for DashScope embedding services."""

    def __init__(self):
        """Initialize the DashScope embedding client."""
        self.api_base = os.getenv("QWEN_API_BASE")
        self.api_key = os.getenv("QWEN_API_KEY")
        self.embedding_model = "text-embedding-v4"

    @lru_cache(maxsize=1000)
    def _generate_single_embedding_cached(self, text_hash: str, text: str) -> tuple:
        """
        Generate a single embedding with caching based on text content.

        Args:
            text_hash (str): Hash of the text for cache key
            text (str): Text to generate embedding for

        Returns:
            tuple: Single embedding vector
        """
        # This method is cached based on the text_hash
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.embedding_model,
            "input": {
                "texts": [text]
            }
        }

        response = requests.post(
            f"{self.api_base}/embeddings",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            raise Exception(f"Embedding API error: {response.status_code} - {response.text}")

        result = response.json()
        return tuple(result["data"][0]["embedding"])

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts (List[str]): List of texts to generate embeddings for

        Returns:
            List[List[float]]: List of embedding vectors

        Raises:
            Exception: If there's an error generating embeddings
        """
        try:
            # For small lists, we can use caching
            if len(texts) <= 10:
                embeddings = []
                for text in texts:
                    text_hash = hashlib.md5(text.encode()).hexdigest()
                    embedding_tuple = self._generate_single_embedding_cached(text_hash, text)
                    embeddings.append(list(embedding_tuple))
                return embeddings
            else:
                # For large lists, use batch API call
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                data = {
                    "model": self.embedding_model,
                    "input": {
                        "texts": texts
                    }
                }

                response = requests.post(
                    f"{self.api_base}/embeddings",
                    headers=headers,
                    json=data
                )

                if response.status_code != 200:
                    raise Exception(f"Embedding API error: {response.status_code} - {response.text}")

                result = response.json()
                return [item["embedding"] for item in result["data"]]

        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")


class DashScopeLLMClient:
    """Client for DashScope LLM services."""

    def __init__(self):
        """Initialize the DashScope LLM client."""
        self.api_base = os.getenv("QWEN_API_BASE")
        self.api_key = os.getenv("QWEN_API_KEY")
        self.llm_model = "qwen-max"

    @lru_cache(maxsize=100)
    def _generate_completion_cached(self, prompt_hash: str, prompt: str, **kwargs) -> str:
        """
        Generate completion with caching based on prompt content.

        Args:
            prompt_hash (str): Hash of the prompt for cache key
            prompt (str): Input prompt
            **kwargs: Additional parameters for the LLM

        Returns:
            str: Generated completion
        """
        # This method is cached based on the prompt_hash
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Default parameters
        params = {
            "model": self.llm_model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        # Update with any additional parameters
        params.update(kwargs)

        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=params
        )

        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.status_code} - {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def generate_completion(self, prompt: str, **kwargs) -> str:
        """
        Generate completion using the LLM.

        Args:
            prompt (str): Input prompt
            **kwargs: Additional parameters for the LLM

        Returns:
            str: Generated completion

        Raises:
            Exception: If there's an error generating completion
        """
        try:
            # For simple prompts, we can use caching
            if len(prompt) < 500 and not kwargs:
                prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
                return self._generate_completion_cached(prompt_hash, prompt, **kwargs)
            else:
                # For complex prompts, make direct API call
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                # Default parameters
                params = {
                    "model": self.llm_model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }

                # Update with any additional parameters
                params.update(kwargs)

                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=params
                )

                if response.status_code != 200:
                    raise Exception(f"LLM API error: {response.status_code} - {response.text}")

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            raise Exception(f"Error generating completion: {str(e)}")


# Global client instances
embedding_client = DashScopeEmbeddingClient()
llm_client = DashScopeLLMClient()