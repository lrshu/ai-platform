"""Unit tests for the metrics collection module."""

import pytest
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lib.metrics import MetricsCollector, TimingContext


def test_metrics_collector_record_timing():
    """Test recording timing metrics."""
    collector = MetricsCollector()

    # Record some timing metrics
    collector.record_timing("test_operation", 100.5, {"test": "value"})
    collector.record_timing("test_operation", 200.0)

    # Check that metrics were recorded
    stats = collector.get_stats("test_operation")
    assert stats["count"] == 2
    assert stats["avg_ms"] == 150.25
    assert stats["min_ms"] == 100.5
    assert stats["max_ms"] == 200.0


def test_metrics_collector_record_counter():
    """Test recording counter metrics."""
    collector = MetricsCollector()

    # Record some counter metrics
    collector.record_counter("test_counter", 1, {"type": "success"})
    collector.record_counter("test_counter", 3)
    collector.record_counter("test_counter", 2, {"type": "warning"})

    # Check that metrics were recorded
    all_metrics = collector.get_all_metrics()
    assert len(all_metrics["test_counter"]) == 3

    # First metric should have context
    assert all_metrics["test_counter"][0]["value"] == 1
    assert all_metrics["test_counter"][0]["context"]["type"] == "success"

    # Second metric should have no context
    assert all_metrics["test_counter"][1]["value"] == 3
    assert all_metrics["test_counter"][1]["context"] == {}


def test_timing_context():
    """Test timing context manager."""
    collector = MetricsCollector()

    # Use timing context
    with TimingContext(collector, "timed_operation", {"source": "test"}):
        time.sleep(0.01)  # Sleep for 10ms

    # Check that timing was recorded
    stats = collector.get_stats("timed_operation")
    assert stats["count"] == 1
    # Timing should be approximately 10ms (allowing for some variance)
    assert stats["avg_ms"] >= 5.0
    assert stats["avg_ms"] <= 50.0  # Upper bound to account for system variance


def test_metrics_collector_clear():
    """Test clearing metrics."""
    collector = MetricsCollector()

    # Record some metrics
    collector.record_timing("test_operation", 100.0)
    collector.record_counter("test_counter", 5)

    # Verify metrics exist
    all_metrics = collector.get_all_metrics()
    assert len(all_metrics) > 0

    # Clear metrics
    collector.clear_metrics()

    # Verify metrics are cleared
    all_metrics = collector.get_all_metrics()
    assert len(all_metrics) == 0


if __name__ == "__main__":
    pytest.main([__file__])