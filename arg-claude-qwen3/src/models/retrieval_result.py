"""
RetrievalResult model for the RAG backend system.
"""

from typing import Optional
from datetime import datetime
import uuid


class RetrievalResult:
    """Represents a document chunk identified as relevant to a query."""

    def __init__(
        self,
        query_id: str,
        chunk_id: str,
        relevance_score: float,
        rank: int,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a RetrievalResult.

        Args:
            query_id: Reference to the Query
            chunk_id: Reference to the DocumentChunk
            relevance_score: Score indicating relevance to the query (0.0 to 1.0)
            rank: Rank of this result in the result set
            id: Unique identifier for the result (generated if not provided)
            created_at: Timestamp when the result was generated
        """
        if not 0.0 <= relevance_score <= 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")

        self.id = id or str(uuid.uuid4())
        self.query_id = query_id
        self.chunk_id = chunk_id
        self.relevance_score = relevance_score
        self.rank = rank
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the RetrievalResult to a dictionary.

        Returns:
            Dictionary representation of the RetrievalResult
        """
        return {
            "id": self.id,
            "query_id": self.query_id,
            "chunk_id": self.chunk_id,
            "relevance_score": self.relevance_score,
            "rank": self.rank,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RetrievalResult':
        """
        Create a RetrievalResult from a dictionary.

        Args:
            data: Dictionary representation of the RetrievalResult

        Returns:
            RetrievalResult instance
        """
        return cls(
            id=data["id"],
            query_id=data["query_id"],
            chunk_id=data["chunk_id"],
            relevance_score=data["relevance_score"],
            rank=data["rank"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    def __str__(self) -> str:
        """String representation of the RetrievalResult."""
        return f"RetrievalResult(id={self.id}, query_id={self.query_id}, score={self.relevance_score:.3f})"

    def __repr__(self) -> str:
        """Detailed string representation of the RetrievalResult."""
        return f"RetrievalResult(id={self.id}, query_id={self.query_id}, chunk_id={self.chunk_id}, score={self.relevance_score:.3f}, rank={self.rank})"