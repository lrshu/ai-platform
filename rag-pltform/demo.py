"""
Demo script for the RAG platform showing core functionality.
"""
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.query import Query
from src.models.search_result import SearchResult
from src.models.conversation import Conversation
from src.models.response import Response
from src.services.pre_retrieval import PreRetrievalService
from src.services.post_retrieval import PostRetrievalService
# Note: GenerationService requires external dependencies, so we won't import it for this demo

def demo_pre_retrieval():
    """Demonstrate the pre-retrieval service."""
    print("=== Pre-Retrieval Service Demo ===")

    # Create pre-retrieval service
    pre_retrieval_service = PreRetrievalService()

    # Process a query
    original_query = "What is artificial intelligence and machine learning?"
    query = Query(original_text=original_query)

    print(f"Original query: {original_query}")

    # Process the query
    processed_query = pre_retrieval_service.process_query(query.original_text)
    print(f"Processed query: {processed_query.original_text}")
    print(f"Expanded query: {processed_query.expanded_text}")
    print()

def demo_post_retrieval():
    """Demonstrate the post-retrieval service."""
    print("=== Post-Retrieval Service Demo ===")

    # Create post-retrieval service
    post_retrieval_service = PostRetrievalService()

    # Create sample search results
    results = [
        SearchResult(
            query_id="query_1",
            chunk_id="chunk_1",
            score=0.85,
            rank=3,
            retrieval_method="vector"
        ),
        SearchResult(
            query_id="query_1",
            chunk_id="chunk_2",
            score=0.92,
            rank=1,
            retrieval_method="keyword"
        ),
        SearchResult(
            query_id="query_1",
            chunk_id="chunk_3",
            score=0.78,
            rank=5,
            retrieval_method="graph"
        ),
        SearchResult(
            query_id="query_1",
            chunk_id="chunk_4",
            score=0.88,
            rank=2,
            retrieval_method="vector"
        )
    ]

    print("Original results:")
    for result in results:
        print(f"  Rank {result.rank}: Score {result.score:.4f} ({result.retrieval_method})")

    # Create a query for processing
    query = Query(original_text="What is artificial intelligence?")

    # Process results
    processed_results = post_retrieval_service.process_results(results, query, rerank=False)

    print("\nProcessed results (sorted by score):")
    for result in processed_results:
        print(f"  Rank {result.rank}: Score {result.score:.4f} ({result.retrieval_method})")
    print()

def demo_generation():
    """Demonstrate the generation service concept."""
    print("=== Generation Service Concept Demo ===")

    print("The GenerationService would be used to:")
    print("1. Assemble prompts from queries and search results")
    print("2. Call the LLM API to generate responses")
    print("3. Create Response objects with the generated content")
    print()

    # Show what a response object looks like without requiring the service
    response = Response(
        query_id="query_123",
        content="Artificial intelligence (AI) refers to the simulation of human intelligence in machines...",
        model_used="qwen3-max"
    )

    print("Sample response object:")
    print(f"  Query ID: {response.query_id}")
    print(f"  Model used: {response.model_used}")
    print(f"  Content preview: {response.content[:50]}...")
    print()

def demo_conversation():
    """Demonstrate the conversation model."""
    print("=== Conversation Model Demo ===")

    # Create a conversation
    conversation = Conversation(
        session_id="session_123",
        context={"topic": "AI", "document_collection": "tech_papers"}
    )

    print("Initial conversation:")
    print(f"  Session ID: {conversation.session_id}")
    print(f"  Context: {conversation.context}")

    # Update context
    conversation.update_context({
        "subtopic": "machine_learning",
        "last_question": "What is AI?"
    })

    print("\nUpdated conversation:")
    print(f"  Context: {conversation.context}")
    print(f"  Context summary: {conversation.get_context_summary()}")
    print()

def main():
    """Run all demos."""
    print("RAG Platform Core Components Demo")
    print("=" * 40)
    print()

    demo_pre_retrieval()
    demo_post_retrieval()
    demo_generation()
    demo_conversation()

    print("Demo completed successfully!")

if __name__ == "__main__":
    main()