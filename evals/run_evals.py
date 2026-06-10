from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from evals.eval_metrics import score_eval_case, summarize_results

BASE_URL = "http://127.0.0.1:8000"
EVALS_PATH = Path(__file__).resolve().parent / "eval_questions.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "eval_results.json"


def post_chat(message: str, debug: bool = True) -> dict:
    payload = json.dumps({
        "message": message,
        "debug": debug,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=180) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def main() -> None:
    if not EVALS_PATH.exists():
        raise FileNotFoundError(f"Missing eval file: {EVALS_PATH}")

    cases = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    rows = []

    print(f"Running {len(cases)} evals against {BASE_URL}...")

    for idx, case in enumerate(cases, start=1):
        question = case["question"]
        print(f"[{idx}/{len(cases)}] {case['id']} - {question}")

        try:
            result = post_chat(question, debug=True)
            row = score_eval_case(case, result)
            rows.append(row)

            status = "PASS" if row["passed"] else "FAIL"
            print(f"  -> {status} | action={row['policy_action']} | confidence={row['confidence']}")
        except urllib.error.HTTPError as e:
            print(f"  -> HTTP ERROR {e.code}: {e.read().decode('utf-8', errors='ignore')}")
            rows.append({
                "id": case.get("id"),
                "category": case.get("category"),
                "question": case.get("question"),
                "passed": False,
                "checks": {"request_succeeded": False},
                "policy_action": "",
                "debug_layers": [],
                "confidence": None,
                "answer": "",
                "num_sources": 0,
            })
        except Exception as e:
            print(f"  -> ERROR: {e}")
            rows.append({
                "id": case.get("id"),
                "category": case.get("category"),
                "question": case.get("question"),
                "passed": False,
                "checks": {"request_succeeded": False},
                "policy_action": "",
                "debug_layers": [],
                "confidence": None,
                "answer": "",
                "num_sources": 0,
            })

    summary = summarize_results(rows)
    report = {
        "summary": summary,
        "rows": rows,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\nSummary")
    print("-------")
    print(f"Passed: {summary['passed']} / {summary['total']} ({summary['pass_rate']}%)")

    for category, stats in summary["by_category"].items():
        print(f"{category}: {stats['passed']} / {stats['total']}")

    print(f"\nSaved detailed results to {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)