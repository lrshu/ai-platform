"""LLM interaction service for communicating with the language model."""

from typing import Optional
from src.lib.dashscope_client import llm_client
from src.lib.logging_config import logger, LLMError


class LLMClientService:
    """Service for interacting with the language model."""

    def __init__(self):
        """Initialize the LLM client service."""
        pass

    def generate_response(self, prompt: str, max_tokens: int = 500,
                         temperature: float = 0.7) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt (str): The prompt to send to the LLM
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for generation (0.0 to 1.0)

        Returns:
            str: The generated response

        Raises:
            LLMError: If there's an error with the LLM service
        """
        try:
            logger.info("Generating response from LLM")
            logger.debug(f"Prompt: {prompt[:100]}...")  # Log first 100 chars of prompt

            response = llm_client.generate_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )

            logger.info("Response generated successfully from LLM")
            return response

        except Exception as e:
            logger.error(f"Error generating response from LLM: {str(e)}")
            raise LLMError(f"Failed to generate response from LLM: {str(e)}")

    def generate_embedding(self, text: str) -> Optional[list]:
        """
        Generate an embedding for the given text.

        Args:
            text (str): The text to generate an embedding for

        Returns:
            Optional[list]: The embedding vector, or None if failed

        Raises:
            LLMError: If there's an error with the embedding service
        """
        try:
            logger.info("Generating embedding from LLM")

            embedding = llm_client.generate_embedding(text)

            logger.info("Embedding generated successfully")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise LLMError(f"Failed to generate embedding: {str(e)}")


# Global instance
llm_client_service = LLMClientService()