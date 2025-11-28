"""
SearchResult model for the RAG system.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseModel


class SearchResult(BaseModel):
    """Retrieved document chunks with relevance scores and metadata."""

    def __init__(
        self,
        query_id: str,
        chunk_id: str,
        score: float,
        rank: int,
        retrieval_method: str = "vector",
        id: Optional[str] = None
    ):
        """Initialize search result.

        Args:
            query_id: Reference to originating query
            chunk_id: Reference to retrieved chunk
            score: Relevance score
            rank: Rank in result set
            retrieval_method: Method used (vector, keyword, graph)
            id: Optional unique identifier
        """
        super().__init__(id)
        self.query_id = query_id
        self.chunk_id = chunk_id
        self.score = score
        self.rank = rank
        self.retrieval_method = retrieval_method

    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary representation.

        Returns:
            Dictionary representation of the search result
        """
        return {
            "id": self.id,
            "query_id": self.query_id,
            "chunk_id": self.chunk_id,
            "score": self.score,
            "rank": self.rank,
            "retrieval_method": self.retrieval_method,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """Create search result from dictionary representation.

        Args:
            data: Dictionary representation of the search result

        Returns:
            SearchResult instance
        """
        result = cls(
            query_id=data["query_id"],
            chunk_id=data["chunk_id"],
            score=data["score"],
            rank=data["rank"],
            retrieval_method=data.get("retrieval_method", "vector"),
            id=data["id"]
        )

        result.created_at = data.get("created_at") and datetime.fromisoformat(data["created_at"])
        result.updated_at = data.get("updated_at") and datetime.fromisoformat(data["updated_at"])

        return result

    def __str__(self) -> str:
        """String representation."""
        return f"SearchResult(chunk_id='{self.chunk_id}', score={self.score:.4f}, rank={self.rank})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"SearchResult(id='{self.id}', query_id='{self.query_id}', chunk_id='{self.chunk_id}', score={self.score:.4f}, rank={self.rank}, method='{self.retrieval_method}')"