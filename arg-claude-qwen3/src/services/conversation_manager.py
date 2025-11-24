"""
Conversation context management service for the RAG backend system.
"""

from typing import List, Optional
from src.models.conversation_context import ConversationContext
from src.lib.database import get_db_connection
from src.lib.exceptions import ChatError
import logging

logger = logging.getLogger(__name__)


class ConversationManager:
    """Service for managing conversation context and history."""

    def __init__(self):
        """Initialize the ConversationManager."""
        self.db = get_db_connection()

    def add_conversation_entry(self, session_id: str, query_id: str, response: str) -> ConversationContext:
        """
        Add a new entry to the conversation history.

        Args:
            session_id: Identifier for the chat session
            query_id: Reference to the Query
            response: The generated response to the query

        Returns:
            ConversationContext object
        """
        try:
            conversation_entry = ConversationContext(
                session_id=session_id,
                query_id=query_id,
                response=response
            )

            # In a real implementation, this would save to the database
            logger.info(f"Added conversation entry for session {session_id}")
            return conversation_entry

        except Exception as e:
            logger.error(f"Failed to add conversation entry for session {session_id}: {e}")
            raise ChatError(f"Failed to add conversation entry: {str(e)}")

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ConversationContext]:
        """
        Get the conversation history for a session.

        Args:
            session_id: Identifier for the chat session
            limit: Maximum number of entries to return

        Returns:
            List of ConversationContext objects
        """
        try:
            # In a real implementation, this would query the database
            logger.info(f"Retrieved conversation history for session {session_id}")
            return []  # Placeholder - would return actual history in real implementation

        except Exception as e:
            logger.error(f"Failed to retrieve conversation history for session {session_id}: {e}")
            raise ChatError(f"Failed to retrieve conversation history: {str(e)}")

    def format_conversation_context(self, session_id: str, max_turns: int = 5) -> List[dict]:
        """
        Format conversation history for use in prompts.

        Args:
            session_id: Identifier for the chat session
            max_turns: Maximum number of conversation turns to include

        Returns:
            List of message dictionaries in the format {"role": "user/assistant", "content": "..."}
        """
        try:
            history = self.get_conversation_history(session_id, max_turns)

            # Format as message history for LLM
            messages = []
            for entry in history:
                # In a real implementation, we'd need to retrieve the original query text
                # For now, we'll just format what we have
                messages.append({
                    "role": "user",
                    "content": f"Previous query (ID: {entry.query_id})"
                })
                messages.append({
                    "role": "assistant",
                    "content": entry.response
                })

            logger.info(f"Formatted conversation context with {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"Failed to format conversation context for session {session_id}: {e}")
            return []  # Return empty context on failure

    def clear_conversation_history(self, session_id: str) -> None:
        """
        Clear the conversation history for a session.

        Args:
            session_id: Identifier for the chat session
        """
        try:
            # In a real implementation, this would delete from the database
            logger.info(f"Cleared conversation history for session {session_id}")

        except Exception as e:
            logger.error(f"Failed to clear conversation history for session {session_id}: {e}")
            raise ChatError(f"Failed to clear conversation history: {str(e)}")

    def get_session_summary(self, session_id: str) -> dict:
        """
        Get a summary of the conversation session.

        Args:
            session_id: Identifier for the chat session

        Returns:
            Dictionary with session summary information
        """
        try:
            history = self.get_conversation_history(session_id)

            summary = {
                "session_id": session_id,
                "total_turns": len(history),
                "first_message": history[0].created_at if history else None,
                "last_message": history[-1].created_at if history else None
            }

            logger.info(f"Generated session summary for {session_id}")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate session summary for session {session_id}: {e}")
            return {
                "session_id": session_id,
                "total_turns": 0,
                "error": str(e)
            }


# Global conversation manager instance
conversation_manager = ConversationManager()


def get_conversation_manager() -> ConversationManager:
    """
    Get the global conversation manager instance.

    Returns:
        ConversationManager instance
    """
    return conversation_manager