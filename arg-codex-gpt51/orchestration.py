from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import indexing
import post_retrieval
import pre_retrieval
import retrieval
from generation import run_generation
from services.graph import GraphStore
from services.models import GenerationResult, RetrievalResult


@dataclass
class SearchOptions:
    top_k: int = 5
    expand_query: bool = True
    rerank: bool = True
    use_vector: bool = True
    use_keyword: bool = False
    use_graph: bool = True


class Orchestrator:
    def __init__(self, graph_store: GraphStore | None = None):
        self.graph_store = graph_store or GraphStore()

    def index(self, name: str, file_path: str) -> str:
        result = indexing.run_indexing(name, file_path, self.graph_store)
        return result.name

    def search(self, name: str, question: str, options: SearchOptions | None = None) -> List[RetrievalResult]:
        opts = options or SearchOptions()
        processed_question = pre_retrieval.preprocess_question(question, use_expansion=opts.expand_query)
        retrieval_results = retrieval.run_retrieval(
            name,
            question,
            processed_question=processed_question,
            options=retrieval.RetrievalOptions(
                top_k=opts.top_k,
                use_vector=opts.use_vector,
                use_keyword=opts.use_keyword,
                use_graph=opts.use_graph,
            ),
        )
        if opts.rerank:
            retrieval_results = post_retrieval.rerank(retrieval_results)
        return retrieval_results

    def chat(self, name: str, question: str, options: SearchOptions | None = None) -> GenerationResult:
        results = self.search(name, question, options)
        return run_generation(question, results)

    def close(self):
        self.graph_store.close()


def index(name: str, file_path: str) -> str:
    orchestrator = Orchestrator()
    try:
        return orchestrator.index(name, file_path)
    finally:
        orchestrator.close()


def search(name: str, question: str, options: Optional[Dict[str, Any]] = None):
    orchestrator = Orchestrator()
    try:
        opts = SearchOptions(**options) if options else None
        return orchestrator.search(name, question, opts)
    finally:
        orchestrator.close()


def chat(name: str, question: str, options: Optional[Dict[str, Any]] = None):
    orchestrator = Orchestrator()
    try:
        opts = SearchOptions(**options) if options else None
        return orchestrator.chat(name, question, opts)
    finally:
        orchestrator.close()
