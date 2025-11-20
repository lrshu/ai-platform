"""
Small-to-Big chunking strategy implementation.
"""

import logging
from typing import List, Dict, Any, Tuple
from app.common.models import Chunk, DocumentMetadata

# Configure logging
logger = logging.getLogger(__name__)


class Chunker:
    """Implementation of Small-to-Big chunking strategy."""

    def __init__(self, parent_chunk_size: int = 1000, child_chunk_size: int = 200, overlap: int = 50):
        """
        Initialize the chunker with chunking parameters.

        Args:
            parent_chunk_size: Size of parent chunks (~1000 tokens)
            child_chunk_size: Size of child chunks (~200 tokens)
            overlap: Overlap between chunks to maintain context
        """
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.overlap = overlap

    def create_chunks(self, document_id: str, document_content: str, source_type: str,
                     title: str = "", author: str = "") -> Tuple[List[Chunk], List[Chunk]]:
        """
        Create parent and child chunks using the Small-to-Big strategy.

        Args:
            document_id: Unique identifier for the document
            document_content: Full content of the document
            source_type: Type of source document (PDF, DOCX, etc.)
            title: Title of the document (if available)
            author: Author of the document (if available)

        Returns:
            Tuple of (parent_chunks, child_chunks)
        """
        try:
            # Create parent chunks first
            parent_chunks = self._create_parent_chunks(
                document_id, document_content, source_type, title, author
            )

            # Create child chunks from parent chunks
            child_chunks = self._create_child_chunks_from_parents(parent_chunks)

            logger.info(f"Created {len(parent_chunks)} parent chunks and {len(child_chunks)} child chunks")
            return parent_chunks, child_chunks

        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            raise

    def _create_parent_chunks(self, document_id: str, document_content: str, source_type: str,
                            title: str, author: str) -> List[Chunk]:
        """
        Create parent chunks from document content.

        Args:
            document_id: Unique identifier for the document
            document_content: Full content of the document
            source_type: Type of source document
            title: Title of the document
            author: Author of the document

        Returns:
            List of parent chunks
        """
        parent_chunks = []
        content_length = len(document_content)
        start_index = 0
        chunk_id = 0

        while start_index < content_length:
            # Calculate end index with overlap
            end_index = min(start_index + self.parent_chunk_size, content_length)

            # Extract chunk content
            chunk_content = document_content[start_index:end_index]

            # Create metadata
            metadata = DocumentMetadata(
                document_id=document_id,
                start_index=start_index,
                end_index=end_index,
                source_type=source_type,
                title=title,
                author=author
            )

            # Create chunk
            chunk = Chunk(
                id=f"{document_id}_parent_{chunk_id}",
                content=chunk_content,
                metadata=metadata
            )

            parent_chunks.append(chunk)
            chunk_id += 1

            # Move start index forward, accounting for overlap
            start_index = end_index - self.overlap
            if start_index >= end_index:  # Prevent infinite loop
                start_index = end_index

        return parent_chunks

    def _create_child_chunks_from_parents(self, parent_chunks: List[Chunk]) -> List[Chunk]:
        """
        Create child chunks from parent chunks.

        Args:
            parent_chunks: List of parent chunks

        Returns:
            List of child chunks
        """
        child_chunks = []
        child_id = 0

        for parent_chunk in parent_chunks:
            parent_content = parent_chunk.content
            parent_length = len(parent_content)
            start_index = 0

            while start_index < parent_length:
                # Calculate end index with overlap
                end_index = min(start_index + self.child_chunk_size, parent_length)

                # Extract chunk content
                chunk_content = parent_content[start_index:end_index]

                # Create metadata based on parent metadata
                metadata = DocumentMetadata(
                    document_id=parent_chunk.metadata.document_id,
                    start_index=parent_chunk.metadata.start_index + start_index,
                    end_index=parent_chunk.metadata.start_index + end_index,
                    parent_id=parent_chunk.id,  # Link to parent
                    source_type=parent_chunk.metadata.source_type,
                    title=parent_chunk.metadata.title,
                    author=parent_chunk.metadata.author
                )

                # Create chunk
                chunk = Chunk(
                    id=f"{parent_chunk.metadata.document_id}_child_{child_id}",
                    content=chunk_content,
                    metadata=metadata
                )

                child_chunks.append(chunk)
                child_id += 1

                # Move start index forward, accounting for overlap
                start_index = end_index - self.overlap
                if start_index >= end_index:  # Prevent infinite loop
                    start_index = end_index

        return child_chunks

    def chunk_with_overlap(self, text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """
        Generic chunking function with overlap.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start_index = 0
        text_length = len(text)

        while start_index < text_length:
            end_index = min(start_index + chunk_size, text_length)
            chunk = text[start_index:end_index]
            chunks.append(chunk)

            # Move start index forward, accounting for overlap
            start_index = end_index - overlap
            if start_index >= end_index:  # Prevent infinite loop
                start_index = end_index

        return chunks