"""
Custom exception classes for the RAG system.
"""


class RAGException(Exception):
    """Base exception class for RAG system."""

    def __init__(self, message: str):
        """Initialize exception.

        Args:
            message: Exception message
        """
        self.message = message
        super().__init__(self.message)


class DocumentProcessingError(RAGException):
    """Exception raised when document processing fails."""

    def __init__(self, message: str, file_path: str = None):
        """Initialize exception.

        Args:
            message: Exception message
            file_path: Path to the file that caused the error (optional)
        """
        self.file_path = file_path
        super().__init__(message)


class DatabaseError(RAGException):
    """Exception raised when database operations fail."""

    def __init__(self, message: str):
        """Initialize exception.

        Args:
            message: Exception message
        """
        super().__init__(message)


class LLMError(RAGException):
    """Exception raised when LLM operations fail."""

    def __init__(self, message: str):
        """Initialize exception.

        Args:
            message: Exception message
        """
        super().__init__(message)


class ConfigurationError(RAGException):
    """Exception raised when configuration is invalid."""

    def __init__(self, message: str):
        """Initialize exception.

        Args:
            message: Exception message
        """
        super().__init__(message)


class ValidationError(RAGException):
    """Exception raised when validation fails."""

    def __init__(self, message: str):
        """Initialize exception.

        Args:
            message: Exception message
        """
        super().__init__(message)