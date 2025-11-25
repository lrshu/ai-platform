"""Query, retrieval, and response data models."""

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class QueryOptions(BaseModel):
    """Configuration options for query processing and retrieval.

    Attributes:
        top_k: Number of chunks to retrieve
        expand_query: Enable query expansion in pre-retrieval
        enable_reranking: Enable post-retrieval reranking
        enable_vector_search: Enable vector similarity search
        enable_keyword_search: Enable keyword/BM25 search
        enable_graph_search: Enable graph traversal search
    """

    top_k: int = 5
    expand_query: bool = False
    enable_reranking: bool = True
    enable_vector_search: bool = True
    enable_keyword_search: bool = True
    enable_graph_search: bool = False


class Query(BaseModel):
    """A user's search query with processing metadata.

    Attributes:
        id: Unique query identifier
        document_name: Target document namespace
        original_text: User's original query
        expanded_text: Query after pre-retrieval expansion
        timestamp: When query was submitted
        options: Configuration for retrieval pipeline
    """

    id: UUID = Field(default_factory=uuid4)
    document_name: str
    original_text: str
    expanded_text: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    options: QueryOptions = Field(default_factory=QueryOptions)


class RetrievedChunk(BaseModel):
    """A single retrieved chunk from the retrieval phase.

    Attributes:
        chunk_id: Reference to DocumentChunk
        text: Chunk text content
        similarity_score: Relevance score (0-1, higher is better)
        source: Retrieval method that returned this chunk
        metadata: Chunk metadata (filename, position, etc.)
    """

    chunk_id: UUID
    text: str
    similarity_score: float
    source: Literal["vector", "keyword", "graph"]
    metadata: dict[str, str | int | list[int] | None]


class RetrievalResult(BaseModel):
    """Output from the retrieval phase.

    Attributes:
        query_id: Reference to originating Query
        chunks: Ranked list of retrieved chunks
        retrieval_methods_used: Which methods contributed
        timestamp: When retrieval completed
        retrieval_duration_ms: Time taken for retrieval
    """

    query_id: UUID
    chunks: list[RetrievedChunk]
    retrieval_methods_used: list[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retrieval_duration_ms: int


class Citation(BaseModel):
    """A source citation in a generated response.

    Attributes:
        chunk_id: Referenced DocumentChunk
        text_excerpt: Quoted text from chunk (≤100 chars)
        filename: Source document filename
    """

    chunk_id: UUID
    text_excerpt: str
    filename: str


class GeneratedResponse(BaseModel):
    """Final answer produced by the generation phase.

    Attributes:
        id: Unique response identifier
        query_id: Reference to originating Query
        answer_text: Generated natural language answer
        citations: Source references
        confidence_score: Confidence in answer quality (0-1)
        timestamp: When generation completed
        generation_duration_ms: Time taken for generation
    """

    id: UUID = Field(default_factory=uuid4)
    query_id: UUID
    answer_text: str
    citations: list[Citation]
    confidence_score: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generation_duration_ms: int
