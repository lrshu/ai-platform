"""
Integration tests for the chunker implementation.
"""

import pytest
from app.indexing.chunker import Chunker
from app.common.models import Chunk, DocumentMetadata


def test_chunker_create_chunks():
    """Test creating parent and child chunks."""
    chunker = Chunker(parent_chunk_size=100, child_chunk_size=20, overlap=5)

    # Create a test document
    document_content = "This is a test document with multiple sentences. " * 10
    document_id = "test_doc_1"
    source_type = "txt"

    # Create chunks
    parent_chunks, child_chunks = chunker.create_chunks(
        document_id, document_content, source_type
    )

    # Verify we got chunks
    assert len(parent_chunks) > 0
    assert len(child_chunks) > 0

    # Verify parent chunks
    for i, chunk in enumerate(parent_chunks):
        assert isinstance(chunk, Chunk)
        assert chunk.id == f"{document_id}_parent_{i}"
        assert len(chunk.content) <= 100  # Should not exceed parent chunk size
        assert chunk.metadata.document_id == document_id
        assert chunk.metadata.source_type == source_type

    # Verify child chunks
    for i, chunk in enumerate(child_chunks):
        assert isinstance(chunk, Chunk)
        assert chunk.id == f"{document_id}_child_{i}"
        assert len(chunk.content) <= 20  # Should not exceed child chunk size
        assert chunk.metadata.document_id == document_id
        assert chunk.metadata.source_type == source_type


def test_chunker_with_overlap():
    """Test chunking with overlap."""
    chunker = Chunker()

    # Test text
    text = "0123456789" * 20  # 200 characters
    chunk_size = 50
    overlap = 10

    # Create chunks with overlap
    chunks = chunker.chunk_with_overlap(text, chunk_size, overlap)

    # Verify chunks
    assert len(chunks) > 0
    for i, chunk in enumerate(chunks):
        assert len(chunk) <= chunk_size
        # Check overlap (except for the first chunk)
        if i > 0:
            previous_chunk = chunks[i-1]
            # The beginning of this chunk should match the end of the previous chunk
            overlap_text = previous_chunk[-overlap:] if len(previous_chunk) >= overlap else previous_chunk
            assert chunk.startswith(overlap_text) or len(chunk) < overlap


def test_chunker_empty_content():
    """Test chunking with empty content."""
    chunker = Chunker()

    # Create chunks from empty content
    parent_chunks, child_chunks = chunker.create_chunks(
        "empty_doc", "", "txt"
    )

    # Should return empty lists
    assert len(parent_chunks) == 0
    assert len(child_chunks) == 0


def test_chunker_small_content():
    """Test chunking with content smaller than chunk size."""
    chunker = Chunker(parent_chunk_size=100, child_chunk_size=20)

    # Create a small document
    document_content = "Small document."
    document_id = "small_doc"
    source_type = "txt"

    # Create chunks
    parent_chunks, child_chunks = chunker.create_chunks(
        document_id, document_content, source_type
    )

    # Should create one parent chunk
    assert len(parent_chunks) == 1
    assert parent_chunks[0].content == document_content
    assert parent_chunks[0].id == f"{document_id}_parent_0"

    # Should create one child chunk
    assert len(child_chunks) == 1
    assert child_chunks[0].content == document_content
    assert child_chunks[0].id == f"{document_id}_child_0"