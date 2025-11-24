"""
Answer generation service for the RAG backend system.
"""

from typing import List, Dict, Any
from src.lib.llm_client import get_llm_client
from src.services.retrieval_service import get_retrieval_service
from src.lib.exceptions import LLMGenerationError
import logging

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Service for generating answers to questions based on retrieved content."""

    def __init__(self):
        """Initialize the AnswerGenerator."""
        self.llm_client = get_llm_client()
        self.retrieval_service = get_retrieval_service()

    def generate_answer(self, question: str, retrieved_content: List[Dict[str, Any]],
                       conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Generate an answer to a question based on retrieved content.

        Args:
            question: The question to answer
            retrieved_content: List of retrieved document chunks with metadata
            conversation_history: Optional conversation history

        Returns:
            Generated answer text

        Raises:
            LLMGenerationError: If answer generation fails
        """
        try:
            # Format retrieved content for the prompt
            content_text = self._format_retrieved_content(retrieved_content)

            # Create prompt for answer generation
            prompt = self._create_answer_prompt(question, content_text, conversation_history)

            # Generate answer using LLM
            answer = self.llm_client.generate_completion(
                prompt,
                temperature=0.7,
                max_tokens=1000
            )

            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer

        except Exception as e:
            logger.error(f"Failed to generate answer for question '{question}': {e}")
            raise LLMGenerationError(f"Failed to generate answer: {str(e)}")

    def _format_retrieved_content(self, retrieved_content: List[Dict[str, Any]]) -> str:
        """
        Format retrieved content for inclusion in the prompt.

        Args:
            retrieved_content: List of retrieved document chunks

        Returns:
            Formatted content string
        """
        if not retrieved_content:
            return "No relevant content found."

        formatted_chunks = []
        for i, chunk in enumerate(retrieved_content):
            content = chunk.get("content", "Content not available")
            source = chunk.get("source", "Unknown source")
            score = chunk.get("relevance_score", 0.0)

            formatted_chunk = f"[{i+1}] Source: {source} (Relevance: {score:.2f})\n{content}"
            formatted_chunks.append(formatted_chunk)

        return "\n\n---\n\n".join(formatted_chunks)

    def _create_answer_prompt(self, question: str, retrieved_content: str,
                            conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Create a prompt for answer generation.

        Args:
            question: The question to answer
            retrieved_content: Formatted retrieved content
            conversation_history: Optional conversation history

        Returns:
            Complete prompt string
        """
        prompt_parts = []

        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("Conversation History:")
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.capitalize()}: {content}")
            prompt_parts.append("")

        # Add instruction
        prompt_parts.append("Based on the following retrieved content, please answer the question.")
        prompt_parts.append("Be concise, accurate, and cite specific information from the content.")
        prompt_parts.append("If the content doesn't contain relevant information, say so.")
        prompt_parts.append("")

        # Add retrieved content
        prompt_parts.append("Retrieved Content:")
        prompt_parts.append(retrieved_content)
        prompt_parts.append("")

        # Add question
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append("Answer:")

        return "\n".join(prompt_parts)

    def generate_answer_with_citations(self, question: str, retrieved_content: List[Dict[str, Any]],
                                     conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate an answer with citations to source material.

        Args:
            question: The question to answer
            retrieved_content: List of retrieved document chunks with metadata
            conversation_history: Optional conversation history

        Returns:
            Dictionary with answer and citations
        """
        try:
            # Format retrieved content for the prompt
            content_text = self._format_retrieved_content(retrieved_content)

            # Create prompt for answer generation with citations
            prompt = self._create_citation_prompt(question, content_text, conversation_history)

            # Generate answer using LLM
            answer = self.llm_client.generate_completion(
                prompt,
                temperature=0.7,
                max_tokens=1200
            )

            # Extract citations (simplified - would be more sophisticated in real implementation)
            citations = self._extract_citations(retrieved_content)

            result = {
                "answer": answer,
                "citations": citations
            }

            logger.info(f"Generated answer with citations for question: {question[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Failed to generate answer with citations for question '{question}': {e}")
            raise LLMGenerationError(f"Failed to generate answer with citations: {str(e)}")

    def _create_citation_prompt(self, question: str, retrieved_content: str,
                              conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Create a prompt for answer generation with citations.

        Args:
            question: The question to answer
            retrieved_content: Formatted retrieved content
            conversation_history: Optional conversation history

        Returns:
            Complete prompt string
        """
        prompt_parts = []

        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("Conversation History:")
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.capitalize()}: {content}")
            prompt_parts.append("")

        # Add instruction
        prompt_parts.append("Based on the following retrieved content, please answer the question.")
        prompt_parts.append("Include citations to the source material in your answer using [1], [2], etc.")
        prompt_parts.append("Be concise, accurate, and cite specific information from the content.")
        prompt_parts.append("If the content doesn't contain relevant information, say so.")
        prompt_parts.append("")

        # Add retrieved content
        prompt_parts.append("Retrieved Content:")
        prompt_parts.append(retrieved_content)
        prompt_parts.append("")

        # Add question
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append("Answer with citations:")

        return "\n".join(prompt_parts)

    def _extract_citations(self, retrieved_content: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract citation information from retrieved content.

        Args:
            retrieved_content: List of retrieved document chunks

        Returns:
            List of citation dictionaries
        """
        citations = []
        for i, chunk in enumerate(retrieved_content):
            citation = {
                "number": i + 1,
                "source": chunk.get("source", "Unknown source"),
                "content": chunk.get("content", "")[:200] + "..." if len(chunk.get("content", "")) > 200 else chunk.get("content", "")
            }
            citations.append(citation)
        return citations


# Global answer generator instance
answer_generator = AnswerGenerator()


def get_answer_generator() -> AnswerGenerator:
    """
    Get the global answer generator instance.

    Returns:
        AnswerGenerator instance
    """
    return answer_generator