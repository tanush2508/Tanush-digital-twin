from __future__ import annotations


def _looks_like_unsupported_personal_question(message: str) -> bool:
    msg = (message or "").lower()

    cues = [
        "favorite sports team",
        "favorite team",
        "political views",
        "politics",
        "religious views",
        "religion",
        "favorite movie",
        "favorite food",
        "favorite color",
        "what do you believe politically",
        "what party",
        "which team do you support",
    ]

    return any(cue in msg for cue in cues)


def _answer_states_missing_info(answer: str) -> bool:
    text = (answer or "").strip().lower()

    patterns = [
        "there's no information",
        "there is no information",
        "not enough grounded information",
        "not enough information",
        "the provided evidence doesn't say",
        "the provided materials",
        "the documents focus on",
        "aren’t stated",
        "aren't stated",
        "not stated",
        "don't mention",
        "doesn't mention",
        "include no information",
        "no information about",
    ]

    return any(pattern in text for pattern in patterns)


def apply_policy(message: str, answer: str, verifier_result: dict, plan: dict | None = None) -> dict:
    confidence = float(verifier_result.get("confidence", 0.0))
    action = verifier_result.get("action", "soften")
    unsupported = verifier_result.get("unsupported_claims", [])
    temporal_issues = verifier_result.get("temporal_issues", [])

    clean_answer = (answer or "").strip()
    plan = plan or {}
    question_type = str(plan.get("question_type", "")).lower()

    if action == "refuse" or confidence < 0.35:
        return {
            "answer": "I do not have enough grounded information in my current data to answer that confidently.",
            "confidence": confidence,
            "action": "refuse",
        }

    unsupported_personal = (
        _looks_like_unsupported_personal_question(message)
        or question_type in {"personal_preference", "political_views", "unsupported_preference"}
    )

    # If the system correctly identifies that evidence is missing for an unsupported personal question,
    # keep the content but label it as soften, not accept.
    if unsupported_personal and _answer_states_missing_info(clean_answer):
        return {
            "answer": "There isn’t enough grounded information in my current data to answer that.",
            "confidence": confidence,
            "action": "soften",
        }

    if unsupported:
        return {
            "answer": "There isn’t enough grounded information in my current data to answer that.",
            "confidence": confidence,
            "action": "soften",
        }

    if action == "soften" and confidence >= 0.8 and not temporal_issues:
        return {
            "answer": clean_answer,
            "confidence": confidence,
            "action": "accept",
        }

    if action == "soften" or temporal_issues or confidence < 0.7:
        if not clean_answer:
            clean_answer = "I can only answer this partially from the available information."

        lower = clean_answer.lower()
        already_softened = (
            lower.startswith("based on the available information")
            or lower.startswith("based on the provided materials")
            or lower.startswith("i do not have enough")
            or lower.startswith("there isn’t enough")
            or lower.startswith("there isn't enough")
        )

        softened = clean_answer if already_softened else f"Based on the available information, {clean_answer}"

        return {
            "answer": softened,
            "confidence": confidence,
            "action": "soften",
        }

    return {
        "answer": clean_answer,
        "confidence": confidence,
        "action": "accept",
    }