from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APIError, APIStatusError, BadRequestError, RateLimitError

from src.config import get_settings
from src.fallbacks import embed_texts_locally, summarize_locally

logger = logging.getLogger(__name__)

_OPENAI_ERRORS = (BadRequestError, APIError, APIStatusError, RateLimitError, APIConnectionError)


@lru_cache(maxsize=1)
def get_llm(model: Optional[str] = None) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=model or "qwen-max",
        base_url=settings.qwen_api_base,
        api_key=settings.qwen_api_key,
        temperature=0.1,
        extra_body={"max_input_tokens": 256000},
    )


@lru_cache(maxsize=1)
def get_embedder(model: Optional[str] = None) -> DashScopeEmbeddings:
    settings = get_settings()
    dashscope_key = settings.qwen_api_key or settings.qwen_api_base  # reuse same key env
    return DashScopeEmbeddings(model=model or "text-embedding-v2", dashscope_api_key=dashscope_key)


def embed_documents_safe(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    try:
        return get_embedder().embed_documents(texts)
    except Exception as exc:  # DashScope raises generic DashScopeServerException
        logger.warning("DashScope embeddings failed, using deterministic fallback: %s", exc)
        return embed_texts_locally(texts)


def embed_query_safe(text: str) -> list[float]:
    vectors = embed_documents_safe([text])
    return vectors[0] if vectors else []


def invoke_prompt_safe(prompt, values: dict, fallback: Optional[str] = None) -> str:
    try:
        return (prompt | get_llm()).invoke(values).content
    except _OPENAI_ERRORS as exc:
        logger.warning("LLM call failed, using fallback response: %s", exc)
        if fallback is not None:
            return fallback
        return summarize_locally(values.get("question", ""), values.get("context", ""))


def run_llm_safe(prompt: ChatOpenAI, **kwargs):
    llm = get_llm()
    try:
        return prompt | llm
    except APIStatusError as exc:
        logger = __import__("logging").getLogger(__name__)
        logger.warning("LLM call failed, using fallback answer: %s", exc)
        return summarize_locally(kwargs.get("question", ""), kwargs.get("context", ""))
