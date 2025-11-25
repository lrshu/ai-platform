"""Contract tests for the search CLI command."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cli.search import search_command


def test_search_command_contract():
    """Test the search command contract."""
    # Mock arguments
    class MockArgs:
        def __init__(self, name, question, top_k=5, expand_query=False, rerank=False):
            self.name = name
            self.question = question
            self.top_k = top_k
            self.expand_query = expand_query
            self.rerank = rerank

    # Test with valid arguments
    args = MockArgs("test_doc", "What is this document about?")

    # Mock the search orchestrator
    with patch('src.cli.search.SearchOrchestrator') as mock_orchestrator:
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.search.return_value = [
            {"content": "This is relevant content", "score": 0.95},
            {"content": "This is also relevant", "score": 0.87}
        ]

        # Call the search command
        result = search_command(args)

        # Verify the orchestrator was called correctly
        mock_orchestrator.assert_called_once()
        mock_instance.search.assert_called_once_with(
            "test_doc",
            "What is this document about?",
            top_k=5,
            expand_query=False,
            rerank=False
        )

        # Verify the command returns success
        assert result == 0


def test_search_command_with_no_results():
    """Test the search command with no results found."""
    # Mock arguments
    class MockArgs:
        def __init__(self, name, question, top_k=5, expand_query=False, rerank=False):
            self.name = name
            self.question = question
            self.top_k = top_k
            self.expand_query = expand_query
            self.rerank = rerank

    # Test with valid arguments
    args = MockArgs("test_doc", "What is this document about?")

    # Mock the search orchestrator to return empty results
    with patch('src.cli.search.SearchOrchestrator') as mock_orchestrator:
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.search.return_value = []

        # Call the search command
        result = search_command(args)

        # Verify the orchestrator was called
        mock_orchestrator.assert_called_once()
        mock_instance.search.assert_called_once_with(
            "test_doc",
            "What is this document about?",
            top_k=5,
            expand_query=False,
            rerank=False
        )

        # Verify the command returns success (no results is not an error)
        assert result == 0


if __name__ == "__main__":
    pytest.main([__file__])