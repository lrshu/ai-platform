"""
Vector store for managing vector embeddings.
"""
from typing import List, Optional, Dict, Any
import logging
from ..models.vector import Vector
from ..lib.database import DatabaseConnection
from ..lib.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class VectorStore:
    """Store for managing vector embeddings in the database."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize vector store.

        Args:
            db_connection: Database connection instance
        """
        self.db_connection = db_connection

    def store_vector(self, vector: Vector) -> None:
        """Store a vector in the database.

        Args:
            vector: Vector to store

        Raises:
            DatabaseError: If storing fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                CREATE (v:Vector {
                    id: $id,
                    chunk_id: $chunk_id,
                    embedding: $embedding,
                    model_name: $model_name,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                """
                session.run(query, {
                    "id": vector.id,
                    "chunk_id": vector.chunk_id,
                    "embedding": vector.embedding,
                    "model_name": vector.model_name,
                    "created_at": vector.created_at.isoformat(),
                    "updated_at": vector.updated_at.isoformat()
                })
            logger.info("Stored vector %s for chunk %s", vector.id, vector.chunk_id)
        except Exception as e:
            logger.error("Failed to store vector %s: %s", vector.id, str(e))
            raise DatabaseError(f"Failed to store vector: {str(e)}")

    def store_vectors(self, vectors: List[Vector]) -> None:
        """Store multiple vectors in the database.

        Args:
            vectors: List of vectors to store

        Raises:
            DatabaseError: If storing fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                UNWIND $vectors AS v
                CREATE (vec:Vector {
                    id: v.id,
                    chunk_id: v.chunk_id,
                    embedding: v.embedding,
                    model_name: v.model_name,
                    created_at: v.created_at,
                    updated_at: v.updated_at
                })
                """

                vector_data = []
                for vector in vectors:
                    vector_data.append({
                        "id": vector.id,
                        "chunk_id": vector.chunk_id,
                        "embedding": vector.embedding,
                        "model_name": vector.model_name,
                        "created_at": vector.created_at.isoformat(),
                        "updated_at": vector.updated_at.isoformat()
                    })

                session.run(query, {"vectors": vector_data})
            logger.info("Stored %d vectors", len(vectors))
        except Exception as e:
            logger.error("Failed to store vectors: %s", str(e))
            raise DatabaseError(f"Failed to store vectors: {str(e)}")

    def get_vector(self, vector_id: str) -> Optional[Vector]:
        """Retrieve a vector from the database.

        Args:
            vector_id: ID of the vector to retrieve

        Returns:
            Vector object or None if not found

        Raises:
            DatabaseError: If retrieval fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (v:Vector {id: $vector_id})
                RETURN v
                """
                result = session.run(query, {"vector_id": vector_id})
                record = result.single()

                if not record:
                    return None

                node = record["v"]
                return Vector.from_dict(dict(node))
        except Exception as e:
            logger.error("Failed to retrieve vector %s: %s", vector_id, str(e))
            raise DatabaseError(f"Failed to retrieve vector: {str(e)}")

    def get_vectors_by_chunk_ids(self, chunk_ids: List[str]) -> List[Vector]:
        """Retrieve vectors by chunk IDs.

        Args:
            chunk_ids: List of chunk IDs

        Returns:
            List of Vector objects

        Raises:
            DatabaseError: If retrieval fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (v:Vector)
                WHERE v.chunk_id IN $chunk_ids
                RETURN v
                """
                result = session.run(query, {"chunk_ids": chunk_ids})

                vectors = []
                for record in result:
                    node = record["v"]
                    vectors.append(Vector.from_dict(dict(node)))

                return vectors
        except Exception as e:
            logger.error("Failed to retrieve vectors by chunk IDs: %s", str(e))
            raise DatabaseError(f"Failed to retrieve vectors: {str(e)}")

    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from the database.

        Args:
            vector_id: ID of the vector to delete

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (v:Vector {id: $vector_id})
                DELETE v
                """
                result = session.run(query, {"vector_id": vector_id})
                return result.consume().counters.nodes_deleted > 0
        except Exception as e:
            logger.error("Failed to delete vector %s: %s", vector_id, str(e))
            raise DatabaseError(f"Failed to delete vector: {str(e)}")