"""Chunk model for the RAG backend system."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class Chunk:
    """Represents a segment of document content with associated embeddings and metadata."""

    id: str
    document_id: str
    content: str
    position: int
    created_at: datetime
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}