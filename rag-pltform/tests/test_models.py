"""
Unit tests for the RAG platform core components.
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.document import Document
from src.models.query import Query
from src.models.search_result import SearchResult
from src.models.conversation import Conversation
from src.models.response import Response

class TestModels(unittest.TestCase):
    """Test the core models of the RAG platform."""

    def test_document_model(self):
        """Test the Document model."""
        doc = Document(
            id="test_doc_1",
            name="Test Document",
            file_path="/path/to/test.pdf",
            chunk_count=5,
            status="completed"
        )

        self.assertEqual(doc.id, "test_doc_1")
        self.assertEqual(doc.name, "Test Document")
        self.assertEqual(doc.file_path, "/path/to/test.pdf")
        self.assertEqual(doc.chunk_count, 5)
        self.assertEqual(doc.status, "completed")

        # Test to_dict and from_dict
        doc_dict = doc.to_dict()
        restored_doc = Document.from_dict(doc_dict)
        self.assertEqual(doc.id, restored_doc.id)
        self.assertEqual(doc.name, restored_doc.name)
        self.assertEqual(doc.file_path, restored_doc.file_path)
        self.assertEqual(doc.chunk_count, restored_doc.chunk_count)
        self.assertEqual(doc.status, restored_doc.status)

    def test_query_model(self):
        """Test the Query model."""
        query = Query(
            original_text="What is machine learning?",
            user_id="user_123"
        )

        self.assertEqual(query.original_text, "What is machine learning?")
        self.assertEqual(query.user_id, "user_123")

        # Test to_dict and from_dict
        query_dict = query.to_dict()
        restored_query = Query.from_dict(query_dict)
        self.assertEqual(query.original_text, restored_query.original_text)
        self.assertEqual(query.user_id, restored_query.user_id)

    def test_search_result_model(self):
        """Test the SearchResult model."""
        result = SearchResult(
            query_id="query_123",
            chunk_id="chunk_123",
            score=0.95,
            rank=1,
            retrieval_method="vector"
        )

        self.assertEqual(result.query_id, "query_123")
        self.assertEqual(result.chunk_id, "chunk_123")
        self.assertEqual(result.score, 0.95)
        self.assertEqual(result.rank, 1)
        self.assertEqual(result.retrieval_method, "vector")

        # Test to_dict and from_dict
        result_dict = result.to_dict()
        restored_result = SearchResult.from_dict(result_dict)
        self.assertEqual(result.query_id, restored_result.query_id)
        self.assertEqual(result.chunk_id, restored_result.chunk_id)
        self.assertEqual(result.score, restored_result.score)
        self.assertEqual(result.rank, restored_result.rank)
        self.assertEqual(result.retrieval_method, restored_result.retrieval_method)

    def test_conversation_model(self):
        """Test the Conversation model."""
        conversation = Conversation(
            session_id="session_123",
            context={"topic": "AI"}
        )

        self.assertEqual(conversation.session_id, "session_123")
        self.assertEqual(conversation.context["topic"], "AI")

        # Test context update
        conversation.update_context({"subtopic": "ML"})
        self.assertEqual(conversation.context["topic"], "AI")
        self.assertEqual(conversation.context["subtopic"], "ML")

        # Test to_dict and from_dict
        conv_dict = conversation.to_dict()
        restored_conv = Conversation.from_dict(conv_dict)
        self.assertEqual(conversation.session_id, restored_conv.session_id)
        self.assertEqual(conversation.context["topic"], restored_conv.context["topic"])

    def test_response_model(self):
        """Test the Response model."""
        response = Response(
            query_id="query_123",
            content="Machine learning is a subset of AI.",
            model_used="qwen3-max"
        )

        self.assertEqual(response.query_id, "query_123")
        self.assertEqual(response.content, "Machine learning is a subset of AI.")
        self.assertEqual(response.model_used, "qwen3-max")

        # Test to_dict and from_dict
        resp_dict = response.to_dict()
        restored_resp = Response.from_dict(resp_dict)
        self.assertEqual(response.query_id, restored_resp.query_id)
        self.assertEqual(response.content, restored_resp.content)
        self.assertEqual(response.model_used, restored_resp.model_used)

if __name__ == "__main__":
    unittest.main()