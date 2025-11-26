"""
Onboarding Checklist model for tracking employee onboarding progress.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class OnboardingChecklist(BaseModel):
    """Onboarding Checklist model tracking employee progress."""

    __tablename__ = "onboarding_checklists"

    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    identity_verified = Column(Boolean, default=False)
    information_collected = Column(Boolean, default=False)
    responsibilities_shown = Column(Boolean, default=False)
    permissions_granted = Column(Boolean, default=False)
    post_tasks_reminded = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)

    # Relationships
    employee = relationship("Employee", back_populates="onboarding_checklist")

    def __repr__(self):
        return f"<OnboardingChecklist(id='{self.id}', employee_id='{self.employee_id}')>"

    def is_complete(self):
        """Check if all onboarding steps are complete."""
        return (self.identity_verified and
                self.information_collected and
                self.responsibilities_shown and
                self.permissions_granted and
                self.post_tasks_reminded and
                self.completed)