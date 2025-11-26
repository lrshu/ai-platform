"""
Employee model for the onboarding system.
"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from . import OnboardingStatus

class Employee(BaseModel):
    """Employee model representing a new hire."""

    __tablename__ = "employees"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    id_number = Column(String)
    school = Column(String)
    education_level = Column(String)  # Will store EducationLevel enum values
    position = Column(String)
    onboarding_status = Column(String, default=OnboardingStatus.NOT_STARTED.value)  # Will store OnboardingStatus enum values

    # Relationships
    id_photo = relationship("IDPhoto", back_populates="employee", uselist=False)
    onboarding_checklist = relationship("OnboardingChecklist", back_populates="employee", uselist=False)
    account_credentials = relationship("AccountCredentials", back_populates="employee")

    def __repr__(self):
        return f"<Employee(id='{self.id}', name='{self.first_name} {self.last_name}')>"