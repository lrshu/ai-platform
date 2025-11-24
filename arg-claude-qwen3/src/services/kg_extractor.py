"""
Knowledge graph extraction service for the RAG backend system.
"""

from typing import List, Tuple
from src.lib.rerank_client import get_rerank_client
from src.lib.llm_client import get_llm_client
from src.lib.exceptions import LLMGenerationError
from src.models.knowledge_graph_node import KnowledgeGraphNode
from src.models.knowledge_graph_relationship import KnowledgeGraphRelationship
import json
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphExtractor:
    """Service for extracting entities and relationships from document chunks."""

    def __init__(self):
        """Initialize the KnowledgeGraphExtractor."""
        self.rerank_client = get_rerank_client()
        self.llm_client = get_llm_client()

    def extract_entities_and_relationships(self, chunk_id: str, text: str) -> Tuple[List[KnowledgeGraphNode], List[KnowledgeGraphRelationship]]:
        """
        Extract entities and relationships from a text chunk.

        Args:
            chunk_id: ID of the chunk being processed
            text: Text content to extract entities and relationships from

        Returns:
            Tuple of (entities, relationships)
        """
        try:
            # Create prompt for entity extraction
            entity_prompt = f"""
            Extract named entities from the following text. Return a JSON array of entities with the following format:
            [
                {{"type": "person|organization|location|concept|other", "name": "entity name", "description": "brief description"}}
            ]

            Text: {text}

            Entities:
            """

            # Generate entity extraction using LLM
            entity_response = self.llm_client.generate_completion(
                entity_prompt,
                temperature=0.3,
                max_tokens=1000
            )

            # Parse entity response
            try:
                entities_data = json.loads(entity_response)
                entities = []
                for entity_data in entities_data:
                    entity = KnowledgeGraphNode(
                        chunk_id=chunk_id,
                        entity_type=entity_data["type"],
                        name=entity_data["name"],
                        description=entity_data.get("description", "")
                    )
                    entities.append(entity)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse entity response for chunk {chunk_id}, using empty list")
                entities = []

            # Create prompt for relationship extraction
            relationship_prompt = f"""
            Extract relationships between entities from the following text. Return a JSON array of relationships with the following format:
            [
                {{"source": "source entity name", "target": "target entity name", "type": "relationship type", "description": "brief description"}}
            ]

            Entities found: {[{"name": e.name, "type": e.entity_type} for e in entities]}

            Text: {text}

            Relationships:
            """

            # Generate relationship extraction using LLM
            relationship_response = self.llm_client.generate_completion(
                relationship_prompt,
                temperature=0.3,
                max_tokens=1000
            )

            # Parse relationship response
            try:
                relationships_data = json.loads(relationship_response)
                relationships = []
                # Create a mapping of entity names to entity objects for reference resolution
                entity_map = {entity.name.lower(): entity for entity in entities}

                for rel_data in relationships_data:
                    source_name = rel_data["source"].lower()
                    target_name = rel_data["target"].lower()

                    # Only create relationships if both entities exist
                    if source_name in entity_map and target_name in entity_map:
                        relationship = KnowledgeGraphRelationship(
                            source_node_id=entity_map[source_name].id,
                            target_node_id=entity_map[target_name].id,
                            relationship_type=rel_data["type"],
                            description=rel_data.get("description", "")
                        )
                        relationships.append(relationship)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse relationship response for chunk {chunk_id}, using empty list")
                relationships = []

            logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships from chunk {chunk_id}")
            return entities, relationships

        except Exception as e:
            logger.error(f"Failed to extract knowledge graph from chunk {chunk_id}: {e}")
            # Return empty lists on failure
            return [], []

    def extract_entities(self, chunk_id: str, text: str) -> List[KnowledgeGraphNode]:
        """
        Extract entities from a text chunk.

        Args:
            chunk_id: ID of the chunk being processed
            text: Text content to extract entities from

        Returns:
            List of KnowledgeGraphNode objects
        """
        entities, _ = self.extract_entities_and_relationships(chunk_id, text)
        return entities

    def extract_relationships(self, chunk_id: str, text: str, entities: List[KnowledgeGraphNode]) -> List[KnowledgeGraphRelationship]:
        """
        Extract relationships from a text chunk.

        Args:
            chunk_id: ID of the chunk being processed
            text: Text content to extract relationships from
            entities: List of entities already extracted from the text

        Returns:
            List of KnowledgeGraphRelationship objects
        """
        _, relationships = self.extract_entities_and_relationships(chunk_id, text)
        return relationships


# Global knowledge graph extractor instance
kg_extractor = KnowledgeGraphExtractor()


def get_kg_extractor() -> KnowledgeGraphExtractor:
    """
    Get the global knowledge graph extractor instance.

    Returns:
        KnowledgeGraphExtractor instance
    """
    return kg_extractor