"""Command line interface for the onboarding system."""

from __future__ import annotations

import argparse

from src import run_cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent Codex Onboarding CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("chat", help="Start onboarding chat session")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "chat":
        run_cli()


if __name__ == "__main__":
    main()
