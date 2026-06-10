from __future__ import annotations

import json

from backend.memory_lifecycle import run_memory_lifecycle


def main() -> None:
    result = run_memory_lifecycle()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()