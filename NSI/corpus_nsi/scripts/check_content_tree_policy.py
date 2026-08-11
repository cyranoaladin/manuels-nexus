#!/usr/bin/env python3
"""Check that production content uses the canonical supports tree."""

from __future__ import annotations


from scripts._qa_common import ROOT, print_result


POLICY = ROOT / "content_tree_policy.md"
SUPPORTS = ROOT / "03_progressions" / "supports"
PILOT_TREES = [ROOT / "premiere" / "sequences", ROOT / "terminale" / "sequences"]


def main() -> None:
    errors: list[str] = []
    if not POLICY.exists():
        errors.append("content_tree_policy.md absent")
    if not SUPPORTS.exists():
        errors.append("03_progressions/supports absent")

    coverage = ROOT / "coverage.md"
    if coverage.exists() and "03_progressions/supports/" not in coverage.read_text(encoding="utf-8", errors="replace"):
        errors.append("coverage.md ignore encore 03_progressions/supports/")

    for tree in PILOT_TREES:
        if not tree.exists():
            continue
        for path in sorted(tree.rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".json", ".yaml", ".yml", ".py"}:
                continue
            if path.name.startswith("_") or path.name == "quality_audit_s01.md":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "canonical_production: true" in text or "production_canon: true" in text:
                errors.append(f"{path.relative_to(ROOT)} se déclare production canonique hors supports/")

    print_result("check_content_tree_policy", errors)


if __name__ == "__main__":
    main()
