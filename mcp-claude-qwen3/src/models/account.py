"""
Account model for the MCP Account Provisioning Server.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Account(BaseModel):
    """
    Represents a provisioned account.
    """
    username: str
    password: str
    account_type: str  # "email" or "git"
    created_at: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.now()


class ProvisioningRequest(BaseModel):
    """
    Represents a request to provision an account.
    """
    name: str
    id_number: str


class BatchProvisioningRequestItem(BaseModel):
    """
    Represents an item in a batch provisioning request.
    """
    name: str
    id_number: str
    account_types: list[str]


class ProvisioningResponse(BaseModel):
    """
    Response model for account provisioning.
    """
    username: str
    password: str


class BatchProvisioningRequest(BaseModel):
    """
    Request model for batch account provisioning.
    """
    requests: list[BatchProvisioningRequestItem]


class BatchProvisioningResult(BaseModel):
    """
    Result model for batch provisioning.
    """
    name: str
    id_number: str
    accounts: list[ProvisioningResponse] = []
    error: str = None


class BatchProvisioningResponse(BaseModel):
    """
    Response model for batch account provisioning.
    """
    results: list[BatchProvisioningResult]


class ErrorResponse(BaseModel):
    """
    Error response model.
    """
    error: str