"""Answer generation service for generating responses to user questions."""

from typing import List, Dict, Any, Optional
from src.models.conversation import Conversation
from src.services.generation.prompt_assembler import prompt_assembler
from src.services.generation.llm_client import llm_client_service
from src.services.retrieval.orchestrator import search_orchestrator
from src.lib.logging_config import logger, LLMError


class AnswerGenerator:
    """Service for generating answers to user questions based on document context."""

    def __init__(self):
        """Initialize the answer generator."""
        pass

    def generate_answer(self, conversation: Conversation, user_message: str,
                       document_name: str) -> str:
        """
        Generate an answer to a user question based on document context.

        Args:
            conversation (Conversation): The conversation object
            user_message (str): The user's message
            document_name (str): Name of the document to search in

        Returns:
            str: The generated answer

        Raises:
            LLMError: If there's an error with the LLM service
        """
        try:
            logger.info(f"Generating answer for conversation {conversation.id}")

            # Step 1: Retrieve relevant context
            logger.info("Retrieving relevant context")
            retrieved_context = search_orchestrator.search(
                document_name=document_name,
                query_text=user_message,
                top_k=3,
                expand_query=True,
                rerank=True
            )

            # Step 2: Assemble prompt
            logger.info("Assembling prompt")
            prompt = prompt_assembler.assemble_prompt(
                conversation=conversation,
                user_message=user_message,
                retrieved_context=retrieved_context
            )

            # Step 3: Generate response from LLM
            logger.info("Generating response from LLM")
            response = llm_client_service.generate_response(
                prompt=prompt,
                max_tokens=300,
                temperature=0.7
            )

            logger.info("Answer generated successfully")
            return response

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise LLMError(f"Failed to generate answer: {str(e)}")


# Global instance
answer_generator = AnswerGenerator()