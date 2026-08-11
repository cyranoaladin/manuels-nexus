#!/usr/bin/env python3
"""Gate: each evaluation file must have a matching barème file (same slug/variant).

Scans 03_progressions/supports/ for evaluation_*.md files and verifies
that a corresponding bareme_*.md file exists with the same suffix.

Pairing rules (fail-closed, no inference):
1. Exact slug match: Pxx_evaluation_SLUG.md ↔ Pxx_bareme_SLUG.md
2. Frontmatter declaration: evaluation has ``bareme: <filename>``
3. Explicit convention map below (each entry justified from RM5-1 triage)

Exit 0 if all pairs exist, exit 1 with details of unpaired evaluations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SUPPORTS = ROOT / "03_progressions" / "supports"

# Explicit slug-mismatch conventions (RM5-1 triage, each justified).
# Key: evaluation filename, Value: (barème filename, justification).
EXPLICIT_PAIRINGS: dict[str, tuple[str, str]] = {
    "P08_evaluation_html_css_dom.md": (
        "P08_bareme_web_http_dom_formulaires.md",
        "même 9 capacités P-IHM-01A..04C, slug historique divergent",
    ),
    "P08_evaluation_http_get_post_formulaires.md": (
        "P08_bareme_web_http_dom_formulaires.md",
        "même 9 capacités P-IHM-01A..04C, variante TP du même thème",
    ),
    "T10_evaluation_sql_insert_update_delete.md": (
        "T10_bareme_sql_select_where_join.md",
        "même 8 capacités T-BDD-03A..03H, slug ne reflète pas le scope complet",
    ),
}


def _extract_bareme_field(path: Path) -> str | None:
    """Extract ``bareme:`` field from YAML frontmatter, if present."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    try:
        fm = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return None
    if not isinstance(fm, dict):
        return None
    bareme = fm.get("bareme")
    return str(bareme) if bareme else None


def main() -> int:
    unique_evals = sorted(set(SUPPORTS.rglob("*_evaluation_*.md")))

    unpaired: list[str] = []
    for eval_path in unique_evals:
        name = eval_path.name
        # Extract: Pxx_evaluation_slug.md or Txx_evaluation_slug.md
        m = re.match(r"(\w+)_evaluation_(.+)\.md", name, re.I)
        if not m:
            continue
        prefix, slug = m.group(1), m.group(2)

        # Rule 1: exact slug match
        bareme_name = f"{prefix}_bareme_{slug}.md"
        bareme_path = eval_path.parent / bareme_name
        if bareme_path.exists():
            continue
        # Case variant
        bareme_alt = eval_path.parent / f"{prefix}_Bareme_{slug}.md"
        if bareme_alt.exists():
            continue

        # Rule 2: frontmatter ``bareme:`` declaration
        declared = _extract_bareme_field(eval_path)
        if declared and (eval_path.parent / declared).exists():
            continue

        # Rule 3: explicit convention map
        if name in EXPLICIT_PAIRINGS:
            conv_bareme, _justification = EXPLICIT_PAIRINGS[name]
            if (eval_path.parent / conv_bareme).exists():
                continue

        rel = eval_path.relative_to(ROOT)
        unpaired.append(f"  {rel} → barème manquant: {bareme_name}")

    if unpaired:
        print(f"check_eval_bareme_pairing: FAIL ({len(unpaired)} évaluation(s) sans barème)")
        for u in unpaired:
            print(u)
        return 1

    print(f"check_eval_bareme_pairing: PASS ({len(unique_evals)} paire(s) vérifiées)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
