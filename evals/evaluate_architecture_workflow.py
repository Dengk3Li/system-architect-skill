#!/usr/bin/env python3
"""Score captured architecture-workflow responses against scenario rubrics."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    cases_path = Path(__file__).with_name("architecture-workflow.json")
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        output = str(case.get("candidate_output", "")).lower()
        for pattern in case.get("required_patterns", []):
            if str(pattern).lower() not in output:
                failures.append(f"{case['id']}: missing required pattern {pattern!r}")
        for pattern in case.get("forbidden_patterns", []):
            if str(pattern).lower() in output:
                failures.append(f"{case['id']}: contains forbidden pattern {pattern!r}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 2
    print(f"PASS scenarios={len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
