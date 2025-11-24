"""
Validation utilities for the RAG backend system.
"""

import re
from typing import Optional
from src.lib.exceptions import RAGBaseException


class ValidationError(RAGBaseException):
    """Raised when validation fails."""

    def __init__(self, message: str):
        super().__init__(message)


def validate_collection_name(name: str) -> str:
    """
    Validate a collection name.

    Args:
        name: Collection name to validate

    Returns:
        The validated collection name

    Raises:
        ValidationError: If the collection name is invalid
    """
    if not name:
        raise ValidationError("Collection name cannot be empty")

    if len(name) > 100:
        raise ValidationError("Collection name cannot exceed 100 characters")

    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValidationError("Collection name can only contain letters, numbers, hyphens, and underscores")

    return name


def validate_document_id(document_id: str) -> str:
    """
    Validate a document ID.

    Args:
        document_id: Document ID to validate

    Returns:
        The validated document ID

    Raises:
        ValidationError: If the document ID is invalid
    """
    if not document_id:
        raise ValidationError("Document ID cannot be empty")

    if len(document_id) > 100:
        raise ValidationError("Document ID cannot exceed 100 characters")

    # Allow alphanumeric characters, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', document_id):
        raise ValidationError("Document ID can only contain letters, numbers, hyphens, and underscores")

    return document_id


def validate_file_path(file_path: str) -> str:
    """
    Validate a file path.

    Args:
        file_path: File path to validate

    Returns:
        The validated file path

    Raises:
        ValidationError: If the file path is invalid
    """
    if not file_path:
        raise ValidationError("File path cannot be empty")

    if len(file_path) > 1000:
        raise ValidationError("File path cannot exceed 1000 characters")

    # Check for invalid characters in file paths
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        if char in file_path:
            raise ValidationError(f"File path contains invalid character: {char}")

    return file_path


def validate_question(question: str) -> str:
    """
    Validate a question.

    Args:
        question: Question to validate

    Returns:
        The validated question

    Raises:
        ValidationError: If the question is invalid
    """
    if not question:
        raise ValidationError("Question cannot be empty")

    if len(question) > 1000:
        raise ValidationError("Question cannot exceed 1000 characters")

    # Check for excessive whitespace
    if re.search(r'\s{5,}', question):
        raise ValidationError("Question contains excessive whitespace")

    return question


def validate_session_id(session_id: str) -> str:
    """
    Validate a session ID.

    Args:
        session_id: Session ID to validate

    Returns:
        The validated session ID

    Raises:
        ValidationError: If the session ID is invalid
    """
    if not session_id:
        raise ValidationError("Session ID cannot be empty")

    if len(session_id) > 100:
        raise ValidationError("Session ID cannot exceed 100 characters")

    # Allow alphanumeric characters, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise ValidationError("Session ID can only contain letters, numbers, hyphens, and underscores")

    return session_id


def validate_top_k(top_k: int) -> int:
    """
    Validate top_k parameter.

    Args:
        top_k: Number of results to return

    Returns:
        The validated top_k value

    Raises:
        ValidationError: If the top_k value is invalid
    """
    if not isinstance(top_k, int):
        raise ValidationError("top_k must be an integer")

    if top_k < 1:
        raise ValidationError("top_k must be greater than 0")

    if top_k > 100:
        raise ValidationError("top_k cannot exceed 100")

    return top_k


def validate_chunk_size(chunk_size: int) -> int:
    """
    Validate chunk size parameter.

    Args:
        chunk_size: Chunk size to validate

    Returns:
        The validated chunk size

    Raises:
        ValidationError: If the chunk size is invalid
    """
    if not isinstance(chunk_size, int):
        raise ValidationError("Chunk size must be an integer")

    if chunk_size < 100:
        raise ValidationError("Chunk size must be at least 100 characters")

    if chunk_size > 10000:
        raise ValidationError("Chunk size cannot exceed 10000 characters")

    return chunk_size


def validate_chunk_overlap(chunk_overlap: int, chunk_size: int) -> int:
    """
    Validate chunk overlap parameter.

    Args:
        chunk_overlap: Chunk overlap to validate
        chunk_size: Chunk size for comparison

    Returns:
        The validated chunk overlap

    Raises:
        ValidationError: If the chunk overlap is invalid
    """
    if not isinstance(chunk_overlap, int):
        raise ValidationError("Chunk overlap must be an integer")

    if chunk_overlap < 0:
        raise ValidationError("Chunk overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValidationError("Chunk overlap must be less than chunk size")

    return chunk_overlap