"""
PDF parser for extracting text content from PDF files.
"""
import fitz  # PyMuPDF
import os
from typing import Optional
import logging
from ..models.document import Document
from ..lib.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for PDF documents."""

    def __init__(self):
        """Initialize PDF parser."""
        pass

    def parse(self, file_path: str) -> str:
        """Parse PDF file and extract text content.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content in markdown format

        Raises:
            DocumentProcessingError: If parsing fails
        """
        # Validate file exists and is readable
        if not os.path.exists(file_path):
            raise DocumentProcessingError(f"File not found: {file_path}", file_path)

        if not os.access(file_path, os.R_OK):
            raise DocumentProcessingError(f"File not readable: {file_path}", file_path)

        # Validate file is a PDF
        if not self._is_pdf(file_path):
            raise DocumentProcessingError(f"File is not a valid PDF: {file_path}", file_path)

        try:
            # Open PDF document
            doc = fitz.open(file_path)

            # Extract text from all pages
            text_content = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_content.append(f"## Page {page_num + 1}\n\n{text}\n")

            doc.close()

            # Combine all text content
            full_text = "\n".join(text_content)
            logger.info("Successfully parsed PDF file: %s (%d pages)", file_path, len(text_content))

            return full_text

        except Exception as e:
            logger.error("Failed to parse PDF file %s: %s", file_path, str(e))
            raise DocumentProcessingError(f"Failed to parse PDF file: {str(e)}", file_path)

    def _is_pdf(self, file_path: str) -> bool:
        """Check if file is a valid PDF.

        Args:
            file_path: Path to the file

        Returns:
            True if file is a valid PDF, False otherwise
        """
        try:
            with fitz.open(file_path) as doc:
                return doc.is_pdf
        except:
            return False

    def get_metadata(self, file_path: str) -> dict:
        """Get PDF metadata.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with PDF metadata
        """
        try:
            with fitz.open(file_path) as doc:
                metadata = doc.metadata
                return {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                    "creationDate": metadata.get("creationDate", ""),
                    "modDate": metadata.get("modDate", ""),
                    "page_count": len(doc)
                }
        except Exception as e:
            logger.warning("Failed to extract metadata from PDF %s: %s", file_path, str(e))
            return {}