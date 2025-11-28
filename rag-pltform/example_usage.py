"""
Example usage of the RAG platform components.
"""
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.document import Document
from src.models.query import Query
from src.models.search_result import SearchResult
from src.models.conversation import Conversation
from src.models.response import Response

def example_document_creation():
    """Example of creating and using Document objects."""
    print("=== Document Creation Example ===")

    # Create a document
    doc = Document(
        name="AI Research Paper",
        file_path="/path/to/ai_paper.pdf",
        chunk_count=15,
        status="completed"
    )

    print(f"Created document: {doc}")
    print(f"Document ID: {doc.id}")
    print(f"Document name: {doc.name}")
    print(f"Chunk count: {doc.chunk_count}")
    print(f"Status: {doc.status}")

    # Convert to dictionary and back
    doc_dict = doc.to_dict()
    print(f"Document as dict: {doc_dict}")

    # Restore from dictionary
    restored_doc = Document.from_dict(doc_dict)
    print(f"Restored document: {restored_doc}")
    print()

def example_query_processing():
    """Example of processing queries."""
    print("=== Query Processing Example ===")

    # Create a query
    query = Query(
        original_text="What are the applications of machine learning in healthcare?",
        user_id="user_123"
    )

    print(f"Original query: {query.original_text}")
    print(f"Query ID: {query.id}")
    print(f"User ID: {query.user_id}")

    # Simulate query processing (normally done by PreRetrievalService)
    query.expanded_text = "machine learning applications healthcare medical diagnosis treatment prediction"
    print(f"Expanded query: {query.expanded_text}")
    print()

def example_search_results():
    """Example of handling search results."""
    print("=== Search Results Example ===")

    # Create search results
    results = [
        SearchResult(
            query_id="query_123",
            chunk_id="chunk_001",
            score=0.95,
            rank=1,
            retrieval_method="vector"
        ),
        SearchResult(
            query_id="query_123",
            chunk_id="chunk_002",
            score=0.88,
            rank=2,
            retrieval_method="keyword"
        ),
        SearchResult(
            query_id="query_123",
            chunk_id="chunk_003",
            score=0.82,
            rank=3,
            retrieval_method="graph"
        )
    ]

    print("Search results:")
    for result in results:
        print(f"  {result}")
    print()

def example_conversation_management():
    """Example of conversation management."""
    print("=== Conversation Management Example ===")

    # Create a conversation
    conversation = Conversation(
        session_id="session_xyz",
        context={
            "topic": "artificial intelligence",
            "document_collection": "research_papers"
        }
    )

    print(f"New conversation: {conversation}")
    print(f"Session ID: {conversation.session_id}")
    print(f"Context: {conversation.context}")

    # Update conversation context
    conversation.update_context({
        "current_subtopic": "neural networks",
        "previous_questions": ["What is AI?", "How does machine learning work?"]
    })

    print(f"Updated context: {conversation.context}")
    print(f"Context summary: {conversation.get_context_summary()}")
    print()

def example_response_generation():
    """Example of response generation."""
    print("=== Response Generation Example ===")

    # Create a response
    response = Response(
        query_id="query_123",
        content="Machine learning has numerous applications in healthcare, including medical image analysis, drug discovery, personalized treatment recommendations, and predictive analytics for patient outcomes.",
        model_used="qwen3-max",
        tokens_used=45
    )

    print(f"Generated response: {response}")
    print(f"Response content: {response.content}")
    print(f"Model used: {response.model_used}")
    print(f"Tokens used: {response.tokens_used}")

    # Update token count
    response.update_tokens(50)
    print(f"Updated tokens used: {response.tokens_used}")
    print()

def main():
    """Run all examples."""
    print("RAG Platform Usage Examples")
    print("=" * 30)
    print()

    example_document_creation()
    example_query_processing()
    example_search_results()
    example_conversation_management()
    example_response_generation()

    print("All examples completed successfully!")

if __name__ == "__main__":
    main()