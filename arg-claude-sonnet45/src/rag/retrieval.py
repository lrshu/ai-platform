"""Document retrieval: vector, keyword, and graph search."""

import time
from uuid import UUID

from dashscope import TextEmbedding

from src.config.logging import get_logger
from src.config.settings import settings
from src.models.query import QueryOptions, RetrievalResult, RetrievedChunk
from src.storage.graph_store import GraphStore

logger = get_logger(__name__)


def get_query_embedding(question: str) -> list[float]:
    """Generate embedding vector for user query.

    Args:
        question: Query text

    Returns:
        1024-dimensional embedding vector

    Raises:
        RuntimeError: If embedding API fails
    """
    try:
        logger.info(
            f"Generating query embedding",
            extra={"stage": "get_query_embedding", "query": question[:50]},
        )

        response = TextEmbedding.call(
            model="text-embedding-v4",
            input=[question],
            api_key=settings.qwen_api_key,
        )

        if response.status_code == 200:
            embedding = response.output["embeddings"][0]["embedding"]
            logger.info(
                f"Generated query embedding",
                extra={"stage": "get_query_embedding", "dimension": len(embedding)},
            )
            return embedding
        else:
            raise RuntimeError(f"Embedding API error: {response.message}")

    except Exception as e:
        logger.error(
            f"Failed to generate query embedding: {e}",
            extra={"stage": "get_query_embedding"},
            exc_info=True,
        )
        raise RuntimeError(f"Failed to generate query embedding: {e}") from e


def vector_search(name: str, query_embedding: list[float], top_k: int = 20) -> list[dict]:
    """Perform vector similarity search in Memgraph.

    Args:
        name: Document namespace to search
        query_embedding: Query embedding vector
        top_k: Number of results to return

    Returns:
        Retrieved chunks with structure:
        {
            "chunk_id": UUID,
            "text": str,
            "similarity_score": float,
            "source": "vector",
            "metadata": dict,
        }

    Raises:
        ValueError: If namespace does not exist
        RuntimeError: If Memgraph query fails
    """
    try:
        logger.info(
            f"Performing vector search in Memgraph",
            extra={"stage": "vector_search", "namespace": name, "top_k": top_k},
        )
        start_time = time.time()

        graph_store = GraphStore()

        # Check if namespace exists
        if not graph_store.namespace_exists(name):
            raise ValueError(f"No documents found for namespace '{name}'")

        # Query Memgraph for similar vectors
        results = graph_store.vector_similarity_search(
            namespace=name,
            query_embedding=query_embedding,
            limit=top_k,
            similarity_threshold=0.0,
        )

        # Format results
        chunks = []
        for result in results:
            chunk = {
                "chunk_id": UUID(result["chunk_id"]),
                "text": result["text"],
                "similarity_score": result["similarity_score"],
                "source": "vector",
                "metadata": result["metadata"],
            }
            chunks.append(chunk)

        graph_store.close()

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Vector search found {len(chunks)} chunks",
            extra={"stage": "vector_search", "count": len(chunks), "duration_ms": duration_ms},
        )

        return chunks

    except Exception as e:
        logger.error(
            f"Vector search failed: {e}",
            extra={"stage": "vector_search", "namespace": name},
            exc_info=True,
        )
        raise


def keyword_search(name: str, question: str, top_k: int = 20) -> list[dict]:
    """Perform keyword/BM25-style search in Memgraph.

    Args:
        name: Document namespace
        question: Query text
        top_k: Number of results

    Returns:
        Retrieved chunks (same structure as vector_search)

    Raises:
        ValueError: If namespace does not exist
        RuntimeError: If Memgraph query fails
    """
    try:
        logger.info(
            f"Performing keyword search in Memgraph",
            extra={"stage": "keyword_search", "namespace": name, "top_k": top_k},
        )
        start_time = time.time()

        graph_store = GraphStore()

        # Check if namespace exists
        if not graph_store.namespace_exists(name):
            raise ValueError(f"No documents found for namespace '{name}'")

        # Perform keyword search (full text search with text stored in Memgraph)
        results = graph_store.keyword_search(name, question, limit=top_k)
        graph_store.close()

        # Format results
        chunks = []
        for data in results:
            chunk = {
                "chunk_id": UUID(data["chunk_id"]),
                "text": data["text"],
                "similarity_score": data.get("relevance_score", 0.5),
                "source": "keyword",
                "metadata": data["metadata"],
            }
            chunks.append(chunk)

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Keyword search found {len(chunks)} chunks",
            extra={"stage": "keyword_search", "count": len(chunks), "duration_ms": duration_ms},
        )

        return chunks

    except Exception as e:
        logger.warning(
            f"Keyword search failed: {e}",
            extra={"stage": "keyword_search", "namespace": name},
        )
        return []  # Graceful degradation


