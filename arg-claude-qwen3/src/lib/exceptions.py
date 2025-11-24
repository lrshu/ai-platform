"""
Custom exception classes for the RAG backend system.
"""


class RAGBaseException(Exception):
    """Base exception class for RAG backend system."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DatabaseConnectionError(RAGBaseException):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message)


class DocumentNotFoundError(RAGBaseException):
    """Raised when a requested document is not found."""

    def __init__(self, document_id: str):
        super().__init__(f"Document with ID {document_id} not found")


class CollectionNotFoundError(RAGBaseException):
    """Raised when a requested collection is not found."""

    def __init__(self, collection_name: str):
        super().__init__(f"Collection {collection_name} not found")


class FileProcessingError(RAGBaseException):
    """Raised when file processing fails."""

    def __init__(self, file_path: str, message: str = "Failed to process file"):
        super().__init__(f"{message}: {file_path}")


class EmbeddingGenerationError(RAGBaseException):
    """Raised when embedding generation fails."""

    def __init__(self, message: str = "Failed to generate embeddings"):
        super().__init__(message)


class LLMGenerationError(RAGBaseException):
    """Raised when LLM generation fails."""

    def __init__(self, message: str = "Failed to generate response from LLM"):
        super().__init__(message)


class QueryExpansionError(RAGBaseException):
    """Raised when query expansion fails."""

    def __init__(self, message: str = "Failed to expand query"):
        super().__init__(message)


class SearchError(RAGBaseException):
    """Raised when search operation fails."""

    def __init__(self, message: str = "Search operation failed"):
        super().__init__(message)


class ChatError(RAGBaseException):
    """Raised when chat operation fails."""

    def __init__(self, message: str = "Chat operation failed"):
        super().__init__(message)