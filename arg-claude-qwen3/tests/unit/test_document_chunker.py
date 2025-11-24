"""
Unit tests for the document chunker service.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.document_chunker import DocumentChunker
from src.models.document_chunk import DocumentChunk


class TestDocumentChunker:
    """Test the document chunker service."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)

    def test_init_with_default_values(self):
        """Test initialization with default values."""
        chunker = DocumentChunker()
        assert chunker.chunk_size == 1000
        assert chunker.chunk_overlap == 200

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 100

    def test_chunk_document_success(self):
        """Test successful document chunking."""
        document_id = "test_doc_123"
        text = "This is a test document. " * 20  # Long enough to create multiple chunks
        metadata = {"source": "test", "category": "example"}

        # Mock the text splitter to return predictable chunks
        with patch.object(self.chunker.text_splitter, 'split_text') as mock_split:
            mock_split.return_value = [
                "This is the first chunk of text.",
                "This is the second chunk of text.",
                "This is the third chunk of text."
            ]

            chunks = self.chunker.chunk_document(document_id, text, metadata)

            # Verify the results
            assert len(chunks) == 3
            assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
            assert all(chunk.document_id == document_id for chunk in chunks)
            assert all(chunk.metadata == metadata for chunk in chunks)
            assert chunks[0].position == 0
            assert chunks[1].position == 1
            assert chunks[2].position == 2

    def test_chunk_document_empty_text(self):
        """Test chunking an empty document."""
        document_id = "test_doc_123"
        text = ""

        with patch.object(self.chunker.text_splitter, 'split_text') as mock_split:
            mock_split.return_value = [""]

            chunks = self.chunker.chunk_document(document_id, text)

            assert len(chunks) == 1
            assert chunks[0].content == ""
            assert chunks[0].document_id == document_id
            assert chunks[0].position == 0

    def test_chunk_document_with_none_metadata(self):
        """Test chunking with None metadata."""
        document_id = "test_doc_123"
        text = "This is a test document."

        with patch.object(self.chunker.text_splitter, 'split_text') as mock_split:
            mock_split.return_value = ["This is a test document."]

            chunks = self.chunker.chunk_document(document_id, text, None)

            assert len(chunks) == 1
            assert chunks[0].metadata == {}

    def test_chunk_document_exception_handling(self):
        """Test exception handling during document chunking."""
        document_id = "test_doc_123"
        text = "This is a test document."

        with patch.object(self.chunker.text_splitter, 'split_text') as mock_split:
            mock_split.side_effect = Exception("Splitting failed")

            with pytest.raises(Exception):
                self.chunker.chunk_document(document_id, text)

    def test_chunk_with_custom_settings_success(self):
        """Test successful chunking with custom settings."""
        document_id = "test_doc_123"
        text = "This is a test document. " * 20
        chunk_size = 50
        chunk_overlap = 10
        metadata = {"custom": "settings"}

        # Create a mock splitter for the custom settings
        with patch('src.services.document_chunker.RecursiveCharacterTextSplitter') as mock_splitter_class:
            mock_splitter_instance = MagicMock()
            mock_splitter_class.return_value = mock_splitter_instance
            mock_splitter_instance.split_text.return_value = [
                "First custom chunk",
                "Second custom chunk"
            ]

            chunks = self.chunker.chunk_with_custom_settings(
                document_id, text, chunk_size, chunk_overlap, metadata
            )

            # Verify the custom splitter was created with correct parameters
            mock_splitter_class.assert_called_once_with(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )

            # Verify the results
            assert len(chunks) == 2
            assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
            assert all(chunk.document_id == document_id for chunk in chunks)
            assert all(chunk.metadata == metadata for chunk in chunks)


if __name__ == "__main__":
    pytest.main([__file__])