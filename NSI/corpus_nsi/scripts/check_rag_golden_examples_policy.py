#!/usr/bin/env python3
"""Ensure pilot sequences remain golden examples, not internal coverage proof."""

from __future__ import annotations



from scripts import ingest_nsi_corpus
from scripts._qa_common import ROOT, print_result


PILOT_PREFIXES = ("premiere/sequences/", "terminale/sequences/")


def main() -> None:
    errors: list[str] = []
    source_dirs = {path.relative_to(ROOT).as_posix() for path in ingest_nsi_corpus.SOURCE_DIRS}
    for prefix in ("premiere/sequences", "terminale/sequences"):
        if prefix in source_dirs:
            errors.append(f"{prefix}/ ne doit pas être indexé dans nsi_corpus")

    for rel in ("coverage.md", "coverage_sources.md", "programme_matrix_premiere.md", "programme_matrix_terminale.md"):
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for prefix in PILOT_PREFIXES:
            if prefix in text:
                errors.append(f"{rel}: preuve pilote {prefix} encore utilisée dans la couverture")

    config = (ROOT / "rag_config.example.yml").read_text(encoding="utf-8", errors="replace")
    if "nsi_golden_examples" not in config:
        errors.append("rag_config.example.yml doit documenter nsi_golden_examples")
    print_result("check_rag_golden_examples_policy", errors)


if __name__ == "__main__":
    main()
