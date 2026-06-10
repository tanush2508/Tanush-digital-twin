from __future__ import annotations

from functools import lru_cache

from openai import AsyncOpenAI, OpenAI

from backend.config import settings


@lru_cache(maxsize=1)
def get_sync_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


@lru_cache(maxsize=1)
def get_async_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)