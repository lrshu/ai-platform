"""Document parsing service for the indexing pipeline."""

import os
from typing import Tuple
from src.lib.pdf_parser import parse_pdf_to_markdown
from src.lib.logging_config import logger, DocumentProcessingError


class DocumentParser:
    """Service for parsing documents in the indexing pipeline."""

    def __init__(self):
        """Initialize the document parser."""
        pass

    def parse_document(self, file_path: str) -> Tuple[str, str]:
        """
        Parse a document and extract content in markdown format.

        Args:
            file_path (str): Path to the document file

        Returns:
            Tuple[str, str]: Tuple of (document_id, markdown_content)

        Raises:
            DocumentProcessingError: If there's an error parsing the document
            FileNotFoundError: If the file is not found
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document file not found: {file_path}")

            # Validate file is readable
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"Document file is not readable: {file_path}")

            # Validate file extension (should be PDF)
            if not file_path.lower().endswith('.pdf'):
                logger.warning(f"File {file_path} is not a PDF file")

            # Validate file size (should not be too large)
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                raise DocumentProcessingError(f"Document file is too large: {file_size} bytes")

            # Generate document ID (in a real implementation, this would be more sophisticated)
            document_id = os.path.basename(file_path).replace(".", "_").replace(" ", "_")

            # Parse PDF to markdown
            logger.info(f"Parsing document: {file_path} (size: {file_size} bytes)")
            markdown_content = parse_pdf_to_markdown(file_path)

            logger.info(f"Successfully parsed document: {file_path}")
            return document_id, markdown_content

        except FileNotFoundError:
            logger.error(f"Document file not found: {file_path}")
            raise
        except PermissionError:
            logger.error(f"Permission denied accessing document file: {file_path}")
            raise
        except DocumentProcessingError:
            # Re-raise DocumentProcessingError
            raise
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {str(e)}")
            raise DocumentProcessingError(f"Failed to parse document: {str(e)}")


# Global instance
document_parser = DocumentParser()