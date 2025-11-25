"""Storage service for the indexing pipeline."""

from typing import List
from datetime import datetime
from neo4j import Transaction
from src.config.database import db_config
from src.models import Document, Chunk
from src.models.kg import Entity, Relationship
from src.lib.logging_config import logger, DatabaseError


class StorageService:
    """Service for storing indexed content in the database."""

    def __init__(self):
        """Initialize the storage service."""
        self.driver = db_config.get_driver()

    def store_document(self, document: Document) -> str:
        """
        Store a document in the database.

        Args:
            document (Document): Document to store

        Returns:
            str: Document ID

        Raises:
            DatabaseError: If there's an error storing the document
        """
        try:
            logger.info(f"Storing document: {document.name}")

            with self.driver.session() as session:
                result = session.write_transaction(
                    self._create_document_node, document
                )

            logger.info(f"Successfully stored document: {document.name}")
            return document.id

        except Exception as e:
            logger.error(f"Error storing document {document.name}: {str(e)}")
            raise DatabaseError(f"Failed to store document: {str(e)}")

    def store_chunks(self, chunks: List[Chunk]) -> List[str]:
        """
        Store chunks in the database.

        Args:
            chunks (List[Chunk]): Chunks to store

        Returns:
            List[str]: List of chunk IDs

        Raises:
            DatabaseError: If there's an error storing the chunks
        """
        try:
            logger.info(f"Storing {len(chunks)} chunks")

            chunk_ids = []
            with self.driver.session() as session:
                for chunk in chunks:
                    result = session.write_transaction(
                        self._create_chunk_node, chunk
                    )
                    chunk_ids.append(chunk.id)

            logger.info(f"Successfully stored {len(chunks)} chunks")
            return chunk_ids

        except Exception as e:
            logger.error(f"Error storing chunks: {str(e)}")
            raise DatabaseError(f"Failed to store chunks: {str(e)}")

    def store_entities_and_relationships(self, entities: List[Entity], relationships: List[Relationship]) -> None:
        """
        Store entities and relationships in the database.

        Args:
            entities (List[Entity]): Entities to store
            relationships (List[Relationship]): Relationships to store

        Raises:
            DatabaseError: If there's an error storing the entities and relationships
        """
        try:
            logger.info(f"Storing {len(entities)} entities and {len(relationships)} relationships")

            with self.driver.session() as session:
                # Store entities
                for entity in entities:
                    session.write_transaction(
                        self._create_entity_node, entity
                    )

                # Store relationships
                for relationship in relationships:
                    session.write_transaction(
                        self._create_relationship, relationship
                    )

            logger.info(f"Successfully stored {len(entities)} entities and {len(relationships)} relationships")

        except Exception as e:
            logger.error(f"Error storing entities and relationships: {str(e)}")
            raise DatabaseError(f"Failed to store entities and relationships: {str(e)}")

    @staticmethod
    def _create_document_node(tx: Transaction, document: Document) -> str:
        """Create a document node in the database."""
        query = (
            "CREATE (d:Document {id: $id, name: $name, file_path: $file_path, "
            "created_at: $created_at, status: $status, chunk_count: $chunk_count, metadata: $metadata}) "
            "RETURN d.id"
        )
        result = tx.run(
            query,
            id=document.id,
            name=document.name,
            file_path=document.file_path,
            created_at=document.created_at.isoformat(),
            status=document.status,
            chunk_count=document.chunk_count,
            metadata=document.metadata
        )
        return result.single()[0]

    @staticmethod
    def _create_chunk_node(tx: Transaction, chunk: Chunk) -> str:
        """Create a chunk node in the database."""
        query = (
            "CREATE (c:Chunk {id: $id, document_id: $document_id, content: $content, "
            "position: $position, created_at: $created_at, metadata: $metadata}) "
            "RETURN c.id"
        )
        result = tx.run(
            query,
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            position=chunk.position,
            created_at=chunk.created_at.isoformat(),
            metadata=chunk.metadata
        )
        return result.single()[0]

    @staticmethod
    def _create_entity_node(tx: Transaction, entity: Entity) -> str:
        """Create an entity node in the database."""
        query = (
            "CREATE (e:Entity {id: $id, name: $name, type: $type, description: $description}) "
            "RETURN e.id"
        )
        result = tx.run(
            query,
            id=entity.id,
            name=entity.name,
            type=entity.type,
            description=entity.description
        )
        return result.single()[0]

    @staticmethod
    def _create_relationship(tx: Transaction, relationship: Relationship) -> str:
        """Create a relationship in the database."""
        query = (
            "MATCH (source:Entity {id: $source_id}), (target:Entity {id: $target_id}) "
            "CREATE (source)-[r:RELATIONSHIP {id: $id, type: $type, description: $description, confidence: $confidence}]->(target) "
            "RETURN r.id"
        )
        result = tx.run(
            query,
            source_id=relationship.source_entity_id,
            target_id=relationship.target_entity_id,
            id=relationship.id,
            type=relationship.type,
            description=relationship.description,
            confidence=relationship.confidence
        )
        return result.single()[0]


# Global instance
storage_service = StorageService()