"""
Main entry point for the RAG platform.
"""
import sys
from pathlib import Path
import logging

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cli import RAGPlatformCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point."""
    print("RAG Platform")
    print("=" * 20)
    print("A Retrieval-Augmented Generation backend system for processing documents and enabling intelligent search.")
    print()

    # Start the CLI application
    cli = RAGPlatformCLI()
    cli.run()

if __name__ == "__main__":
    main()
