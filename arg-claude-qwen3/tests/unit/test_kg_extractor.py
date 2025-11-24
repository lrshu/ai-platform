"""
Unit tests for the knowledge graph extractor service.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.kg_extractor import KnowledgeGraphExtractor
from src.models.knowledge_graph_node import KnowledgeGraphNode
from src.models.knowledge_graph_relationship import KnowledgeGraphRelationship


class TestKnowledgeGraphExtractor:
    """Test the knowledge graph extractor service."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.extractor = KnowledgeGraphExtractor()

    def test_extract_entities_and_relationships_success(self):
        """Test successful extraction of entities and relationships."""
        chunk_id = "test_chunk_123"
        text = "Apple Inc. was founded by Steve Jobs in Cupertino."

        # Mock LLM responses
        entity_response = """[
            {"type": "organization", "name": "Apple Inc.", "description": "Technology company"},
            {"type": "person", "name": "Steve Jobs", "description": "Co-founder of Apple"},
            {"type": "location", "name": "Cupertino", "description": "City in California"}
        ]"""

        relationship_response = """[
            {"source": "Steve Jobs", "target": "Apple Inc.", "type": "founded", "description": "Steve Jobs founded Apple Inc."},
            {"source": "Apple Inc.", "target": "Cupertino", "type": "located_in", "description": "Apple Inc. is located in Cupertino"}
        ]"""

        with patch.object(self.extractor.llm_client, 'generate_completion') as mock_llm:
            # Configure mock to return different responses for different calls
            mock_llm.side_effect = [entity_response, relationship_response]

            entities, relationships = self.extractor.extract_entities_and_relationships(chunk_id, text)

            # Verify entities
            assert len(entities) == 3
            assert all(isinstance(entity, KnowledgeGraphNode) for entity in entities)

            # Find entities by name
            apple_entity = next((e for e in entities if e.name == "Apple Inc."), None)
            steve_entity = next((e for e in entities if e.name == "Steve Jobs"), None)
            cupertino_entity = next((e for e in entities if e.name == "Cupertino"), None)

            assert apple_entity is not None
            assert apple_entity.entity_type == "organization"
            assert apple_entity.description == "Technology company"

            assert steve_entity is not None
            assert steve_entity.entity_type == "person"
            assert steve_entity.description == "Co-founder of Apple"

            assert cupertino_entity is not None
            assert cupertino_entity.entity_type == "location"
            assert cupertino_entity.description == "City in California"

            # Verify relationships
            assert len(relationships) == 2
            assert all(isinstance(rel, KnowledgeGraphRelationship) for rel in relationships)

            # Check relationship properties
            founded_rel = relationships[0]
            located_rel = relationships[1]

            assert founded_rel.relationship_type == "founded"
            assert founded_rel.description == "Steve Jobs founded Apple Inc."

            assert located_rel.relationship_type == "located_in"
            assert located_rel.description == "Apple Inc. is located in Cupertino"

    def test_extract_entities_and_relationships_invalid_json(self):
        """Test extraction when LLM returns invalid JSON."""
        chunk_id = "test_chunk_123"
        text = "Test text"

        with patch.object(self.extractor.llm_client, 'generate_completion') as mock_llm:
            # Return invalid JSON
            mock_llm.return_value = "This is not valid JSON"

            entities, relationships = self.extractor.extract_entities_and_relationships(chunk_id, text)

            # Should return empty lists when JSON parsing fails
            assert entities == []
            assert relationships == []

    def test_extract_entities_and_relationships_llm_error(self):
        """Test extraction when LLM client fails."""
        chunk_id = "test_chunk_123"
        text = "Test text"

        with patch.object(self.extractor.llm_client, 'generate_completion') as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")

            entities, relationships = self.extractor.extract_entities_and_relationships(chunk_id, text)

            # Should return empty lists when LLM fails
            assert entities == []
            assert relationships == []

    def test_extract_entities_success(self):
        """Test successful entity extraction."""
        chunk_id = "test_chunk_123"
        text = "Apple Inc. was founded by Steve Jobs."

        # Mock the extract_entities_and_relationships method
        mock_entities = [
            KnowledgeGraphNode(chunk_id, "organization", "Apple Inc.", "Technology company"),
            KnowledgeGraphNode(chunk_id, "person", "Steve Jobs", "Co-founder of Apple")
        ]

        with patch.object(self.extractor, 'extract_entities_and_relationships') as mock_extract:
            mock_extract.return_value = (mock_entities, [])

            entities = self.extractor.extract_entities(chunk_id, text)

            assert entities == mock_entities

    def test_extract_relationships_success(self):
        """Test successful relationship extraction."""
        chunk_id = "test_chunk_123"
        text = "Apple Inc. was founded by Steve Jobs."
        entities = [
            KnowledgeGraphNode(chunk_id, "organization", "Apple Inc.", "Technology company"),
            KnowledgeGraphNode(chunk_id, "person", "Steve Jobs", "Co-founder of Apple")
        ]

        # Mock the extract_entities_and_relationships method
        mock_relationships = [
            KnowledgeGraphRelationship(
                source_node_id=entities[1].id,
                target_node_id=entities[0].id,
                relationship_type="founded",
                description="Steve Jobs founded Apple Inc."
            )
        ]

        with patch.object(self.extractor, 'extract_entities_and_relationships') as mock_extract:
            mock_extract.return_value = ([], mock_relationships)

            relationships = self.extractor.extract_relationships(chunk_id, text, entities)

            assert relationships == mock_relationships


if __name__ == "__main__":
    pytest.main([__file__])