"""
Document chunker for splitting text into smaller segments.
"""
import re
from typing import List, Tuple
from ..models.chunk import Chunk
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunker for splitting documents into smaller segments."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """Initialize document chunker.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "! ", "? ", " ", ""]

    def chunk(self, document_id: str, text: str) -> List[Chunk]:
        """Split text into chunks.

        Args:
            document_id: ID of the parent document
            text: Text to chunk

        Returns:
            List of Chunk objects
        """
        if not text.strip():
            return []

        chunks = []
        position = 0
        start = 0

        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))

            # If we're not at the end of the text, try to find a good split point
            if end < len(text):
                # Look for the best separator within the overlap window
                best_split = end
                for separator in self.separators:
                    # Look for separator in the overlap window
                    search_start = max(end - self.chunk_overlap, start)
                    split_pos = text.rfind(separator, search_start, end)
                    if split_pos != -1:
                        best_split = split_pos + len(separator)
                        break

                end = best_split

            # Extract chunk content
            content = text[start:end].strip()

            # Only create chunk if it has content
            if content:
                chunk = Chunk(
                    document_id=document_id,
                    content=content,
                    position=position
                )
                chunks.append(chunk)
                position += 1

            # Move start position
            start = end - self.chunk_overlap if end < len(text) else end

            # If we're not making progress, force advancement
            if start <= 0 or (end == len(text) and start >= end):
                break

        logger.info("Created %d chunks from document %s", len(chunks), document_id)
        return chunks

    def chunk_with_metadata(self, document_id: str, text: str, page_numbers: List[int] = None) -> List[Chunk]:
        """Split text into chunks with page number metadata.

        Args:
            document_id: ID of the parent document
            text: Text to chunk
            page_numbers: List of page numbers for each character position

        Returns:
            List of Chunk objects with page number metadata
        """
        chunks = self.chunk(document_id, text)

        if page_numbers and len(page_numbers) == len(text):
            # Add page number metadata to chunks
            for chunk in chunks:
                # Find the page number for this chunk
                start_pos = text.find(chunk.content)
                if start_pos != -1:
                    page_num = page_numbers[start_pos]
                    chunk.metadata["page_number"] = page_num

        return chunks