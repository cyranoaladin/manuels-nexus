"""Non-vacuant ratchet test for mypy --strict.

Verifies that mypy actually ran AND succeeded (not silently skipped).
Pins the exact set of known errors in tests/mypy_baseline.txt.
- mypy didn't run (missing, crashed) -> FAILS.
- A NEW error not in baseline -> FAILS (regression).
- Errors REMOVED from actual but still in baseline -> FAILS (update baseline).
- Baseline == actual -> PASS.

To update after fixing errors:
  mypy --strict scripts/ scrapping_NSI/ 2>&1 | grep ': error:' \
    | sed 's|<repo_root>/||' | sort > tests/mypy_baseline.txt
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("mypy_baseline.txt")

# Sentinel that mypy prints on success (any version)
SUCCESS_SENTINEL = "no issues found"


def _normalise(line: str) -> str:
    root_str = str(ROOT) + "/"
    return line[len(root_str):] if line.startswith(root_str) else line


def test_mypy_ratchet() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", "scripts/", "scrapping_NSI/"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=300,
    )

    # NON-VACUANT GUARD: mypy must have actually run.
    # If mypy is missing or crashed, stdout won't contain the sentinel or errors.
    stdout = result.stdout
    has_sentinel = SUCCESS_SENTINEL in stdout
    has_errors = ": error:" in stdout
    assert has_sentinel or has_errors, (
        f"mypy did not produce recognisable output (returncode={result.returncode}).\n"
        f"stdout[:500]={stdout[:500]}"
    )

    actual = sorted(
        _normalise(line)
        for line in stdout.splitlines()
        if ": error:" in line
    )
    baseline = sorted(
        line.strip()
        for line in BASELINE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )

    new_errors = sorted(set(actual) - set(baseline))
    fixed_errors = sorted(set(baseline) - set(actual))

    messages: list[str] = []
    if new_errors:
        messages.append(
            f"{len(new_errors)} NEW mypy error(s) — fix them before merging:\n"
            + "\n".join(f"  + {e}" for e in new_errors[:20])
        )
    if fixed_errors:
        messages.append(
            f"{len(fixed_errors)} error(s) FIXED — update tests/mypy_baseline.txt:\n"
            + "\n".join(f"  - {e}" for e in fixed_errors[:20])
        )
    assert not messages, "\n\n".join(messages)
