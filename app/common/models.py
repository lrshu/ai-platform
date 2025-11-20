"""
Shared Pydantic models for the RAG backend system.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path


class SearchRequest(BaseModel):
    """Represents a search query with dynamic pipeline control parameters."""

    query: str = Field(..., description="The natural language query text")
    use_hyde: bool = Field(False, description="Flag to enable/disable HyDE query expansion")
    use_rerank: bool = Field(False, description="Flag to enable/disable reranking of results")
    top_k: int = Field(10, description="Number of top results to return", ge=1, le=100)
    top_p: float = Field(0.9, description="Nucleus sampling parameter for generation", ge=0.0, le=1.0)
    temperature: float = Field(0.7, description="Temperature parameter for generation", ge=0.0, le=2.0)

    @field_validator('query')
    @classmethod
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('query must not be empty')
        return v.strip()


class DocumentMetadata(BaseModel):
    """Metadata tracking the origin and position of content within a document."""

    document_id: str = Field(..., description="Identifier of the source document")
    start_index: int = Field(..., description="Start position of the content in the document", ge=0)
    end_index: int = Field(..., description="End position of the content in the document", ge=0)
    parent_id: Optional[str] = Field(None, description="Reference to parent chunk for Small-to-Big strategy")
    source_type: str = Field(..., description="Type of source document (PDF, DOCX, etc.)")
    title: Optional[str] = Field(None, description="Title of the document (if available)")
    author: Optional[str] = Field(None, description="Author of the document (if available)")

    @field_validator('end_index')
    @classmethod
    def end_index_must_be_greater_than_start(cls, v, info):
        if 'start_index' in info.data and v <= info.data['start_index']:
            raise ValueError('end_index must be greater than start_index')
        return v


class Chunk(BaseModel):
    """Represents a document chunk with content and embedding."""

    id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="The text content of the chunk")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the chunk content")
    metadata: DocumentMetadata = Field(..., description="Metadata about the chunk's origin")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the chunk was created")


class Entity(BaseModel):
    """Extracted information from documents stored as graph nodes."""

    id: str = Field(..., description="Unique identifier for the entity")
    name: str = Field(..., description="Name of the entity")
    type: str = Field(..., description="Type/category of the entity")
    description: Optional[str] = Field(None, description="Description of the entity")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the entity was created")


class Relationship(BaseModel):
    """Relationships between entities stored as graph edges."""

    id: str = Field(..., description="Unique identifier for the relationship")
    source_entity_id: str = Field(..., description="ID of the source entity")
    target_entity_id: str = Field(..., description="ID of the target entity")
    relationship_type: str = Field(..., description="Type of relationship")
    description: Optional[str] = Field(None, description="Description of the relationship")
    confidence: float = Field(..., description="Confidence score of the relationship extraction", ge=0.0, le=1.0)


class GenerationResponse(BaseModel):
    """Response from the LLM generation module."""

    response_text: str = Field(..., description="The generated text response")
    sources: List[Chunk] = Field(..., description="Chunks used as context for generation")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the response was generated")


class IndexingRequest(BaseModel):
    """Request to trigger document indexing."""

    document_urls: List[str] = Field(..., description="URLs of documents to index", min_length=1)
    collection_name: str = Field("default", description="Name of the collection to index documents into")


class IndexingResponse(BaseModel):
    """Response from indexing request."""

    job_id: str = Field(..., description="Identifier for the indexing job")
    status: str = Field(..., description="Status of the indexing job", pattern="^(started|processing|completed|failed)$")


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")