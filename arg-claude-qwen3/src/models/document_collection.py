"""
DocumentCollection model for the RAG backend system.
"""

from typing import Optional
from datetime import datetime
import uuid


class DocumentCollection:
    """Represents a named grouping of related documents."""

    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a DocumentCollection.

        Args:
            name: User-provided name for the collection
            id: Unique identifier for the collection (generated if not provided)
            created_at: Timestamp when the collection was created
            updated_at: Timestamp when the collection was last updated
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the DocumentCollection to a dictionary.

        Returns:
            Dictionary representation of the DocumentCollection
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentCollection':
        """
        Create a DocumentCollection from a dictionary.

        Args:
            data: Dictionary representation of the DocumentCollection

        Returns:
            DocumentCollection instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    def __str__(self) -> str:
        """String representation of the DocumentCollection."""
        return f"DocumentCollection(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Detailed string representation of the DocumentCollection."""
        return f"DocumentCollection(id={self.id}, name={self.name}, created_at={self.created_at}, updated_at={self.updated_at})"