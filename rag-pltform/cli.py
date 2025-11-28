"""
CLI application for the RAG platform.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.lib.database import DatabaseConnection
from src.lib.config import config
from src.services.indexing import IndexingService
from src.services.orchestration import OrchestrationService
from src.models.document import Document
from src.models.conversation import Conversation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGPlatformCLI:
    """CLI application for the RAG platform."""

    def __init__(self):
        """Initialize the CLI application."""
        self.db_connection: Optional[DatabaseConnection] = None
        self.indexing_service: Optional[IndexingService] = None
        self.orchestration_service: Optional[OrchestrationService] = None
        self.current_conversation: Optional[Conversation] = None

    def initialize(self):
        """Initialize the RAG platform services."""
        logger.info("Initializing RAG platform")

        # Validate configuration
        try:
            config.validate()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

        # Initialize database connection
        self.db_connection = DatabaseConnection(
            uri=config.database_url,
            user=config.database_user,
            password=config.database_password
        )

        try:
            # Connect to database
            self.db_connection.connect()
            logger.info("Connected to database successfully")

            # Initialize services
            self.indexing_service = IndexingService(self.db_connection)
            self.orchestration_service = OrchestrationService(self.db_connection)

            logger.info("RAG platform initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG platform: {e}")
            raise

    def shutdown(self):
        """Shutdown the RAG platform services."""
        if self.db_connection:
            self.db_connection.disconnect()
            logger.info("Disconnected from database")

    def index_document(self, document_id: str, name: str, content: str, metadata: dict = None):
        """Index a document."""
        if not self.indexing_service:
            raise RuntimeError("RAG platform not initialized")

        document = Document(
            id=document_id,
            name=name,
            content=content,
            metadata=metadata or {}
        )

        self.indexing_service.index_document(document, collection_name=name)
        logger.info(f"Document '{name}' indexed successfully")

    def search(self, collection_name: str, question: str, top_k: int = 5):
        """Perform a search."""
        if not self.orchestration_service:
            raise RuntimeError("RAG platform not initialized")

        search_results, chunk_contents = self.orchestration_service.search(
            name=collection_name,
            question=question,
            top_k=top_k
        )

        print(f"\nSearch Results for: {question}")
        print("=" * 50)
        for i, (result, content) in enumerate(zip(search_results, chunk_contents)):
            print(f"{i+1}. Score: {result.score:.4f}")
            print(f"   Content: {content[:200]}...")
            print()

    def chat(self, collection_name: str, question: str, top_k: int = 5):
        """Engage in a conversation."""
        if not self.orchestration_service:
            raise RuntimeError("RAG platform not initialized")

        response, conversation = self.orchestration_service.chat(
            name=collection_name,
            question=question,
            conversation=self.current_conversation,
            top_k=top_k
        )

        # Update current conversation
        self.current_conversation = conversation

        print(f"\nQuestion: {question}")
        print(f"Answer: {response.content}")
        print()

    def run(self):
        """Run the CLI application."""
        try:
            self.initialize()

            print("RAG Platform CLI")
            print("=" * 20)
            print("Commands:")
            print("  index <id> <name> <content> - Index a document")
            print("  search <collection> <question> - Search for information")
            print("  chat <collection> <question> - Chat about documents")
            print("  quit - Exit the application")
            print()

            while True:
                try:
                    command = input("> ").strip().split()
                    if not command:
                        continue

                    if command[0] == "quit":
                        break
                    elif command[0] == "index" and len(command) >= 4:
                        document_id = command[1]
                        name = command[2]
                        content = " ".join(command[3:])
                        self.index_document(document_id, name, content)
                    elif command[0] == "search" and len(command) >= 3:
                        collection_name = command[1]
                        question = " ".join(command[2:])
                        self.search(collection_name, question)
                    elif command[0] == "chat" and len(command) >= 3:
                        collection_name = command[1]
                        question = " ".join(command[2:])
                        self.chat(collection_name, question)
                    else:
                        print("Invalid command. Type 'quit' to exit.")
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")

        finally:
            self.shutdown()

def main():
    """Main entry point."""
    cli = RAGPlatformCLI()
    cli.run()

if __name__ == "__main__":
    main()