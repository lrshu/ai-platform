"""
Simple integration test to verify the core services work together.
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.indexing import IndexingService
from src.services.orchestration import OrchestrationService
from src.services.pre_retrieval import PreRetrievalService
from src.services.retrieval import RetrievalService
from src.services.post_retrieval import PostRetrievalService
from src.services.generation import GenerationService

class TestServices(unittest.TestCase):
    """Test the core services of the RAG platform."""

    def test_service_initialization(self):
        """Test that all services can be initialized."""
        # Create mock database connection
        mock_db = Mock()

        # Test service initialization
        indexing_service = IndexingService(mock_db)
        pre_retrieval_service = PreRetrievalService()
        retrieval_service = RetrievalService(mock_db)
        post_retrieval_service = PostRetrievalService()
        generation_service = GenerationService()
        orchestration_service = OrchestrationService(
            mock_db,
            pre_retrieval_service,
            retrieval_service,
            post_retrieval_service,
            generation_service
        )

        # Verify services were created
        self.assertIsNotNone(indexing_service)
        self.assertIsNotNone(pre_retrieval_service)
        self.assertIsNotNone(retrieval_service)
        self.assertIsNotNone(post_retrieval_service)
        self.assertIsNotNone(generation_service)
        self.assertIsNotNone(orchestration_service)

if __name__ == "__main__":
    unittest.main()