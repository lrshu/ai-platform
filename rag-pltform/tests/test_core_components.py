"""
Test core components of the RAG platform without external dependencies.
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.query import Query
from src.models.search_result import SearchResult
from src.models.conversation import Conversation
from src.models.response import Response

class TestCoreComponents(unittest.TestCase):
    """Test the core components of the RAG platform."""

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