def graph_search(name: str, question: str, top_k: int = 10) -> list[dict]:
    """Perform graph traversal search via entity relationships (placeholder).

    Args:
        name: Document namespace
        question: Query text
        top_k: Number of results

    Returns:
        Retrieved chunks (same structure as vector_search)

    Note:
        This is optional for MVP. Returns empty list as entity extraction
        is not yet implemented.
    """
    logger.info(
        f"Graph search not implemented (MVP)",
        extra={"stage": "graph_search"},
    )
    return []  # Optional feature for future


def hybrid_search(
    name: str,
    question: str,
    query_embedding: list[float],
    options: QueryOptions,
) -> RetrievalResult:
    """Execute hybrid retrieval combining vector, keyword, and graph search.

    Args:
        name: Document namespace
        question: Original or preprocessed query
        query_embedding: Query embedding vector
        options: Search configuration

    Returns:
        RetrievalResult with merged and deduplicated chunks

    Raises:
        ValueError: If namespace does not exist or no search methods enabled
    """
    try:
        logger.info(
            f"Starting hybrid search",
            extra={"stage": "hybrid_search", "namespace": name},
        )
        start_time = time.time()

        all_chunks = []
        methods_used = []

        # Vector search
        if options.enable_vector_search:
            try:
                vector_chunks = vector_search(name, query_embedding, top_k=20)
                all_chunks.extend(vector_chunks)
                methods_used.append("vector")
                logger.info(
                    f"Vector search contributed {len(vector_chunks)} chunks",
                    extra={"stage": "hybrid_search"},
                )
            except Exception as e:
                logger.warning(
                    f"Vector search failed in hybrid search: {e}",
                    extra={"stage": "hybrid_search"},
                )

        # Keyword search
        if options.enable_keyword_search:
            try:
                keyword_chunks = keyword_search(name, question, top_k=20)
                # Filter out chunks without text (placeholder implementation)
                keyword_chunks = [c for c in keyword_chunks if c["text"]]
                all_chunks.extend(keyword_chunks)
                if keyword_chunks:
                    methods_used.append("keyword")
                logger.info(
                    f"Keyword search contributed {len(keyword_chunks)} chunks",
                    extra={"stage": "hybrid_search"},
                )
            except Exception as e:
                logger.warning(
                    f"Keyword search failed in hybrid search: {e}",
                    extra={"stage": "hybrid_search"},
                )

        # Graph search (optional)
        if options.enable_graph_search:
            try:
                graph_chunks = graph_search(name, question, top_k=10)
                all_chunks.extend(graph_chunks)
                if graph_chunks:
                    methods_used.append("graph")
                logger.info(
                    f"Graph search contributed {len(graph_chunks)} chunks",
                    extra={"stage": "hybrid_search"},
                )
            except Exception as e:
                logger.warning(
                    f"Graph search failed in hybrid search: {e}",
                    extra={"stage": "hybrid_search"},
                )

        if not methods_used:
            raise ValueError("No search methods enabled or all failed")

        # Deduplicate by chunk_id
        seen_ids = set()
        unique_chunks = []
        for chunk in all_chunks:
            if chunk["chunk_id"] not in seen_ids:
                seen_ids.add(chunk["chunk_id"])
                unique_chunks.append(chunk)

        # Sort by similarity score (descending)
        unique_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)

        # Take top 40 (or all if fewer)
        unique_chunks = unique_chunks[:40]

        # Convert to RetrievedChunk models
        retrieved_chunks = [
            RetrievedChunk(
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                similarity_score=chunk["similarity_score"],
                source=chunk["source"],
                metadata=chunk["metadata"],
            )
            for chunk in unique_chunks
        ]

        duration_ms = int((time.time() - start_time) * 1000)

        result = RetrievalResult(
            query_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            chunks=retrieved_chunks,
            retrieval_methods_used=methods_used,
            retrieval_duration_ms=duration_ms,
        )

        logger.info(
            f"Hybrid search completed: {len(retrieved_chunks)} unique chunks from {methods_used}",
            extra={
                "stage": "hybrid_search",
                "count": len(retrieved_chunks),
                "methods": methods_used,
                "duration_ms": duration_ms,
            },
        )

        return result

    except Exception as e:
        logger.error(
            f"Hybrid search failed: {e}",
            extra={"stage": "hybrid_search", "namespace": name},
            exc_info=True,
        )
        raise
