from __future__ import annotations

import hashlib
import logging
from typing import Iterable, List

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    return text or "(empty)"


def _hash_bytes(text: str) -> bytes:
    return hashlib.sha256(text.encode("utf-8")).digest()


def deterministic_embedding(text: str, *, dimension: int = 256) -> List[float]:
    payload = _normalize_text(text)
    digest = _hash_bytes(payload)
    return [((digest[i % len(digest)] / 255.0) * 2) - 1 for i in range(dimension)]


def embed_texts_locally(texts: Iterable[str], *, dimension: int = 256) -> List[List[float]]:
    return [deterministic_embedding(text, dimension=dimension) for text in texts]


def summarize_locally(question: str, context: str) -> str:
    prefix = context.strip().splitlines()[0][:200] if context.strip() else "No context provided."
    return f"Context clue: {prefix}\nAnswer (best effort): {question}"
