from __future__ import annotations

import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def split_paragraph_chunks(text: str, max_chars: int = 1200) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = para if not current else f"{current}\n\n{para}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(para) <= max_chars:
                current = para
            else:
                start = 0
                while start < len(para):
                    end = min(start + max_chars, len(para))
                    chunks.append(para[start:end].strip())
                    start = end
                current = ""

    if current:
        chunks.append(current)

    return chunks


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)