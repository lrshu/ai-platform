"""Conversation model for the RAG backend system."""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Conversation:
    """Represents a conversation session between a user and the system."""

    id: str
    user_id: str
    document_name: str
    created_at: datetime
    updated_at: datetime
    title: Optional[str] = None
    is_active: bool = True