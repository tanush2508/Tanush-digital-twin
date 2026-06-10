from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    debug: bool = False


class SourceSnippet(BaseModel):
    chunk_id: str
    source: str
    title: str
    layer: str
    snippet: str
    score: float


class DebugTrace(BaseModel):
    planner: dict = Field(default_factory=dict)
    retrieved_chunks: list[dict] = Field(default_factory=list)
    verifier: dict = Field(default_factory=dict)
    policy: dict = Field(default_factory=dict)
    timings_ms: dict[str, float] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[SourceSnippet] = Field(default_factory=list)
    debug: DebugTrace | None = None


class StatusResponse(BaseModel):
    app_name: str
    index_ready: bool
    memory_counts: dict[str, int]