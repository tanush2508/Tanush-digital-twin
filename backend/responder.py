from __future__ import annotations

from backend.clients import get_async_client
from backend.config import settings
from backend.prompts import RESPONDER_SYSTEM_PROMPT


async def generate_answer(message: str, evidence_packet: list[dict]) -> dict:
    client = get_async_client()

    evidence_text = _format_evidence(evidence_packet)

    response = await client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": RESPONDER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""Question:
{message}

Evidence:
{evidence_text}

Write a grounded answer based only on the evidence. Keep it concise and natural.
""",
            },
        ],
        prompt_cache_key=f"{settings.prompt_cache_key_prefix}:responder",
        prompt_cache_retention=settings.prompt_cache_retention,
        service_tier=settings.service_tier,
    )

    answer = response.output_text.strip()
    cited_chunk_ids = [item["chunk_id"] for item in evidence_packet]

    return {
        "answer": answer,
        "citations": cited_chunk_ids,
    }


def _format_evidence(evidence_packet: list[dict]) -> str:
    # Keep only fields the model actually needs.
    blocks: list[str] = []

    for idx, item in enumerate(evidence_packet, start=1):
        blocks.append(
            f"""[{idx}]
source: {item['source']}
title: {item['title']}
layer: {item['layer']}
content: {item['content']}
"""
        )

    return "\n".join(blocks)