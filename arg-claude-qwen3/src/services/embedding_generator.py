"""
Embedding generation service for the RAG backend system.
"""

from typing import List
from dashscope import TextEmbedding
from src.lib.exceptions import EmbeddingGenerationError
from src.models.vector_embedding import VectorEmbedding
from src.lib.config import get_config
import logging
import traceback

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Service for generating vector embeddings for document chunks."""

    def __init__(self):
        """Initialize the EmbeddingGenerator with DashScope embeddings."""
        config = get_config()
        self.api_key = config.qwen_api_key
        self.model = TextEmbedding.Models.text_embedding_v4

    def generate_embeddings(self, chunk_ids: List[str], texts: List[str],
                          model_name: str = "text-embedding-v4") -> List[VectorEmbedding]:
        """
        Generate embeddings for a list of texts using DashScope embeddings.

        Args:
            chunk_ids: List of chunk IDs corresponding to the texts
            texts: List of text strings to embed
            model_name: Name of the embedding model to use

        Returns:
            List of VectorEmbedding objects

        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        if len(chunk_ids) != len(texts):
            raise ValueError("chunk_ids and texts must have the same length")

        if not texts:
            return []

        try:
            # Generate embeddings using DashScope embeddings
            print("texts", texts)
            response = TextEmbedding.call(
                model=self.model,
                input=texts,
                api_key=self.api_key
            )

            if response.status_code != 200:
                raise Exception(f"DashScope API error: {response.message}")

            # Extract embeddings from response
            embeddings = [item['embedding'] for item in response.output['embeddings']]

            # Create VectorEmbedding objects
            vector_embeddings = []
            for chunk_id, vector in zip(chunk_ids, embeddings):
                embedding = VectorEmbedding(
                    chunk_id=chunk_id,
                    vector=vector,
                    model_name=model_name
                )
                vector_embeddings.append(embedding)

            logger.info(f"Generated embeddings for {len(vector_embeddings)} chunks")
            return vector_embeddings

        except Exception as e:
            # print stack
            traceback.print_stack()
            logger.error(f"Failed to generate embeddings: {e}")
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {str(e)}")

    def generate_embedding(self, chunk_id: str, text: str,
                          model_name: str = "text-embedding-v4") -> VectorEmbedding:
        """
        Generate embedding for a single text using DashScope embeddings.

        Args:
            chunk_id: ID of the chunk being embedded
            text: Text string to embed
            model_name: Name of the embedding model to use

        Returns:
            VectorEmbedding object

        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        try:
            # Generate embedding using DashScope embeddings
            response = TextEmbedding.call(
                model=self.model,
                input=text,
                api_key=self.api_key
            )

            if response.status_code != 200:
                raise Exception(f"DashScope API error: {response.message}")

            # Extract embedding from response
            vector = response.output['embeddings'][0]['embedding']

            # Create VectorEmbedding object
            embedding = VectorEmbedding(
                chunk_id=chunk_id,
                vector=vector,
                model_name=model_name
            )

            logger.info(f"Generated embedding for chunk {chunk_id}")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding for chunk {chunk_id}: {e}")
            raise EmbeddingGenerationError(f"Failed to generate embedding: {str(e)}")


# Global embedding generator instance
_embedding_generator: EmbeddingGenerator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """
    Get the global embedding generator instance.

    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator