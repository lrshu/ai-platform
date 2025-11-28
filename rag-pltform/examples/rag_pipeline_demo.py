"""
Example script demonstrating the RAG pipeline functionality.
"""
import os
import sys
import logging
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.lib.database import DatabaseConnection
from src.lib.config import config
from src.services.indexing import IndexingService
from src.services.orchestration import OrchestrationService
from src.models.document import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Demonstrate the RAG pipeline functionality."""
    logger.info("Starting RAG pipeline demo")

    # Validate configuration
    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        return

    # Initialize database connection
    db_connection = DatabaseConnection(
        uri=config.database_url,
        user=config.database_user,
        password=config.database_password
    )

    try:
        # Connect to database
        db_connection.connect()
        logger.info("Connected to database successfully")

        # Initialize services
        indexing_service = IndexingService(db_connection)
        orchestration_service = OrchestrationService(db_connection)

        # Example document for indexing
        sample_document = Document(
            id="sample_doc_1",
            name="Sample Document",
            content="""
            The field of artificial intelligence (AI) has seen tremendous growth in recent years.
            Machine learning, a subset of AI, enables computers to learn from data without being
            explicitly programmed. Deep learning, a further subset of machine learning, uses
            neural networks with multiple layers to model complex patterns in data.

            Natural language processing (NLP) is another important area of AI that focuses on
            the interaction between computers and humans through natural language. Applications
            of NLP include machine translation, sentiment analysis, and chatbots.

            Computer vision is the field of AI that enables computers to interpret and understand
            visual information from the world. This includes image recognition, object detection,
            and video analysis. Self-driving cars heavily rely on computer vision technologies.

            Reinforcement learning is a type of machine learning where an agent learns to make
            decisions by performing actions in an environment to maximize some notion of cumulative reward.
            """,
            metadata={
                "source": "sample",
                "category": "technology",
                "author": "AI Researcher"
            }
        )

        # Index the document
        logger.info("Indexing sample document")
        indexing_service.index_document(sample_document, collection_name="sample_collection")
        logger.info("Document indexed successfully")

        # Perform a search
        logger.info("Performing search operation")
        search_results, chunk_contents = orchestration_service.search(
            name="sample_collection",
            question="What is natural language processing?",
            top_k=3
        )

        logger.info(f"Found {len(search_results)} search results")
        for i, (result, content) in enumerate(zip(search_results, chunk_contents)):
            logger.info(f"Result {i+1}: Score={result.score:.4f}, Content={content[:100]}...")

        # Engage in a conversation
        logger.info("Starting conversation")
        response, conversation = orchestration_service.chat(
            name="sample_collection",
            question="What is natural language processing?",
            top_k=3
        )

        logger.info(f"Response: {response.content}")
        logger.info(f"Conversation ID: {conversation.id}")

        # Follow-up question
        logger.info("Asking follow-up question")
        followup_response, updated_conversation = orchestration_service.chat(
            name="sample_collection",
            question="What are some applications of NLP?",
            conversation=conversation,
            top_k=3
        )

        logger.info(f"Follow-up response: {followup_response.content}")

    except Exception as e:
        logger.error(f"Error in RAG pipeline demo: {e}")
        raise
    finally:
        # Disconnect from database
        db_connection.disconnect()
        logger.info("Disconnected from database")

if __name__ == "__main__":
    main()