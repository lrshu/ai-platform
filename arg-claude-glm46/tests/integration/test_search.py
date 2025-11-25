"""Integration tests for the search pipeline."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.retrieval.hybrid_search import HybridSearchOrchestrator
from src.services.retrieval.vector_search import VectorSearchService
from src.services.retrieval.graph_search import GraphSearchService


def test_vector_search_service():
    """Test vector search service."""
    # Mock the database driver
    with patch('src.services.retrieval.vector_search.db_config') as mock_db_config:
        mock_driver = MagicMock()
        mock_db_config.get_driver.return_value = mock_driver

        # Mock session and transaction
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        # Mock the search result
        mock_session.read_transaction.return_value = [
            {"chunk_id": "chunk1", "content": "Test content 1", "score": 0.95},
            {"chunk_id": "chunk2", "content": "Test content 2", "score": 0.87}
        ]

        # Create service instance
        service = VectorSearchService()

        # Mock embedding generation
        with patch('src.services.retrieval.vector_search.embedder') as mock_embedder:
            mock_embedder.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]

            # Call the search method
            results = service.search("test_doc", "test query", top_k=5)

            # Verify results
            assert len(results) == 2
            assert results[0]["content"] == "Test content 1"
            assert results[0]["score"] == 0.95
            assert results[1]["content"] == "Test content 2"
            assert results[1]["score"] == 0.87

            # Verify mocks were called correctly
            mock_embedder.generate_embeddings.assert_called_once_with(["test query"])


def test_graph_search_service():
    """Test graph search service."""
    # Mock the database driver
    with patch('src.services.retrieval.graph_search.db_config') as mock_db_config:
        mock_driver = MagicMock()
        mock_db_config.get_driver.return_value = mock_driver

        # Mock session and transaction
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        # Mock the search result
        mock_session.read_transaction.return_value = [
            {"chunk_id": "chunk3", "content": "Graph content 1", "score": 0.92},
            {"chunk_id": "chunk4", "content": "Graph content 2", "score": 0.85}
        ]

        # Create service instance
        service = GraphSearchService()

        # Call the search method
        results = service.search("test_doc", "test query", top_k=5)

        # Verify results
        assert len(results) == 2
        assert results[0]["content"] == "Graph content 1"
        assert results[0]["score"] == 0.92
        assert results[1]["content"] == "Graph content 2"
        assert results[1]["score"] == 0.85


def test_hybrid_search_orchestrator():
    """Test hybrid search orchestrator."""
    # Mock vector search service
    with patch('src.services.retrieval.hybrid_search.VectorSearchService') as mock_vector_service:
        mock_vector_instance = MagicMock()
        mock_vector_service.return_value = mock_vector_instance
        mock_vector_instance.search.return_value = [
            {"chunk_id": "chunk1", "content": "Vector content 1", "score": 0.95},
            {"chunk_id": "chunk2", "content": "Vector content 2", "score": 0.87}
        ]

        # Mock graph search service
        with patch('src.services.retrieval.hybrid_search.GraphSearchService') as mock_graph_service:
            mock_graph_instance = MagicMock()
            mock_graph_service.return_value = mock_graph_instance
            mock_graph_instance.search.return_value = [
                {"chunk_id": "chunk3", "content": "Graph content 1", "score": 0.92},
                {"chunk_id": "chunk4", "content": "Graph content 2", "score": 0.85}
            ]

            # Create orchestrator instance
            orchestrator = HybridSearchOrchestrator()

            # Call the search method
            results = orchestrator.search("test_doc", "test query", top_k=5)

            # Verify results (should combine both vector and graph results)
            assert len(results) >= 2  # At least the top results from each
            # Verify that mocks were called
            mock_vector_instance.search.assert_called_once_with("test_doc", "test query", top_k=5)
            mock_graph_instance.search.assert_called_once_with("test_doc", "test query", top_k=5)


if __name__ == "__main__":
    pytest.main([__file__])