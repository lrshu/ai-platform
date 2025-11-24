"""
Query model for the RAG backend system.
"""

from typing import Optional
from datetime import datetime
import uuid


class Query:
    """Represents a user-provided question or search term."""

    def __init__(
        self,
        content: str,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a Query.

        Args:
            content: The query text
            id: Unique identifier for the query (generated if not provided)
            created_at: Timestamp when the query was submitted
        """
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the Query to a dictionary.

        Returns:
            Dictionary representation of the Query
        """
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Query':
        """
        Create a Query from a dictionary.

        Args:
            data: Dictionary representation of the Query

        Returns:
            Query instance
        """
        return cls(
            id=data["id"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    def __str__(self) -> str:
        """String representation of the Query."""
        return f"Query(id={self.id}, content={self.content[:50]}...)"

    def __repr__(self) -> str:
        """Detailed string representation of the Query."""
        return f"Query(id={self.id}, content={self.content}, created_at={self.created_at})"