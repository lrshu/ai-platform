"""
Chunk model for the RAG system.
"""
from typing import Dict, Any, Optional, Union
from .base import BaseModel


class Chunk(BaseModel):
    """Represents a segment of document content with associated vector embedding and position information."""

    def __init__(
        self,
        document_id: str,
        content: str,
        position: int,
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Union[str, int, float]]] = None
    ):
        """Initialize chunk.

        Args:
            document_id: Reference to parent document
            content: The actual content of the chunk
            position: Position of chunk within document
            id: Optional unique identifier
            metadata: Additional chunk metadata (e.g., page number, section)
        """
        super().__init__(id)
        self.document_id = document_id
        self.content = content
        self.position = position
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary representation.

        Returns:
            Dictionary representation of the chunk
        """
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "position": self.position,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chunk':
        """Create chunk from dictionary representation.

        Args:
            data: Dictionary representation of the chunk

        Returns:
            Chunk instance
        """
        chunk = cls(
            document_id=data["document_id"],
            content=data["content"],
            position=data["position"],
            id=data["id"],
            metadata=data.get("metadata", {})
        )

        chunk.created_at = data.get("created_at") and datetime.fromisoformat(data["created_at"])
        chunk.updated_at = data.get("updated_at") and datetime.fromisoformat(data["updated_at"])

        return chunk

    def __str__(self) -> str:
        """String representation."""
        return f"Chunk(document_id='{self.document_id}', position={self.position}, content_length={len(self.content)})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Chunk(id='{self.id}', document_id='{self.document_id}', position={self.position}, content='{self.content[:50]}...')"