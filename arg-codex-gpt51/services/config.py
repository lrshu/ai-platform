from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    qwen_api_base: str
    qwen_api_key: str
    database_url: str
    database_user: str | None = None
    database_password: str | None = None


_cached_settings: Optional[Settings] = None


def get_settings(env_path: str | Path | None = None) -> Settings:
    global _cached_settings
    if _cached_settings is not None:
        return _cached_settings

    load_dotenv(env_path)

    from os import getenv

    _cached_settings = Settings(
        qwen_api_base=getenv("QWEN_API_BASE", ""),
        qwen_api_key=getenv("QWEN_API_KEY", ""),
        database_url=getenv("DATABASE_URL", "bolt://127.0.0.1:7687"),
        database_user=getenv("DATABASE_USER") or None,
        database_password=getenv("DATABASE_PASSWORD") or None,
    )
    return _cached_settings
