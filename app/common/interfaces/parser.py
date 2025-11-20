"""
Abstract base class for document parsing interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
from pathlib import Path


class IDocumentParser(ABC):
    """Abstract base class for document parsing operations."""

    @abstractmethod
    async def parse_document(self, document_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a document and extract content.

        Args:
            document_path: Path to the document file

        Returns:
            List of parsed content chunks with metadata
        """
        pass

    @abstractmethod
    async def parse_document_from_bytes(self, document_bytes: bytes, file_type: str) -> List[Dict[str, Any]]:
        """
        Parse a document from bytes.

        Args:
            document_bytes: Document content as bytes
            file_type: Type of the document (pdf, docx, etc.)

        Returns:
            List of parsed content chunks with metadata
        """
        pass

    @abstractmethod
    async def parse_document_stream(self, document_path: Path) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Parse a document and yield content chunks as a stream.

        Args:
            document_path: Path to the document file

        Yields:
            Parsed content chunks with metadata
        """
        pass

    @abstractmethod
    async def extract_metadata(self, document_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from a document.

        Args:
            document_path: Path to the document file

        Returns:
            Dictionary of extracted metadata
        """
        pass

    @abstractmethod
    async def get_supported_formats(self) -> List[str]:
        """
        Get list of supported document formats.

        Returns:
            List of supported file extensions
        """
        pass