"""LangGraph state definitions."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages

from .models import AccountInfo, EmployeeProfile, IdentityDocument, RoleBriefing
from .checklist import Checklist


class OnboardingState(MessagesState):
    """Conversation state for onboarding workflow."""

    identity: IdentityDocument | None
    profile: EmployeeProfile | None
    accounts: AccountInfo | None
    role_briefing: RoleBriefing | None
    followups: list[str]
    checklist: Checklist
    messages: Annotated[list, add_messages]
