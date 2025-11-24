"""
Unit tests for the monitoring module.
"""

import pytest
import logging
from unittest.mock import Mock, patch
from src.lib.monitoring import (
    MetricsCollector, get_metrics_collector, log_function_call,
    log_execution_block, log_document_processing, log_search_query,
    log_chat_interaction
)


class TestMetricsCollector:
    """Test the MetricsCollector class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.logger = Mock(spec=logging.Logger)
        self.collector = MetricsCollector(self.logger)

    def test_increment_counter(self):
        """Test incrementing a counter."""
        self.collector.increment_counter("test_counter")
        assert self.collector.metrics["test_counter"] == 1

        self.collector.increment_counter("test_counter", 5)
        assert self.collector.metrics["test_counter"] == 6

    def test_gauge(self):
        """Test setting a gauge."""
        self.collector.gauge("test_gauge", 42.5)
        assert self.collector.metrics["test_gauge"] == 42.5

    def test_timer(self):
        """Test recording a timer."""
        self.collector.timer("test_timer", 1.234)
        # Timer just logs, doesn't store the value
        self.logger.info.assert_called_once()

    def test_get_system_metrics(self):
        """Test getting system metrics."""
        metrics = self.collector.get_system_metrics()
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "memory_rss" in metrics
        assert "num_threads" in metrics


class TestMonitoringFunctions:
    """Test the monitoring functions."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.logger = Mock(spec=logging.Logger)
        # Reset the global metrics collector
        import src.lib.monitoring
        src.lib.monitoring._metrics_collector = None

    def test_get_metrics_collector(self):
        """Test getting the metrics collector."""
        # First call should create a new instance
        collector = get_metrics_collector(self.logger)
        assert isinstance(collector, MetricsCollector)

        # Subsequent calls should return the same instance
        collector2 = get_metrics_collector(self.logger)
        assert collector is collector2

    def test_get_metrics_collector_without_logger(self):
        """Test getting metrics collector without logger after first call."""
        # First call with logger
        collector = get_metrics_collector(self.logger)

        # Second call without logger should work
        collector2 = get_metrics_collector()
        assert collector is collector2

    def test_get_metrics_collector_without_logger_first(self):
        """Test getting metrics collector without logger on first call."""
        # Reset the global metrics collector to None
        import src.lib.monitoring
        src.lib.monitoring._metrics_collector = None

        with pytest.raises(ValueError, match="Logger must be provided"):
            get_metrics_collector()

    def test_log_function_call_success(self):
        """Test logging function call decorator with success."""
        @log_function_call(self.logger)
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

        # Check that success was logged (start, end, and system metrics)
        assert self.logger.info.call_count >= 2
        assert self.logger.error.call_count == 0

    def test_log_function_call_exception(self):
        """Test logging function call decorator with exception."""
        @log_function_call(self.logger)
        def test_function():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            test_function()

        # Check that error was logged (start message and system metrics)
        assert self.logger.info.call_count >= 1
        assert self.logger.error.call_count == 1

    def test_log_execution_block_success(self):
        """Test logging execution block with success."""
        with log_execution_block(self.logger, "test_block"):
            pass

        # Check that success was logged (start, end, and system metrics)
        assert self.logger.info.call_count >= 2
        assert self.logger.error.call_count == 0

    def test_log_execution_block_exception(self):
        """Test logging execution block with exception."""
        with pytest.raises(ValueError):
            with log_execution_block(self.logger, "test_block"):
                raise ValueError("test error")

        # Check that error was logged (start message and system metrics)
        assert self.logger.info.call_count >= 1
        assert self.logger.error.call_count == 1

    def test_log_document_processing(self):
        """Test logging document processing."""
        log_document_processing(self.logger, "doc_123", "index", 1024)

        # Check that processing was logged
        self.logger.info.assert_called_once()
        assert "Processing document doc_123: index" in self.logger.info.call_args[0][0]

    def test_log_document_processing_without_size(self):
        """Test logging document processing without size."""
        log_document_processing(self.logger, "doc_123", "search")

        # Check that processing was logged
        self.logger.info.assert_called_once()
        assert "Processing document doc_123: search" in self.logger.info.call_args[0][0]

    def test_log_search_query(self):
        """Test logging search query."""
        log_search_query(self.logger, "What is RAG?", 5)

        # Check that query was logged
        self.logger.info.assert_called_once()
        assert "Search query executed" in self.logger.info.call_args[0][0]

    def test_log_chat_interaction(self):
        """Test logging chat interaction."""
        log_chat_interaction(self.logger, "session_123", 25, 150)

        # Check that interaction was logged
        self.logger.info.assert_called_once()
        assert "Chat interaction in session session_123" in self.logger.info.call_args[0][0]


if __name__ == "__main__":
    pytest.main([__file__])