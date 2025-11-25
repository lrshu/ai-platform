from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class Chunk:
    content: str
    metadata: dict | None = None


@dataclass
class VectorRecord:
    content: str
    embedding: Sequence[float]
    metadata: dict | None = None


@dataclass
class GraphEdge:
    source: str
    relation: str
    target: str
    weight: float = 1.0


@dataclass
class RetrievalResult:
    content: str
    score: float
    metadata: dict | None = None


@dataclass
class GenerationResult:
    answer: str
    citations: List[RetrievalResult]
