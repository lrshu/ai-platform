"""
PDF parsing service for the RAG backend system.
"""

import os
from typing import Optional
from pypdf import PdfReader
from src.lib.exceptions import FileProcessingError
from src.lib.utils import file_exists
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Service for parsing PDF documents."""

    def parse_pdf(self, file_path: str) -> str:
        """
        Parse a PDF document and extract text content.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content from the PDF

        Raises:
            FileProcessingError: If PDF parsing fails
            FileNotFoundError: If file doesn't exist
        """
        if not file_exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not file_path.lower().endswith('.pdf'):
            raise FileProcessingError(file_path, "File is not a PDF")

        try:
            reader = PdfReader(file_path)
            text_content = []

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num} of {file_path}: {e}")
                    continue

            full_text = "\n\n".join(text_content)
            logger.info(f"Successfully parsed PDF {file_path} with {len(reader.pages)} pages")
            return full_text

        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise FileProcessingError(file_path, f"Failed to parse PDF: {str(e)}")

    def get_pdf_metadata(self, file_path: str) -> dict:
        """
        Get metadata from a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing PDF metadata
        """
        if not file_exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            reader = PdfReader(file_path)
            metadata = reader.metadata

            if metadata:
                # Convert metadata to a regular dictionary
                metadata_dict = {}
                for key, value in metadata.items():
                    # Remove leading '/' from keys
                    clean_key = key.lstrip('/')
                    metadata_dict[clean_key] = value
                return metadata_dict
            else:
                return {}

        except Exception as e:
            logger.warning(f"Failed to extract metadata from PDF {file_path}: {e}")
            return {}

    def get_page_count(self, file_path: str) -> int:
        """
        Get the number of pages in a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            Number of pages in the PDF
        """
        if not file_exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            reader = PdfReader(file_path)
            return len(reader.pages)
        except Exception as e:
            logger.error(f"Failed to get page count for PDF {file_path}: {e}")
            raise FileProcessingError(file_path, f"Failed to get page count: {str(e)}")


# Global PDF parser instance
pdf_parser = PDFParser()


def get_pdf_parser() -> PDFParser:
    """
    Get the global PDF parser instance.

    Returns:
        PDFParser instance
    """
    return pdf_parser