"""Metrics collection for performance monitoring."""

import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict
from threading import Lock


class MetricsCollector:
    """Collector for performance metrics."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics = defaultdict(list)
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)

    def record_timing(self, operation: str, duration_ms: float,
                     context: Optional[Dict[str, Any]] = None):
        """
        Record timing metric for an operation.

        Args:
            operation (str): Name of the operation
            duration_ms (float): Duration in milliseconds
            context (Dict[str, Any], optional): Additional context
        """
        with self.lock:
            metric_data = {
                'timestamp': time.time(),
                'duration_ms': duration_ms,
                'context': context or {}
            }
            self.metrics[operation].append(metric_data)
            self.logger.debug(f"Recorded timing for {operation}: {duration_ms}ms")

    def record_counter(self, metric_name: str, value: int = 1,
                      context: Optional[Dict[str, Any]] = None):
        """
        Record a counter metric.

        Args:
            metric_name (str): Name of the metric
            value (int): Value to increment by (default: 1)
            context (Dict[str, Any], optional): Additional context
        """
        with self.lock:
            metric_data = {
                'timestamp': time.time(),
                'value': value,
                'context': context or {}
            }
            self.metrics[metric_name].append(metric_data)
            self.logger.debug(f"Recorded counter {metric_name}: {value}")

    def get_stats(self, operation: str) -> Dict[str, Any]:
        """
        Get statistics for an operation.

        Args:
            operation (str): Name of the operation

        Returns:
            Dict[str, Any]: Statistics including count, avg, min, max
        """
        with self.lock:
            if operation not in self.metrics:
                return {}

            timings = [m['duration_ms'] for m in self.metrics[operation]
                      if 'duration_ms' in m]

            if not timings:
                return {}

            return {
                'count': len(timings),
                'avg_ms': sum(timings) / len(timings),
                'min_ms': min(timings),
                'max_ms': max(timings),
                'total_ms': sum(timings)
            }

    def get_all_metrics(self) -> Dict[str, list]:
        """
        Get all collected metrics.

        Returns:
            Dict[str, list]: All metrics data
        """
        with self.lock:
            return dict(self.metrics)

    def clear_metrics(self):
        """Clear all collected metrics."""
        with self.lock:
            self.metrics.clear()


class TimingContext:
    """Context manager for timing operations."""

    def __init__(self, metrics_collector: MetricsCollector, operation: str,
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialize timing context.

        Args:
            metrics_collector (MetricsCollector): Metrics collector instance
            operation (str): Name of the operation
            context (Dict[str, Any], optional): Additional context
        """
        self.metrics_collector = metrics_collector
        self.operation = operation
        self.context = context
        self.start_time = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Record timing."""
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.metrics_collector.record_timing(
                self.operation, duration_ms, self.context
            )


# Global metrics collector instance
metrics_collector = MetricsCollector()


def timing(operation: str, context: Optional[Dict[str, Any]] = None):
    """
    Decorator for timing function execution.

    Args:
        operation (str): Name of the operation
        context (Dict[str, Any], optional): Additional context

    Returns:
        Callable: Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with TimingContext(metrics_collector, operation, context):
                return func(*args, **kwargs)
        return wrapper
    return decorator