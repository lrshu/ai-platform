"""
Search CLI command for the RAG backend system.
"""

import argparse
import sys
from typing import List
from src.services.retrieval_service import get_retrieval_service
from src.lib.exceptions import SearchError
from src.lib.logger import get_logger
from src.lib.validation import validate_collection_name, validate_question, validate_top_k, ValidationError
import logging

logger = get_logger(__name__)


def search_documents(name: str, question: str, top_k: int = 5,
                    enable_query_expansion: bool = True, enable_reranking: bool = True,
                    enable_vector_search: bool = True, enable_graph_search: bool = True) -> List[dict]:
    """
    Search for relevant document chunks using hybrid retrieval.

    Args:
        name: Name/identifier for the document collection
        question: The question to search for
        top_k: Number of results to return
        enable_query_expansion: Whether to expand the query
        enable_reranking: Whether to re-rank results
        enable_vector_search: Whether to perform vector search
        enable_graph_search: Whether to perform graph search

    Returns:
        List of search results
    """
    try:
        # Validate inputs
        validate_collection_name(name)
        validate_question(question)
        validate_top_k(top_k)

        # Get retrieval service
        retrieval_service = get_retrieval_service()

        # Perform hybrid search
        results = retrieval_service.hybrid_search(
            query_text=question,
            collection_name=name,
            top_k=top_k,
            enable_query_expansion=enable_query_expansion,
            enable_reranking=enable_reranking,
            enable_vector_search=enable_vector_search,
            enable_graph_search=enable_graph_search
        )

        # Format results for display
        formatted_results = []
        for result in results:
            formatted_results.append({
                "chunk_id": result.chunk_id,
                "relevance_score": result.relevance_score,
                "rank": result.rank
            })

        logger.info(f"Search completed with {len(results)} results")
        print(f"Search completed. Found {len(results)} relevant document chunks.")

        # Display results
        for result in results:
            print(f"Rank {result.rank}: Chunk {result.chunk_id} (Score: {result.relevance_score:.3f})")

        return formatted_results

    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        print(f"Error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        print(f"Error: Search failed: {e}")
        raise


def main():
    """Main entry point for the search CLI command."""
    parser = argparse.ArgumentParser(description="Search for relevant document chunks in the RAG system")
    parser.add_argument('--name', required=True, help='Collection name')
    parser.add_argument('--question', required=True, help='Question to search for')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    parser.add_argument('--no-expand', action='store_true', help='Disable query expansion')
    parser.add_argument('--no-rerank', action='store_true', help='Disable result re-ranking')
    parser.add_argument('--no-vector', action='store_true', help='Disable vector search')
    parser.add_argument('--no-graph', action='store_true', help='Disable graph search')

    # Parse arguments
    args = parser.parse_args()

    try:
        search_documents(
            name=args.name,
            question=args.question,
            top_k=args.top_k,
            enable_query_expansion=not args.no_expand,
            enable_reranking=not args.no_rerank,
            enable_vector_search=not args.no_vector,
            enable_graph_search=not args.no_graph
        )
        return 0
    except Exception as e:
        logger.error(f"Search command failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())