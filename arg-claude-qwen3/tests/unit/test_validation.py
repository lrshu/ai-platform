"""
Unit tests for the validation module.
"""

import pytest
from src.lib.validation import (
    validate_collection_name, validate_document_id, validate_file_path,
    validate_question, validate_session_id, validate_top_k,
    validate_chunk_size, validate_chunk_overlap, ValidationError
)


class TestValidation:
    """Test the validation functions."""

    def test_validate_collection_name_success(self):
        """Test successful collection name validation."""
        valid_names = ["test_collection", "my-collection", "collection_123", "a" * 100]
        for name in valid_names:
            result = validate_collection_name(name)
            assert result == name

    def test_validate_collection_name_empty(self):
        """Test collection name validation with empty string."""
        with pytest.raises(ValidationError):
            validate_collection_name("")

    def test_validate_collection_name_too_long(self):
        """Test collection name validation with too long string."""
        with pytest.raises(ValidationError):
            validate_collection_name("a" * 101)

    def test_validate_collection_name_invalid_characters(self):
        """Test collection name validation with invalid characters."""
        invalid_names = ["test collection", "test@collection", "test/collection", "test.collection"]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                validate_collection_name(name)

    def test_validate_document_id_success(self):
        """Test successful document ID validation."""
        valid_ids = ["doc_123", "my-document", "document_123", "a" * 100]
        for doc_id in valid_ids:
            result = validate_document_id(doc_id)
            assert result == doc_id

    def test_validate_document_id_empty(self):
        """Test document ID validation with empty string."""
        with pytest.raises(ValidationError):
            validate_document_id("")

    def test_validate_document_id_too_long(self):
        """Test document ID validation with too long string."""
        with pytest.raises(ValidationError):
            validate_document_id("a" * 101)

    def test_validate_document_id_invalid_characters(self):
        """Test document ID validation with invalid characters."""
        invalid_ids = ["doc 123", "doc@123", "doc/123", "doc.123"]
        for doc_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_document_id(doc_id)

    def test_validate_file_path_success(self):
        """Test successful file path validation."""
        valid_paths = ["/path/to/file.pdf", "file.txt", "a" * 1000]
        for path in valid_paths:
            result = validate_file_path(path)
            assert result == path

    def test_validate_file_path_empty(self):
        """Test file path validation with empty string."""
        with pytest.raises(ValidationError):
            validate_file_path("")

    def test_validate_file_path_too_long(self):
        """Test file path validation with too long string."""
        with pytest.raises(ValidationError):
            validate_file_path("a" * 1001)

    def test_validate_file_path_invalid_characters(self):
        """Test file path validation with invalid characters."""
        invalid_paths = ["file<name", "file>name", 'file"name', "file|name", "file?name", "file*name"]
        for path in invalid_paths:
            with pytest.raises(ValidationError):
                validate_file_path(path)

    def test_validate_question_success(self):
        """Test successful question validation."""
        valid_questions = ["What is this?", "How does it work?", "a" * 1000]
        for question in valid_questions:
            result = validate_question(question)
            assert result == question

    def test_validate_question_empty(self):
        """Test question validation with empty string."""
        with pytest.raises(ValidationError):
            validate_question("")

    def test_validate_question_too_long(self):
        """Test question validation with too long string."""
        with pytest.raises(ValidationError):
            validate_question("a" * 1001)

    def test_validate_question_excessive_whitespace(self):
        """Test question validation with excessive whitespace."""
        with pytest.raises(ValidationError):
            validate_question("What is this     question?")

    def test_validate_session_id_success(self):
        """Test successful session ID validation."""
        valid_ids = ["session_123", "my-session", "session_123", "a" * 100]
        for session_id in valid_ids:
            result = validate_session_id(session_id)
            assert result == session_id

    def test_validate_session_id_empty(self):
        """Test session ID validation with empty string."""
        with pytest.raises(ValidationError):
            validate_session_id("")

    def test_validate_session_id_too_long(self):
        """Test session ID validation with too long string."""
        with pytest.raises(ValidationError):
            validate_session_id("a" * 101)

    def test_validate_session_id_invalid_characters(self):
        """Test session ID validation with invalid characters."""
        invalid_ids = ["session 123", "session@123", "session/123", "session.123"]
        for session_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_session_id(session_id)

    def test_validate_top_k_success(self):
        """Test successful top_k validation."""
        valid_values = [1, 5, 10, 50, 100]
        for value in valid_values:
            result = validate_top_k(value)
            assert result == value

    def test_validate_top_k_invalid_type(self):
        """Test top_k validation with invalid type."""
        invalid_values = ["5", 5.5, [], {}]
        for value in invalid_values:
            with pytest.raises(ValidationError):
                validate_top_k(value)

    def test_validate_top_k_negative(self):
        """Test top_k validation with negative value."""
        with pytest.raises(ValidationError):
            validate_top_k(-1)

    def test_validate_top_k_zero(self):
        """Test top_k validation with zero."""
        with pytest.raises(ValidationError):
            validate_top_k(0)

    def test_validate_top_k_too_large(self):
        """Test top_k validation with too large value."""
        with pytest.raises(ValidationError):
            validate_top_k(101)

    def test_validate_chunk_size_success(self):
        """Test successful chunk size validation."""
        valid_sizes = [100, 500, 1000, 5000, 10000]
        for size in valid_sizes:
            result = validate_chunk_size(size)
            assert result == size

    def test_validate_chunk_size_invalid_type(self):
        """Test chunk size validation with invalid type."""
        invalid_sizes = ["1000", 1000.5, [], {}]
        for size in invalid_sizes:
            with pytest.raises(ValidationError):
                validate_chunk_size(size)

    def test_validate_chunk_size_too_small(self):
        """Test chunk size validation with too small value."""
        with pytest.raises(ValidationError):
            validate_chunk_size(50)

    def test_validate_chunk_size_too_large(self):
        """Test chunk size validation with too large value."""
        with pytest.raises(ValidationError):
            validate_chunk_size(10001)

    def test_validate_chunk_overlap_success(self):
        """Test successful chunk overlap validation."""
        valid_overlaps = [(0, 1000), (100, 1000), (500, 1000), (999, 1000)]
        for overlap, chunk_size in valid_overlaps:
            result = validate_chunk_overlap(overlap, chunk_size)
            assert result == overlap

    def test_validate_chunk_overlap_invalid_type(self):
        """Test chunk overlap validation with invalid type."""
        invalid_overlaps = [("100", 1000), (100.5, 1000), ([], 1000), ({}, 1000)]
        for overlap, chunk_size in invalid_overlaps:
            with pytest.raises(ValidationError):
                validate_chunk_overlap(overlap, chunk_size)

    def test_validate_chunk_overlap_negative(self):
        """Test chunk overlap validation with negative value."""
        with pytest.raises(ValidationError):
            validate_chunk_overlap(-1, 1000)

    def test_validate_chunk_overlap_too_large(self):
        """Test chunk overlap validation with too large value."""
        with pytest.raises(ValidationError):
            validate_chunk_overlap(1000, 1000)

    def test_validate_chunk_overlap_equal_to_chunk_size(self):
        """Test chunk overlap validation with value equal to chunk size."""
        with pytest.raises(ValidationError):
            validate_chunk_overlap(1000, 1000)


if __name__ == "__main__":
    pytest.main([__file__])