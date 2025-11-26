"""Configuration helpers for agent runtime."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    qwen_api_base: str
    qwen_api_key: str
    mcp_server: str
    langsmith_api_key: str | None = None
    langsmith_project: str | None = None
    default_llm: Literal["qwen3-max", "qwen3-vl-max"] = "qwen3-max"


ENV_PATH = Path(".env")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from `.env` once per process."""

    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)

    from os import getenv

    qwen_api_base = getenv("QWEN_API_BASE")
    qwen_api_key = getenv("QWEN_API_KEY")
    mcp_server = getenv("MCP_SERVER", "http://127.0.0.1:9012/mcp")
    langsmith_api_key = getenv("LANGSMITH_API_KEY")
    langsmith_project = getenv("LANGSMITH_PROJECT", "default")
    default_llm = getenv("DEFAULT_LLM", "qwen3-max")

    missing = [
        name
        for name, value in (
            ("QWEN_API_BASE", qwen_api_base),
            ("QWEN_API_KEY", qwen_api_key),
        )
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required environment variables: {joined}. Please define them in .env."
        )

    return Settings(
        qwen_api_base=qwen_api_base,
        qwen_api_key=qwen_api_key,
        mcp_server=mcp_server,
        langsmith_api_key=langsmith_api_key,
        langsmith_project=langsmith_project,
        default_llm=default_llm,  # type: ignore[arg-type]
    )
