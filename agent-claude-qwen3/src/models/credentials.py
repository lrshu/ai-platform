"""
Account Credentials model for storing provisioned account information.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
from . import AccountType

class AccountCredentials(BaseModel):
    """Account Credentials model for storing provisioned account information."""

    __tablename__ = "account_credentials"

    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    account_type = Column(String)  # Will store AccountType enum values
    username = Column(String)
    provisioned_at = Column(DateTime, default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="account_credentials")

    def __repr__(self):
        return f"<AccountCredentials(id='{self.id}', employee_id='{self.employee_id}', type='{self.account_type}')>"