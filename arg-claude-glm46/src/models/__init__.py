"""Base models for the RAG backend system."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


@dataclass
class Document:
    """Represents a PDF file that has been indexed in the system."""

    id: str
    name: str
    file_path: str
    created_at: datetime
    status: str  # pending, processing, completed, failed
    chunk_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}


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


@dataclass
class Entity:
    """Represents a named entity extracted from document content."""

    id: str
    name: str
    type: str  # person, organization, location, etc.
    description: Optional[str] = None


@dataclass
class EntityMention:
    """Represents a specific mention of an entity within a chunk."""

    id: str
    entity_id: str
    chunk_id: str
    position_start: int
    position_end: int
    confidence: float


@dataclass
class Relationship:
    """Represents a relationship between two entities extracted from document content."""

    id: str
    source_entity_id: str
    target_entity_id: str
    type: str  # works_for, located_in, etc.
    description: str
    confidence: float


@dataclass
class Query:
    """Represents a user query processed by the system."""

    id: str
    content: str
    created_at: datetime
    expanded_content: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class SearchResult:
    """Represents a search result returned to the user."""

    id: str
    query_id: str
    chunk_id: str
    relevance_score: float
    rank: int
    reranked_score: Optional[float] = None


@dataclass
class Conversation:
    """Represents a conversation session with context preservation."""

    id: str
    created_at: datetime
    updated_at: datetime
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.context is None:
            self.context = {}


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation."""

    id: str
    conversation_id: str
    query_id: str
    response: str
    turn_number: int
    created_at: datetime