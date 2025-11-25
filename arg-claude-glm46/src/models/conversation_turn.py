"""ConversationTurn model for the RAG backend system."""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation (user message and system response)."""

    id: str
    conversation_id: str
    turn_number: int
    user_message: str
    system_response: str
    created_at: datetime
    response_time_ms: Optional[int] = None
    user_message_embedding: Optional[List[float]] = None
    system_response_embedding: Optional[List[float]] = None