from __future__ import annotations

from typing import Any


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def contains_any(text: str, phrases: list[str]) -> bool:
    text = normalize_text(text)
    return any(p.lower() in text for p in phrases)


def contains_none(text: str, phrases: list[str]) -> bool:
    text = normalize_text(text)
    return all(p.lower() not in text for p in phrases)


def extract_debug_policy_action(result: dict[str, Any]) -> str:
    return (
        result.get("debug", {})
        .get("policy", {})
        .get("action", "")
        .strip()
        .lower()
    )


def extract_debug_layers(result: dict[str, Any]) -> list[str]:
    planner = result.get("debug", {}).get("planner", {})
    layers = planner.get("target_layers", [])
    return [str(layer).lower() for layer in layers]


def score_eval_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    answer = result.get("answer", "")
    sources = result.get("sources", [])
    policy_action = extract_debug_policy_action(result)
    debug_layers = extract_debug_layers(result)

    must_include_any = case.get("must_include_any", [])
    must_not_include_any = case.get("must_not_include_any", [])
    expected_layers = [x.lower() for x in case.get("expected_layers", [])]
    expected_action = case.get("expected_action", "").lower()

    checks = {
        "has_answer": bool(answer.strip()),
        "has_sources": len(sources) > 0,
        "expected_action_match": (policy_action == expected_action) if expected_action else True,
        "expected_layers_overlap": bool(set(debug_layers) & set(expected_layers)) if expected_layers else True,
        "must_include_any_match": contains_any(answer, must_include_any) if must_include_any else True,
        "must_not_include_any_match": contains_none(answer, must_not_include_any) if must_not_include_any else True,
    }

    passed = all(checks.values())

    return {
        "id": case.get("id"),
        "category": case.get("category"),
        "question": case.get("question"),
        "passed": passed,
        "checks": checks,
        "policy_action": policy_action,
        "debug_layers": debug_layers,
        "confidence": result.get("confidence"),
        "answer": answer,
        "num_sources": len(sources),
    }


def summarize_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    passed = sum(1 for row in rows if row["passed"])
    by_category: dict[str, dict[str, int]] = {}

    for row in rows:
        category = row["category"]
        if category not in by_category:
            by_category[category] = {"total": 0, "passed": 0}
        by_category[category]["total"] += 1
        if row["passed"]:
            by_category[category]["passed"] += 1

    return {
        "total": total,
        "passed": passed,
        "pass_rate": round((passed / total) * 100, 1) if total else 0.0,
        "by_category": by_category,
    }