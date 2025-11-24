"""
Document indexing orchestration service for the RAG backend system.
"""

from typing import List, Tuple
from src.services.pdf_parser import get_pdf_parser
from src.services.document_chunker import get_document_chunker
from src.services.embedding_generator import get_embedding_generator
from src.services.kg_extractor import get_kg_extractor
from src.models.document_collection import DocumentCollection
from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.models.vector_embedding import VectorEmbedding
from src.models.knowledge_graph_node import KnowledgeGraphNode
from src.models.knowledge_graph_relationship import KnowledgeGraphRelationship
from src.lib.database import get_db_connection
from src.lib.exceptions import DocumentNotFoundError, CollectionNotFoundError, FileProcessingError
import logging

logger = logging.getLogger(__name__)


class IndexingService:
    """Orchestration service for document indexing."""

    def __init__(self):
        """Initialize the IndexingService."""
        self.pdf_parser = get_pdf_parser()
        self.document_chunker = get_document_chunker()
        self.embedding_generator = get_embedding_generator()
        self.kg_extractor = get_kg_extractor()
        self.db = get_db_connection()

    def index_document(self, collection_name: str, file_path: str) -> str:
        """
        Index a PDF document into the RAG system.

        Args:
            collection_name: Name of the document collection
            file_path: Path to the PDF file

        Returns:
            ID of the indexed document

        Raises:
            FileProcessingError: If document processing fails
            CollectionNotFoundError: If collection doesn't exist
        """
        try:
            logger.info(f"Starting indexing process for {file_path} into collection {collection_name}")

            # Step 1: Parse PDF document
            text_content = self.pdf_parser.parse_pdf(file_path)
            metadata = self.pdf_parser.get_pdf_metadata(file_path)

            # Step 2: Create or get collection
            collection = self._get_or_create_collection(collection_name)

            # Step 3: Create document record
            document = Document(
                collection_id=collection.id,
                file_path=file_path,
                title=metadata.get("title") if metadata else None
            )

            # Save document to database (simplified - in real implementation would use DB)
            logger.info(f"Created document record: {document.id}")

            # Step 4: Split document into chunks
            chunks = self.document_chunker.chunk_document(
                document_id=document.id,
                text=text_content,
                metadata=metadata
            )

            # Step 5: Generate embeddings and extract knowledge graph for each chunk
            chunk_ids = [chunk.id for chunk in chunks]
            chunk_texts = [chunk.content for chunk in chunks]

            # Generate embeddings
            embeddings = self.embedding_generator.generate_embeddings(chunk_ids, chunk_texts)

            # Extract knowledge graph entities and relationships
            all_entities = []
            all_relationships = []

            for chunk in chunks:
                entities, relationships = self.kg_extractor.extract_entities_and_relationships(
                    chunk.id, chunk.content
                )
                all_entities.extend(entities)
                all_relationships.extend(relationships)

            # Step 6: Store all data (simplified - in real implementation would use DB)
            logger.info(f"Processed {len(chunks)} chunks, {len(embeddings)} embeddings, "
                       f"{len(all_entities)} entities, and {len(all_relationships)} relationships")

            logger.info(f"Successfully indexed document {document.id} into collection {collection_name}")
            return document.id

        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}")
            raise FileProcessingError(file_path, f"Failed to index document: {str(e)}")

    def _get_or_create_collection(self, collection_name: str) -> DocumentCollection:
        """
        Get an existing collection or create a new one.

        Args:
            collection_name: Name of the collection

        Returns:
            DocumentCollection object
        """
        # In a real implementation, this would query the database
        # For now, we'll create a new collection each time
        collection = DocumentCollection(name=collection_name)
        logger.info(f"Created collection: {collection.id}")
        return collection

    def index_documents_batch(self, collection_name: str, file_paths: List[str]) -> List[str]:
        """
        Index multiple documents in batch.

        Args:
            collection_name: Name of the document collection
            file_paths: List of paths to PDF files

        Returns:
            List of indexed document IDs
        """
        document_ids = []
        for file_path in file_paths:
            try:
                document_id = self.index_document(collection_name, file_path)
                document_ids.append(document_id)
            except Exception as e:
                logger.error(f"Failed to index document {file_path}: {e}")
                # Continue with other documents
                continue

        logger.info(f"Batch indexing completed. Indexed {len(document_ids)} out of {len(file_paths)} documents")
        return document_ids


# Global indexing service instance
indexing_service = IndexingService()


def get_indexing_service() -> IndexingService:
    """
    Get the global indexing service instance.

    Returns:
        IndexingService instance
    """
    return indexing_service