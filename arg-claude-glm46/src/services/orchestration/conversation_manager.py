"""Conversation manager for orchestrating the conversation flow."""

import uuid
import time
from datetime import datetime
from typing import List, Optional
from src.models.conversation import Conversation
from src.services.generation.answer_generator import answer_generator
from src.lib.logging_config import logger, LLMError
from src.lib.metrics import metrics_collector, TimingContext


class ConversationManager:
    """Manager for orchestrating the conversation flow."""

    def __init__(self):
        """Initialize the conversation manager."""
        pass

    def create_conversation(self, user_id: str, document_name: str,
                          title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation.

        Args:
            user_id (str): ID of the user
            document_name (str): Name of the document to converse about
            title (str, optional): Title for the conversation

        Returns:
            Conversation: The created conversation object

        Raises:
            ValueError: If input parameters are invalid
        """
        try:
            # Validate input parameters
            if not user_id or not isinstance(user_id, str):
                raise ValueError("User ID must be a non-empty string")

            if not document_name or not isinstance(document_name, str):
                raise ValueError("Document name must be a non-empty string")

            logger.info(f"Creating new conversation for user {user_id}")

            conversation = Conversation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                document_name=document_name,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                title=title or f"Conversation about {document_name}",
                is_active=True
            )

            logger.info(f"Conversation {conversation.id} created successfully")
            return conversation

        except ValueError as e:
            logger.error(f"Invalid input parameters: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def process_message(self, conversation: Conversation, user_message: str) -> str:
        """
        Process a user message and generate a response.

        Args:
            conversation (Conversation): The conversation object
            user_message (str): The user's message

        Returns:
            str: The system's response

        Raises:
            ValueError: If input parameters are invalid
            LLMError: If there's an error with the LLM service
        """
        start_time = time.time()
        context = {
            'conversation_id': conversation.id,
            'user_id': conversation.user_id,
            'document_name': conversation.document_name
        }

        try:
            # Validate input parameters
            if not conversation or not isinstance(conversation, Conversation):
                raise ValueError("Conversation must be a valid Conversation object")

            if not user_message or not isinstance(user_message, str):
                raise ValueError("User message must be a non-empty string")

            if not conversation.is_active:
                raise ValueError("Cannot process message for an inactive conversation")

            logger.info(f"Processing message for conversation {conversation.id}")

            # Generate answer using the answer generator
            with TimingContext(metrics_collector, "answer_generation", context):
                response = answer_generator.generate_answer(
                    conversation=conversation,
                    user_message=user_message,
                    document_name=conversation.document_name
                )

            # Update conversation timestamp
            conversation.updated_at = datetime.now()

            logger.info(f"Message processed successfully for conversation {conversation.id}")

            # Record overall message processing timing
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_timing("message_processing", duration_ms, context)

            return response

        except ValueError as e:
            logger.error(f"Invalid input parameters: {str(e)}")
            metrics_collector.record_counter("conversation_errors", 1, {"error_type": "ValueError", **context})
            raise
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            metrics_collector.record_counter("conversation_errors", 1, {"error_type": "Exception", **context})
            raise LLMError(f"Failed to process message: {str(e)}")

    def end_conversation(self, conversation: Conversation) -> None:
        """
        End a conversation.

        Args:
            conversation (Conversation): The conversation to end

        Raises:
            ValueError: If input parameters are invalid
        """
        try:
            # Validate input parameters
            if not conversation or not isinstance(conversation, Conversation):
                raise ValueError("Conversation must be a valid Conversation object")

            logger.info(f"Ending conversation {conversation.id}")

            conversation.is_active = False
            conversation.updated_at = datetime.now()

            logger.info(f"Conversation {conversation.id} ended successfully")

        except ValueError as e:
            logger.error(f"Invalid input parameters: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            raise


# Global instance
conversation_manager = ConversationManager()