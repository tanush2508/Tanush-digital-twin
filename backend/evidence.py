from __future__ import annotations

from backend.config import settings
from backend.memory_models import SearchResult


def build_evidence_packet(results: list[SearchResult]) -> list[dict]:
    packet: list[dict] = []

    for result in results[: settings.max_evidence_chunks]:
        packet.append(
            {
                "chunk_id": result.chunk.id,
                "memory_id": result.chunk.memory_id,
                "source": result.chunk.source,
                "title": result.chunk.title,
                "layer": result.chunk.layer,
                "content": result.chunk.content,
                "score": round(result.score, 4),
                "tags": result.chunk.tags,
            }
        )

    return packet