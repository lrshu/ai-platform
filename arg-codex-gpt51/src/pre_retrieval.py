from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from src.clients import get_llm, invoke_prompt_safe

PROMPT = ChatPromptTemplate.from_template(
    """You rewrite search queries. Expand the question with synonyms,
    additional keywords, and clarifications while keeping intent.
    Question: {question}"""
)


def expand_query(question: str) -> str:
    return invoke_prompt_safe(PROMPT, {"question": question}, fallback=question)


def preprocess_question(question: str, *, use_expansion: bool = True) -> str:
    return expand_query(question) if use_expansion else question
