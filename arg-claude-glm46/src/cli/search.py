"""CLI handler for the search command."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.retrieval.orchestrator import search_orchestrator
from src.lib.logging_config import logger


def search_command(args):
    """
    Handle the search command.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Validate input parameters
        if not args.name or not args.name.strip():
            logger.error("Document name is required for search command")
            print("Error: Document name is required", file=sys.stderr)
            return 1

        if not args.question or not args.question.strip():
            logger.error("Question is required for search command")
            print("Error: Question is required", file=sys.stderr)
            return 1

        if args.top_k <= 0:
            logger.error("Top K must be a positive integer")
            print("Error: Top K must be a positive integer", file=sys.stderr)
            return 1

        logger.info(f"Search command invoked with parameters:")
        logger.info(f"  Document name: {args.name}")
        logger.info(f"  Question: {args.question}")
        logger.info(f"  Top K: {args.top_k}")
        logger.info(f"  Expand query: {args.expand_query}")
        logger.info(f"  Re-rank: {args.rerank}")

        print(f"Searching for '{args.question}' in document collection '{args.name}'...")
        print(f"Parameters: top_k={args.top_k}, expand_query={args.expand_query}, rerank={args.rerank}")

        # Call the search orchestrator
        results = search_orchestrator.search(
            document_name=args.name.strip(),
            query_text=args.question.strip(),
            top_k=args.top_k,
            expand_query=args.expand_query,
            rerank=args.rerank
        )

        # Print results
        if results:
            print(f"\nFound {len(results)} relevant results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Score: {result.get('score', 0):.4f}")
                if 'vector_score' in result:
                    print(f"   Vector Score: {result['vector_score']:.4f}")
                if 'graph_score' in result:
                    print(f"   Graph Score: {result['graph_score']:.4f}")
                if 'reranked_score' in result:
                    print(f"   Re-ranked Score: {result['reranked_score']}")
                print(f"   Content: {result['content'][:200]}...")
            logger.info(f"Search completed successfully with {len(results)} results")
        else:
            print("\nNo relevant results found.")
            logger.info("Search completed with no results found")
            return 4  # No results found exit code

        return 0

    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        logger.exception("Full traceback:")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # This is just for testing the module directly
    pass