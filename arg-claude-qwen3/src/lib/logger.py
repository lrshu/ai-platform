"""
Logging configuration for the RAG backend system.
"""

import logging
from typing import Optional
from src.lib.config import get_config


def setup_logging(level: Optional[int] = None) -> None:
    """
    Set up logging configuration.

    Args:
        level: Logging level (defaults to INFO or DEBUG if DEBUG env var is set)
    """
    config = get_config()
    if level is None:
        level = logging.DEBUG if config.is_debug else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Optionally add file handler
    log_file = config.log_file
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize logging on module import
setup_logging()