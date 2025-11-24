"""
KnowledgeGraphRelationship model for the RAG backend system.
"""

from typing import Optional
from datetime import datetime
import uuid


class KnowledgeGraphRelationship:
    """Represents a relationship between two entities."""

    def __init__(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        description: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a KnowledgeGraphRelationship.

        Args:
            source_node_id: Reference to the source KnowledgeGraphNode
            target_node_id: Reference to the target KnowledgeGraphNode
            relationship_type: Type of relationship (e.g., "works_at", "located_in")
            description: Description of the relationship
            id: Unique identifier for the relationship (generated if not provided)
            created_at: Timestamp when the relationship was created
        """
        if source_node_id == target_node_id:
            raise ValueError("A relationship cannot have the same source and target node")

        self.id = id or str(uuid.uuid4())
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.relationship_type = relationship_type
        self.description = description
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the KnowledgeGraphRelationship to a dictionary.

        Returns:
            Dictionary representation of the KnowledgeGraphRelationship
        """
        return {
            "id": self.id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'KnowledgeGraphRelationship':
        """
        Create a KnowledgeGraphRelationship from a dictionary.

        Args:
            data: Dictionary representation of the KnowledgeGraphRelationship

        Returns:
            KnowledgeGraphRelationship instance
        """
        return cls(
            id=data["id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            relationship_type=data["relationship_type"],
            description=data["description"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    def __str__(self) -> str:
        """String representation of the KnowledgeGraphRelationship."""
        return f"KnowledgeGraphRelationship(id={self.id}, type={self.relationship_type})"

    def __repr__(self) -> str:
        """Detailed string representation of the KnowledgeGraphRelationship."""
        return f"KnowledgeGraphRelationship(id={self.id}, source={self.source_node_id}, target={self.target_node_id}, type={self.relationship_type})"