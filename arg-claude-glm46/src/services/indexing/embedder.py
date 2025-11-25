"""Embedding generation service for the indexing pipeline."""

from typing import List
from src.lib.dashscope_client import embedding_client
from src.lib.logging_config import logger, EmbeddingError


class Embedder:
    """Service for generating embeddings in the indexing pipeline."""

    def __init__(self):
        """Initialize the embedder."""
        pass

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts (List[str]): List of texts to generate embeddings for

        Returns:
            List[List[float]]: List of embedding vectors

        Raises:
            EmbeddingError: If there's an error generating embeddings
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")

            # Generate embeddings using DashScope client
            embeddings = embedding_client.generate_embeddings(texts)

            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise EmbeddingError(f"Failed to generate embeddings: {str(e)}")


# Global instance
embedder = Embedder()