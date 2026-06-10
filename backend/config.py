from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass(frozen=True)
class Settings:
    app_name: str = "Digital Twin"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip().replace("\n", "").replace("\r", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    index_dir: Path = base_dir / os.getenv("INDEX_DIR", ".index")
    top_k: int = int(os.getenv("TOP_K", "8"))
    max_evidence_chunks: int = int(os.getenv("MAX_EVIDENCE_CHUNKS", "6"))

    # latency-related knobs
    prompt_cache_key_prefix: str = os.getenv("PROMPT_CACHE_KEY_PREFIX", "digital_twin_v1")
    prompt_cache_retention: str = os.getenv("PROMPT_CACHE_RETENTION", "in_memory")
    service_tier: str = os.getenv("OPENAI_SERVICE_TIER", "auto")

    def validate(self) -> None:
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")


settings = Settings()
settings.index_dir.mkdir(parents=True, exist_ok=True)