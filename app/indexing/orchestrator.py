"""
Indexing orchestrator for RAG backend implementation.
"""

import asyncio
import logging
from typing import List, Dict, Any
from pathlib import Path
from app.common.factory import provider_factory
from app.common.models import Chunk, Entity, Relationship
from app.indexing.chunker import Chunker

# Configure logging
logger = logging.getLogger(__name__)


class IndexingOrchestrator:
    """Orchestrator for the document indexing pipeline."""

    def __init__(self):
        """Initialize the indexing orchestrator."""
        self.parser = provider_factory.create_parser_provider()
        self.embedder = provider_factory.create_embedder_provider()
        self.database = provider_factory.create_database_provider()
        self.chunker = Chunker()

        # Connect to database
        asyncio.create_task(self._connect_database())

    async def _connect_database(self):
        """Connect to the database."""
        try:
            await self.database.connect()
            logger.info("Connected to database for indexing")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def index_document(self, document_path: Path, collection_name: str = "default") -> Dict[str, Any]:
        """
        Index a document through the complete pipeline.

        Args:
            document_path: Path to the document file
            collection_name: Name of the collection to index into

        Returns:
            Dictionary with indexing results
        """
        try:
            logger.info(f"Starting indexing process for document: {document_path}")

            # Step 1: Parse document
            parsed_chunks = await self._parse_document(document_path)
            logger.info(f"Parsed document into {len(parsed_chunks)} chunks")

            # Step 2: Create parent and child chunks
            parent_chunks, child_chunks = await self._create_chunks(
                document_path.name, parsed_chunks, collection_name
            )
            logger.info(f"Created {len(parent_chunks)} parent chunks and {len(child_chunks)} child chunks")

            # Step 3: Generate embeddings
            parent_embeddings = await self._generate_embeddings(parent_chunks)
            child_embeddings = await self._generate_embeddings(child_chunks)
            logger.info("Generated embeddings for chunks")

            # Step 4: Extract entities and relationships
            entities, relationships = await self._extract_entities_and_relationships(parsed_chunks)
            logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")

            # Step 5: Store in database
            await self._store_in_database(
                parent_chunks, child_chunks,
                parent_embeddings, child_embeddings,
                entities, relationships,
                collection_name
            )
            logger.info("Stored all data in database")

            # Return results
            return {
                "status": "completed",
                "document_id": document_path.name,
                "parent_chunks": len(parent_chunks),
                "child_chunks": len(child_chunks),
                "entities": len(entities),
                "relationships": len(relationships)
            }

        except Exception as e:
            logger.error(f"Error indexing document {document_path}: {e}")
            return {
                "status": "failed",
                "document_id": document_path.name,
                "error": str(e)
            }

    async def _parse_document(self, document_path: Path) -> List[Dict[str, Any]]:
        """
        Parse document using the configured parser.

        Args:
            document_path: Path to the document file

        Returns:
            List of parsed content chunks
        """
        logger.info(f"Parsing document: {document_path}")
        return await self.parser.parse_document(document_path)

    async def _create_chunks(self, document_id: str, parsed_chunks: List[Dict[str, Any]],
                           collection_name: str) -> tuple[List[Chunk], List[Chunk]]:
        """
        Create parent and child chunks from parsed content.

        Args:
            document_id: ID of the document
            parsed_chunks: List of parsed content chunks
            collection_name: Name of the collection

        Returns:
            Tuple of (parent_chunks, child_chunks)
        """
        # Combine all parsed content into a single string for chunking
        full_content = "\n".join([chunk.get('content', '') for chunk in parsed_chunks])

        # Get metadata from first chunk (assuming consistent metadata)
        first_chunk = parsed_chunks[0] if parsed_chunks else {}
        source_type = first_chunk.get('metadata', {}).get('source_type', 'unknown')
        title = first_chunk.get('metadata', {}).get('title', '')
        author = first_chunk.get('metadata', {}).get('author', '')

        # Create chunks using the chunker
        parent_chunks, child_chunks = self.chunker.create_chunks(
            document_id, full_content, source_type, title, author
        )

        return parent_chunks, child_chunks

    async def _generate_embeddings(self, chunks: List[Chunk]) -> List[List[float]]:
        """
        Generate embeddings for chunks.

        Args:
            chunks: List of chunks to embed

        Returns:
            List of embeddings
        """
        if not chunks:
            return []

        # Extract content from chunks
        contents = [chunk.content for chunk in chunks]

        # Generate embeddings
        embeddings = await self.embedder.embed_text(contents)

        # Attach embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        return embeddings

    async def _extract_entities_and_relationships(self, parsed_chunks: List[Dict[str, Any]]) -> \
            tuple[List[Entity], List[Relationship]]:
        """
        Extract entities and relationships from parsed content.

        Args:
            parsed_chunks: List of parsed content chunks

        Returns:
            Tuple of (entities, relationships)
        """
        # For now, return empty lists
        # In a real implementation, this would use an LLM to extract entities and relationships
        return [], []

    async def _store_in_database(self, parent_chunks: List[Chunk], child_chunks: List[Chunk],
                               parent_embeddings: List[List[float]], child_embeddings: List[List[float]],
                               entities: List[Entity], relationships: List[Relationship],
                               collection_name: str) -> None:
        """
        Store all data in the database.

        Args:
            parent_chunks: Parent chunks to store
            child_chunks: Child chunks to store
            parent_embeddings: Embeddings for parent chunks
            child_embeddings: Embeddings for child chunks
            entities: Entities to store
            relationships: Relationships to store
            collection_name: Name of the collection
        """
        # Store parent chunks with embeddings
        for chunk in parent_chunks:
            await self.database.store_vector(
                f"{collection_name}_parents",
                chunk.embedding,
                {
                    "chunk_id": chunk.id,
                    "content": chunk.content,
                    "metadata": chunk.metadata.dict()
                }
            )

        # Store child chunks with embeddings
        for chunk in child_chunks:
            await self.database.store_vector(
                f"{collection_name}_children",
                chunk.embedding,
                {
                    "chunk_id": chunk.id,
                    "content": chunk.content,
                    "metadata": chunk.metadata.dict()
                }
            )

        # Store entities as graph nodes
        for entity in entities:
            await self.database.store_graph_node(
                "Entity",
                {
                    "entity_id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "description": entity.description
                }
            )

        # Store relationships as graph edges
        for relationship in relationships:
            await self.database.store_graph_relationship(
                relationship.source_entity_id,
                relationship.target_entity_id,
                relationship.relationship_type,
                {
                    "relationship_id": relationship.id,
                    "description": relationship.description,
                    "confidence": relationship.confidence
                }
            )

    async def batch_index_documents(self, document_paths: List[Path], collection_name: str = "default") -> List[Dict[str, Any]]:
        """
        Index multiple documents concurrently.

        Args:
            document_paths: List of paths to document files
            collection_name: Name of the collection to index into

        Returns:
            List of indexing results
        """
        tasks = [
            self.index_document(doc_path, collection_name)
            for doc_path in document_paths
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "status": "failed",
                    "document_id": document_paths[i].name,
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results