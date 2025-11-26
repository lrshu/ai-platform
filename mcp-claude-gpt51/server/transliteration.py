from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from pypinyin import Style, lazy_pinyin

from server.config import get_settings


class TransliterationError(Exception):
    """Raised when a name cannot be transliterated."""


def _load_overrides(path: str) -> Dict[str, str]:
    overrides_path = Path(path)
    if not overrides_path.exists():
        raise TransliterationError(f"Override file not found: {path}")
    try:
        data = json.loads(overrides_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TransliterationError("Invalid override file format") from exc
    if not isinstance(data, dict):
        raise TransliterationError("Override file must contain a JSON object")
    return {str(key): str(value) for key, value in data.items()}


def _apply_overrides(name: str, overrides: Dict[str, str]) -> List[str]:
    return [overrides.get(char, char) for char in name]


def transliterate_name(name: str) -> str:
    settings = get_settings()
    overrides: Dict[str, str] = {}
    if settings.transliteration_overrides:
        overrides = _load_overrides(settings.transliteration_overrides)
    normalized_chars = _apply_overrides(name.strip(), overrides)
    if not normalized_chars:
        raise TransliterationError("Name is empty after normalization")
    try:
        pinyin_segments = lazy_pinyin(
            normalized_chars,
            style=Style.NORMAL,
            strict=True,
        )
    except ValueError as exc:
        raise TransliterationError("Unsupported character for transliteration") from exc
    handle = "".join(pinyin_segments).lower()
    if not handle.isascii():
        raise TransliterationError("Transliteration must produce ASCII")
    return handle
