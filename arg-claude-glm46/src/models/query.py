"""Query model for the RAG backend system."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Query:
    """Represents a user query processed by the system."""

    id: str
    content: str
    created_at: datetime
    expanded_content: Optional[str] = None
    user_id: Optional[str] = None