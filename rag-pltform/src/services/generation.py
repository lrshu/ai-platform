"""
Generation service for creating responses to user queries.
"""
import logging
import time
from typing import List, Optional
from ..models.query import Query
from ..models.response import Response
from ..models.search_result import SearchResult
from ..models.chunk import Chunk
from ..lib.llm_client import QwenClient
from ..lib.exceptions import LLMError

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for generating responses to user queries."""

    def __init__(self, llm_client: Optional[QwenClient] = None):
        """Initialize generation service.

        Args:
            llm_client: LLM client for text generation (optional, will create default if not provided)
        """
        self.llm_client = llm_client or QwenClient()

    def generate_response(
        self,
        query: Query,
        search_results: List[SearchResult],
        chunk_contents: List[str],
        conversation_context: Optional[dict] = None
    ) -> Response:
        """Generate a response to a user query.

        Args:
            query: Query object
            search_results: List of SearchResult objects
            chunk_contents: List of chunk content strings corresponding to search results
            conversation_context: Optional conversation context

        Returns:
            Response object

        Raises:
            LLMError: If text generation fails
            ValueError: If inputs are invalid
        """
        start_time = time.time()
        logger.info("Generating response for query: %s", query.original_text)

        # Validate inputs
        if not query or not isinstance(query, Query):
            raise ValueError("Invalid query object")

        if len(search_results) != len(chunk_contents):
            raise ValueError("Mismatch between search results and chunk contents length")

        # Assemble prompt
        assemble_start = time.time()
        prompt = self._assemble_prompt(query, search_results, chunk_contents, conversation_context)
        assemble_duration = time.time() - assemble_start
        logger.debug("Prompt assembly completed in %.2f seconds", assemble_duration)

        # Generate response using LLM
        generation_start = time.time()
        try:
            generated_text = self.llm_client.generate_text(prompt, max_tokens=1000, temperature=0.7)
            generation_duration = time.time() - generation_start
            logger.info("Text generation completed in %.2f seconds", generation_duration)

            # Create response object
            response = Response(
                query_id=query.id,
                content=generated_text,
                model_used="qwen3-max"
                # tokens_used will be updated if we can get token count from LLM
            )

            total_duration = time.time() - start_time
            logger.info("Response generation completed in %.2f seconds", total_duration)

            return response

        except Exception as e:
            logger.error("Failed to generate response: %s", str(e))
            raise LLMError(f"Failed to generate response: {str(e)}")

    def _assemble_prompt(
        self,
        query: Query,
        search_results: List[SearchResult],
        chunk_contents: List[str],
        conversation_context: Optional[dict] = None
    ) -> str:
        """Assemble prompt for LLM.

        Args:
            query: Query object
            search_results: List of SearchResult objects
            chunk_contents: List of chunk content strings
            conversation_context: Optional conversation context

        Returns:
            Assembled prompt string
        """
        # Start with instruction
        prompt_parts = [
            "You are a helpful assistant that answers questions based on provided document content.",
            "Answer the question concisely and accurately using only the information provided in the document excerpts below.",
            "If the information is not available in the provided content, say so clearly.",
            ""
        ]

        # Add conversation context if available
        if conversation_context:
            context_summary = "; ".join([f"{k}: {v}" for k, v in conversation_context.items() if isinstance(v, (str, int, float, bool))])
            if context_summary:
                prompt_parts.append(f"Context: {context_summary}")
                prompt_parts.append("")

        # Add the question
        prompt_parts.append(f"Question: {query.original_text}")
        prompt_parts.append("")

        # Add document excerpts
        prompt_parts.append("Relevant document excerpts:")
        for i, (result, content) in enumerate(zip(search_results, chunk_contents)):
            prompt_parts.append(f"[{i+1}] (Score: {result.score:.4f}, Method: {result.retrieval_method})")
            prompt_parts.append(content.strip())
            prompt_parts.append("")

        # Add instruction for answer
        prompt_parts.append("Answer:")

        return "\n".join(prompt_parts)

    def generate_follow_up_response(
        self,
        query: Query,
        search_results: List[SearchResult],
        chunk_contents: List[str],
        previous_responses: List[Response],
        conversation_context: Optional[dict] = None
    ) -> Response:
        """Generate a follow-up response in a conversation.

        Args:
            query: Query object
            search_results: List of SearchResult objects
            chunk_contents: List of chunk content strings
            previous_responses: List of previous Response objects
            conversation_context: Optional conversation context

        Returns:
            Response object

        Raises:
            LLMError: If text generation fails
            ValueError: If inputs are invalid
        """
        start_time = time.time()
        logger.info("Generating follow-up response for query: %s", query.original_text)

        # Validate inputs
        if not query or not isinstance(query, Query):
            raise ValueError("Invalid query object")

        if len(search_results) != len(chunk_contents):
            raise ValueError("Mismatch between search results and chunk contents length")

        # Assemble prompt with conversation history
        assemble_start = time.time()
        prompt = self._assemble_follow_up_prompt(
            query, search_results, chunk_contents, previous_responses, conversation_context
        )
        assemble_duration = time.time() - assemble_start
        logger.debug("Follow-up prompt assembly completed in %.2f seconds", assemble_duration)

        # Generate response using LLM
        generation_start = time.time()
        try:
            generated_text = self.llm_client.generate_text(prompt, max_tokens=1000, temperature=0.7)
            generation_duration = time.time() - generation_start
            logger.info("Follow-up text generation completed in %.2f seconds", generation_duration)

            # Create response object
            response = Response(
                query_id=query.id,
                content=generated_text,
                model_used="qwen3-max"
                # tokens_used will be updated if we can get token count from LLM
            )

            total_duration = time.time() - start_time
            logger.info("Follow-up response generation completed in %.2f seconds", total_duration)

            return response

        except Exception as e:
            logger.error("Failed to generate follow-up response: %s", str(e))
            raise LLMError(f"Failed to generate follow-up response: {str(e)}")

    def _assemble_follow_up_prompt(
        self,
        query: Query,
        search_results: List[SearchResult],
        chunk_contents: List[str],
        previous_responses: List[Response],
        conversation_context: Optional[dict] = None
    ) -> str:
        """Assemble prompt for follow-up response with conversation history.

        Args:
            query: Query object
            search_results: List of SearchResult objects
            chunk_contents: List of chunk content strings
            previous_responses: List of previous Response objects
            conversation_context: Optional conversation context

        Returns:
            Assembled prompt string
        """
        # Start with instruction
        prompt_parts = [
            "You are a helpful assistant engaged in a conversation about document content.",
            "Answer the question concisely and accurately using only the information provided in the document excerpts below.",
            "Consider the conversation history when formulating your response.",
            "If the information is not available in the provided content, say so clearly.",
            ""
        ]

        # Add conversation context if available
        if conversation_context:
            context_summary = "; ".join([f"{k}: {v}" for k, v in conversation_context.items() if isinstance(v, (str, int, float, bool))])
            if context_summary:
                prompt_parts.append(f"Context: {context_summary}")
                prompt_parts.append("")

        # Add conversation history
        if previous_responses:
            prompt_parts.append("Conversation history:")
            for i, response in enumerate(previous_responses[-3:]):  # Last 3 responses
                prompt_parts.append(f"Assistant: {response.content}")
            prompt_parts.append("")

        # Add the question
        prompt_parts.append(f"Question: {query.original_text}")
        prompt_parts.append("")

        # Add document excerpts
        prompt_parts.append("Relevant document excerpts:")
        for i, (result, content) in enumerate(zip(search_results, chunk_contents)):
            prompt_parts.append(f"[{i+1}] (Score: {result.score:.4f}, Method: {result.retrieval_method})")
            prompt_parts.append(content.strip())
            prompt_parts.append("")

        # Add instruction for answer
        prompt_parts.append("Answer:")

        return "\n".join(prompt_parts)