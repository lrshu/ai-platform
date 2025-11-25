"""Answer generation from retrieved context using LLM."""

import re
import time
from uuid import UUID

from langchain_openai import ChatOpenAI

from src.config.logging import get_logger
from src.config.settings import settings
from src.models.query import Citation, GeneratedResponse

logger = get_logger(__name__)


def _create_llm() -> ChatOpenAI:
    """Create LLM client instance.

    Returns:
        Configured ChatOpenAI client
    """
    return ChatOpenAI(
        model="qwen-max",
        openai_api_base=settings.qwen_api_base,
        openai_api_key=settings.qwen_api_key,
        temperature=0.1,  # Low temperature for factual responses
        max_tokens=2000,
    )


def _create_prompt(question: str, chunks: list[dict]) -> str:
    """Create prompt for answer generation.

    Args:
        question: User's question
        chunks: Retrieved context chunks

    Returns:
        Formatted prompt string
    """
    # Build context section with citations
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[{i}] {chunk['text']}")

    context = "\n\n".join(context_parts)

    prompt = f"""You are a helpful assistant. Answer the question using ONLY the provided context below.

IMPORTANT RULES:
1. Include citations [1], [2], etc. for each claim using the context numbers
2. If information is not in the context, explicitly say "I don't have enough information to answer this"
3. Do not make up or infer information beyond what is explicitly stated
4. Keep your answer concise and focused on the question

Context:
{context}

Question: {question}

Answer:"""

    return prompt


def _parse_citations(answer_text: str, chunks: list[dict]) -> list[Citation]:
    """Parse citations from generated answer.

    Args:
        answer_text: Generated answer with citation markers [1], [2], etc.
        chunks: Original chunks for citation mapping

    Returns:
        List of Citation objects
    """
    citations = []
    seen_indices = set()

    # Find all citation markers [1], [2], etc.
    citation_pattern = r"\[(\d+)\]"
    matches = re.findall(citation_pattern, answer_text)

    for match in matches:
        index = int(match) - 1  # Convert to 0-based index

        if index < 0 or index >= len(chunks):
            continue  # Invalid citation index

        if index in seen_indices:
            continue  # Already processed

        seen_indices.add(index)

        chunk = chunks[index]
        # Extract text excerpt (first 100 chars)
        excerpt = chunk["text"][:100]
        if len(chunk["text"]) > 100:
            excerpt += "..."

        citation = Citation(
            chunk_id=UUID(chunk["chunk_id"]),
            text_excerpt=excerpt,
            filename=chunk["metadata"].get("filename", "unknown"),
        )
        citations.append(citation)

    return citations


def generate_answer(question: str, chunks: list[dict]) -> GeneratedResponse:
    """Generate natural language answer with citations from retrieved context.

    Args:
        question: User's original question
        chunks: Top-k reranked chunks

    Returns:
        GeneratedResponse with answer and citations

    Raises:
        RuntimeError: If LLM API fails
        ValueError: If chunks list is empty
    """
    if not chunks:
        raise ValueError("chunks list cannot be empty")

    try:
        logger.info(
            f"Generating answer from {len(chunks)} chunks",
            extra={"stage": "generate_answer", "chunks": len(chunks)},
        )
        start_time = time.time()

        # Create LLM client
        llm = _create_llm()

        # Create prompt
        prompt = _create_prompt(question, chunks)

        # Generate answer
        response = llm.invoke(prompt)
        answer_text = response.content

        # Parse citations
        citations = _parse_citations(answer_text, chunks)

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate confidence score (simple heuristic: ratio of citations to chunks)
        confidence_score = min(len(citations) / max(len(chunks), 1), 1.0) if citations else 0.5

        result = GeneratedResponse(
            query_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            answer_text=answer_text,
            citations=citations,
            confidence_score=confidence_score,
            generation_duration_ms=duration_ms,
        )

        logger.info(
            f"Generated answer with {len(citations)} citations",
            extra={
                "stage": "generate_answer",
                "citations": len(citations),
                "duration_ms": duration_ms,
                "confidence": confidence_score,
            },
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed to generate answer: {e}",
            extra={"stage": "generate_answer"},
            exc_info=True,
        )
        raise RuntimeError(f"Failed to generate answer: {e}") from e
