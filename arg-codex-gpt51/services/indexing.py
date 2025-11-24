from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
from services.util import thread_pool_runner
import asyncio


from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from pypdf import PdfReader

from services.clients import embed_documents_safe, get_llm
from services.graph import GraphStore
from services.models import Chunk, GraphEdge, VectorRecord
from services.parsers import MarkdownParser

logger = logging.getLogger(__name__)


@dataclass
class IndexingResult:
    name: str
    chunk_count: int


def parse_pdf(file_path: str | Path) -> str:
    reader = PdfReader(str(file_path))
    texts = [page.extract_text() or "" for page in reader.pages]
    parser = MarkdownParser()
    markdown = parser.from_text("\n".join(texts))
    logger.debug("Extracted %d pages", len(texts))
    return markdown


def chunk_markdown(markdown: str, *, chunk_size: int = 800, chunk_overlap: int = 80) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(markdown)
    logger.debug("Chunked into %d segments", len(chunks))
    return chunks


def embed_chunks(chunks: Iterable[str]) -> List[VectorRecord]:
    texts = list(chunks)
    embeddings = embed_documents_safe(texts)
    return [VectorRecord(content=text, embedding=vector) for text, vector in zip(texts, embeddings)]


def extract_graph(chunks: List[str]) -> List[GraphEdge]:
    if not chunks:
        return []
    llm = get_llm()
    try:
        # Qwen via DashScope rejects OpenAI-style response_format payloads, so force
        # the transformer into the unstructured/json-repair path by disabling
        # tool/structured output usage.
        transformer = LLMGraphTransformer(llm=llm, strict_mode=False, ignore_tool_usage=True)
    except Exception as exc:
        logger.warning("Failed to initialize LLMGraphTransformer: %s", exc)
        return []
    documents = [Document(page_content=text, metadata={"id": f"chunk_{idx}"}) for idx, text in enumerate(chunks)]
    try:
        batched_documents = [[doc] for doc in documents]
        graph_docs_batches = asyncio.run(
            thread_pool_runner(
                transformer.convert_to_graph_documents,
                batched_documents,
                max_workers=20,
            )
        )
        graph_docs = []
        for batch in graph_docs_batches:
            if isinstance(batch, Exception):
                logger.warning("Graph extraction worker failed: %s", batch)
                continue
            graph_docs.extend(batch or [])
    except Exception as exc:
        logger.warning("Graph extraction failed via LLMGraphTransformer: %s", exc)
        return []
    edges: List[GraphEdge] = []
    for doc in graph_docs:
        for relationship in getattr(doc, "relationships", []) or []:
            edges.append(
                GraphEdge(
                    source=relationship.source.id,
                    relation=relationship.type,
                    target=relationship.target.id,
                    weight=relationship.properties.get("weight", 1.0) if relationship.properties else 1.0,
                )
            )
    logger.info("Created %d graph edges via LLMGraphTransformer", len(edges))
    return edges


def run_indexing(name: str, file_path: str, graph_store: GraphStore | None = None) -> IndexingResult:
    graph_store = graph_store or GraphStore()
    markdown = parse_pdf(file_path)
    chunk_texts = chunk_markdown(markdown)
    vector_records = embed_chunks(chunk_texts)
    edges = extract_graph(chunk_texts)
    graph_store.store_vectors(name, vector_records)
    if edges:
        graph_store.store_graph(name, edges)
    logger.info("Indexed collection %s with %d chunks", name, len(chunk_texts))
    return IndexingResult(name=name, chunk_count=len(chunk_texts))
