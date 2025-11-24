"""
Document model for the RAG backend system.
"""

from typing import Optional
from datetime import datetime
import uuid


class Document:
    """Represents a single document that has been indexed."""

    def __init__(
        self,
        collection_id: str,
        file_path: str,
        title: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a Document.

        Args:
            collection_id: Reference to the DocumentCollection
            file_path: Path to the original document file
            title: Title of the document (extracted from metadata or filename)
            id: Unique identifier for the document (generated if not provided)
            created_at: Timestamp when the document was indexed
            updated_at: Timestamp when the document was last updated
        """
        self.id = id or str(uuid.uuid4())
        self.collection_id = collection_id
        self.file_path = file_path
        self.title = title or self._extract_title_from_path(file_path)
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def _extract_title_from_path(self, file_path: str) -> str:
        """
        Extract title from file path.

        Args:
            file_path: Path to the file

        Returns:
            Extracted title
        """
        import os
        filename = os.path.basename(file_path)
        name, _ = os.path.splitext(filename)
        return name.replace('_', ' ').replace('-', ' ').title()

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the Document to a dictionary.

        Returns:
            Dictionary representation of the Document
        """
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "file_path": self.file_path,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        """
        Create a Document from a dictionary.

        Args:
            data: Dictionary representation of the Document

        Returns:
            Document instance
        """
        return cls(
            id=data["id"],
            collection_id=data["collection_id"],
            file_path=data["file_path"],
            title=data["title"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    def __str__(self) -> str:
        """String representation of the Document."""
        return f"Document(id={self.id}, title={self.title})"

    def __repr__(self) -> str:
        """Detailed string representation of the Document."""
        return f"Document(id={self.id}, collection_id={self.collection_id}, title={self.title}, file_path={self.file_path})"