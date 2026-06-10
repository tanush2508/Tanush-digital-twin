from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


MemoryLayer = Literal["long_term", "current", "archive"]


@dataclass
class MemoryRecord:
    id: str
    layer: MemoryLayer
    source: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
    visibility: str = "professional"
    importance: float = 0.5
    promotion_candidate: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkRecord:
    id: str
    memory_id: str
    layer: MemoryLayer
    source: str
    title: str
    content: str
    chunk_index: int
    tags: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
    visibility: str = "professional"
    importance: float = 0.5
    promotion_candidate: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    chunk: ChunkRecord
    score: float