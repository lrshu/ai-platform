"""Prompt assembly service for generating prompts for the LLM."""

from typing import List, Dict, Any, Optional
from src.models.conversation import Conversation
from src.lib.logging_config import logger


class PromptAssembler:
    """Service for assembling prompts for the LLM based on conversation context."""

    def __init__(self):
        """Initialize the prompt assembler."""
        pass

    def assemble_prompt(self, conversation: Conversation, user_message: str,
                       retrieved_context: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Assemble a prompt for the LLM based on conversation history and context.

        Args:
            conversation (Conversation): The conversation object
            user_message (str): The user's message
            retrieved_context (List[Dict[str, Any]], optional): Retrieved context from search

        Returns:
            str: The assembled prompt for the LLM
        """
        try:
            logger.info(f"Assembling prompt for conversation {conversation.id}")

            # Start with system instructions
            prompt = self._get_system_instructions(conversation.document_name)

            # Add conversation history if available
            # For simplicity, we'll include the last 3 turns
            prompt += self._add_conversation_history(conversation)

            # Add retrieved context if available
            if retrieved_context:
                prompt += self._add_retrieved_context(retrieved_context)

            # Add the current user message
            prompt += f"\nUser: {user_message}\n\nAssistant:"

            logger.info("Prompt assembled successfully")
            return prompt

        except Exception as e:
            logger.error(f"Error assembling prompt: {str(e)}")
            # Fallback to a simple prompt
            return f"Answer the following question based on the document context:\n\n{user_message}"

    def _get_system_instructions(self, document_name: str) -> str:
        """Get the system instructions for the prompt."""
        return f"""You are a helpful assistant that answers questions based on the document: {document_name}.
Provide accurate and concise answers based on the given context. If the context doesn't contain enough information to answer the question, say so."""

    def _add_conversation_history(self, conversation: Conversation) -> str:
        """Add conversation history to the prompt."""
        # In a real implementation, this would fetch actual conversation turns
        # For now, we'll return an empty string as a placeholder
        return "\n\nPrevious conversation:\n"

    def _add_retrieved_context(self, retrieved_context: List[Dict[str, Any]]) -> str:
        """Add retrieved context to the prompt."""
        if not retrieved_context:
            return ""

        context_text = "\n\nRelevant document context:\n"
        for i, ctx in enumerate(retrieved_context[:3]):  # Limit to top 3 contexts
            content = ctx.get('content', '')
            if content:
                context_text += f"{i+1}. {content}\n"

        return context_text


# Global instance
prompt_assembler = PromptAssembler()