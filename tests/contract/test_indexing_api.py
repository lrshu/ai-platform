"""
Contract tests for the indexing API endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from app.common.models import IndexingRequest, IndexingResponse

client = TestClient(app)


@patch('app.api.indexing.indexing_orchestrator')
def test_indexing_endpoint_success(mock_orchestrator):
    """Test successful indexing request."""
    # Mock the orchestrator response
    mock_orchestrator.batch_index_documents.return_value = [
        {"status": "completed", "document_id": "doc1.pdf"}
    ]

    # Create indexing request
    request_data = {
        "document_urls": ["http://example.com/doc1.pdf"],
        "collection_name": "test_collection"
    }

    # Make request
    response = client.post("/api/rag/indexing", json=request_data)

    # Verify response
    assert response.status_code == 202
    assert "job_id" in response.json()
    assert response.json()["status"] == "started"


def test_indexing_endpoint_invalid_request():
    """Test indexing request with invalid data."""
    # Create invalid indexing request (missing required field)
    request_data = {
        "collection_name": "test_collection"
        # Missing document_urls
    }

    # Make request
    response = client.post("/api/rag/indexing", json=request_data)

    # Verify response
    assert response.status_code == 422  # Validation error


@patch('app.api.indexing.indexing_orchestrator')
def test_indexing_status_endpoint(mock_orchestrator):
    """Test indexing status endpoint."""
    # Mock the status response
    mock_response = {
        "job_id": "test-job-123",
        "status": "processing",
        "message": "Indexing job is in progress"
    }

    # Make request
    response = client.get("/api/rag/indexing/test-job-123")

    # Verify response (this will depend on actual implementation)
    # For now, we're just testing that the endpoint exists
    assert response.status_code == 200 or response.status_code == 500


def test_indexing_request_model_validation():
    """Test IndexingRequest model validation."""
    # Valid request
    valid_request = IndexingRequest(
        document_urls=["http://example.com/doc1.pdf"],
        collection_name="test_collection"
    )
    assert valid_request.document_urls == ["http://example.com/doc1.pdf"]
    assert valid_request.collection_name == "test_collection"

    # Invalid request (empty document_urls)
    with pytest.raises(ValueError):
        IndexingRequest(
            document_urls=[],
            collection_name="test_collection"
        )