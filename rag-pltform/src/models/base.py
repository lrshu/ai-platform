"""
Base model classes for the RAG system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


class BaseModel(ABC):
    """Base class for all models."""

    def __init__(self, id: Optional[str] = None):
        """Initialize model.

        Args:
            id: Optional unique identifier. If not provided, a UUID will be generated.
        """
        self.id = id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation.

        Returns:
            Dictionary representation of the model
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary representation.

        Args:
            data: Dictionary representation of the model

        Returns:
            Model instance
        """
        pass

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, BaseModel):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(id={self.id})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(id={self.id}, created_at={self.created_at})"