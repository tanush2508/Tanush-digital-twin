from __future__ import annotations

from pathlib import Path

from backend.config import settings
from backend.memory_models import ChunkRecord, MemoryRecord
from backend.utils import read_json, read_jsonl, read_text, slugify, split_paragraph_chunks


def load_long_term_records() -> list[MemoryRecord]:
    base = settings.data_dir / "long_term"
    records: list[MemoryRecord] = []

    for path in sorted(base.rglob("*")):
        if path.is_dir():
            continue

        rel = path.relative_to(settings.data_dir).as_posix()

        if path.suffix == ".md":
            text = read_text(path)
            title = path.stem.replace("_", " ").title()
            records.append(
                MemoryRecord(
                    id=f"mem_{slugify(rel)}",
                    layer="long_term",
                    source=rel,
                    title=title,
                    content=text,
                    tags=_infer_tags_from_path(rel),
                    promotion_candidate=True,
                )
            )
        elif path.suffix == ".json":
            data = read_json(path)
            content = _json_to_text(data)
            title = data.get("title") or path.stem.replace("_", " ").title()
            tags = data.get("tags", []) if isinstance(data.get("tags"), list) else []
            records.append(
                MemoryRecord(
                    id=f"mem_{slugify(rel)}",
                    layer="long_term",
                    source=rel,
                    title=title,
                    content=content,
                    tags=_infer_tags_from_path(rel) + tags,
                    promotion_candidate=True,
                    metadata=data,
                )
            )

    return records


def load_current_records() -> list[MemoryRecord]:
    path = settings.data_dir / "current" / "current_state.json"
    if not path.exists():
        return []

    data = read_json(path)
    updated_at = data.get("updated_at")
    items = data.get("items", [])

    records: list[MemoryRecord] = []
    for idx, item in enumerate(items):
        content = item.get("content", "").strip()
        if not content:
            continue
        item_id = item.get("id", f"current_{idx}")
        title = item.get("title", "Current Context")
        records.append(
            MemoryRecord(
                id=item_id,
                layer="current",
                source="current/current_state.json",
                title=title,
                content=content,
                tags=item.get("tags", []),
                updated_at=updated_at,
                importance=float(item.get("importance", 0.5)),
                promotion_candidate=bool(item.get("promotion_candidate", False)),
                metadata=item,
            )
        )

    return records


def load_archive_records() -> list[MemoryRecord]:
    path = settings.data_dir / "archive" / "archive.jsonl"
    rows = read_jsonl(path)

    records: list[MemoryRecord] = []
    for idx, row in enumerate(rows):
        content = row.get("content", "").strip()
        if not content:
            continue
        item_id = row.get("id", f"archive_{idx}")
        title = row.get("title", "Archived Context")
        records.append(
            MemoryRecord(
                id=item_id,
                layer="archive",
                source="archive/archive.jsonl",
                title=title,
                content=content,
                tags=row.get("tags", []),
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
                importance=float(row.get("importance", 0.5)),
                promotion_candidate=bool(row.get("promotion_candidate", False)),
                metadata=row,
            )
        )

    return records


def load_all_records() -> list[MemoryRecord]:
    return [
        *load_long_term_records(),
        *load_current_records(),
        *load_archive_records(),
    ]


def chunk_records(records: list[MemoryRecord], max_chars: int = 1200) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []

    for record in records:
        pieces = split_paragraph_chunks(record.content, max_chars=max_chars)
        for idx, piece in enumerate(pieces):
            chunks.append(
                ChunkRecord(
                    id=f"{record.id}_chunk_{idx}",
                    memory_id=record.id,
                    layer=record.layer,
                    source=record.source,
                    title=record.title,
                    content=piece,
                    chunk_index=idx,
                    tags=record.tags,
                    created_at=record.created_at,
                    updated_at=record.updated_at,
                    visibility=record.visibility,
                    importance=record.importance,
                    promotion_candidate=record.promotion_candidate,
                    metadata=record.metadata,
                )
            )

    return chunks


def _infer_tags_from_path(rel_path: str) -> list[str]:
    path = rel_path.lower()
    tags: list[str] = []

    if "project" in path or "projects/" in path:
        tags.append("project")
    if "repaintwiz" in path:
        tags.extend(["repaintwiz", "deployment", "computer_vision", "startup"])
    if "voice" in path:
        tags.extend(["voice", "agents", "realtime"])
    if "experience" in path:
        tags.append("experience")
    if "preference" in path:
        tags.append("preferences")
    if "style" in path:
        tags.append("writing_style")
    if "bio" in path:
        tags.append("bio")

    return sorted(set(tags))


def _json_to_text(data: dict) -> str:
    lines: list[str] = []

    for key, value in data.items():
        if isinstance(value, list):
            joined = ", ".join(str(v) for v in value)
            lines.append(f"{key}: {joined}")
        elif isinstance(value, dict):
            inner = ", ".join(f"{k}={v}" for k, v in value.items())
            lines.append(f"{key}: {inner}")
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines).strip()