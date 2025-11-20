"""
Example script demonstrating how to use the RAG backend for document search.
"""

import asyncio
from app.common.factory import provider_factory
from app.common.models import SearchRequest


async def main():
    """Main function to demonstrate document search."""
    # Create search request
    search_request = SearchRequest(
        query="What is the RAG backend?",
        use_hyde=True,
        use_rerank=True,
        top_k=5
    )

    print(f"Search query: {search_request.query}")
    print(f"Use HyDE: {search_request.use_hyde}")
    print(f"Use reranking: {search_request.use_rerank}")
    print(f"Top K results: {search_request.top_k}")

    # In a complete implementation, you would:
    # 1. Create the retrieval components
    # 2. Generate query embedding
    # 3. Perform vector search
    # 4. Apply reranking if requested
    # 5. Generate answer using LLM

    print("\nIn a complete implementation, this would:")
    print("1. Generate query embedding using Qwen embedder")
    print("2. Perform vector search in Memgraph database")
    print("3. Apply HyDE query expansion if requested")
    print("4. Apply reranking if requested")
    print("5. Generate answer using Qwen generator")
    print("6. Return results with streaming response")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())