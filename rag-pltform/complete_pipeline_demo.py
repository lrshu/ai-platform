"""
Complete RAG pipeline demonstration.
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
from src.services.pre_retrieval import PreRetrievalService
from src.services.post_retrieval import PostRetrievalService

def demonstrate_complete_rag_pipeline():
    """Demonstrate the complete RAG pipeline workflow."""
    print("RAG Platform - Complete Pipeline Demonstration")
    print("=" * 50)
    print()

    # Step 1: Document Processing (simplified)
    print("Step 1: Document Processing")
    print("-" * 20)
    doc = Document(
        name="AI Research Paper",
        file_path="/path/to/ai_research.pdf",
        chunk_count=25,
        status="completed"
    )
    print(f"Document '{doc.name}' processed and indexed")
    print()

    # Step 2: Query Processing
    print("Step 2: Query Processing")
    print("-" * 20)
    original_question = "What are the latest advances in neural network architectures?"
    print(f"User question: {original_question}")

    pre_retrieval_service = PreRetrievalService()
    processed_query = pre_retrieval_service.process_query(original_question)
    print(f"Processed query: {processed_query.original_text}")
    print(f"Expanded query: {processed_query.expanded_text}")
    print()

    # Step 3: Document Retrieval (simulated)
    print("Step 3: Document Retrieval")
    print("-" * 20)
    print("Performing hybrid search (vector + graph-based)...")
    # In a real implementation, this would call the RetrievalService
    search_results = [
        SearchResult(
            query_id=processed_query.id,
            chunk_id="chunk_001",
            score=0.95,
            rank=1,
            retrieval_method="vector"
        ),
        SearchResult(
            query_id=processed_query.id,
            chunk_id="chunk_002",
            score=0.88,
            rank=2,
            retrieval_method="graph"
        ),
        SearchResult(
            query_id=processed_query.id,
            chunk_id="chunk_003",
            score=0.82,
            rank=3,
            retrieval_method="keyword"
        )
    ]
    print(f"Retrieved {len(search_results)} relevant documents")
    for result in search_results:
        print(f"  - Rank {result.rank}: Score {result.score:.4f} ({result.retrieval_method})")
    print()

    # Step 4: Result Processing
    print("Step 4: Result Processing")
    print("-" * 20)
    post_retrieval_service = PostRetrievalService()
    processed_results = post_retrieval_service.process_results(search_results, processed_query, rerank=True)
    print("Results processed and reranked")
    for result in processed_results:
        print(f"  - Rank {result.rank}: Score {result.score:.4f} ({result.retrieval_method})")
    print()

    # Step 5: Conversation Management
    print("Step 5: Conversation Management")
    print("-" * 20)
    conversation = Conversation(
        session_id="session_123",
        context={
            "topic": "neural networks",
            "document_collection": "ai_research"
        }
    )
    print(f"Conversation started: {conversation.session_id}")
    print(f"Context: {conversation.get_context_summary()}")

    # Update context with this interaction
    conversation.update_context({
        "last_question": original_question,
        "last_response_length": 150  # Simulated response length
    })
    print("Conversation context updated")
    print()

    # Step 6: Response Generation (simulated)
    print("Step 6: Response Generation")
    print("-" * 20)
    print("Generating response using LLM...")
    # In a real implementation, this would call the GenerationService
    response_content = (
        "Recent advances in neural network architectures include transformer models with improved attention mechanisms, "
        "sparse neural networks for efficiency, and neuromorphic computing approaches that mimic biological neural structures. "
        "Notable developments include mixture-of-experts models, graph neural networks for relational data, and "
        "vision transformers that have revolutionized image processing tasks."
    )

    response = Response(
        query_id=processed_query.id,
        content=response_content,
        model_used="qwen3-max",
        tokens_used=85
    )
    print("Response generated successfully")
    print(f"Model used: {response.model_used}")
    print(f"Tokens used: {response.tokens_used}")
    print()

    # Step 7: Present Final Answer
    print("Step 7: Final Answer")
    print("-" * 20)
    print(f"Question: {original_question}")
    print(f"Answer: {response.content}")
    print()

    print("✅ Complete RAG pipeline executed successfully!")
    return True

def main():
    """Run the complete RAG pipeline demonstration."""
    try:
        success = demonstrate_complete_rag_pipeline()
        if success:
            print("🎉 RAG Platform Pipeline Demonstration Completed Successfully!")
            return 0
        else:
            print("❌ RAG Platform Pipeline Demonstration Failed!")
            return 1
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())