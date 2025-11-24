"""
KnowledgeGraphNode model for the RAG backend system.
"""

from typing import Optional
from datetime import datetime
import uuid


class KnowledgeGraphNode:
    """Represents an entity extracted from document content."""

    def __init__(
        self,
        chunk_id: str,
        entity_type: str,
        name: str,
        description: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a KnowledgeGraphNode.

        Args:
            chunk_id: Reference to the DocumentChunk
            entity_type: Type of entity (e.g., person, place, organization)
            name: Name of the entity
            description: Description of the entity
            id: Unique identifier for the node (generated if not provided)
            created_at: Timestamp when the node was created
        """
        self.id = id or str(uuid.uuid4())
        self.chunk_id = chunk_id
        self.entity_type = entity_type
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the KnowledgeGraphNode to a dictionary.

        Returns:
            Dictionary representation of the KnowledgeGraphNode
        """
        return {
            "id": self.id,
            "chunk_id": self.chunk_id,
            "entity_type": self.entity_type,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'KnowledgeGraphNode':
        """
        Create a KnowledgeGraphNode from a dictionary.

        Args:
            data: Dictionary representation of the KnowledgeGraphNode

        Returns:
            KnowledgeGraphNode instance
        """
        return cls(
            id=data["id"],
            chunk_id=data["chunk_id"],
            entity_type=data["entity_type"],
            name=data["name"],
            description=data["description"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    def __str__(self) -> str:
        """String representation of the KnowledgeGraphNode."""
        return f"KnowledgeGraphNode(id={self.id}, name={self.name}, type={self.entity_type})"

    def __repr__(self) -> str:
        """Detailed string representation of the KnowledgeGraphNode."""
        return f"KnowledgeGraphNode(id={self.id}, chunk_id={self.chunk_id}, name={self.name}, type={self.entity_type})"