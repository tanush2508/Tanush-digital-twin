from __future__ import annotations

from backend.clients import get_async_client, get_sync_client
from backend.config import settings


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = get_sync_client()
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


async def embed_texts_async(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = get_async_client()
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]