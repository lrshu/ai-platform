"""Memgraph unified storage for both graph relationships and vector embeddings."""

import json
from typing import Any, List, Optional, Tuple
from uuid import UUID

from neo4j import Driver, GraphDatabase

from src.config.logging import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


class GraphStore:
    """Unified Memgraph storage for graph operations and vector similarity search.

    Handles document and chunk node storage, relationships, graph queries,
    and vector embedding storage with similarity search capabilities.
    """

    def __init__(self) -> None:
        """Initialize Memgraph connection."""
        self.driver: Driver = GraphDatabase.driver(
            settings.database_url,
            auth=(settings.database_user, settings.database_password)
            if settings.database_user
            else None,
        )
        logger.info("Initialized Memgraph connection", extra={"stage": "graph_store_init"})
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        """Initialize graph schema with constraints and indexes."""
        with self.driver.session() as session:
            try:
                # Create uniqueness constraints
                session.run("CREATE CONSTRAINT ON (d:Document) ASSERT d.id IS UNIQUE;")
                session.run("CREATE CONSTRAINT ON (c:Chunk) ASSERT c.id IS UNIQUE;")
                # Create indexes for performance
                session.run("CREATE INDEX ON :Document(name);")
                session.run("CREATE INDEX ON :Document(namespace);")
                session.run("CREATE INDEX ON :Chunk(document_id);")
                session.run("CREATE INDEX ON :Chunk(namespace);")
                logger.info("Initialized graph schema with vector support", extra={"stage": "schema_init"})
            except Exception as e:
                # Constraints/indexes may already exist
                logger.debug(
                    f"Schema initialization note: {e}", extra={"stage": "schema_init"}
                )

    def close(self) -> None:
        """Close the database connection."""
        self.driver.close()
        logger.info("Closed Memgraph connection", extra={"stage": "graph_store_close"})

    def create_document_node(
        self,
        doc_id: UUID,
        namespace: str,
        filename: str,
        file_path: str,
        chunk_count: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Create a Document node in the graph.

        Args:
            doc_id: Document UUID
            namespace: Document namespace/collection
            filename: Original filename
            file_path: File path
            chunk_count: Number of chunks
            metadata: Additional metadata
        """
        with self.driver.session() as session:
            try:
                session.run(
                    """
                    CREATE (d:Document {
                        id: $id,
                        namespace: $namespace,
                        filename: $filename,
                        file_path: $file_path,
                        chunk_count: $chunk_count,
                        metadata: $metadata
                    })
                    """,
                    id=str(doc_id),
                    namespace=namespace,
                    filename=filename,
                    file_path=file_path,
                    chunk_count=chunk_count,
                    metadata=json.dumps(metadata) if metadata else "{}",
                )
                logger.info(
                    f"Created Document node: {doc_id}",
                    extra={"stage": "document_create", "document_id": str(doc_id)},
                )
            except Exception as e:
                logger.error(
                    f"Failed to create Document node: {e}",
                    extra={"stage": "document_create", "document_id": str(doc_id)},
                    exc_info=True,
                )
                raise RuntimeError(f"Failed to create document node: {e}") from e

    def create_chunk_with_embedding(
        self,
        chunk_id: str,
        namespace: str,
        document_id: UUID,
        text: str,
        embedding: List[float],
        position: int,
        char_offset: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Create a Chunk node with vector embedding.

        Args:
            chunk_id: Unique chunk ID
            namespace: Document namespace
            document_id: Parent document UUID
            text: Chunk text content
            embedding: Vector embedding as list of floats
            position: Position in document
            char_offset: Character offset
            metadata: Additional metadata
        """
        with self.driver.session() as session:
            try:
                session.run(
                    """
                    MATCH (d:Document {id: $doc_id})
                    CREATE (c:Chunk {
                        id: $chunk_id,
                        namespace: $namespace,
                        document_id: $doc_id,
                        text: $text,
                        embedding: $embedding,
                        position: $position,
                        char_offset: $char_offset,
                        metadata: $metadata
                    })
                    CREATE (d)-[:CONTAINS {position: $position}]->(c)
                    """,
                    chunk_id=chunk_id,
                    namespace=namespace,
                    doc_id=str(document_id),
                    text=text,
                    embedding=embedding,  # Memgraph stores lists directly
                    position=position,
                    char_offset=char_offset,
                    metadata=json.dumps(metadata) if metadata else "{}",
                )
                logger.debug(
                    f"Created chunk with embedding: {chunk_id}",
                    extra={"stage": "chunk_create", "chunk_id": chunk_id},
                )
            except Exception as e:
                logger.error(
                    f"Failed to create chunk: {e}",
                    extra={"stage": "chunk_create", "chunk_id": chunk_id},
                    exc_info=True,
                )
                raise RuntimeError(f"Failed to create chunk node: {e}") from e

    def batch_create_chunks_with_embeddings(
        self,
        namespace: str,
        document_id: UUID,
        chunks_data: List[Tuple[str, str, List[float], int, int, dict]],
    ) -> None:
        """Batch create multiple chunks with embeddings.

        Args:
            namespace: Document namespace
            document_id: Parent document UUID
            chunks_data: List of tuples (chunk_id, text, embedding, position, char_offset, metadata)
        """
        with self.driver.session() as session:
            try:
                # Prepare batch data
                chunks = [
                    {
                        "id": chunk_id,
                        "namespace": namespace,
                        "document_id": str(document_id),
                        "text": text,
                        "embedding": embedding,
                        "position": position,
                        "char_offset": char_offset,
                        "metadata": json.dumps(metadata) if metadata else "{}",
                    }
                    for chunk_id, text, embedding, position, char_offset, metadata in chunks_data
                ]

                # Batch create chunks
                session.run(
                    """
                    MATCH (d:Document {id: $doc_id})
                    UNWIND $chunks AS chunk
                    CREATE (c:Chunk {
                        id: chunk.id,
                        namespace: chunk.namespace,
                        document_id: chunk.document_id,
                        text: chunk.text,
                        embedding: chunk.embedding,
                        position: chunk.position,
                        char_offset: chunk.char_offset,
                        metadata: chunk.metadata
                    })
                    CREATE (d)-[:CONTAINS {position: chunk.position}]->(c)
                    """,
                    doc_id=str(document_id),
                    chunks=chunks,
                )
                logger.info(
                    f"Created {len(chunks)} chunks with embeddings",
                    extra={
                        "stage": "batch_chunk_create",
                        "document_id": str(document_id),
                        "count": len(chunks),
                    },
                )
            except Exception as e:
                logger.error(
                    f"Failed to batch create chunks: {e}",
                    extra={"stage": "batch_chunk_create", "document_id": str(document_id)},
                    exc_info=True,
                )
                raise RuntimeError(f"Failed to batch create chunks: {e}") from e

    def vector_similarity_search(
        self,
        namespace: str,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.0,
    ) -> List[dict[str, Any]]:
        """Perform vector similarity search using cosine similarity.

        Args:
            namespace: Document namespace to search in
            query_embedding: Query vector embedding
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of chunks with similarity scores, sorted by relevance
        """
        with self.driver.session() as session:
            try:
                # Memgraph doesn't have built-in vector functions yet,
                # so we'll compute cosine similarity in Cypher
                # This will be optimized when Memgraph adds native vector support
                result = session.run(
                    """
                    MATCH (c:Chunk {namespace: $namespace})
                    WITH c,
                         reduce(dot = 0.0, i IN range(0, size($query_embedding)-1) |
                                dot + c.embedding[i] * $query_embedding[i]) AS dot_product,
                         sqrt(reduce(sum1 = 0.0, val IN c.embedding | sum1 + val * val)) AS norm1,
                         sqrt(reduce(sum2 = 0.0, val IN $query_embedding | sum2 + val * val)) AS norm2
                    WITH c, dot_product / (norm1 * norm2) AS similarity
                    WHERE similarity >= $threshold
                    RETURN c.id AS chunk_id,
                           c.text AS text,
                           c.document_id AS document_id,
                           c.position AS position,
                           c.metadata AS metadata,
                           similarity
                    ORDER BY similarity DESC
                    LIMIT $limit
                    """,
                    namespace=namespace,
                    query_embedding=query_embedding,
                    threshold=similarity_threshold,
                    limit=limit,
                )

                chunks = []
                for record in result:
                    chunk_data = {
                        "chunk_id": record["chunk_id"],
                        "text": record["text"],
                        "document_id": record["document_id"],
                        "position": record["position"],
                        "metadata": json.loads(record["metadata"]) if record["metadata"] else {},
                        "similarity_score": float(record["similarity"]),
                    }
                    chunks.append(chunk_data)

                logger.info(
                    f"Vector search found {len(chunks)} similar chunks",
                    extra={"stage": "vector_search", "count": len(chunks)},
                )
                return chunks

            except Exception as e:
                logger.error(
                    f"Vector similarity search failed: {e}",
                    extra={"stage": "vector_search"},
                    exc_info=True,
                )
                return []

    def keyword_search(
        self,
        namespace: str,
        query: str,
        limit: int = 20
    ) -> List[dict[str, Any]]:
        """Perform keyword search on chunk text.

        Args:
            namespace: Document namespace
            query: Search query
            limit: Maximum results

        Returns:
            List of chunk data dicts
        """
        with self.driver.session() as session:
            try:
                # Simple text containment search
                # For production, consider Memgraph's full-text search capabilities
                result = session.run(
                    """
                    MATCH (c:Chunk {namespace: $namespace})
                    WHERE toLower(c.text) CONTAINS toLower($query)
                    RETURN c.id AS chunk_id,
                           c.text AS text,
                           c.document_id AS document_id,
                           c.position AS position,
                           c.metadata AS metadata,
                           1.0 AS relevance_score
                    LIMIT $limit
                    """,
                    namespace=namespace,
                    query=query,
                    limit=limit,
                )

                chunks = []
                for record in result:
                    chunk_data = {
                        "chunk_id": record["chunk_id"],
                        "text": record["text"],
                        "document_id": record["document_id"],
                        "position": record["position"],
                        "metadata": json.loads(record["metadata"]) if record["metadata"] else {},
                        "relevance_score": float(record["relevance_score"]),
                    }
                    chunks.append(chunk_data)

                logger.info(
                    f"Keyword search found {len(chunks)} matching chunks",
                    extra={"stage": "keyword_search", "count": len(chunks)},
                )
                return chunks

            except Exception as e:
                logger.warning(
                    f"Keyword search failed: {e}",
                    extra={"stage": "keyword_search"},
                )
                return []

    def get_document_info(self, namespace: str, filename: str) -> Optional[dict]:
        """Get document information by namespace and filename.

        Args:
            namespace: Document namespace
            filename: Document filename

        Returns:
            Document info dict or None if not found
        """
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MATCH (d:Document {namespace: $namespace, filename: $filename})
                    RETURN d.id AS id,
                           d.filename AS filename,
                           d.chunk_count AS chunk_count,
                           d.metadata AS metadata
                    """,
                    namespace=namespace,
                    filename=filename,
                )
                record = result.single()
                if record:
                    return {
                        "id": record["id"],
                        "filename": record["filename"],
                        "chunk_count": record["chunk_count"],
                        "metadata": json.loads(record["metadata"]) if record["metadata"] else {},
                    }
                return None
            except Exception as e:
                logger.warning(
                    f"Failed to get document info: {e}",
                    extra={"stage": "document_info"},
                )
                return None

    def namespace_exists(self, namespace: str) -> bool:
        """Check if any documents exist for a namespace.

        Args:
            namespace: Document namespace

        Returns:
            True if namespace has documents
        """
        with self.driver.session() as session:
            try:
                result = session.run(
                    "MATCH (d:Document {namespace: $namespace}) RETURN count(d) AS count",
                    namespace=namespace,
                )
                count = result.single()["count"]
                return count > 0
            except Exception as e:
                logger.warning(
                    f"Failed to check namespace existence: {e}",
                    extra={"stage": "namespace_check"},
                )
                return False

    def get_chunk_by_id(self, chunk_id: str) -> Optional[dict]:
        """Get a chunk by its ID.

        Args:
            chunk_id: Chunk UUID

        Returns:
            Chunk data dict or None if not found
        """
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MATCH (c:Chunk {id: $chunk_id})
                    RETURN c.id AS chunk_id,
                           c.text AS text,
                           c.document_id AS document_id,
                           c.position AS position,
                           c.metadata AS metadata
                    """,
                    chunk_id=chunk_id,
                )
                record = result.single()
                if record:
                    return {
                        "chunk_id": record["chunk_id"],
                        "text": record["text"],
                        "document_id": record["document_id"],
                        "position": record["position"],
                        "metadata": json.loads(record["metadata"]) if record["metadata"] else {},
                    }
                return None
            except Exception as e:
                logger.warning(
                    f"Failed to get chunk: {e}",
                    extra={"stage": "get_chunk"},
                )
                return None