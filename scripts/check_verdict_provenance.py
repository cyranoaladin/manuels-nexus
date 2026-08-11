#!/usr/bin/env python3
"""Gate: verdict files with content changes must have monotonically fresh judged_at.

Rule (monotone): for any *_substance_review.json modified between base and HEAD,
if a content field changed (quote, justification, anchor, verdict, proofs, scientific_flags),
then judged_at MUST have changed AND be strictly more recent than the base version.
No time-window heuristic — pure monotonicity.

Fail-closed: if the base ref is unavailable or git diff fails, exit 2 with an
explicit message ("base ref indisponible : guard NON exécuté"). Never PASS empty.

Usage:
    python -m scripts.check_verdict_provenance [--base BASE_REF]

Exit codes:
    0: all changed verdicts have valid monotone provenance (or no verdicts changed)
    1: provenance violation detected
    2: guard could not execute (base unavailable, git error)
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Fields whose modification requires a fresh judged_at
CONTENT_FIELDS_TOP = {"capacities"}
CONTENT_FIELDS_CAP = {"capacity_id", "official_label", "verdict", "justification", "scientific_flags"}
CONTENT_FIELDS_PROOF = {"anchor", "quote", "teaches", "file", "present"}


def _resolve_base(base_ref: str) -> str | None:
    """Verify that base_ref is resolvable by git."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", base_ref],
        capture_output=True, text=True, cwd=ROOT,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_changed_verdict_files(base_ref: str) -> list[str] | None:
    """Return relative paths of verdict files changed between base_ref and HEAD.

    Returns None if git diff fails (fail-closed).
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref, "HEAD"],
        capture_output=True, text=True, cwd=ROOT,
    )
    if result.returncode != 0:
        return None
    changed = []
    for line in result.stdout.strip().splitlines():
        if line.endswith("_substance_review.json"):
            changed.append(line)
    return changed


class _BaseCorrupt:
    """Sentinel: base file exists but is not valid JSON."""

    def __init__(self, detail: str) -> None:
        self.detail = detail


def get_base_version(base_ref: str, rel_path: str) -> dict[str, Any] | None | _BaseCorrupt:
    """Read the verdict file content at the base ref.

    Returns:
        dict  — valid base data
        None  — file did not exist at base (genuinely new file)
        _BaseCorrupt — file existed but could not be parsed (fail-closed)
    """
    result = subprocess.run(
        ["git", "show", f"{base_ref}:{rel_path}"],
        capture_output=True, text=True, cwd=ROOT,
    )
    if result.returncode != 0:
        return None  # file didn't exist at base (new file)
    try:
        data: dict[str, Any] = json.loads(result.stdout)
        return data
    except json.JSONDecodeError as e:
        return _BaseCorrupt(f"JSON invalide dans la base ({e})")


def _content_changed(base_data: dict[str, Any], head_data: dict[str, Any]) -> bool:
    """Return True if any content field differs between base and head."""
    base_caps = base_data.get("capacities", [])
    head_caps = head_data.get("capacities", [])

    if len(base_caps) != len(head_caps):
        return True

    for bc, hc in zip(base_caps, head_caps):
        for field in CONTENT_FIELDS_CAP:
            if bc.get(field) != hc.get(field):
                return True
        for proof_key in ("proof_course", "proof_practice", "proof_correction"):
            bp = bc.get(proof_key, {})
            hp = hc.get(proof_key, {})
            for field in CONTENT_FIELDS_PROOF:
                if bp.get(field) != hp.get(field):
                    return True
    return False


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def check_provenance(base_ref: str = "HEAD~1") -> tuple[list[str], list[str], bool]:
    """Check monotone provenance for all changed verdict files.

    Returns (errors, inspected_files, guard_executed).
    If guard_executed is False, errors contains the reason.
    """
    # Fail-closed: verify base is resolvable
    resolved = _resolve_base(base_ref)
    if resolved is None:
        return (
            [f"base ref indisponible ({base_ref!r}) : guard NON exécuté"],
            [],
            False,
        )

    changed = get_changed_verdict_files(resolved)
    if changed is None:
        return (
            ["git diff failed : guard NON exécuté"],
            [],
            False,
        )

    errors: list[str] = []
    inspected: list[str] = []

    for rel_path in changed:
        head_path = ROOT / rel_path
        if not head_path.exists():
            continue  # deleted file, skip

        inspected.append(rel_path)

        try:
            head_data = json.loads(head_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"{rel_path}: unreadable ({e})")
            continue

        head_judged_at = _parse_dt(head_data.get("judged_at"))
        if head_judged_at is None:
            errors.append(
                f"{rel_path}: missing or invalid judged_at — "
                "verdict must be produced by judge_campaign"
            )
            continue

        # Get base version
        base_result = get_base_version(resolved, rel_path)
        if base_result is None:
            # New file — just needs valid judged_at (already checked)
            continue
        if isinstance(base_result, _BaseCorrupt):
            errors.append(
                f"{rel_path}: base illisible ({base_result.detail}) — "
                "comparaison impossible, re-jugement requis."
            )
            continue
        base_data = base_result

        # Check if content actually changed
        if not _content_changed(base_data, head_data):
            continue  # metadata-only change, no provenance concern

        # Content changed → judged_at must be strictly monotone
        base_judged_at = _parse_dt(base_data.get("judged_at"))

        if base_judged_at is None:
            # Base had no judged_at, head has one — OK (upgrade)
            continue

        if head_judged_at == base_judged_at:
            errors.append(
                f"{rel_path}: content fields changed but judged_at unchanged "
                f"({head_judged_at.isoformat()}) — verdict was edited manually "
                "without re-running judge_campaign."
            )
        elif head_judged_at < base_judged_at:
            errors.append(
                f"{rel_path}: judged_at regressed "
                f"(base={base_judged_at.isoformat()}, head={head_judged_at.isoformat()}) — "
                "monotonicity violation."
            )

    return errors, inspected, True


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="HEAD~1", help="Base ref for diff")
    args = parser.parse_args()

    errors, inspected, executed = check_provenance(args.base)

    if not executed:
        print("check_verdict_provenance: FAIL (guard non exécuté)")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(2)

    if inspected:
        print(f"check_verdict_provenance: inspected {len(inspected)} verdict file(s):")
        for f in inspected:
            print(f"    {f}")

    if errors:
        print("check_verdict_provenance: FAIL")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("check_verdict_provenance: PASS")


if __name__ == "__main__":
    main()
