"""CLI interface for RAG backend operations."""

import argparse
import json
import sys
import time
from pathlib import Path

from src.config.logging import get_logger, setup_logging
from src.config.settings import settings
from src.models.query import QueryOptions
from src.rag.orchestration import chat_with_documents, index_document, search_documents

logger = get_logger(__name__)


def cmd_indexing(args: argparse.Namespace) -> int:
    """Handle indexing command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Validate file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            return 1

        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"Error: File exceeds 10MB limit (actual: {size_mb:.1f}MB)", file=sys.stderr)
            return 1

        if not file_path.suffix.lower() == ".pdf":
            print("Error: File must be a PDF (.pdf extension required)", file=sys.stderr)
            return 1

        # Start indexing
        start_time = time.time()
        if not args.json:
            print(f"Indexing document: {file_path.name}")
            if start_time:  # Show progress for operations >2s
                print("Processing...", end="", flush=True)

        options = {}
        if args.chunk_size:
            options["chunk_size"] = args.chunk_size
        if args.chunk_overlap:
            options["chunk_overlap"] = args.chunk_overlap

        document_id = index_document(args.name, str(file_path), options)
        duration = time.time() - start_time

        # Output result
        if args.json:
            result = {
                "status": "success",
                "document_id": str(document_id),
                "filename": file_path.name,
                "duration_seconds": round(duration, 1),
            }
            print(json.dumps(result, indent=2))
        else:
            print("\r✓ Document indexed successfully")
            print(f"Document ID: {document_id}")
            print(f"Filename: {file_path.name}")
            print(f"Time taken: {duration:.1f}s")

        return 0

    except FileNotFoundError as e:
        error_msg = f"Error: {e}"
        if args.json:
            print(json.dumps({"status": "error", "message": error_msg}), file=sys.stderr)
        else:
            print(error_msg, file=sys.stderr)
        return 1

    except ValueError as e:
        error_msg = f"Error: {e}"
        if args.json:
            print(json.dumps({"status": "error", "message": error_msg}), file=sys.stderr)
        else:
            print(error_msg, file=sys.stderr)
        return 1

    except Exception as e:
        error_msg = f"Error: Failed to index document: {e}"
        if args.json:
            print(json.dumps({"status": "error", "message": error_msg}), file=sys.stderr)
        else:
            print(error_msg, file=sys.stderr)
        logger.error(f"Indexing failed: {e}", exc_info=True)
        return 2


def cmd_search(args: argparse.Namespace) -> int:
    """Handle search command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        options = QueryOptions(
            top_k=args.top_k,
            expand_query=args.expand_query,
            enable_reranking=not args.no_rerank,
            enable_vector_search=not args.vector_only or True,
            enable_keyword_search=not args.vector_only,
            enable_graph_search=not args.vector_only,
        )

        results = search_documents(args.name, args.question, options)

        if args.json:
            output = {
                "status": "success",
                "query": args.question,
                "results": results,
                "count": len(results),
            }
            print(json.dumps(output, indent=2))
        else:
            if results:
                print(f"Found {len(results)} relevant chunks:\n")
                for i, result in enumerate(results, 1):
                    print(f"[{i}] Similarity: {result['similarity_score']:.2f} | "
                          f"Source: {result['metadata']['filename']} "
                          f"(chunk {result['metadata']['position']})")
                    print(result['text'][:200] + "...\n")
            else:
                print("No relevant results found for query")

        return 0

    except Exception as e:
        error_msg = f"Error: Search failed: {e}"
        if args.json:
            print(json.dumps({"status": "error", "message": error_msg}), file=sys.stderr)
        else:
            print(error_msg, file=sys.stderr)
        logger.error(f"Search failed: {e}", exc_info=True)
        return 2


def cmd_chat(args: argparse.Namespace) -> int:
    """Handle chat command (interactive REPL).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for normal exit, 1 for error)
    """
    try:
        print(f"RAG Chat - Namespace: {args.name}")
        print("Type 'exit', 'quit', or Ctrl+C to end session.\n")

        options = QueryOptions(
            top_k=args.top_k,
            expand_query=args.expand_query,
            enable_reranking=not args.no_rerank,
        )

        while True:
            try:
                question = input("You: ").strip()

                if question.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    return 0

                if not question:
                    continue

                # Generate response
                response = chat_with_documents(args.name, question, options)

                if args.json:
                    output = {
                        "query": question,
                        "answer": response.answer_text,
                        "citations": [c.model_dump() for c in response.citations],
                        "duration_seconds": response.generation_duration_ms / 1000,
                    }
                    print(json.dumps(output, indent=2))
                else:
                    print(f"Assistant: {response.answer_text}\n")
                    if response.citations:
                        print("Sources:")
                        for i, citation in enumerate(response.citations, 1):
                            print(f"[{i}] {citation.filename}")
                    print()

            except KeyboardInterrupt:
                print("\nGoodbye!")
                return 2

    except Exception as e:
        print(f"Error: Chat session failed: {e}", file=sys.stderr)
        logger.error(f"Chat failed: {e}", exc_info=True)
        return 2


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="RAG Backend CLI - Document indexing, search, and chat"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # Indexing command
    parser_index = subparsers.add_parser("indexing", help="Index a PDF document")
    parser_index.add_argument("--name", required=True, help="Document namespace")
    parser_index.add_argument("--file", required=True, help="Path to PDF file")
    parser_index.add_argument("--chunk-size", type=int, help="Chunk size (default: 512)")
    parser_index.add_argument("--chunk-overlap", type=int, help="Chunk overlap (default: 50)")

    # Search command
    parser_search = subparsers.add_parser("search", help="Search indexed documents")
    parser_search.add_argument("--name", required=True, help="Document namespace")
    parser_search.add_argument("--question", required=True, help="Search query")
    parser_search.add_argument("--top-k", type=int, default=5, help="Number of results (default: 5)")
    parser_search.add_argument("--expand-query", action="store_true", help="Enable query expansion")
    parser_search.add_argument("--no-rerank", action="store_true", help="Disable reranking")
    parser_search.add_argument("--vector-only", action="store_true", help="Use only vector search")

    # Chat command
    parser_chat = subparsers.add_parser("chat", help="Interactive chat with documents")
    parser_chat.add_argument("--name", required=True, help="Document namespace")
    parser_chat.add_argument("--top-k", type=int, default=5, help="Number of chunks (default: 5)")
    parser_chat.add_argument("--expand-query", action="store_true", help="Enable query expansion")
    parser_chat.add_argument("--no-rerank", action="store_true", help="Disable reranking")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    # Route to command handler
    if args.command == "indexing":
        return cmd_indexing(args)
    elif args.command == "search":
        return cmd_search(args)
    elif args.command == "chat":
        return cmd_chat(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
