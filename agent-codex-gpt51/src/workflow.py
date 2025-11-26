"""LangGraph workflow describing the onboarding steps."""

from __future__ import annotations

from typing import Callable

from langgraph.graph import END, START, StateGraph

from .checklist import ChecklistItem
from .services import (
    build_followup_tasks,
    build_profile,
    describe_role,
    open_access,
    verify_identity,
)
from .state import OnboardingState


def _identity_node(state: OnboardingState) -> OnboardingState:
    payload = {
        "image_path": state.identity.image_path if state.identity else "",
        "full_name": state.profile.full_name if state.profile else "",
        "id_number": state.profile.id_number if state.profile else "",
    }
    state.identity = verify_identity(payload)
    state.checklist.mark_done(ChecklistItem.ID_VERIFICATION)
    return state


def _profile_node(state: OnboardingState) -> OnboardingState:
    data = state.profile.model_dump() if state.profile else {}
    state.profile = build_profile(data, state.identity)
    state.checklist.mark_done(ChecklistItem.INFO_COMPLETION)
    return state


def _role_node(state: OnboardingState) -> OnboardingState:
    state.role_briefing = describe_role(state.profile)
    state.checklist.mark_done(ChecklistItem.ROLE_BRIEFING)
    return state


def _access_node(state: OnboardingState) -> OnboardingState:
    state.accounts = open_access(state.profile)
    state.checklist.mark_done(ChecklistItem.ACCESS_SETUP)
    return state


def _followup_node(state: OnboardingState) -> OnboardingState:
    state.followups = build_followup_tasks(state.profile)
    state.checklist.mark_done(ChecklistItem.FINAL_GUIDANCE)
    return state


def build_workflow() -> StateGraph:
    graph = StateGraph(OnboardingState)
    graph.add_node("identity", _identity_node)
    graph.add_node("profile", _profile_node)
    graph.add_node("role", _role_node)
    graph.add_node("access", _access_node)
    graph.add_node("followup", _followup_node)

    graph.add_edge(START, "identity")
    graph.add_edge("identity", "profile")
    graph.add_edge("profile", "role")
    graph.add_edge("role", "access")
    graph.add_edge("access", "followup")
    graph.add_edge("followup", END)
    return graph
