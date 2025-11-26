"""LLM factory helpers."""

from __future__ import annotations

from typing import Literal

from langchain.chat_models.base import init_chat_model
from langchain_core.language_models import BaseChatModel

from .config import get_settings


MODEL_MAP = {
    "qwen3-max": ("openai", "gpt-4o-mini"),
    "qwen3-vl-max": ("openai", "gpt-4o-mini"),
}


def get_model(name: Literal["qwen3-max", "qwen3-vl-max"]) -> BaseChatModel:
    provider, model_name = MODEL_MAP[name]
    settings = get_settings()
    return init_chat_model(
        model=model_name,
        model_provider=provider,
        api_key=settings.qwen_api_key,
        base_url=settings.qwen_api_base,
    )
