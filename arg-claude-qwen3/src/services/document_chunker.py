"""
Document chunking service for the RAG backend system.
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.models.document_chunk import DocumentChunk
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Service for splitting documents into chunks."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the DocumentChunker.

        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_document(self, document_id: str, text: str, metadata: dict = None) -> List[DocumentChunk]:
        """
        Split a document text into chunks.

        Args:
            document_id: ID of the document being chunked
            text: Text content to chunk
            metadata: Additional metadata to include in each chunk

        Returns:
            List of DocumentChunk objects
        """
        try:
            # Split text into chunks
            texts = self.text_splitter.split_text(text)

            # Create DocumentChunk objects
            chunks = []
            for i, chunk_text in enumerate(texts):
                chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk_text,
                    position=i,
                    metadata=metadata or {}
                )
                chunks.append(chunk)

            logger.info(f"Split document {document_id} into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Failed to chunk document {document_id}: {e}")
            raise

    def chunk_with_custom_settings(self, document_id: str, text: str, chunk_size: int,
                                 chunk_overlap: int, metadata: dict = None) -> List[DocumentChunk]:
        """
        Split a document text into chunks with custom settings.

        Args:
            document_id: ID of the document being chunked
            text: Text content to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            metadata: Additional metadata to include in each chunk

        Returns:
            List of DocumentChunk objects
        """
        # Create a temporary text splitter with custom settings
        custom_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        try:
            # Split text into chunks
            texts = custom_splitter.split_text(text)

            # Create DocumentChunk objects
            chunks = []
            for i, chunk_text in enumerate(texts):
                chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk_text,
                    position=i,
                    metadata=metadata or {}
                )
                chunks.append(chunk)

            logger.info(f"Split document {document_id} into {len(chunks)} chunks with custom settings")
            return chunks

        except Exception as e:
            logger.error(f"Failed to chunk document {document_id} with custom settings: {e}")
            raise


# Global document chunker instance
document_chunker = DocumentChunker()


def get_document_chunker() -> DocumentChunker:
    """
    Get the global document chunker instance.

    Returns:
        DocumentChunker instance
    """
    return document_chunker