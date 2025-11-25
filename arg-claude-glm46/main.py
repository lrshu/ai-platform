#!/usr/bin/env python3
"""
Main entry point for the RAG backend system.
"""

import argparse
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import configuration
try:
    from src.config import load_env
    # Load environment variables
    load_env()
except ImportError:
    # Fallback if config module is not available
    import dotenv
    dotenv.load_dotenv()


def indexing_command(args):
    """Handle the indexing command."""
    # Import the actual indexing command implementation
    try:
        from src.cli.indexing import indexing_command as actual_indexing_command
        return actual_indexing_command(args)
    except ImportError as e:
        print(f"Error importing indexing command: {e}", file=sys.stderr)
        return 1


def search_command(args):
    """Handle the search command."""
    # Import the actual search command implementation
    try:
        from src.cli.search import search_command as actual_search_command
        return actual_search_command(args)
    except ImportError as e:
        print(f"Error importing search command: {e}", file=sys.stderr)
        return 1


def chat_command(args):
    """Handle the chat command."""
    # Import the actual chat command implementation
    try:
        from src.cli.chat import chat_command as actual_chat_command
        return actual_chat_command(args)
    except ImportError as e:
        print(f"Error importing chat command: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for the RAG backend system."""
    parser = argparse.ArgumentParser(description="RAG Backend System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Indexing command
    indexing_parser = subparsers.add_parser("indexing", help="Index a PDF document")
    indexing_parser.add_argument("--name", required=True, help="Unique name identifier for the document")
    indexing_parser.add_argument("--file", required=True, help="Path to the PDF file to be indexed")
    indexing_parser.set_defaults(func=indexing_command)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for information in indexed documents")
    search_parser.add_argument("--name", required=True, help="Name identifier of the document collection to search")
    search_parser.add_argument("--question", required=True, help="The question to search for")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    search_parser.add_argument("--expand-query", action="store_true", help="Enable query expansion")
    search_parser.add_argument("--rerank", action="store_true", help="Enable result reranking")
    search_parser.set_defaults(func=search_command)

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Engage in conversational QA")
    chat_parser.add_argument("--name", required=True, help="Name identifier of the document collection to use")
    chat_parser.add_argument("--user-id", help="User ID for the conversation")
    chat_parser.set_defaults(func=chat_command)

    # Parse arguments
    args = parser.parse_args()

    # Check if a command was provided
    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    # Execute the appropriate command
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())