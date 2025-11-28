"""
Graph store for managing knowledge graph entities and relationships.
"""
from typing import List, Optional, Dict, Any
import logging
from ..models.knowledge_graph import EntityNode, ConceptNode, Relationship
from ..lib.database import DatabaseConnection
from ..lib.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class GraphStore:
    """Store for managing knowledge graph entities and relationships in the database."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize graph store.

        Args:
            db_connection: Database connection instance
        """
        self.db_connection = db_connection

    def store_entity(self, entity: EntityNode) -> None:
        """Store an entity node in the database.

        Args:
            entity: Entity node to store

        Raises:
            DatabaseError: If storing fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                CREATE (e:Entity {
                    id: $id,
                    name: $name,
                    type: $type,
                    properties: $properties,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                """
                session.run(query, {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "properties": entity.properties,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat()
                })
            logger.info("Stored entity %s (%s)", entity.id, entity.name)
        except Exception as e:
            logger.error("Failed to store entity %s: %s", entity.id, str(e))
            raise DatabaseError(f"Failed to store entity: {str(e)}")

    def store_concept(self, concept: ConceptNode) -> None:
        """Store a concept node in the database.

        Args:
            concept: Concept node to store

        Raises:
            DatabaseError: If storing fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                CREATE (c:Concept {
                    id: $id,
                    name: $name,
                    description: $description,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                """
                session.run(query, {
                    "id": concept.id,
                    "name": concept.name,
                    "description": concept.description,
                    "created_at": concept.created_at.isoformat(),
                    "updated_at": concept.updated_at.isoformat()
                })
            logger.info("Stored concept %s (%s)", concept.id, concept.name)
        except Exception as e:
            logger.error("Failed to store concept %s: %s", concept.id, str(e))
            raise DatabaseError(f"Failed to store concept: {str(e)}")

    def store_relationship(self, relationship: Relationship) -> None:
        """Store a relationship in the database.

        Args:
            relationship: Relationship to store

        Raises:
            DatabaseError: If storing fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (source {id: $source_id}), (target {id: $target_id})
                CREATE (source)-[r:RELATIONSHIP {
                    id: $id,
                    type: $type,
                    confidence: $confidence,
                    source_chunk_id: $source_chunk_id,
                    created_at: $created_at,
                    updated_at: $updated_at
                }]->(target)
                """
                session.run(query, {
                    "source_id": relationship.source_id,
                    "target_id": relationship.target_id,
                    "id": relationship.id,
                    "type": relationship.type,
                    "confidence": relationship.confidence,
                    "source_chunk_id": relationship.source_chunk_id,
                    "created_at": relationship.created_at.isoformat(),
                    "updated_at": relationship.updated_at.isoformat()
                })
            logger.info("Stored relationship %s (%s)", relationship.id, relationship.type)
        except Exception as e:
            logger.error("Failed to store relationship %s: %s", relationship.id, str(e))
            raise DatabaseError(f"Failed to store relationship: {str(e)}")

    def get_entity(self, entity_id: str) -> Optional[EntityNode]:
        """Retrieve an entity node from the database.

        Args:
            entity_id: ID of the entity to retrieve

        Returns:
            EntityNode object or None if not found

        Raises:
            DatabaseError: If retrieval fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (e:Entity {id: $entity_id})
                RETURN e
                """
                result = session.run(query, {"entity_id": entity_id})
                record = result.single()

                if not record:
                    return None

                node = record["e"]
                return EntityNode.from_dict(dict(node))
        except Exception as e:
            logger.error("Failed to retrieve entity %s: %s", entity_id, str(e))
            raise DatabaseError(f"Failed to retrieve entity: {str(e)}")

    def get_entities_by_chunk_id(self, chunk_id: str) -> List[EntityNode]:
        """Retrieve entities associated with a chunk.

        Args:
            chunk_id: ID of the chunk

        Returns:
            List of EntityNode objects

        Raises:
            DatabaseError: If retrieval fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (c:Chunk {id: $chunk_id})-[:CONTAINS_ENTITY]->(e:Entity)
                RETURN e
                """
                result = session.run(query, {"chunk_id": chunk_id})

                entities = []
                for record in result:
                    node = record["e"]
                    entities.append(EntityNode.from_dict(dict(node)))

                return entities
        except Exception as e:
            logger.error("Failed to retrieve entities for chunk %s: %s", chunk_id, str(e))
            raise DatabaseError(f"Failed to retrieve entities: {str(e)}")

    def get_relationships_by_entity(self, entity_id: str) -> List[Relationship]:
        """Retrieve relationships for an entity.

        Args:
            entity_id: ID of the entity

        Returns:
            List of Relationship objects

        Raises:
            DatabaseError: If retrieval fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (e {id: $entity_id})-[r:RELATIONSHIP]->(t)
                RETURN r
                """
                result = session.run(query, {"entity_id": entity_id})

                relationships = []
                for record in result:
                    rel = record["r"]
                    relationships.append(Relationship.from_dict(dict(rel)))

                return relationships
        except Exception as e:
            logger.error("Failed to retrieve relationships for entity %s: %s", entity_id, str(e))
            raise DatabaseError(f"Failed to retrieve relationships: {str(e)}")

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity from the database.

        Args:
            entity_id: ID of the entity to delete

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (e:Entity {id: $entity_id})
                DETACH DELETE e
                """
                result = session.run(query, {"entity_id": entity_id})
                return result.consume().counters.nodes_deleted > 0
        except Exception as e:
            logger.error("Failed to delete entity %s: %s", entity_id, str(e))
            raise DatabaseError(f"Failed to delete entity: {str(e)}")