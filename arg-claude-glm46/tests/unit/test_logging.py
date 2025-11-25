"""Unit tests for the logging configuration module."""

import pytest
import sys
import os
import logging
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lib.logging_config import StructuredLogger, RAGLogger


def test_structured_logger_info():
    """Test structured logger info method."""
    logger = StructuredLogger("test_logger")

    # Test logging without context
    with patch.object(logger.logger, 'info') as mock_info:
        logger.info("Test message")
        mock_info.assert_called_once_with("Test message")

    # Test logging with context
    with patch.object(logger.logger, 'info') as mock_info:
        logger.info("Test message", {"user_id": "123", "operation": "indexing"})
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "Test message" in args[0]
        assert "Context:" in args[0]
        assert "user_id" in args[0]
        assert "123" in args[0]


def test_structured_logger_error():
    """Test structured logger error method."""
    logger = StructuredLogger("test_logger")

    # Test logging without context
    with patch.object(logger.logger, 'error') as mock_error:
        logger.error("Test error")
        mock_error.assert_called_once_with("Test error")

    # Test logging with context
    with patch.object(logger.logger, 'error') as mock_error:
        logger.error("Test error", {"error_code": "404"})
        mock_error.assert_called_once()
        args = mock_error.call_args[0]
        assert "Test error" in args[0]
        assert "Context:" in args[0]
        assert "error_code" in args[0]


def test_rag_logger_backward_compatibility():
    """Test RAGLogger backward compatibility."""
    logger = RAGLogger("test_logger")

    # Test that old-style calls still work
    with patch.object(logger.logger, 'info') as mock_info:
        logger.info("Test message")
        mock_info.assert_called_once_with("Test message")

    # Test that new-style calls work
    with patch.object(logger.logger, 'info') as mock_info:
        logger.info("Test message", {"context": "test"})
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "Test message" in args[0]
        assert "Context:" in args[0]


def test_rag_logger_levels():
    """Test all logging levels."""
    logger = RAGLogger("test_logger")

    # Test debug
    with patch.object(logger.logger, 'debug') as mock_debug:
        logger.debug("Debug message")
        mock_debug.assert_called_once_with("Debug message")

    # Test warning
    with patch.object(logger.logger, 'warning') as mock_warning:
        logger.warning("Warning message")
        mock_warning.assert_called_once_with("Warning message")

    # Test exception
    with patch.object(logger.logger, 'exception') as mock_exception:
        logger.exception("Exception message")
        mock_exception.assert_called_once_with("Exception message")


if __name__ == "__main__":
    pytest.main([__file__])