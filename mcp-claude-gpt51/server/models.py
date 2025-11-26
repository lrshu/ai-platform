from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AccountType(str, Enum):
    EMAIL = "email"
    GIT = "git"


class IdentitySubmission(BaseModel):
    name: str = Field(min_length=1)
    national_id: str = Field(pattern=r"^[0-9]{17}[0-9Xx]$")
    request_context: Optional[str] = None
    request_type: AccountType


class ProvisioningResponse(BaseModel):
    account_type: AccountType
    handle: str
    password: str
    timestamp: datetime
    audit_id: str
    status_code: str
    message: str


class AuditOutcome(str, Enum):
    SUCCESS = "success"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"


class AuditRecord(BaseModel):
    audit_id: str
    masked_id: str
    request_type: AccountType
    outcome: AuditOutcome
    created_at: datetime
    detail: Optional[str] = None
