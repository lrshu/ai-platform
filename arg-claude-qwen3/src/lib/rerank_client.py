"""
DashScope API client for reranking search results.
"""

import requests
from typing import List, Dict, Any
import logging
from src.lib.config import get_config

logger = logging.getLogger(__name__)


class RerankClient:
    """Client for DashScope reranking API."""

    def __init__(self):
        """Initialize rerank client with API configuration."""
        config = get_config()
        self.api_base = config.qwen_api_base
        self.api_key = config.qwen_api_key
        self.model = "dashscope-rerank"

        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is required")

    def rerank(self, query: str, documents: List[str]) -> List[Dict[str, Any]]:
        """
        Rerank documents based on their relevance to a query.

        Args:
            query: Search query
            documents: List of document texts to rerank

        Returns:
            List of reranked results with scores and indices
        """
        url = f"{self.api_base}/rerank"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "query": query,
            "documents": documents
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            results = data["results"]

            logger.info(f"Reranked {len(documents)} documents")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to rerank documents: {e}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            raise


# Global rerank client instance
rerank_client = RerankClient()


def get_rerank_client() -> RerankClient:
    """
    Get the global rerank client instance.

    Returns:
        RerankClient instance
    """
    return rerank_client