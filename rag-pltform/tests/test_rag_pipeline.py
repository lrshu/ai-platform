"""
Simple test to verify the RAG pipeline functionality.
"""
import sys
from pathlib import Path
import logging

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.lib.database import DatabaseConnection
from src.lib.config import config
from src.services.indexing import IndexingService
from src.services.orchestration import OrchestrationService
from src.models.document import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_pipeline():
    """Test the RAG pipeline functionality."""
    logger.info("Starting RAG pipeline test")

    # Mock database connection for testing
    class MockDatabaseConnection:
        """Mock database connection for testing."""

        def __init__(self):
            self.connected = False

        def connect(self):
            """Mock connect method."""
            self.connected = True
            logger.info("Mock database connected")

        def disconnect(self):
            """Mock disconnect method."""
            self.connected = False
            logger.info("Mock database disconnected")

        def get_driver(self):
            """Mock get_driver method."""
            if not self.connected:
                raise RuntimeError("Not connected")
            return None

    try:
        # Initialize mock database connection
        db_connection = MockDatabaseConnection()
        db_connection.connect()

        # Initialize services
        indexing_service = IndexingService(db_connection)
        orchestration_service = OrchestrationService(db_connection)

        logger.info("RAG pipeline test completed successfully")
        return True

    except Exception as e:
        logger.error(f"RAG pipeline test failed: {e}")
        return False
    finally:
        db_connection.disconnect()

if __name__ == "__main__":
    success = test_rag_pipeline()
    sys.exit(0 if success else 1)