#!/usr/bin/env python3
"""
Employee Onboarding Multi-Agent System
"""

import argparse
import sys
from src.app import chat_mode, serve_mode

def main():
    parser = argparse.ArgumentParser(description="Employee Onboarding Multi-Agent System")
    parser.add_argument(
        "mode",
        nargs='?',
        choices=["chat", "serve"],
        help="Run mode: 'chat' for interactive agent, 'serve' for REST API"
    )

    args = parser.parse_args()

    if args.mode == "chat":
        chat_mode()
    elif args.mode == "serve":
        serve_mode()
    else:
        # Default behavior - show help
        parser.print_help()

if __name__ == "__main__":
    main()
