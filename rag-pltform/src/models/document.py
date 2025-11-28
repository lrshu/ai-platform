"""
Document model for the RAG system.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseModel


class DocumentStatus:
    """Document status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(BaseModel):
    """Represents a PDF document that has been parsed and indexed."""

    def __init__(
        self,
        name: str,
        file_path: str,
        id: Optional[str] = None,
        chunk_count: int = 0,
        status: str = DocumentStatus.PENDING
    ):
        """Initialize document.

        Args:
            name: User-provided name for the document collection
            file_path: Path to the original PDF file
            id: Optional unique identifier
            chunk_count: Number of chunks created from the document
            status: Indexing status
        """
        super().__init__(id)
        self.name = name
        self.file_path = file_path
        self.indexed_at: Optional[datetime] = None
        self.chunk_count = chunk_count
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation.

        Returns:
            Dictionary representation of the document
        """
        return {
            "id": self.id,
            "name": self.name,
            "file_path": self.file_path,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "chunk_count": self.chunk_count,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary representation.

        Args:
            data: Dictionary representation of the document

        Returns:
            Document instance
        """
        doc = cls(
            name=data["name"],
            file_path=data["file_path"],
            id=data["id"],
            chunk_count=data.get("chunk_count", 0),
            status=data.get("status", DocumentStatus.PENDING)
        )

        if data.get("indexed_at"):
            doc.indexed_at = datetime.fromisoformat(data["indexed_at"])

        doc.created_at = datetime.fromisoformat(data["created_at"])
        doc.updated_at = datetime.fromisoformat(data["updated_at"])

        return doc

    def mark_as_indexed(self) -> None:
        """Mark document as indexed."""
        self.indexed_at = datetime.now()
        self.status = DocumentStatus.COMPLETED
        self.update_timestamp()

    def mark_as_failed(self) -> None:
        """Mark document as failed during indexing."""
        self.status = DocumentStatus.FAILED
        self.update_timestamp()

    def __str__(self) -> str:
        """String representation."""
        return f"Document(name='{self.name}', file_path='{self.file_path}', status='{self.status}')"