#!/usr/bin/env python3
"""Check the documented QA gate policy stays explicit and bounded."""

from __future__ import annotations


from scripts._qa_common import ROOT, print_result


POLICY = ROOT / "qa_gate_policy.md"
BLOCKING_CLASSES = {"blocking_structure", "blocking_privacy", "blocking_tests", "blocking_substance"}
MAX_BLOCKING_NON_TEST_GATES = 40


def parse_policy() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if not POLICY.exists():
        return rows
    for line in POLICY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| scripts/"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 2:
            rows.append((cells[0], cells[1]))
    return rows


def main() -> None:
    errors: list[str] = []
    rows = parse_policy()
    if not rows:
        errors.append("qa_gate_policy.md ne contient aucun script classé")
    unknown = [(script, klass) for script, klass in rows if klass not in BLOCKING_CLASSES and klass not in {"informational_metric", "legacy"}]
    for script, klass in unknown:
        errors.append(f"{script}: classe inconnue {klass}")
    missing = [script for script, _ in rows if not (ROOT / script).exists()]
    for script in missing:
        errors.append(f"{script}: script absent")

    blocking_non_tests = [script for script, klass in rows if klass in BLOCKING_CLASSES and klass != "blocking_tests"]
    if len(blocking_non_tests) > MAX_BLOCKING_NON_TEST_GATES:
        errors.append(
            f"{len(blocking_non_tests)} gates bloquants hors tests (> {MAX_BLOCKING_NON_TEST_GATES})"
        )
    if "scripts/check_substance_anchors.py" not in {script for script, _ in rows}:
        errors.append("juge de substance absent de qa_gate_policy.md")

    print(f"{len(blocking_non_tests)} gates bloquants hors tests documentés.")
    print_result("check_gate_policy_consistency", errors)


if __name__ == "__main__":
    main()
