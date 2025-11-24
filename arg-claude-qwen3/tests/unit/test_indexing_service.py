"""
Unit tests for the indexing service.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.services.indexing_service import IndexingService
from src.models.document_collection import DocumentCollection
from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.models.vector_embedding import VectorEmbedding
from src.models.knowledge_graph_node import KnowledgeGraphNode
from src.models.knowledge_graph_relationship import KnowledgeGraphRelationship
from src.lib.exceptions import FileProcessingError, CollectionNotFoundError


class TestIndexingService:
    """Test the indexing service."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.indexing_service = IndexingService()

    def test_index_document_success(self):
        """Test successful document indexing."""
        collection_name = "test_collection"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("Test PDF content")
            file_path = f.name

        # Mock all the dependencies
        with patch.multiple(self.indexing_service,
                           pdf_parser=MagicMock(),
                           document_chunker=MagicMock(),
                           embedding_generator=MagicMock(),
                           kg_extractor=MagicMock()):

            # Mock PDF parser
            self.indexing_service.pdf_parser.parse_pdf.return_value = "Test content"
            self.indexing_service.pdf_parser.get_pdf_metadata.return_value = {"title": "Test Document"}

            # Mock document chunker
            mock_chunk = DocumentChunk("doc_123", "Test content", 0)
            self.indexing_service.document_chunker.chunk_document.return_value = [mock_chunk]

            # Mock embedding generator
            mock_embedding = VectorEmbedding("chunk_123", [0.1, 0.2, 0.3], "text-embedding-v4")
            self.indexing_service.embedding_generator.generate_embeddings.return_value = [mock_embedding]

            # Mock knowledge graph extractor
            mock_entity = KnowledgeGraphNode("chunk_123", "concept", "Test", "Test entity")
            mock_relationship = KnowledgeGraphRelationship("node_1", "node_2", "related_to", "Test relationship")
            self.indexing_service.kg_extractor.extract_entities_and_relationships.return_value = (
                [mock_entity], [mock_relationship]
            )

            # Mock collection creation
            with patch.object(self.indexing_service, '_get_or_create_collection') as mock_collection:
                mock_collection.return_value = DocumentCollection(collection_name)

                # Mock database connection
                with patch.object(self.indexing_service, 'db'):
                    document_id = self.indexing_service.index_document(collection_name, file_path)

                    # Verify the result
                    assert document_id is not None
                    assert isinstance(document_id, str)

        # Clean up
        os.unlink(file_path)

    def test_index_document_file_not_found(self):
        """Test document indexing with non-existent file."""
        collection_name = "test_collection"
        file_path = "/path/that/does/not/exist.pdf"

        with patch.object(self.indexing_service.pdf_parser, 'parse_pdf') as mock_parse:
            mock_parse.side_effect = FileNotFoundError("File not found")

            with pytest.raises(FileProcessingError):
                self.indexing_service.index_document(collection_name, file_path)

    def test_index_document_parser_error(self):
        """Test document indexing when PDF parser fails."""
        collection_name = "test_collection"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("Invalid PDF content")
            file_path = f.name

        with patch.object(self.indexing_service.pdf_parser, 'parse_pdf') as mock_parse:
            mock_parse.side_effect = Exception("Parser failed")

            with pytest.raises(FileProcessingError):
                self.indexing_service.index_document(collection_name, file_path)

        # Clean up
        os.unlink(file_path)

    def test_get_or_create_collection(self):
        """Test getting or creating a collection."""
        collection_name = "test_collection"

        collection = self.indexing_service._get_or_create_collection(collection_name)

        assert isinstance(collection, DocumentCollection)
        assert collection.name == collection_name

    def test_index_documents_batch_success(self):
        """Test successful batch document indexing."""
        collection_name = "test_collection"

        # Create temporary files
        files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
                f.write(f"Test PDF content {i}")
                files.append(f.name)

        # Mock the index_document method
        with patch.object(self.indexing_service, 'index_document') as mock_index:
            mock_index.return_value = "doc_123"

            document_ids = self.indexing_service.index_documents_batch(collection_name, files)

            # Verify the results
            assert len(document_ids) == 3
            assert all(isinstance(doc_id, str) for doc_id in document_ids)

        # Clean up
        for file_path in files:
            os.unlink(file_path)

    def test_index_documents_batch_partial_failure(self):
        """Test batch document indexing with some failures."""
        collection_name = "test_collection"

        # Create temporary files
        files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
                f.write(f"Test PDF content {i}")
                files.append(f.name)

        # Mock the index_document method to fail for the second file
        def mock_index_document(collection_name, file_path):
            if file_path == files[1]:
                raise Exception("Failed to index document")
            return "doc_123"

        with patch.object(self.indexing_service, 'index_document', side_effect=mock_index_document):
            document_ids = self.indexing_service.index_documents_batch(collection_name, files)

            # Should have indexed 2 out of 3 documents
            assert len(document_ids) == 2
            assert all(isinstance(doc_id, str) for doc_id in document_ids)

        # Clean up
        for file_path in files:
            os.unlink(file_path)


if __name__ == "__main__":
    pytest.main([__file__])