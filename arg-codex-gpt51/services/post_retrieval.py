from __future__ import annotations

from typing import Iterable, List

from rapidfuzz import fuzz

from services.models import RetrievalResult


def rerank(results: Iterable[RetrievalResult]) -> List[RetrievalResult]:
    ranked = sorted(results, key=lambda r: r.score, reverse=True)
    return ranked
