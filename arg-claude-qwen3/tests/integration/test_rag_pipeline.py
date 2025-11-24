"""
Integration tests for the RAG backend pipeline.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the actual modules
from src.cli.indexing import index_document
from src.cli.search import search_documents
from src.cli.chat import chat_with_documents
from src.lib.exceptions import FileProcessingError


class TestRAGPipeline:
    """Test the complete RAG pipeline from indexing to chat."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary PDF-like text file for testing
        self.test_pdf_content = """
        # Test Document

        This is a test document for the RAG system.

        ## Introduction

        The RAG (Retrieval-Augmented Generation) system combines retrieval and generation
        to provide accurate answers based on document content.

        ## Key Features

        1. Document indexing with vector embeddings
        2. Hybrid search (vector + graph)
        3. Query expansion and result re-ranking
        4. Conversational question answering

        ## Conclusion

        The RAG system provides a powerful way to interact with document collections
        using natural language queries.
        """

        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False)
        self.temp_file.write(self.test_pdf_content)
        self.temp_file.close()

        # Test collection name
        self.collection_name = "test_collection"

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_complete_rag_workflow(self):
        """Test the complete RAG workflow: index -> search -> chat."""
        # Mock all the service dependencies to avoid actual API calls and database operations
        with patch.multiple('src.services.indexing_service.IndexingService',
                           pdf_parser=MagicMock(),
                           document_chunker=MagicMock(),
                           embedding_generator=MagicMock(),
                           kg_extractor=MagicMock()), \
             patch('src.services.indexing_service.IndexingService._get_or_create_collection') as mock_collection, \
             patch('src.services.search_service.SearchService.search') as mock_search, \
             patch('src.services.chat_service.ChatService.chat_with_documents') as mock_chat:

            # Mock indexing service dependencies
            from src.models.document_collection import DocumentCollection
            mock_collection.return_value = DocumentCollection(self.collection_name)

            # Mock search service
            mock_search.return_value = [
                {"content": "RAG system combines retrieval and generation", "relevance_score": 0.95}
            ]

            # Mock chat service
            mock_chat.return_value = {
                "answer": "The RAG system combines retrieval and generation to provide accurate answers.",
                "session_id": "test_session_123",
                "sources": [
                    {"source": "Test Document", "relevance_score": 0.95}
                ],
                "citations": [
                    {"number": 1, "source": "Test Document"}
                ]
            }

            # 1. Index the document
            document_id = index_document(
                name=self.collection_name,
                file_path=self.temp_file.name
            )
            assert document_id is not None

            # 2. Search for information
            search_results = search_documents(
                name=self.collection_name,
                question="What is RAG?"
            )
            assert len(search_results) > 0

            # 3. Chat with the document
            chat_response = chat_with_documents(
                name=self.collection_name,
                question="Can you explain RAG in simple terms?"
            )
            assert chat_response is not None
            assert "retrieval" in chat_response["answer"].lower() or "generation" in chat_response["answer"].lower()

    def test_indexing_with_invalid_file(self):
        """Test indexing with an invalid file path."""
        with pytest.raises(FileNotFoundError):
            index_document(
                name=self.collection_name,
                file_path="/path/that/does/not/exist.pdf"
            )

    def test_search_empty_collection(self):
        """Test searching in an empty collection."""
        with patch('src.services.search_service.SearchService.search') as mock_search:
            mock_search.return_value = []

            results = search_documents(
                name="nonexistent_collection",
                question="What is this?"
            )
            assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__])