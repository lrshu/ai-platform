"""Error handling and logging infrastructure."""

import logging
import sys
import json
from typing import Optional, Dict, Any
from datetime import datetime
from functools import partial


class StructuredLogger:
    """Custom structured logger for the RAG backend system."""

    def __init__(self, name: str = "rag_backend"):
        """Initialize the structured logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create console handler if not already configured
        if not self.logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)

            # Add handler to logger
            self.logger.addHandler(console_handler)

    def _log_with_context(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a message with optional structured context."""
        if context:
            # Add context to the message
            context_str = json.dumps(context, default=str)
            full_message = f"{message} | Context: {context_str}"
        else:
            full_message = message

        # Log using the appropriate level
        log_method = getattr(self.logger, level)
        log_method(full_message)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message with optional context."""
        self._log_with_context("info", message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message with optional context."""
        self._log_with_context("warning", message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message with optional context."""
        self._log_with_context("error", message, context)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message with optional context."""
        self._log_with_context("debug", message, context)

    def exception(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log exception with traceback and optional context."""
        if context:
            context_str = json.dumps(context, default=str)
            full_message = f"{message} | Context: {context_str}"
        else:
            full_message = message

        self.logger.exception(full_message)


class RAGLogger(StructuredLogger):
    """Backward-compatible RAG logger."""

    def __init__(self, name: str = "rag_backend"):
        """Initialize the RAG logger."""
        super().__init__(name)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message (backward compatibility)."""
        super().info(message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message (backward compatibility)."""
        super().warning(message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message (backward compatibility)."""
        super().error(message, context)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message (backward compatibility)."""
        super().debug(message, context)

    def exception(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log exception with traceback (backward compatibility)."""
        super().exception(message, context)


class RAGException(Exception):
    """Base exception class for RAG backend system."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        """Initialize the RAG exception."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.timestamp = datetime.now()

    def __str__(self):
        """String representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class DocumentProcessingError(RAGException):
    """Exception for document processing errors."""

    def __init__(self, message: str):
        """Initialize document processing error."""
        super().__init__(message, "DOC_PROC_001")


class DatabaseError(RAGException):
    """Exception for database errors."""

    def __init__(self, message: str):
        """Initialize database error."""
        super().__init__(message, "DB_001")


class LLMError(RAGException):
    """Exception for LLM-related errors."""

    def __init__(self, message: str):
        """Initialize LLM error."""
        super().__init__(message, "LLM_001")


class EmbeddingError(RAGException):
    """Exception for embedding generation errors."""

    def __init__(self, message: str):
        """Initialize embedding error."""
        super().__init__(message, "EMBED_001")


# Global logger instance
logger = RAGLogger()


def setup_logging(log_level: str = "INFO"):
    """
    Set up logging configuration.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )