"""
Abstract base class for text embedding interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Union


class IEmbedder(ABC):
    """Abstract base class for text embedding operations."""

    @abstractmethod
    async def embed_text(self, text: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings for text.

        Args:
            text: Single text string or list of text strings to embed

        Returns:
            List of embeddings (one for each input text)
        """
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query (may be optimized for search).

        Args:
            query: Query text to embed

        Returns:
            Embedding for the query
        """
        pass

    @abstractmethod
    async def embed_document(self, document: str) -> List[List[float]]:
        """
        Generate embeddings for a document (may be optimized for document processing).

        Args:
            document: Document text to embed

        Returns:
            List of embeddings for chunks of the document
        """
        pass