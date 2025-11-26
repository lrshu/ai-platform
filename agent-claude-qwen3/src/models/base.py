"""
Base model class for the onboarding system.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
import uuid
from ..utils.database import Base

class BaseModel(Base):
    """Base model class with common fields."""

    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}')>"