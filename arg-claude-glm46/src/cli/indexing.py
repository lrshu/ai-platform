"""CLI handler for the indexing command."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.indexing.orchestrator import indexing_orchestrator
from src.lib.logging_config import logger


def indexing_command(args):
    """
    Handle the indexing command.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Validate input parameters
        if not args.name or not args.name.strip():
            logger.error("Document name is required for indexing command")
            print("Error: Document name is required", file=sys.stderr)
            return 1

        if not args.file or not args.file.strip():
            logger.error("File path is required for indexing command")
            print("Error: File path is required", file=sys.stderr)
            return 1

        # Check if file exists
        if not os.path.exists(args.file):
            logger.error(f"File not found: {args.file}")
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 2

        # Check if file is a PDF (basic check)
        if not args.file.lower().endswith('.pdf'):
            logger.warning(f"File {args.file} is not a PDF file. Proceeding anyway.")

        logger.info(f"Indexing document '{args.name}' from file '{args.file}'")

        # Call the indexing orchestrator
        document_id = indexing_orchestrator.index_document(args.name.strip(), args.file)

        # Print success message
        print(f"Successfully indexed document '{args.name}' with ID: {document_id}")
        return 0

    except FileNotFoundError:
        logger.error(f"File not found: {args.file}")
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 2

    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # This is just for testing the module directly
    pass