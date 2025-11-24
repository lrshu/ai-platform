"""
Chat CLI command for the RAG backend system.
"""

import argparse
import sys
from typing import Dict, Any, Optional
from src.services.chat_service import get_chat_service
from src.lib.exceptions import ChatError
from src.lib.logger import get_logger
from src.lib.validation import validate_collection_name, validate_question, validate_session_id, validate_top_k, ValidationError
import logging

logger = get_logger(__name__)


def chat_with_documents(name: str, question: str, session_id: Optional[str] = None,
                       top_k: int = 5, enable_query_expansion: bool = True,
                       enable_reranking: bool = True, enable_vector_search: bool = True,
                       enable_graph_search: bool = True) -> Dict[str, Any]:
    """
    Generate answers to questions based on indexed document content.

    Args:
        name: Name/identifier for the document collection
        question: The question to answer
        session_id: Identifier for the chat session (for context)
        top_k: Number of results to return
        enable_query_expansion: Whether to expand the query
        enable_reranking: Whether to re-rank results
        enable_vector_search: Whether to perform vector search
        enable_graph_search: Whether to perform graph search

    Returns:
        Dictionary containing the answer and sources
    """
    try:
        # Validate inputs
        validate_collection_name(name)
        validate_question(question)
        validate_top_k(top_k)

        if session_id:
            validate_session_id(session_id)

        # Get chat service
        chat_service = get_chat_service()

        # Have conversation with documents
        response = chat_service.chat_with_documents(
            collection_name=name,
            question=question,
            session_id=session_id,
            top_k=top_k,
            enable_query_expansion=enable_query_expansion,
            enable_reranking=enable_reranking,
            enable_vector_search=enable_vector_search,
            enable_graph_search=enable_graph_search
        )

        logger.info(f"Chat completed for session {response['session_id']}")

        # Display results
        print(f"Answer: {response['answer']}")
        print(f"\nSession ID: {response['session_id']}")

        if response['sources']:
            print(f"\nSources ({len(response['sources'])} found):")
            for i, source in enumerate(response['sources'][:3]):  # Show top 3 sources
                print(f"  [{i+1}] {source.get('source', 'Unknown source')} (Score: {source.get('relevance_score', 0.0):.3f})")

        if response['citations']:
            print(f"\nCitations:")
            for citation in response['citations']:
                print(f"  [{citation['number']}] {citation['source']}")

        return response

    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        print(f"Error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        print(f"Error: Chat failed: {e}")
        raise


def main():
    """Main entry point for the chat CLI command."""
    parser = argparse.ArgumentParser(description="Have a conversation about indexed documents in the RAG system")
    parser.add_argument('--name', required=True, help='Collection name')
    parser.add_argument('--question', required=True, help='Question to ask')
    parser.add_argument('--session-id', help='Session identifier for context')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    parser.add_argument('--no-expand', action='store_true', help='Disable query expansion')
    parser.add_argument('--no-rerank', action='store_true', help='Disable result re-ranking')
    parser.add_argument('--no-vector', action='store_true', help='Disable vector search')
    parser.add_argument('--no-graph', action='store_true', help='Disable graph search')

    # Parse arguments
    args = parser.parse_args()

    try:
        chat_with_documents(
            name=args.name,
            question=args.question,
            session_id=args.session_id,
            top_k=args.top_k,
            enable_query_expansion=not args.no_expand,
            enable_reranking=not args.no_rerank,
            enable_vector_search=not args.no_vector,
            enable_graph_search=not args.no_graph
        )
        return 0
    except Exception as e:
        logger.error(f"Chat command failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())