"""Indexing orchestrator for coordinating the indexing pipeline."""

import uuid
import time
from datetime import datetime
from typing import List
from src.models import Document, Chunk
from src.models.kg import Entity, Relationship
from src.services.indexing.parser import document_parser
from src.services.indexing.chunker import chunker
from src.services.indexing.embedder import embedder
from src.services.indexing.kg_extractor import kg_extractor
from src.services.indexing.storage import storage_service
from src.lib.logging_config import logger, DocumentProcessingError
from src.lib.metrics import metrics_collector, TimingContext


class IndexingOrchestrator:
    """Orchestrator for coordinating the document indexing pipeline."""

    def __init__(self):
        """Initialize the indexing orchestrator."""
        pass

    def _generate_embeddings_with_timing(self, chunk_contents: List[str], context: dict):
        """Generate embeddings with timing metrics."""
        with TimingContext(metrics_collector, "embedding_generation", context):
            return embedder.generate_embeddings(chunk_contents)

    def _extract_kg_with_timing(self, markdown_content: str, context: dict):
        """Extract knowledge graph with timing metrics."""
        with TimingContext(metrics_collector, "kg_extraction", context):
            return kg_extractor.extract_entities_and_relationships(markdown_content)

    def index_document(self, name: str, file_path: str) -> str:
        """
        Index a document through the complete pipeline.

        Args:
            name (str): Name identifier for the document
            file_path (str): Path to the PDF file to be indexed

        Returns:
            str: Document ID

        Raises:
            DocumentProcessingError: If there's an error during indexing
        """
        start_time = time.time()
        context = {
            'document_name': name,
            'file_path': file_path
        }

        try:
            logger.info(f"Starting indexing pipeline for document: {name}")
            logger.info(f"Document file path: {file_path}")

            # Step 1: Parse document
            logger.info("Step 1: Parsing document")
            with TimingContext(metrics_collector, "document_parsing", context):
                document_id, markdown_content = document_parser.parse_document(file_path)
            logger.info(f"Document parsed successfully. Document ID: {document_id}")
            logger.debug(f"Markdown content length: {len(markdown_content)} characters")

            # Step 2: Create document object
            logger.info("Step 2: Creating document object")
            document = Document(
                id=document_id,
                name=name,
                file_path=file_path,
                created_at=datetime.now(),
                status="processing"
            )
            logger.info("Document object created successfully")

            # Step 3: Chunk document
            logger.info("Step 3: Chunking document")
            with TimingContext(metrics_collector, "document_chunking", context):
                chunks = chunker.chunk_document(document_id, markdown_content)
            document.chunk_count = len(chunks)
            logger.info(f"Document chunked successfully. Number of chunks: {len(chunks)}")

            # Step 4: Generate embeddings for chunks and extract knowledge graph in parallel
            logger.info("Step 4: Generating embeddings and extracting knowledge graph in parallel")
            chunk_contents = [chunk.content for chunk in chunks]
            logger.info(f"Processing {len(chunk_contents)} chunks and extracting knowledge graph")

            # Run embedding generation and knowledge graph extraction in parallel
            embeddings = None
            entities = []
            relationships = []

            with ThreadPoolExecutor(max_workers=2) as executor:
                # Submit both tasks
                future_embeddings = executor.submit(self._generate_embeddings_with_timing, chunk_contents, context)
                future_kg = executor.submit(self._extract_kg_with_timing, markdown_content, context)

                # Collect results
                embeddings = future_embeddings.result()
                entities, relationships = future_kg.result()

            logger.info("Parallel processing completed successfully")

            # Attach embeddings to chunks
            logger.info("Attaching embeddings to chunks")
            for i, chunk in enumerate(chunks):
                chunk.embedding = embeddings[i]
            logger.info("Embeddings attached to chunks successfully")

            logger.info(f"Knowledge graph extracted. Entities: {len(entities)}, Relationships: {len(relationships)}")

            # Step 6: Update document status
            logger.info("Step 6: Updating document status")
            document.status = "completed"
            logger.info("Document status updated to completed")

            # Step 7: Store everything in database
            logger.info("Step 7: Storing data in database")
            logger.info("Storing document")
            with TimingContext(metrics_collector, "document_storage", context):
                storage_service.store_document(document)
            logger.info("Storing chunks")
            with TimingContext(metrics_collector, "chunks_storage", context):
                storage_service.store_chunks(chunks)
            logger.info("Storing entities and relationships")
            with TimingContext(metrics_collector, "kg_storage", context):
                storage_service.store_entities_and_relationships(entities, relationships)
            logger.info("All data stored successfully")

            logger.info(f"Successfully completed indexing pipeline for document: {name}")

            # Record overall indexing timing
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_timing("indexing_pipeline", duration_ms, context)

            return document_id

        except Exception as e:
            logger.error(f"Error during indexing pipeline for document {name}: {str(e)}")
            logger.exception("Full traceback:")
            metrics_collector.record_counter("indexing_errors", 1, {"error_type": "Exception", **context})
            raise DocumentProcessingError(f"Failed to index document: {str(e)}")


# Global instance
indexing_orchestrator = IndexingOrchestrator()