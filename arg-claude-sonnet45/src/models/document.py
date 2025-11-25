"""Document and chunk data models."""

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents an uploaded document in the system.

    Attributes:
        id: Unique document identifier
        name: Namespace/collection name for grouping
        filename: Original filename
        file_path: Absolute path to stored PDF file
        file_size: File size in bytes
        upload_timestamp: When document was uploaded
        processing_status: Current processing state
        chunk_count: Total number of chunks created
        error_message: Error details if processing failed
    """

    id: UUID = Field(default_factory=uuid4)
    name: str
    filename: str
    file_path: str
    file_size: int
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_status: Literal["pending", "processing", "completed", "failed"] = "pending"
    chunk_count: int = 0
    error_message: str | None = None


class ChunkMetadata(BaseModel):
    """Metadata associated with a document chunk.

    Attributes:
        document_name: Copy of parent document name
        filename: Copy of original filename
        page_numbers: Source page numbers if available
        section_header: Nearest markdown header
    """

    document_name: str
    filename: str
    page_numbers: list[int] | None = None
    section_header: str | None = None


class DocumentChunk(BaseModel):
    """A semantically coherent segment of a document.

    Attributes:
        id: Unique chunk identifier
        document_id: Parent document ID
        text: Chunk text content (markdown)
        embedding: Vector embedding (1024d for Qwen)
        position: Ordinal position in document
        char_offset: Character offset in original markdown
        metadata: Additional chunk metadata
    """

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    embedding: list[float]
    position: int
    char_offset: int
    metadata: ChunkMetadata
