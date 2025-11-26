"""
ID Photo model for employee identity verification.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
from . import VerificationStatus

class IDPhoto(BaseModel):
    """ID Photo model for storing employee identity verification data."""

    __tablename__ = "id_photos"

    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    file_path = Column(String)
    verification_status = Column(String, default=VerificationStatus.PENDING.value)  # Will store VerificationStatus enum values
    verification_notes = Column(Text)
    uploaded_at = Column(DateTime, default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="id_photo")

    def __repr__(self):
        return f"<IDPhoto(id='{self.id}', employee_id='{self.employee_id}', status='{self.verification_status}')>"