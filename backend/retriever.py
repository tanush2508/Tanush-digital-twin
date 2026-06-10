from __future__ import annotations

from backend.config import settings
from backend.embed import embed_texts
from backend.memory_models import SearchResult
from backend.vector_store import LocalVectorStore


_LAYER_WEIGHTS = {
    "timeless": {"long_term": 0.22, "current": 0.00, "archive": 0.02},
    "current": {"long_term": 0.08, "current": 0.24, "archive": 0.06},
    "historical": {"long_term": 0.10, "current": 0.02, "archive": 0.22},
    "mixed": {"long_term": 0.16, "current": 0.14, "archive": 0.12},
}


def retrieve_chunks(
    message: str,
    plan: dict,
    top_k: int | None = None,
    store: LocalVectorStore | None = None,
) -> list[SearchResult]:
    query_vector = embed_texts([message])[0]
    return retrieve_chunks_from_vector(
        query_vector=query_vector,
        plan=plan,
        top_k=top_k,
        store=store,
    )


def retrieve_chunks_from_vector(
    query_vector: list[float],
    plan: dict,
    top_k: int | None = None,
    store: LocalVectorStore | None = None,
) -> list[SearchResult]:
    store = store or LocalVectorStore()

    target_layers = plan.get("target_layers") or ["long_term"]
    temporal_mode = plan.get("temporal_mode", "timeless")
    target_tags = set(tag.lower() for tag in plan.get("target_tags", []))
    question_type = str(plan.get("question_type", "general")).lower()

    initial_results = store.search(
        query_vector=query_vector,
        top_k=(top_k or settings.top_k) * 4,
        allowed_layers=target_layers,
    )

    rescored: list[SearchResult] = []
    for result in initial_results:
        chunk = result.chunk
        chunk_tags = set(tag.lower() for tag in chunk.tags)

        score = result.score
        score += _LAYER_WEIGHTS.get(temporal_mode, _LAYER_WEIGHTS["timeless"]).get(chunk.layer, 0.0)
        score += _tag_bonus(chunk_tags, target_tags)
        score += 0.04 * float(chunk.importance)
        score += _source_bonus(chunk.source, chunk_tags, question_type)
        score += _temporal_penalty(chunk.layer, temporal_mode, question_type)
        score += _generic_penalty(chunk.source, chunk_tags, question_type)

        rescored.append(SearchResult(chunk=chunk, score=score))

    rescored.sort(key=lambda x: x.score, reverse=True)

    deduped = _dedupe_by_memory_id(rescored)
    return deduped[: (top_k or settings.top_k)]


def _tag_bonus(chunk_tags: set[str], target_tags: set[str]) -> float:
    if not target_tags:
        return 0.0

    overlap = len(chunk_tags & target_tags)
    return min(0.04 * overlap, 0.16)


def _source_bonus(source: str, chunk_tags: set[str], question_type: str) -> float:
    src = source.lower()

    # Strong preference for real project docs on project questions.
    if "project" in question_type:
        bonus = 0.0
        if "projects/" in src:
            bonus += 0.20
        if "project" in chunk_tags:
            bonus += 0.12
        if "deployment" in chunk_tags:
            bonus += 0.08
        return bonus

    return 0.0


def _temporal_penalty(layer: str, temporal_mode: str, question_type: str) -> float:
    # On timeless project/identity questions, discourage temporal leakage.
    if temporal_mode == "timeless" and "project" in question_type:
        if layer == "current":
            return -0.14
        if layer == "archive":
            return -0.18

    if temporal_mode == "timeless" and "identity" in question_type:
        if layer in {"current", "archive"}:
            return -0.10

    return 0.0


def _generic_penalty(source: str, chunk_tags: set[str], question_type: str) -> float:
    src = source.lower()

    if "project" in question_type:
        penalty = 0.0
        if "preferences" in src:
            penalty -= 0.06
        if "profile.json" in src:
            penalty -= 0.06
        if "bio.md" in src:
            penalty -= 0.04
        return penalty

    return 0.0


def _dedupe_by_memory_id(results: list[SearchResult]) -> list[SearchResult]:
    best_by_memory_id: dict[str, SearchResult] = {}
    for result in results:
        memory_id = result.chunk.memory_id
        existing = best_by_memory_id.get(memory_id)
        if existing is None or result.score > existing.score:
            best_by_memory_id[memory_id] = result

    deduped = list(best_by_memory_id.values())
    deduped.sort(key=lambda x: x.score, reverse=True)
    return deduped