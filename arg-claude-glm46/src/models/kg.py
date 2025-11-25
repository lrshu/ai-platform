"""Entity and Relationship models for knowledge graph extraction."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Entity:
    """Represents a named entity extracted from document content."""

    id: str
    name: str
    type: str  # person, organization, location, etc.
    description: Optional[str] = None


@dataclass
class EntityMention:
    """Represents a specific mention of an entity within a chunk."""

    id: str
    entity_id: str
    chunk_id: str
    position_start: int
    position_end: int
    confidence: float


@dataclass
class Relationship:
    """Represents a relationship between two entities extracted from document content."""

    id: str
    source_entity_id: str
    target_entity_id: str
    type: str  # works_for, located_in, etc.
    description: str
    confidence: float