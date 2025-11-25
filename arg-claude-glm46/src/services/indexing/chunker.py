"""Chunking service for the indexing pipeline."""

import uuid
from typing import List
from datetime import datetime
from src.models.chunk import Chunk
from src.lib.langchain_setup import split_text_by_tokens
from src.lib.logging_config import logger


class Chunker:
    """Service for chunking document content in the indexing pipeline."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the chunker.

        Args:
            chunk_size (int): Maximum chunk size in tokens
            chunk_overlap (int): Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document_id: str, content: str) -> List[Chunk]:
        """
        Split document content into chunks.

        Args:
            document_id (str): ID of the document
            content (str): Document content to chunk

        Returns:
            List[Chunk]: List of chunk objects
        """
        try:
            logger.info(f"Chunking document {document_id} with size {self.chunk_size}, overlap {self.chunk_overlap}")

            # Split text into chunks
            text_chunks = split_text_by_tokens(content, self.chunk_size, self.chunk_overlap)

            # Create Chunk objects
            chunks = []
            for i, chunk_content in enumerate(text_chunks):
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    content=chunk_content,
                    position=i,
                    created_at=datetime.now()
                )
                chunks.append(chunk)

            logger.info(f"Created {len(chunks)} chunks for document {document_id}")
            return chunks

        except Exception as e:
            logger.error(f"Error chunking document {document_id}: {str(e)}")
            raise


# Global instance
chunker = Chunker()