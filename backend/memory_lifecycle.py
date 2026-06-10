from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.config import settings
from backend.utils import read_json, read_jsonl


def parse_iso(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except Exception:
        return None


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def load_current_state() -> dict:
    path = settings.data_dir / "current" / "current_state.json"
    if not path.exists():
        return {"updated_at": None, "items": []}
    return read_json(path)


def load_archive_rows() -> list[dict]:
    path = settings.data_dir / "archive" / "archive.jsonl"
    return read_jsonl(path)


def append_archive_rows(rows: list[dict]) -> None:
    path = settings.data_dir / "archive" / "archive.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if path.exists():
        existing = path.read_text(encoding="utf-8").splitlines()

    new_lines = existing + [json.dumps(row) for row in rows]
    path.write_text("\n".join(new_lines) + ("\n" if new_lines else ""), encoding="utf-8")


def save_current_state(data: dict) -> None:
    path = settings.data_dir / "current" / "current_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_long_term_note(title: str, content: str, source_tag: str = "memory_consolidation") -> Path:
    notes_dir = settings.data_dir / "long_term" / "consolidated"
    notes_dir.mkdir(parents=True, exist_ok=True)

    slug = title.lower().strip().replace(" ", "_").replace("/", "_")
    path = notes_dir / f"{slug}.md"

    body = f"# {title}\n\n{content}\n\nSource: {source_tag}\n"
    path.write_text(body, encoding="utf-8")
    return path


def should_expire_current_item(item: dict, updated_at: datetime | None, now: datetime) -> bool:
    expires_in_days = item.get("expires_in_days")
    if expires_in_days is None:
        return False

    if updated_at is None:
        return False

    expiry_time = updated_at + timedelta(days=int(expires_in_days))
    return now >= expiry_time


def promote_archive_item(item: dict) -> bool:
    importance = float(item.get("importance", 0.0))
    promotion_candidate = bool(item.get("promotion_candidate", False))
    content = (item.get("content") or "").lower()

    high_signal_terms = [
        "built",
        "launched",
        "designed",
        "digital twin",
        "deployment",
        "inference",
        "agent",
        "production",
        "project",
    ]

    strong_signal = any(term in content for term in high_signal_terms)
    return promotion_candidate and importance >= 0.85 and strong_signal


def summarize_for_long_term(item: dict) -> tuple[str, str]:
    title = item.get("title", "Consolidated Memory")
    content = item.get("content", "").strip()

    summary = (
        "This item was promoted from time-sensitive memory into long-term memory because it appears "
        "durable and relevant to Tanush's ongoing professional identity.\n\n"
        f"Promoted content:\n{content}"
    )

    return title, summary


def run_memory_lifecycle() -> dict:
    current_state = load_current_state()
    archive_rows = load_archive_rows()

    current_items = current_state.get("items", [])
    updated_at = parse_iso(current_state.get("updated_at"))
    now = now_utc()

    still_current = []
    newly_archived = []
    promoted = []

    for item in current_items:
        if should_expire_current_item(item, updated_at, now):
            archived_item = deepcopy(item)
            archived_item["created_at"] = archived_item.get("created_at") or (updated_at.isoformat() if updated_at else now.isoformat())
            archived_item["updated_at"] = now.isoformat()
            newly_archived.append(archived_item)
        else:
            still_current.append(item)

    if newly_archived:
        append_archive_rows(newly_archived)

    current_state["items"] = still_current
    current_state["updated_at"] = now.isoformat()
    save_current_state(current_state)

    # Promotion scan over archive
    for item in archive_rows + newly_archived:
        if promote_archive_item(item):
            title, summary = summarize_for_long_term(item)
            path = append_long_term_note(title=title, content=summary)
            promoted.append({
                "title": title,
                "path": str(path),
            })

    return {
        "archived_count": len(newly_archived),
        "still_current_count": len(still_current),
        "promoted_count": len(promoted),
        "promoted": promoted,
    }