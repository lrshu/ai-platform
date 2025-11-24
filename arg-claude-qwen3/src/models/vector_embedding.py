"""
VectorEmbedding model for the RAG backend system.
"""

from typing import Optional, List
from datetime import datetime
import uuid


class VectorEmbedding:
    """Represents the numerical vector representation of a document chunk."""

    def __init__(
        self,
        chunk_id: str,
        vector: List[float],
        model_name: str = "text-embedding-v4",
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a VectorEmbedding.

        Args:
            chunk_id: Reference to the DocumentChunk
            vector: The vector embedding values
            model_name: Name of the model used to generate the embedding
            id: Unique identifier for the embedding (generated if not provided)
            created_at: Timestamp when the embedding was generated
        """
        self.id = id or str(uuid.uuid4())
        self.chunk_id = chunk_id
        self.vector = vector
        self.model_name = model_name
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the VectorEmbedding to a dictionary.

        Returns:
            Dictionary representation of the VectorEmbedding
        """
        return {
            "id": self.id,
            "chunk_id": self.chunk_id,
            "vector": self.vector,
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VectorEmbedding':
        """
        Create a VectorEmbedding from a dictionary.

        Args:
            data: Dictionary representation of the VectorEmbedding

        Returns:
            VectorEmbedding instance
        """
        return cls(
            id=data["id"],
            chunk_id=data["chunk_id"],
            vector=data["vector"],
            model_name=data["model_name"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    def __str__(self) -> str:
        """String representation of the VectorEmbedding."""
        return f"VectorEmbedding(id={self.id}, chunk_id={self.chunk_id}, model_name={self.model_name})"

    def __repr__(self) -> str:
        """Detailed string representation of the VectorEmbedding."""
        return f"VectorEmbedding(id={self.id}, chunk_id={self.chunk_id}, model_name={self.model_name}, vector_length={len(self.vector)})"