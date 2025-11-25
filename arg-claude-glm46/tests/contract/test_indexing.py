"""Contract tests for the indexing CLI command."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cli.indexing import indexing_command


def test_indexing_command_contract():
    """Test the indexing command contract."""
    # Mock arguments
    class MockArgs:
        def __init__(self, name, file):
            self.name = name
            self.file = file

    # Test with valid arguments
    args = MockArgs("test_doc", "/path/to/test.pdf")

    # Mock the indexing orchestrator
    with patch('src.cli.indexing.IndexingOrchestrator') as mock_orchestrator:
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.index_document.return_value = "test_doc_id"

        # Call the indexing command
        result = indexing_command(args)

        # Verify the orchestrator was called correctly
        mock_orchestrator.assert_called_once()
        mock_instance.index_document.assert_called_once_with("test_doc", "/path/to/test.pdf")

        # Verify the command returns success
        assert result == 0


def test_indexing_command_with_file_not_found():
    """Test the indexing command with file not found error."""
    # Mock arguments
    class MockArgs:
        def __init__(self, name, file):
            self.name = name
            self.file = file

    # Test with valid arguments
    args = MockArgs("test_doc", "/path/to/nonexistent.pdf")

    # Mock the indexing orchestrator to raise FileNotFoundError
    with patch('src.cli.indexing.IndexingOrchestrator') as mock_orchestrator:
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.index_document.side_effect = FileNotFoundError("File not found")

        # Call the indexing command
        result = indexing_command(args)

        # Verify the orchestrator was called
        mock_orchestrator.assert_called_once()
        mock_instance.index_document.assert_called_once_with("test_doc", "/path/to/nonexistent.pdf")

        # Verify the command returns error
        assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])