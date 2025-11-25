"""RAG pipeline orchestration - coordinates all stages."""

from pathlib import Path
from uuid import UUID

from src.config.logging import get_logger
from src.config.settings import settings
from src.models.query import GeneratedResponse, QueryOptions
from src.rag.indexing import chunk_text, embed_chunks, parse_pdf, store_document

logger = get_logger(__name__)


def index_document(
    name: str,
    file_path: str,
    options: dict[str, int] | None = None,
) -> UUID:
    """Orchestrate complete indexing pipeline.

    Pipeline: parse_pdf → chunk_text → embed_chunks → store_document

    Args:
        name: Document namespace
        file_path: Path to PDF file
        options: Optional overrides for chunk_size, overlap

    Returns:
        Document ID

    Raises:
        Any exception from pipeline stages
    """
    logger.info(
        f"Starting indexing pipeline for {file_path}",
        extra={"stage": "index_document", "namespace": name, "file": file_path},
    )

    # Parse PDF to markdown
    markdown = parse_pdf(file_path)

    # Chunk text
    chunk_size = options.get("chunk_size", settings.chunk_size) if options else settings.chunk_size
    chunk_overlap = (
        options.get("chunk_overlap", settings.chunk_overlap)
        if options
        else settings.chunk_overlap
    )
    chunks = chunk_text(markdown, chunk_size=chunk_size, overlap=chunk_overlap)

    # Embed chunks
    embeddings = embed_chunks(chunks)

    # Store document
    path = Path(file_path)
    metadata = {
        "filename": path.name,
        "file_path": str(path.absolute()),
        "file_size": path.stat().st_size,
    }

    document_id = store_document(name, embeddings, metadata)

    logger.info(
        f"Indexing pipeline completed",
        extra={
            "stage": "index_document",
            "document_id": str(document_id),
            "chunks": len(embeddings),
        },
    )

    return document_id


def search_documents(
    name: str,
    question: str,
    options: QueryOptions,
) -> list[dict]:
    """Orchestrate retrieval pipeline and return reranked chunks.

    Pipeline: preprocess_query → hybrid_search → rerank_chunks

    Args:
        name: Document namespace
        question: User query
        options: Search configuration

    Returns:
        Top-k reranked chunks

    Note:
        Reranking will be added in Phase 7 (User Story 5)
    """
    from src.rag.retrieval import get_query_embedding, hybrid_search

    logger.info(
        f"Starting search pipeline",
        extra={"stage": "search_documents", "namespace": name},
    )

    # Generate query embedding
    query_embedding = get_query_embedding(question)

    # Hybrid search
    retrieval_result = hybrid_search(name, question, query_embedding, options)

    # Take top-k chunks (reranking will be added in Phase 7)
    top_chunks = retrieval_result.chunks[: options.top_k]

    # Convert to dict format for CLI output
    results = [
        {
            "chunk_id": str(chunk.chunk_id),
            "text": chunk.text,
            "similarity_score": chunk.similarity_score,
            "source": chunk.source,
            "metadata": chunk.metadata,
        }
        for chunk in top_chunks
    ]

    logger.info(
        f"Search pipeline completed: {len(results)} results",
        extra={"stage": "search_documents", "count": len(results)},
    )

    return results


def chat_with_documents(
    name: str,
    question: str,
    options: QueryOptions,
) -> GeneratedResponse:
    """Orchestrate full RAG pipeline and return generated answer.

    Pipeline: search_documents → generate_answer

    Args:
        name: Document namespace
        question: User question
        options: Pipeline configuration

    Returns:
        Generated answer with citations
    """
    from src.rag.generation import generate_answer

    logger.info(
        f"Starting chat pipeline",
        extra={"stage": "chat_with_documents", "namespace": name},
    )

    # Search for relevant chunks
    chunks = search_documents(name, question, options)

    if not chunks:
        # No relevant context found
        logger.warning(
            f"No relevant chunks found for query",
            extra={"stage": "chat_with_documents"},
        )
        # Return empty response
        from src.models.query import GeneratedResponse
        from uuid import UUID

        return GeneratedResponse(
            query_id=UUID("00000000-0000-0000-0000-000000000000"),
            answer_text="I don't have enough information in the indexed documents to answer this question.",
            citations=[],
            confidence_score=0.0,
            generation_duration_ms=0,
        )

    # Generate answer from chunks
    response = generate_answer(question, chunks)

    logger.info(
        f"Chat pipeline completed",
        extra={"stage": "chat_with_documents", "citations": len(response.citations)},
    )

    return response
