from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from services.clients import invoke_prompt_safe
from services.models import GenerationResult, RetrievalResult


ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant that answers questions using provided context.
    If the answer is not in the context, say so explicitly.

    Context:
    {context}

    Question: {question}
    """
)


def run_generation(question: str, results: list[RetrievalResult]) -> GenerationResult:
    context = "\n\n".join(f"- {r.content}" for r in results) if results else "No context"
    answer = invoke_prompt_safe(ANSWER_PROMPT, {"context": context, "question": question})
    return GenerationResult(answer=answer, citations=results)
