from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from src.clients import embed_documents_safe, embed_query_safe
from src.graph import GraphStore
from src.models import RetrievalResult


@dataclass
class RetrievalOptions:
    top_k: int = 5
    use_vector: bool = True
    use_keyword: bool = False
    use_graph: bool = True


def build_query_embedding(original_question: str, processed_question: str | None = None) -> List[float]:
    return embed_query_safe(processed_question or original_question)


def run_retrieval(
    name: str,
    original_question: str,
    *,
    processed_question: str | None = None,
    options: RetrievalOptions | None = None,
) -> List[RetrievalResult]:
    opts = options or RetrievalOptions()
    graph_store = GraphStore()
    try:
        query_embedding = build_query_embedding(original_question, processed_question)
        candidates: list[RetrievalResult] = []
        if opts.use_vector:
            candidates.extend(graph_store.vector_search(name, query_embedding, opts.top_k))
        if opts.use_keyword:
            candidates.extend(graph_store.keyword_search(name, original_question, opts.top_k))
        if opts.use_graph:
            candidates.extend(graph_store.graph_search(name, original_question, opts.top_k))
        if not candidates:
            return []
        # Sort by score descending and deduplicate by chunk id to keep best scoring hits.
        seen = set()
        ordered: list[RetrievalResult] = []
        for item in sorted(candidates, key=lambda r: r.score, reverse=True):
            cid = item.metadata.get("cid") if item.metadata else None
            if cid in seen:
                continue
            if cid is not None:
                seen.add(cid)
            ordered.append(item)
            if len(ordered) >= opts.top_k:
                break
        return ordered
    finally:
        graph_store.close()
