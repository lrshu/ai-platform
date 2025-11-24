"""
DocumentChunk model for the RAG backend system.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class DocumentChunk:
    """Represents a segment of text extracted from a document."""

    def __init__(
        self,
        document_id: str,
        content: str,
        position: int,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a DocumentChunk.

        Args:
            document_id: Reference to the Document
            content: The extracted text content of the chunk
            position: Position of the chunk within the document
            metadata: Additional metadata about the chunk
            id: Unique identifier for the chunk (generated if not provided)
            created_at: Timestamp when the chunk was created
        """
        self.id = id or str(uuid.uuid4())
        self.document_id = document_id
        self.content = content
        self.position = position
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the DocumentChunk to a dictionary.

        Returns:
            Dictionary representation of the DocumentChunk
        """
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "position": self.position,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentChunk':
        """
        Create a DocumentChunk from a dictionary.

        Args:
            data: Dictionary representation of the DocumentChunk

        Returns:
            DocumentChunk instance
        """
        return cls(
            id=data["id"],
            document_id=data["document_id"],
            content=data["content"],
            position=data["position"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    def __str__(self) -> str:
        """String representation of the DocumentChunk."""
        return f"DocumentChunk(id={self.id}, document_id={self.document_id}, position={self.position})"

    def __repr__(self) -> str:
        """Detailed string representation of the DocumentChunk."""
        return f"DocumentChunk(id={self.id}, document_id={self.document_id}, position={self.position}, content_length={len(self.content)})"