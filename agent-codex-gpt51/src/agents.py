"""Agent constructors."""

from __future__ import annotations

from typing import Sequence

from langchain.tools import BaseTool

from deepagents import create_deep_agent

from .prompts import (
    access_prompt,
    base_system_prompt,
    followup_prompt,
    identity_prompt,
    info_collection_prompt,
    role_brief_prompt,
)
from .llm import get_model


def create_onboarding_agent(tools: Sequence[BaseTool] | None = None):
    """Main orchestrator agent."""

    return create_deep_agent(
        model=get_model("qwen3-max"),
        tools=tools,
        system_prompt=base_system_prompt(),
    )


def create_identity_agent(tools: Sequence[BaseTool] | None = None):
    return create_deep_agent(
        model=get_model("qwen3-vl-max"),
        tools=tools,
        system_prompt=identity_prompt(),
    )


def create_info_agent(tools: Sequence[BaseTool] | None = None):
    return create_deep_agent(
        model=get_model("qwen3-max"),
        tools=tools,
        system_prompt=info_collection_prompt(),
    )


def create_role_brief_agent(tools: Sequence[BaseTool] | None = None):
    return create_deep_agent(
        model=get_model("qwen3-max"),
        tools=tools,
        system_prompt=role_brief_prompt(),
    )


def create_access_agent(tools: Sequence[BaseTool] | None = None):
    return create_deep_agent(
        model=get_model("qwen3-max"),
        tools=tools,
        system_prompt=access_prompt(),
    )


def create_followup_agent(tools: Sequence[BaseTool] | None = None):
    return create_deep_agent(
        model=get_model("qwen3-max"),
        tools=tools,
        system_prompt=followup_prompt(),
    )
