#!/usr/bin/env python3
"""
Main entry point for the RAG backend system.
"""

import sys
import os

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli.main import main

if __name__ == "__main__":
    main()
