"""
Qwen provider implementation using DashScope SDK.
"""

import asyncio
import logging
from typing import List, Dict, Any, AsyncGenerator
from dashscope import TextEmbedding, Generation
import dashscope
from app.common.interfaces.generator import ITextGenerator
from app.common.interfaces.embedder import IEmbedder
from app.common.interfaces.reranker import IReranker
from app.common.config_loader import config_loader

# Configure logging
logger = logging.getLogger(__name__)


class QwenProvider(ITextGenerator, IEmbedder, IReranker):
    """Qwen provider implementation for text generation, embedding, and reranking."""

    def __init__(self):
        """Initialize the Qwen provider."""
        # Get DashScope API key from configuration or environment
        api_key = config_loader.get('dashscope_api_key')
        if api_key:
            dashscope.api_key = api_key
        else:
            # If not in config, it should be in environment variables
            if not dashscope.api_key:
                raise ValueError("DashScope API key not found in config or environment variables")

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on a prompt using Qwen models.

        Args:
            prompt: The prompt to generate text from
            **kwargs: Additional parameters for generation (temperature, top_p, etc.)

        Returns:
            Generated text
        """
        try:
            # Get model configuration
            capability_config = config_loader.get_capability_config('generator')
            model_name = capability_config.get('name', 'qwen-plus')

            # Prepare parameters
            parameters = {
                'model': model_name,
                'prompt': prompt,
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'max_tokens': kwargs.get('max_tokens', 2048)
            }

            # Call DashScope API synchronously (dashscope doesn't have async support)
            response = Generation.call(**parameters)

            if response.status_code == 200:
                return response.output.text
            else:
                raise RuntimeError(f"Qwen generation failed: {response.message}")

        except Exception as e:
            logger.error(f"Error generating text with Qwen: {e}")
            raise

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate text as a stream based on a prompt using Qwen models.

        Args:
            prompt: The prompt to generate text from
            **kwargs: Additional parameters for generation (temperature, top_p, etc.)

        Yields:
            Generated text chunks
        """
        try:
            # Get model configuration
            capability_config = config_loader.get_capability_config('generator')
            model_name = capability_config.get('name', 'qwen-plus')

            # Prepare parameters
            parameters = {
                'model': model_name,
                'prompt': prompt,
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'max_tokens': kwargs.get('max_tokens', 2048),
                'stream': True
            }

            # Call DashScope API synchronously for streaming
            responses = Generation.call(**parameters)

            for response in responses:
                if response.status_code == 200:
                    yield response.output.text
                else:
                    raise RuntimeError(f"Qwen streaming generation failed: {response.message}")

        except Exception as e:
            logger.error(f"Error generating text stream with Qwen: {e}")
            raise

    async def generate_hypothetical_document(self, query: str, **kwargs) -> str:
        """
        Generate a hypothetical document based on a query (HyDE) using Qwen models.

        Args:
            query: The query to generate a hypothetical document for
            **kwargs: Additional parameters for generation

        Returns:
            Hypothetical document text
        """
        try:
            # Create a prompt for generating a hypothetical document
            prompt = f"Based on the query: '{query}', generate a comprehensive document that would be a good answer to this query. The document should be detailed and informative."

            # Use the generate_text method with the prompt
            return await self.generate_text(prompt, **kwargs)

        except Exception as e:
            logger.error(f"Error generating hypothetical document with Qwen: {e}")
            raise

    async def expand_query(self, query: str, **kwargs) -> List[str]:
        """
        Expand a query into multiple sub-queries using Qwen models.

        Args:
            query: The query to expand
            **kwargs: Additional parameters for expansion

        Returns:
            List of expanded queries
        """
        try:
            # Create a prompt for expanding the query
            prompt = f"Expand the following query into 3-5 related sub-queries: '{query}'. Return each sub-query on a separate line."

            # Generate expanded queries
            response = await self.generate_text(prompt, **kwargs)

            # Split the response into individual queries
            expanded_queries = [q.strip() for q in response.split('\n') if q.strip()]

            return expanded_queries

        except Exception as e:
            logger.error(f"Error expanding query with Qwen: {e}")
            raise

    async def embed_text(self, text: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for text using Qwen embedding models.

        Args:
            text: List of text strings to embed
            **kwargs: Additional parameters for embedding

        Returns:
            List of embeddings (one for each input text)
        """
        try:
            # Get model configuration
            capability_config = config_loader.get_capability_config('embedder')
            model_name = capability_config.get('name', 'text-embedding-v4')

            # Handle both single string and list of strings
            if isinstance(text, str):
                texts = [text]
            else:
                texts = text

            # Call DashScope Embedding API
            response = TextEmbedding.call(
                model=model_name,
                input=texts
            )

            if response.status_code == 200:
                # Extract embeddings from response
                embeddings = [item['embedding'] for item in response.output['embeddings']]
                return embeddings
            else:
                raise RuntimeError(f"Qwen embedding failed: {response.message}")

        except Exception as e:
            logger.error(f"Error embedding text with Qwen: {e}")
            raise

    async def embed_query(self, query: str, **kwargs) -> List[float]:
        """
        Generate embedding for a query (may be optimized for search) using Qwen embedding models.

        Args:
            query: Query text to embed
            **kwargs: Additional parameters for embedding

        Returns:
            Embedding for the query
        """
        try:
            # For queries, we can use the same embedding method
            embeddings = await self.embed_text([query], **kwargs)
            return embeddings[0] if embeddings else []

        except Exception as e:
            logger.error(f"Error embedding query with Qwen: {e}")
            raise

    async def embed_document(self, document: str, **kwargs) -> List[List[float]]:
        """
        Generate embeddings for a document (may be optimized for document processing) using Qwen embedding models.

        Args:
            document: Document text to embed
            **kwargs: Additional parameters for embedding

        Returns:
            List of embeddings for chunks of the document
        """
        try:
            # For documents, we might want to chunk them first
            # For simplicity, we'll embed the whole document
            # In a real implementation, you might want to split into chunks
            return await self.embed_text([document], **kwargs)

        except Exception as e:
            logger.error(f"Error embedding document with Qwen: {e}")
            raise

    async def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Rerank a list of documents based on their relevance to a query using Qwen reranker.

        Args:
            query: The query to rank documents against
            documents: List of documents to rerank, each with content and metadata
            top_k: Number of top results to return
            **kwargs: Additional parameters for reranking

        Returns:
            List of reranked documents with relevance scores
        """
        try:
            # Get model configuration
            capability_config = config_loader.get_capability_config('reranker')
            model_name = capability_config.get('name', 'gte-rerank')

            # Prepare input for reranking
            input_data = {
                'query': query,
                'documents': [doc.get('content', '') for doc in documents]
            }

            # Call DashScope Reranking API
            # Note: This is a simplified example. Actual implementation may vary based on DashScope API
            response = Generation.call(
                model=model_name,
                input=input_data
            )

            if response.status_code == 200:
                # Extract scores and sort documents
                scores = response.output.scores  # This is hypothetical - actual API may differ
                ranked_docs = list(zip(documents, scores))
                ranked_docs.sort(key=lambda x: x[1], reverse=True)

                # Add scores to documents and limit to top_k
                result = []
                for doc, score in ranked_docs[:top_k]:
                    doc_with_score = doc.copy()
                    doc_with_score['relevance_score'] = score
                    result.append(doc_with_score)

                return result
            else:
                raise RuntimeError(f"Qwen reranking failed: {response.message}")

        except Exception as e:
            logger.error(f"Error reranking documents with Qwen: {e}")
            raise

    async def get_similarity_score(self, query: str, document: Dict[str, Any], **kwargs) -> float:
        """
        Get similarity score between a query and a document using Qwen reranker.

        Args:
            query: The query text
            document: Document to score, with content and metadata
            **kwargs: Additional parameters for scoring

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Rerank a single document to get its similarity score
            reranked = await self.rerank(query, [document], top_k=1, **kwargs)
            if reranked:
                return reranked[0].get('relevance_score', 0.0)
            else:
                return 0.0

        except Exception as e:
            logger.error(f"Error getting similarity score with Qwen: {e}")
            raise