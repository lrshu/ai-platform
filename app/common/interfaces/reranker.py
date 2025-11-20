"""
Abstract base class for result reranking interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IReranker(ABC):
    """Abstract base class for result reranking operations."""

    @abstractmethod
    async def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Rerank a list of documents based on their relevance to a query.

        Args:
            query: The query to rank documents against
            documents: List of documents to rerank, each with content and metadata
            top_k: Number of top results to return

        Returns:
            List of reranked documents with relevance scores
        """
        pass

    @abstractmethod
    async def get_similarity_score(self, query: str, document: Dict[str, Any]) -> float:
        """
        Get similarity score between a query and a document.

        Args:
            query: The query text
            document: Document to score, with content and metadata

        Returns:
            Similarity score between 0 and 1
        """
        pass