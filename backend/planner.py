from __future__ import annotations

import json
from typing import Any

from backend.clients import get_async_client
from backend.config import settings
from backend.prompts import PLANNER_SYSTEM_PROMPT


def _parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def _has_any(text: str, phrases: list[str]) -> bool:
    return any(p in text for p in phrases)


def _normalize_plan(message: str, raw_plan: dict[str, Any]) -> dict[str, Any]:
    msg = message.lower()

    current_cues = [
        "right now", "currently", "current", "today", "this week", "active", "ongoing",
        "at the moment", "working on now", "focused on now"
    ]
    historical_cues = [
        "recently", "earlier", "before", "previously", "last week", "last month",
        "in the past", "history", "timeline", "what were you"
    ]
    project_cues = [
        "project", "best project", "strongest project", "which project",
        "example project", "tell me about repaintwiz", "shows your", "demonstrates your"
    ]

    question_type = raw_plan.get("question_type", "general")
    temporal_mode = raw_plan.get("temporal_mode", "timeless")
    target_layers = raw_plan.get("target_layers", ["long_term"])
    target_tags = raw_plan.get("target_tags", [])
    needs_multi_source_synthesis = bool(raw_plan.get("needs_multi_source_synthesis", False))
    desired_answer_style = raw_plan.get("desired_answer_style", "concise_first_person_professional")
    should_cite = bool(raw_plan.get("should_cite", True))

    if not isinstance(target_layers, list) or not target_layers:
        target_layers = ["long_term"]
    if not isinstance(target_tags, list):
        target_tags = []

    # Hard routing rules for obvious temporal questions.
    if _has_any(msg, current_cues):
        temporal_mode = "current"
        target_layers = ["current", "long_term"]
        if "current_focus" not in target_tags:
            target_tags.append("current_focus")

    elif _has_any(msg, historical_cues):
        temporal_mode = "historical"
        target_layers = ["archive", "long_term"]

    # Hard routing rules for project/capability questions.
    if _has_any(msg, project_cues):
        question_type = "project_showcase"
        needs_multi_source_synthesis = True

        # Unless the user explicitly made it temporal, keep this timeless.
        if not _has_any(msg, current_cues + historical_cues):
            temporal_mode = "timeless"
            target_layers = ["long_term"]

        for tag in ["project", "deployment"]:
            if tag not in target_tags:
                target_tags.append(tag)

    # Clean up tag noise.
    clean_tags = []
    seen = set()
    for tag in target_tags:
        t = str(tag).strip().lower().replace(" ", "_")
        if t and t not in seen:
            seen.add(t)
            clean_tags.append(t)

    return {
        "question_type": question_type,
        "temporal_mode": temporal_mode,
        "target_layers": target_layers,
        "target_tags": clean_tags,
        "needs_multi_source_synthesis": needs_multi_source_synthesis,
        "desired_answer_style": desired_answer_style,
        "should_cite": should_cite,
    }


async def plan_query(message: str) -> dict:
    client = get_async_client()

    response = await client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        text={"format": {"type": "json_object"}},
        prompt_cache_key=f"{settings.prompt_cache_key_prefix}:planner",
        prompt_cache_retention=settings.prompt_cache_retention,
        service_tier=settings.service_tier,
    )

    raw_plan = _parse_json_object(response.output_text)
    return _normalize_plan(message, raw_plan)