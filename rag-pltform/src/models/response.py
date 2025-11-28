"""
Response model for the RAG system.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseModel


class Response(BaseModel):
    """Generated answer to a user query."""

    def __init__(
        self,
        query_id: str,
        content: str,
        model_used: str = "qwen3-max",
        id: Optional[str] = None,
        tokens_used: int = 0
    ):
        """Initialize response.

        Args:
            query_id: Reference to originating query
            content: Generated response content
            model_used: Name of LLM used
            id: Optional unique identifier
            tokens_used: Number of tokens consumed
        """
        super().__init__(id)
        self.query_id = query_id
        self.content = content
        self.model_used = model_used
        self.tokens_used = tokens_used
        self.generated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary representation.

        Returns:
            Dictionary representation of the response
        """
        return {
            "id": self.id,
            "query_id": self.query_id,
            "content": self.content,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "generated_at": self.generated_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """Create response from dictionary representation.

        Args:
            data: Dictionary representation of the response

        Returns:
            Response instance
        """
        response = cls(
            query_id=data["query_id"],
            content=data["content"],
            model_used=data.get("model_used", "qwen3-max"),
            id=data["id"],
            tokens_used=data.get("tokens_used", 0)
        )

        response.generated_at = datetime.fromisoformat(data["generated_at"])
        response.created_at = datetime.fromisoformat(data["created_at"])
        response.updated_at = datetime.fromisoformat(data["updated_at"])

        return response

    def update_tokens(self, tokens_used: int) -> None:
        """Update the number of tokens used.

        Args:
            tokens_used: Number of tokens used
        """
        self.tokens_used = tokens_used
        self.update_timestamp()

    def __str__(self) -> str:
        """String representation."""
        return f"Response(query_id='{self.query_id}', content_length={len(self.content)}, model='{self.model_used}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Response(id='{self.id}', query_id='{self.query_id}', content='{content_preview}', model='{self.model_used}', tokens={self.tokens_used})"