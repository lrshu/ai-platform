"""
KnowledgeGraph model for the RAG system.
"""
from typing import Dict, Any, Optional, List, Union
from .base import BaseModel
from datetime import datetime


class EntityNode(BaseModel):
    """Represents an entity in the knowledge graph."""

    def __init__(
        self,
        name: str,
        type: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Union[str, int, float]]] = None
    ):
        """Initialize entity node.

        Args:
            name: Name of the entity
            type: Type/category of entity (person, organization, location, etc.)
            id: Optional unique identifier
            properties: Additional entity properties
        """
        super().__init__(id)
        self.name = name
        self.type = type
        self.properties = properties or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity node to dictionary representation.

        Returns:
            Dictionary representation of the entity node
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityNode':
        """Create entity node from dictionary representation.

        Args:
            data: Dictionary representation of the entity node

        Returns:
            EntityNode instance
        """
        node = cls(
            name=data["name"],
            type=data["type"],
            id=data["id"],
            properties=data.get("properties", {})
        )

        node.created_at = data.get("created_at") and datetime.fromisoformat(data["created_at"])
        node.updated_at = data.get("updated_at") and datetime.fromisoformat(data["updated_at"])

        return node

    def __str__(self) -> str:
        """String representation."""
        return f"EntityNode(name='{self.name}', type='{self.type}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"EntityNode(id='{self.id}', name='{self.name}', type='{self.type}', properties={self.properties})"


class ConceptNode(BaseModel):
    """Represents a concept in the knowledge graph."""

    def __init__(
        self,
        name: str,
        description: str,
        id: Optional[str] = None
    ):
        """Initialize concept node.

        Args:
            name: Name of the concept
            description: Description of the concept
            id: Optional unique identifier
        """
        super().__init__(id)
        self.name = name
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert concept node to dictionary representation.

        Returns:
            Dictionary representation of the concept node
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConceptNode':
        """Create concept node from dictionary representation.

        Args:
            data: Dictionary representation of the concept node

        Returns:
            ConceptNode instance
        """
        node = cls(
            name=data["name"],
            description=data["description"],
            id=data["id"]
        )

        node.created_at = data.get("created_at") and datetime.fromisoformat(data["created_at"])
        node.updated_at = data.get("updated_at") and datetime.fromisoformat(data["updated_at"])

        return node

    def __str__(self) -> str:
        """String representation."""
        return f"ConceptNode(name='{self.name}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ConceptNode(id='{self.id}', name='{self.name}', description='{self.description}')"


class Relationship(BaseModel):
    """Represents a relationship between nodes in the knowledge graph."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        type: str,
        id: Optional[str] = None,
        confidence: float = 1.0,
        source_chunk_id: Optional[str] = None
    ):
        """Initialize relationship.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            type: Type of relationship
            id: Optional unique identifier
            confidence: Confidence score of the relationship
            source_chunk_id: Reference to originating chunk
        """
        super().__init__(id)
        self.source_id = source_id
        self.target_id = target_id
        self.type = type
        self.confidence = confidence
        self.source_chunk_id = source_chunk_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary representation.

        Returns:
            Dictionary representation of the relationship
        """
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "confidence": self.confidence,
            "source_chunk_id": self.source_chunk_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create relationship from dictionary representation.

        Args:
            data: Dictionary representation of the relationship

        Returns:
            Relationship instance
        """
        rel = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            type=data["type"],
            id=data["id"],
            confidence=data.get("confidence", 1.0),
            source_chunk_id=data.get("source_chunk_id")
        )

        rel.created_at = data.get("created_at") and datetime.fromisoformat(data["created_at"])
        rel.updated_at = data.get("updated_at") and datetime.fromisoformat(data["updated_at"])

        return rel

    def __str__(self) -> str:
        """String representation."""
        return f"Relationship(type='{self.type}', confidence={self.confidence})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Relationship(id='{self.id}', source_id='{self.source_id}', target_id='{self.target_id}', type='{self.type}', confidence={self.confidence})"