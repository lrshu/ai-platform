"""
Qwen API client for LLM operations.
"""
import openai
from typing import List, Optional, Dict, Any
import logging
from .config import config
from .exceptions import LLMError

logger = logging.getLogger(__name__)


class QwenClient:
    """Client for interacting with Qwen models via DashScope API."""

    def __init__(self):
        """Initialize Qwen client."""
        self.client = openai.OpenAI(
            base_url=config.QWEN_API_BASE,
            api_key=config.QWEN_API_KEY
        )
        self.embedding_model = "text-embedding-v4"
        self.generation_model = "qwen3-max"

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Text to generate embedding for

        Returns:
            List of floats representing the embedding

        Raises:
            LLMError: If embedding generation fails
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Failed to generate embedding: %s", str(e))
            raise LLMError(f"Failed to generate embedding: {str(e)}")

    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text response from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text response

        Raises:
            LLMError: If text generation fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.generation_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Failed to generate text: %s", str(e))
            raise LLMError(f"Failed to generate text: {str(e)}")

    def rerank(self, query: str, documents: List[str]) -> List[Dict[str, Any]]:
        """Rerank documents based on relevance to query.

        Args:
            query: Query text
            documents: List of document texts to rerank

        Returns:
            List of dictionaries with 'index' and 'relevance_score' keys

        Raises:
            LLMError: If reranking fails
        """
        try:
            # For now, we'll implement a simple placeholder
            # In a real implementation, this would call the DashScope rerank API
            logger.warning("Rerank functionality is not fully implemented yet")

            # Return a simple ranking based on document length as placeholder
            ranked_docs = []
            for i, doc in enumerate(documents):
                ranked_docs.append({
                    "index": i,
                    "relevance_score": len(doc)  # Placeholder score
                })

            # Sort by relevance score (descending)
            ranked_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
            return ranked_docs
        except Exception as e:
            logger.error("Failed to rerank documents: %s", str(e))
            raise LLMError(f"Failed to rerank documents: {str(e)}")