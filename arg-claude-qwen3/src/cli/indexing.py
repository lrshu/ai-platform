"""
Indexing CLI command for the RAG backend system.
"""

import argparse
import sys
import os
from src.services.indexing_service import get_indexing_service
from src.lib.exceptions import FileProcessingError, CollectionNotFoundError
from src.lib.logger import get_logger
from src.lib.validation import validate_collection_name, validate_file_path, ValidationError
import logging

logger = get_logger(__name__)


def index_document(name: str, file_path: str) -> str:
    """
    Index a document by parsing, chunking, and storing it.

    Args:
        name: Name/identifier for the document collection
        file_path: Path to the PDF document to index

    Returns:
        Document ID of the indexed document
    """
    try:
        # Validate inputs
        validate_collection_name(name)
        validate_file_path(file_path)

        # Validate file path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF document")

        # Get indexing service
        indexing_service = get_indexing_service()

        # Index the document
        document_id = indexing_service.index_document(name, file_path)

        logger.info(f"Successfully indexed document {file_path} into collection {name}")
        print(f"Document indexed successfully with ID: {document_id}")
        return document_id

    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        print(f"Error: {e.message}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}")
        print(f"Error: File not found: {file_path}")
        raise
    except ValueError as e:
        logger.error(f"Invalid file type: {file_path}")
        print(f"Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to index document {file_path}: {e}")
        print(f"Error: Failed to index document: {e}")
        raise


def main():
    """Main entry point for the indexing CLI command."""
    parser = argparse.ArgumentParser(description="Index a PDF document into the RAG system")
    parser.add_argument('--name', required=True, help='Collection name')
    parser.add_argument('--file', required=True, help='Path to PDF file')

    # Parse known args to handle help separately
    args = parser.parse_args()

    try:
        document_id = index_document(args.name, args.file)
        return 0
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())