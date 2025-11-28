"""
Query model for the RAG system.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseModel


class Query(BaseModel):
    """User question that may be expanded or processed before retrieval."""

    def __init__(
        self,
        original_text: str,
        id: Optional[str] = None,
        expanded_text: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Initialize query.

        Args:
            original_text: Original user query
            id: Optional unique identifier
            expanded_text: Expanded query after preprocessing
            user_id: Identifier for user (optional)
        """
        super().__init__(id)
        self.original_text = original_text
        self.expanded_text = expanded_text or original_text
        self.user_id = user_id
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary representation.

        Returns:
            Dictionary representation of the query
        """
        return {
            "id": self.id,
            "original_text": self.original_text,
            "expanded_text": self.expanded_text,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Query':
        """Create query from dictionary representation.

        Args:
            data: Dictionary representation of the query

        Returns:
            Query instance
        """
        query = cls(
            original_text=data["original_text"],
            id=data["id"],
            expanded_text=data.get("expanded_text", data["original_text"]),
            user_id=data.get("user_id")
        )

        query.timestamp = datetime.fromisoformat(data["timestamp"])
        query.created_at = datetime.fromisoformat(data["created_at"])
        query.updated_at = datetime.fromisoformat(data["updated_at"])

        return query

    def expand_query(self, expanded_text: str) -> None:
        """Expand the query with additional text.

        Args:
            expanded_text: Expanded query text
        """
        self.expanded_text = expanded_text
        self.update_timestamp()

    def __str__(self) -> str:
        """String representation."""
        return f"Query(original='{self.original_text}', expanded='{self.expanded_text}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Query(id='{self.id}', original='{self.original_text}', expanded='{self.expanded_text}', user_id='{self.user_id}')"