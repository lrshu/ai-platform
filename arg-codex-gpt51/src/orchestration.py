from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.generation import run_generation
from src.indexing import IndexingResult, run_indexing
from src.post_retrieval import rerank
from src.pre_retrieval import preprocess_question
from src.retrieval import RetrievalOptions, run_retrieval
from src.models import GenerationResult, RetrievalResult


@dataclass
class SearchOptions:
    top_k: int = 5
    expand_query: bool = True
    rerank: bool = True
    use_vector: bool = True
    use_keyword: bool = False
    use_graph: bool = True


def index(name: str, file_path: str) -> IndexingResult:
    return run_indexing(name, file_path)


def search(name: str, question: str, options: Optional[SearchOptions] = None) -> List[RetrievalResult]:
    opts = options or SearchOptions()
    processed_question = preprocess_question(question, use_expansion=opts.expand_query)
    retrieval_results = run_retrieval(
        name,
        question,
        processed_question=processed_question,
        options=RetrievalOptions(
            top_k=opts.top_k,
            use_vector=opts.use_vector,
            use_keyword=opts.use_keyword,
            use_graph=opts.use_graph,
        ),
    )
    if opts.rerank:
        retrieval_results = rerank(retrieval_results)
    return retrieval_results


def chat(name: str, question: str, options: Optional[SearchOptions] = None) -> GenerationResult:
    results = search(name, question, options)
    return run_generation(question, results)
