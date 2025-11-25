from __future__ import annotations

import argparse
from typing import Any, Dict

from src import orchestration


def str_to_bool(value: str | None) -> bool:
    if value is None or isinstance(value, bool):
        raise argparse.ArgumentTypeError("Boolean value expected")
    normalized = value.lower()
    if normalized in {"true", "t", "1", "yes", "y"}:
        return True
    if normalized in {"false", "f", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def add_bool_option(parser: argparse.ArgumentParser, name: str, help_text: str) -> None:
    parser.add_argument(
        f"--{name.replace('_', '-')}",
        f"--{name}",
        dest=name,
        type=str_to_bool,
        nargs="?",
        const=True,
        default=None,
        metavar="{true,false}",
        help=help_text,
    )


def add_search_option_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--top-k", type=int, default=None, help="Number of top documents to retrieve")
    add_bool_option(parser, "expand_query", "Enable or disable query expansion")
    add_bool_option(parser, "rerank", "Enable or disable reranking")
    add_bool_option(parser, "use_vector", "Use vector search")
    add_bool_option(parser, "use_keyword", "Use keyword search")
    add_bool_option(parser, "use_graph", "Use graph search")


def build_search_options(args: argparse.Namespace) -> orchestration.SearchOptions | None:
    option_map: Dict[str, Any] = {}
    for field in ("top_k", "expand_query", "rerank", "use_vector", "use_keyword", "use_graph"):
        value = getattr(args, field, None)
        if value is not None:
            option_map[field] = value
    if not option_map:
        return None
    return orchestration.SearchOptions(**option_map)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG Backend CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("indexing", help="Index a PDF file")
    index_parser.add_argument("--name", required=True)
    index_parser.add_argument("--file", required=True)

    search_parser = subparsers.add_parser("search", help="Search a collection")
    search_parser.add_argument("--name", required=True)
    search_parser.add_argument("--question", required=True)
    add_search_option_arguments(search_parser)

    chat_parser = subparsers.add_parser("chat", help="Chat with a collection")
    chat_parser.add_argument("--name", required=True)
    chat_parser.add_argument("--question", required=True)
    add_search_option_arguments(chat_parser)

    return parser


def cli():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "indexing":
        result = orchestration.index(args.name, args.file)
        print(f"Indexed document {result.name} with {result.chunk_count} chunks")
    elif args.command == "search":
        opts = build_search_options(args)
        results = orchestration.search(args.name, args.question, opts)
        limit = opts.top_k if opts and opts.top_k is not None else orchestration.SearchOptions().top_k
        for item in results[: limit]:
            print(f"- {item.score:.4f}: {item.content[:80]}")
    elif args.command == "chat":
        opts = build_search_options(args)
        answer = orchestration.chat(args.name, args.question, opts)
        print(answer.answer)


def main():
    cli()


if __name__ == "__main__":
    main()
