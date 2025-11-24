"""
ConversationContext model for the RAG backend system.
"""

from typing import Optional
from datetime import datetime
import uuid


class ConversationContext:
    """Represents the history of previous questions and answers in a chat session."""

    def __init__(
        self,
        session_id: str,
        query_id: str,
        response: str,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a ConversationContext.

        Args:
            session_id: Identifier for the chat session
            query_id: Reference to the Query
            response: The generated response to the query
            id: Unique identifier for the conversation (generated if not provided)
            created_at: Timestamp when the conversation entry was created
        """
        self.id = id or str(uuid.uuid4())
        self.session_id = session_id
        self.query_id = query_id
        self.response = response
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the ConversationContext to a dictionary.

        Returns:
            Dictionary representation of the ConversationContext
        """
        return {
            "id": self.id,
            "session_id": self.session_id,
            "query_id": self.query_id,
            "response": self.response,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationContext':
        """
        Create a ConversationContext from a dictionary.

        Args:
            data: Dictionary representation of the ConversationContext

        Returns:
            ConversationContext instance
        """
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            query_id=data["query_id"],
            response=data["response"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    def __str__(self) -> str:
        """String representation of the ConversationContext."""
        return f"ConversationContext(id={self.id}, session_id={self.session_id}, query_id={self.query_id})"

    def __repr__(self) -> str:
        """Detailed string representation of the ConversationContext."""
        return f"ConversationContext(id={self.id}, session_id={self.session_id}, query_id={self.query_id}, response_length={len(self.response)}, created_at={self.created_at})"