from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from backend.config import settings
from backend.memory_models import ChunkRecord, SearchResult
from backend.utils import ensure_parent_dir


class LocalVectorStore:
    def __init__(self, index_dir: Path | None = None) -> None:
        self.index_dir = index_dir or settings.index_dir
        self.vectors_path = self.index_dir / "vectors.npy"
        self.chunks_path = self.index_dir / "chunks.json"
        self._vectors: np.ndarray | None = None
        self._chunks: list[ChunkRecord] = []

    def save(self, chunks: list[ChunkRecord], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")

        ensure_parent_dir(self.vectors_path)
        np_vectors = np.array(vectors, dtype=np.float32)
        np.save(self.vectors_path, np_vectors)

        serializable = [asdict(chunk) for chunk in chunks]
        self.chunks_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

        self._vectors = np_vectors
        self._chunks = chunks

    def load(self) -> None:
        if not self.vectors_path.exists() or not self.chunks_path.exists():
            raise FileNotFoundError("Vector index not found. Run scripts/build_index.py first.")

        self._vectors = np.load(self.vectors_path)
        raw_chunks = json.loads(self.chunks_path.read_text(encoding="utf-8"))
        self._chunks = [ChunkRecord(**item) for item in raw_chunks]

    def is_ready(self) -> bool:
        return self.vectors_path.exists() and self.chunks_path.exists()

    def search(
        self,
        query_vector: list[float],
        top_k: int = 8,
        allowed_layers: list[str] | None = None,
    ) -> list[SearchResult]:
        if self._vectors is None or not self._chunks:
            self.load()

        assert self._vectors is not None

        q = np.array(query_vector, dtype=np.float32)
        q = _normalize(q)
        docs = _normalize(self._vectors)

        scores = docs @ q

        results: list[SearchResult] = []
        for idx, score in enumerate(scores.tolist()):
            chunk = self._chunks[idx]
            if allowed_layers and chunk.layer not in allowed_layers:
                continue
            results.append(SearchResult(chunk=chunk, score=float(score)))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def count_by_layer(self) -> dict[str, int]:
        if not self._chunks:
            try:
                self.load()
            except FileNotFoundError:
                return {"long_term": 0, "current": 0, "archive": 0}

        counts = {"long_term": 0, "current": 0, "archive": 0}
        for chunk in self._chunks:
            counts[chunk.layer] = counts.get(chunk.layer, 0) + 1
        return counts


def _normalize(arr: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(arr, axis=-1, keepdims=True)
    norms = np.where(norms == 0, 1e-8, norms)
    return arr / norms