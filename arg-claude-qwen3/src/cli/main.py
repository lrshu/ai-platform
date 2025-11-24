"""
Main CLI entry point for the RAG backend system.
"""

import argparse
import sys


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="RAG Backend System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Indexing command
    indexing_parser = subparsers.add_parser('indexing', help='Index a document')
    indexing_parser.add_argument('--name', required=True, help='Collection name')
    indexing_parser.add_argument('--file', required=True, help='Path to PDF file')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('--name', required=True, help='Collection name')
    search_parser.add_argument('--question', required=True, help='Question to search for')
    search_parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    search_parser.add_argument('--no-expand', action='store_true', help='Disable query expansion')
    search_parser.add_argument('--no-rerank', action='store_true', help='Disable result re-ranking')
    search_parser.add_argument('--no-vector', action='store_true', help='Disable vector search')
    search_parser.add_argument('--no-graph', action='store_true', help='Disable graph search')

    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Chat with documents')
    chat_parser.add_argument('--name', required=True, help='Collection name')
    chat_parser.add_argument('--question', required=True, help='Question to ask')
    chat_parser.add_argument('--session-id', help='Session identifier for context')
    chat_parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    chat_parser.add_argument('--no-expand', action='store_true', help='Disable query expansion')
    chat_parser.add_argument('--no-rerank', action='store_true', help='Disable result re-ranking')
    chat_parser.add_argument('--no-vector', action='store_true', help='Disable vector search')
    chat_parser.add_argument('--no-graph', action='store_true', help='Disable graph search')

    # Parse arguments first to handle help without requiring environment variables
    args = parser.parse_args()

    # Only import the implementation functions when actually needed
    if args.command == 'indexing':
        from src.cli.indexing import index_document
        try:
            index_document(args.name, args.file)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'search':
        from src.cli.search import search_documents
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
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'chat':
        from src.cli.chat import chat_with_documents
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
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()