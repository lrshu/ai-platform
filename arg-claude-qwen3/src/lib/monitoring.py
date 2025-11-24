"""
Monitoring and metrics collection for the RAG backend system.
"""

import logging
import time
import functools
from typing import Any, Callable, Optional
from contextlib import contextmanager
import psutil
import os


class MetricsCollector:
    """Collects and logs performance metrics."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        if name not in self.metrics:
            self.metrics[name] = 0
        self.metrics[name] += value
        self.logger.debug(f"Counter {name}: {self.metrics[name]}")

    def gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        self.metrics[name] = value
        self.logger.debug(f"Gauge {name}: {value}")

    def timer(self, name: str, duration: float) -> None:
        """Record a timer metric."""
        self.logger.info(f"Timer {name}: {duration:.4f}s")

    def get_system_metrics(self) -> dict:
        """Get system-level metrics."""
        process = psutil.Process(os.getpid())
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "memory_rss": process.memory_info().rss,
            "num_threads": process.num_threads()
        }


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(logger: Optional[logging.Logger] = None) -> MetricsCollector:
    """
    Get the global metrics collector instance.

    Args:
        logger: Logger to use for the metrics collector (required on first call)

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        if logger is None:
            raise ValueError("Logger must be provided on first call to get_metrics_collector")
        _metrics_collector = MetricsCollector(logger)
    return _metrics_collector


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with timing and metrics.

    Args:
        logger: Logger to use for logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            logger.info(f"Calling function: {func_name}")

            # Get metrics collector
            metrics_collector = get_metrics_collector(logger)

            # Record start time and system metrics
            start_time = time.time()
            start_metrics = metrics_collector.get_system_metrics()

            try:
                # Call the function
                result = func(*args, **kwargs)

                # Calculate duration
                duration = time.time() - start_time
                metrics_collector.timer(f"{func_name}.duration", duration)

                # Log success
                logger.info(f"Function {func_name} completed successfully in {duration:.4f}s")

                # Record end system metrics
                end_metrics = metrics_collector.get_system_metrics()
                logger.debug(f"System metrics for {func_name}: "
                           f"CPU: {start_metrics['cpu_percent']:.1f}% -> {end_metrics['cpu_percent']:.1f}%, "
                           f"Memory: {start_metrics['memory_percent']:.1f}% -> {end_metrics['memory_percent']:.1f}%")

                # Increment success counter
                metrics_collector.increment_counter(f"{func_name}.success")

                return result

            except Exception as e:
                # Calculate duration even for failed calls
                duration = time.time() - start_time
                metrics_collector.timer(f"{func_name}.duration", duration)

                # Log error
                logger.error(f"Function {func_name} failed after {duration:.4f}s: {str(e)}")

                # Increment error counter
                metrics_collector.increment_counter(f"{func_name}.error")

                # Re-raise the exception
                raise

        return wrapper
    return decorator


@contextmanager
def log_execution_block(logger: logging.Logger, block_name: str):
    """
    Context manager to log execution of a code block with timing.

    Args:
        logger: Logger to use for logging
        block_name: Name of the code block being executed
    """
    logger.info(f"Starting execution block: {block_name}")

    # Get metrics collector
    metrics_collector = get_metrics_collector(logger)

    # Record start time
    start_time = time.time()

    try:
        # Yield control to the code block
        yield

        # Calculate duration
        duration = time.time() - start_time
        metrics_collector.timer(f"{block_name}.duration", duration)

        # Log success
        logger.info(f"Execution block {block_name} completed successfully in {duration:.4f}s")

        # Increment success counter
        metrics_collector.increment_counter(f"{block_name}.success")

    except Exception as e:
        # Calculate duration even for failed blocks
        duration = time.time() - start_time
        metrics_collector.timer(f"{block_name}.duration", duration)

        # Log error
        logger.error(f"Execution block {block_name} failed after {duration:.4f}s: {str(e)}")

        # Increment error counter
        metrics_collector.increment_counter(f"{block_name}.error")

        # Re-raise the exception
        raise


def log_document_processing(logger: logging.Logger, document_id: str,
                          operation: str, size: Optional[int] = None):
    """
    Log document processing operations.

    Args:
        logger: Logger to use for logging
        document_id: ID of the document being processed
        operation: Type of operation (index, search, etc.)
        size: Size of the document in bytes (optional)
    """
    metrics_collector = get_metrics_collector(logger)

    # Log the operation
    if size is not None:
        logger.info(f"Processing document {document_id}: {operation} ({size} bytes)")
        metrics_collector.gauge(f"document.{document_id}.size", size)
    else:
        logger.info(f"Processing document {document_id}: {operation}")

    # Increment operation counter
    metrics_collector.increment_counter(f"document.{operation}")


def log_search_query(logger: logging.Logger, query: str, results_count: int):
    """
    Log search query operations.

    Args:
        logger: Logger to use for logging
        query: Search query text
        results_count: Number of results returned
    """
    metrics_collector = get_metrics_collector(logger)

    # Log the query (truncated for privacy)
    truncated_query = query[:100] + "..." if len(query) > 100 else query
    logger.info(f"Search query executed: '{truncated_query}' returned {results_count} results")

    # Increment search counter and record results
    metrics_collector.increment_counter("search.query")
    metrics_collector.gauge("search.results_count", results_count)


def log_chat_interaction(logger: logging.Logger, session_id: str,
                        message_length: int, response_length: int):
    """
    Log chat interaction metrics.

    Args:
        logger: Logger to use for logging
        session_id: Chat session ID
        message_length: Length of the user message
        response_length: Length of the AI response
    """
    metrics_collector = get_metrics_collector(logger)

    # Log the interaction
    logger.info(f"Chat interaction in session {session_id}: "
               f"message ({message_length} chars) -> response ({response_length} chars)")

    # Record metrics
    metrics_collector.increment_counter("chat.interaction")
    metrics_collector.gauge(f"chat.session.{session_id}.message_length", message_length)
    metrics_collector.gauge(f"chat.session.{session_id}.response_length", response_length)