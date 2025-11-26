"""Structured data models for onboarding."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EmployeeProfile(BaseModel):
    """Full employee profile captured during onboarding."""

    full_name: str = Field(..., description="Employee full legal name")
    id_number: str = Field(..., description="Government ID number extracted from ID photo")
    university: str = Field(..., description="Graduated university name")
    degree: Literal["本科", "硕士", "博士", "专科"] = Field(..., description="Highest degree")
    role: Literal["行政", "IT"] = Field(..., description="Target department role")
    position: str = Field(..., description="Specific job title within the role")


class IdentityDocument(BaseModel):
    """Metadata for uploaded identity documents."""

    image_path: str
    extracted_name: str
    extracted_id_number: str
    is_valid: bool
    feedback: str


class AccountInfo(BaseModel):
    """Account provisioning response info."""

    email_account: str | None = None
    git_account: str | None = None
    instructions: str


class RoleBriefing(BaseModel):
    """Role briefing content returned to the employee."""

    position: str
    summary: str
    responsibilities: list[str]
    probation_goals: list[str]
