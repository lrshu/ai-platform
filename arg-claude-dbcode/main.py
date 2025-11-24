#!/usr/bin/env python3
"""Main CLI for RAG backend system."""

import argparse
from orchestration import Orchestration

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="RAG Backend System CLI")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Indexing command
    index_parser = subparsers.add_parser("indexing", help="Index a PDF document")
    index_parser.add_argument("--name", required=True, help="Name identifier for the document")
    index_parser.add_argument("--file", required=True, help="Path to the PDF file")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search indexed content")
    search_parser.add_argument("--name", required=True, help="Name identifier of the document to search")
    search_parser.add_argument("--question", required=True, help="Search question")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of top results to return")
    search_parser.add_argument("--no-expand", action="store_false", dest="expand", help="Disable query expansion")
    search_parser.add_argument("--no-rerank", action="store_false", dest="rerank", help="Disable reranking")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Generate answer from indexed content")
    chat_parser.add_argument("--name", required=True, help="Name identifier of the document to use")
    chat_parser.add_argument("--question", required=True, help="Question to answer")
    chat_parser.add_argument("--top-k", type=int, default=5, help="Number of top results to use")
    chat_parser.add_argument("--no-expand", action="store_false", dest="expand", help="Disable query expansion")
    chat_parser.add_argument("--no-rerank", action="store_false", dest="rerank", help="Disable reranking")

    # Parse arguments
    args = parser.parse_args()

    # Initialize orchestration
    orchestration = Orchestration()

    try:
        if args.command == "indexing":
            # Run indexing
            result = orchestration.index_document(args.name, args.file)
            if result["success"]:
                print(f"✓ Indexing successful!")
                print(f"  Document ID: {result['document_id']}")
                print(f"  Chunks processed: {result['chunk_count']}")
                print(f"  Status: {result['message']}")
            else:
                print(f"✗ Indexing failed: {result['error']}")

        elif args.command == "search":
            # Run search
            options = {
                "top_k": args.top_k,
                "expand_query": args.expand,
                "rerank": args.rerank
            }
            result = orchestration.retrieve_results(args.name, args.question, options)
            if result["success"]:
                print(f"✓ Search successful!")
                print(f"  Question: {result['question']}")
                print(f"  Expanded queries: {len(result['expanded_queries'])}")
                print(f"  Results found: {len(result['results'])}")
                print(f"  Options: top_k={args.top_k}, expand={args.expand}, rerank={args.rerank}")
                print("\n" + "="*50)
                for i, item in enumerate(result["results"], 1):
                    print(f"\nResult {i} (Score: {item['final_score']:.4f}):")
                    print(f"Match types: {item['match_type']}")
                    print(f"Content: {item['content'][:200]}..." if len(item['content']) > 200 else f"Content: {item['content']}")
            else:
                print(f"✗ Search failed: {result['error']}")

        elif args.command == "chat":
            # Run chat
            options = {
                "top_k": args.top_k,
                "expand_query": args.expand,
                "rerank": args.rerank
            }
            result = orchestration.generate_response(args.name, args.question, options)
            if result["success"]:
                print(f"✓ Answer generated successfully!")
                print("\n" + "="*50)
                print(f"Question: {result['question']}")
                print("\n" + "-"*50)
                print(f"Answer: {result['answer']}")
                print("\n" + "-"*50)
                print(f"Sources ({len(result['sources'])}):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"\nSource {i} (Score: {source['score']:.4f}):")
                    print(f"Content: {source['content'][:150]}..." if len(source['content']) > 150 else f"Content: {source['content']}")
            else:
                print(f"✗ Answer generation failed: {result['error']}")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main()