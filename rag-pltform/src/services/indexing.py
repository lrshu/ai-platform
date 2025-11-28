"""
Indexing service for processing documents through the RAG pipeline.
"""
import logging
import time
from typing import List, Optional
from ..models.document import Document
from ..models.chunk import Chunk
from ..models.vector import Vector
from ..lib.pdf_parser import PDFParser
from ..lib.chunker import DocumentChunker
from ..lib.llm_client import QwenClient
from ..lib.vector_store import VectorStore
from ..lib.graph_store import GraphStore
from ..lib.database import DatabaseConnection
from ..lib.exceptions import DocumentProcessingError, DatabaseError, LLMError

logger = logging.getLogger(__name__)


class IndexingService:
    """Service for indexing documents through the RAG pipeline."""

    def __init__(
        self,
        db_connection: DatabaseConnection,
        pdf_parser: Optional[PDFParser] = None,
        chunker: Optional[DocumentChunker] = None,
        llm_client: Optional[QwenClient] = None,
        vector_store: Optional[VectorStore] = None,
        graph_store: Optional[GraphStore] = None
    ):
        """Initialize indexing service.

        Args:
            db_connection: Database connection instance
            pdf_parser: PDF parser instance (optional, will create default if not provided)
            chunker: Document chunker instance (optional, will create default if not provided)
            llm_client: LLM client instance (optional, will create default if not provided)
            vector_store: Vector store instance (optional, will create default if not provided)
            graph_store: Graph store instance (optional, will create default if not provided)
        """
        self.db_connection = db_connection
        self.pdf_parser = pdf_parser or PDFParser()
        self.chunker = chunker or DocumentChunker()
        self.llm_client = llm_client or QwenClient()
        self.vector_store = vector_store or VectorStore(db_connection)
        self.graph_store = graph_store or GraphStore(db_connection)

    def index_document(self, name: str, file_path: str) -> Document:
        """Index a document through the complete RAG pipeline.

        Args:
            name: Name for the document collection
            file_path: Path to the PDF file to index

        Returns:
            Document object representing the indexed document

        Raises:
            DocumentProcessingError: If document processing fails
            DatabaseError: If database operations fail
            LLMError: If LLM operations fail
        """
        start_time = time.time()
        logger.info("Starting indexing process for document: %s (%s)", name, file_path)

        # Validate inputs
        if not name or not name.strip():
            raise DocumentProcessingError("Document name cannot be empty", file_path)

        if not file_path or not file_path.strip():
            raise DocumentProcessingError("File path cannot be empty", file_path)

        # Create document object
        document = Document(name=name, file_path=file_path)
        document.status = "processing"

        try:
            # 1. Parse PDF document
            logger.info("Parsing PDF document: %s", file_path)
            parse_start = time.time()
            text_content = self.pdf_parser.parse(file_path)
            parse_duration = time.time() - parse_start
            logger.info("PDF parsing completed in %.2f seconds", parse_duration)

            # Validate parsed content
            if not text_content or not text_content.strip():
                raise DocumentProcessingError("No text content found in PDF", file_path)

            # 2. Chunk document
            logger.info("Chunking document: %s", document.id)
            chunk_start = time.time()
            chunks = self.chunker.chunk(document.id, text_content)
            chunk_duration = time.time() - chunk_start
            logger.info("Document chunking completed in %.2f seconds", chunk_duration)

            if not chunks:
                logger.warning("No chunks created from document: %s", document.id)
                # Create a single chunk with all content if chunking failed
                from ..models.chunk import Chunk
                chunk = Chunk(document_id=document.id, content=text_content[:1000], position=0)
                chunks = [chunk]

            document.chunk_count = len(chunks)
            logger.info("Created %d chunks from document", len(chunks))

            # 3. Process each chunk
            vectors = []
            failed_chunks = 0
            embedding_start = time.time()

            for i, chunk in enumerate(chunks):
                logger.debug("Processing chunk %d/%d", i + 1, len(chunks))

                # Generate vector embedding
                try:
                    embedding = self.llm_client.generate_embedding(chunk.content)
                    vector = Vector(
                        chunk_id=chunk.id,
                        embedding=embedding,
                        model_name="text-embedding-v4"
                    )
                    vectors.append(vector)
                except LLMError as e:
                    logger.warning("Failed to generate embedding for chunk %s: %s", chunk.id, str(e))
                    failed_chunks += 1
                    # Continue with other chunks

            embedding_duration = time.time() - embedding_start
            logger.info("Embedding generation completed in %.2f seconds", embedding_duration)

            # Log statistics
            if failed_chunks > 0:
                logger.warning("Failed to generate embeddings for %d/%d chunks", failed_chunks, len(chunks))

            # 4. Store data in database
            logger.info("Storing document data in database")
            store_start = time.time()

            # Store document
            self._store_document(document)

            # Store chunks
            self._store_chunks(chunks)

            # Store vectors
            self._store_vectors(vectors)

            # Store knowledge graph (placeholder for now)
            self._store_knowledge_graph(chunks, document.id)

            store_duration = time.time() - store_start
            logger.info("Database storage completed in %.2f seconds", store_duration)

            # Mark document as completed
            document.mark_as_indexed()
            self._update_document(document)

            total_duration = time.time() - start_time
            logger.info("Successfully indexed document: %s in %.2f seconds", document.id, total_duration)
            return document

        except DocumentProcessingError:
            # Re-raise document processing errors
            raise
        except Exception as e:
            logger.error("Failed to index document %s: %s", document.id, str(e))
            document.mark_as_failed()
            try:
                self._update_document(document)
            except:
                pass  # Ignore errors when updating failed document
            raise DocumentProcessingError(f"Failed to index document: {str(e)}", file_path)

    def _store_document(self, document: Document) -> None:
        """Store document in database.

        Args:
            document: Document to store
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                CREATE (d:Document {
                    id: $id,
                    name: $name,
                    file_path: $file_path,
                    indexed_at: $indexed_at,
                    chunk_count: $chunk_count,
                    status: $status,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                """
                session.run(query, document.to_dict())
            logger.info("Stored document %s", document.id)
        except Exception as e:
            logger.error("Failed to store document %s: %s", document.id, str(e))
            raise DatabaseError(f"Failed to store document: {str(e)}")

    def _store_chunks(self, chunks: List[Chunk]) -> None:
        """Store chunks in database.

        Args:
            chunks: List of chunks to store
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                UNWIND $chunks AS c
                CREATE (ch:Chunk {
                    id: c.id,
                    document_id: c.document_id,
                    content: c.content,
                    position: c.position,
                    metadata: c.metadata,
                    created_at: c.created_at,
                    updated_at: c.updated_at
                })
                CREATE (d:Document {id: c.document_id})-[:HAS_CHUNK]->(ch)
                """

                chunk_data = []
                for chunk in chunks:
                    chunk_data.append(chunk.to_dict())

                session.run(query, {"chunks": chunk_data})
            logger.info("Stored %d chunks", len(chunks))
        except Exception as e:
            logger.error("Failed to store chunks: %s", str(e))
            raise DatabaseError(f"Failed to store chunks: {str(e)}")

    def _store_vectors(self, vectors: List[Vector]) -> None:
        """Store vectors in database.

        Args:
            vectors: List of vectors to store
        """
        if vectors:
            self.vector_store.store_vectors(vectors)

    def _store_knowledge_graph(self, chunks: List[Chunk], document_id: str) -> None:
        """Store knowledge graph data in database.

        Args:
            chunks: List of chunks to process
            document_id: ID of the parent document
        """
        # This is a placeholder implementation
        # In a real implementation, this would extract entities and relationships
        # from the chunks and store them in the knowledge graph
        logger.info("Knowledge graph storage is not fully implemented yet")
        pass

    def _update_document(self, document: Document) -> None:
        """Update document in database.

        Args:
            document: Document to update
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (d:Document {id: $id})
                SET d.indexed_at = $indexed_at,
                    d.chunk_count = $chunk_count,
                    d.status = $status,
                    d.updated_at = $updated_at
                """
                session.run(query, document.to_dict())
            logger.info("Updated document %s", document.id)
        except Exception as e:
            logger.error("Failed to update document %s: %s", document.id, str(e))
            raise DatabaseError(f"Failed to update document: {str(e)}")