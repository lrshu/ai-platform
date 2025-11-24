"""
Qwen API client for generating text embeddings.
"""

import requests
from typing import List, Optional
import logging
from src.lib.config import get_config

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client for Qwen text embedding API."""

    def __init__(self):
        """Initialize embedding client with API configuration."""
        config = get_config()
        self.api_base = config.qwen_api_base
        self.api_key = config.qwen_api_key
        self.model = "text-embedding-v4"

        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is required")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        url = f"{self.api_base}/embeddings"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": texts
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]

            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0]


# Global embedding client instance
embedding_client = EmbeddingClient()


def get_embedding_client() -> EmbeddingClient:
    """
    Get the global embedding client instance.

    Returns:
        EmbeddingClient instance
    """
    return embedding_client