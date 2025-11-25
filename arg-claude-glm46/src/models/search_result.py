"""SearchResult model for the RAG backend system."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    """Represents a search result returned to the user."""

    id: str
    query_id: str
    chunk_id: str
    relevance_score: float
    rank: int
    reranked_score: Optional[float] = None