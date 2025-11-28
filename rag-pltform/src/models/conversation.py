"""
Conversation model for the RAG system.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base import BaseModel


class Conversation(BaseModel):
    """Series of related queries and responses with shared context."""

    def __init__(
        self,
        session_id: str,
        id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize conversation.

        Args:
            session_id: Identifier for user session
            id: Optional unique identifier
            context: Shared context between queries
        """
        super().__init__(id)
        self.session_id = session_id
        self.context = context or {}
        self.started_at = datetime.now()
        self.last_activity = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary representation.

        Returns:
            Dictionary representation of the conversation
        """
        return {
            "id": self.id,
            "session_id": self.session_id,
            "context": self.context,
            "started_at": self.started_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary representation.

        Args:
            data: Dictionary representation of the conversation

        Returns:
            Conversation instance
        """
        conversation = cls(
            session_id=data["session_id"],
            id=data["id"],
            context=data.get("context", {})
        )

        conversation.started_at = datetime.fromisoformat(data["started_at"])
        conversation.last_activity = datetime.fromisoformat(data["last_activity"])
        conversation.created_at = datetime.fromisoformat(data["created_at"])
        conversation.updated_at = datetime.fromisoformat(data["updated_at"])

        return conversation

    def update_context(self, new_context: Dict[str, Any]) -> None:
        """Update conversation context.

        Args:
            new_context: New context to merge with existing context
        """
        self.context.update(new_context)
        self.last_activity = datetime.now()
        self.update_timestamp()

    def update_last_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
        self.update_timestamp()

    def get_context_summary(self) -> str:
        """Get a summary of the conversation context.

        Returns:
            Summary of context as string
        """
        if not self.context:
            return "No context"

        # Create a simple summary of key context elements
        summary_parts = []
        for key, value in self.context.items():
            if isinstance(value, (str, int, float, bool)):
                summary_parts.append(f"{key}: {value}")
            else:
                summary_parts.append(f"{key}: [{type(value).__name__}]")

        return "; ".join(summary_parts)

    def __str__(self) -> str:
        """String representation."""
        return f"Conversation(session_id='{self.session_id}', context_keys={list(self.context.keys())})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Conversation(id='{self.id}', session_id='{self.session_id}', context_keys={list(self.context.keys())}, started_at='{self.started_at}')"