"""
Abstract base class for text generation interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator


class ITextGenerator(ABC):
    """Abstract base class for text generation operations."""

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on a prompt.

        Args:
            prompt: The prompt to generate text from
            **kwargs: Additional parameters for generation (temperature, top_p, etc.)

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate text as a stream based on a prompt.

        Args:
            prompt: The prompt to generate text from
            **kwargs: Additional parameters for generation (temperature, top_p, etc.)

        Yields:
            Generated text chunks
        """
        pass

    @abstractmethod
    async def generate_hypothetical_document(self, query: str, **kwargs) -> str:
        """
        Generate a hypothetical document based on a query (HyDE).

        Args:
            query: The query to generate a hypothetical document for
            **kwargs: Additional parameters for generation

        Returns:
            Hypothetical document text
        """
        pass

    @abstractmethod
    async def expand_query(self, query: str, **kwargs) -> List[str]:
        """
        Expand a query into multiple sub-queries.

        Args:
            query: The query to expand
            **kwargs: Additional parameters for expansion

        Returns:
            List of expanded queries
        """
        pass