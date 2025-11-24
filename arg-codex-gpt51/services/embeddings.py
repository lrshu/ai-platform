from __future__ import annotations

from functools import lru_cache
from langchain_openai import OpenAIEmbeddings

from services.config import get_settings


@lru_cache(maxsize=1)
def get_embedder() -> OpenAIEmbeddings:
    settings = get_settings()
    return OpenAIEmbeddings(
        model="text-embedding-v4",
        api_key=settings.qwen_api_key,
        base_url=settings.qwen_api_base,
    )
