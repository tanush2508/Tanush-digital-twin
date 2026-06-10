from __future__ import annotations

import json
from typing import Any

from backend.clients import get_async_client
from backend.config import settings
from backend.prompts import VERIFIER_SYSTEM_PROMPT


def _parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


async def verify_answer(message: str, evidence_packet: list[dict], drafted_answer: str) -> dict:
    client = get_async_client()

    slim_evidence = [
        {
            "source": item["source"],
            "title": item["title"],
            "layer": item["layer"],
            "content": item["content"],
        }
        for item in evidence_packet
    ]

    response = await client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""Question:
{message}

Evidence:
{json.dumps(slim_evidence, indent=2)}

Drafted answer:
{drafted_answer}
""",
            },
        ],
        text={"format": {"type": "json_object"}},
        prompt_cache_key=f"{settings.prompt_cache_key_prefix}:verifier",
        prompt_cache_retention=settings.prompt_cache_retention,
        service_tier=settings.service_tier,
    )

    result = _parse_json_object(response.output_text)

    return {
        "supported_claims": result.get("supported_claims", []),
        "partially_supported_claims": result.get("partially_supported_claims", []),
        "unsupported_claims": result.get("unsupported_claims", []),
        "temporal_issues": result.get("temporal_issues", []),
        "confidence": float(result.get("confidence", 0.0)),
        "action": result.get("action", "soften"),
    }