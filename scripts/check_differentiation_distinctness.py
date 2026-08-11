#!/usr/bin/env python3
"""Check that adapted versions are not cosmetic copies of standard supports."""

from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
import re

from scripts._qa_common import ROOT, strip_frontmatter, print_result


SUPPORTS = ROOT / "03_progressions" / "supports"
ADAPT_MARKERS = [
    "aide",
    "donnée fournie",
    "mots utiles",
    "méthode guidée",
    "exercice guidé",
    "question aménagée",
    "aide intégrée",
    "espace de réponse",
    "différenciation",
    "réponses rapides",
    "étape",
    "etape",
    "charge cognitive",
    "guidage",
]


def normalize(text: str) -> str:
    text = strip_frontmatter(text)
    text = re.sub(r"`[^`]+`", " CODE ", text)
    text = re.sub(r"\s+", " ", text.lower())
    return text.strip()


def nearest_standard(version_path: Path) -> Path | None:
    seq = version_path.parent.name
    base = version_path.parent
    candidates = [
        path for path in base.glob(f"{seq}_*.md")
        if "version_amenagee" not in path.name.lower()
        and "version_aménagée" not in path.name.lower()
        and path.name != version_path.name
    ]
    preferred = [path for path in candidates if any(token in path.name.lower() for token in ["td", "tp", "evaluation", "cours"])]
    return (preferred or candidates)[0] if (preferred or candidates) else None


def main() -> None:
    errors: list[str] = []
    checked = 0
    for path in sorted(SUPPORTS.rglob("*version*amenagee*.md")):
        standard = nearest_standard(path)
        if standard is None:
            errors.append(f"{path.relative_to(ROOT)}: support standard introuvable")
            continue
        checked += 1
        adapted_text = path.read_text(encoding="utf-8", errors="replace")
        standard_text = standard.read_text(encoding="utf-8", errors="replace")
        ratio = SequenceMatcher(None, normalize(adapted_text), normalize(standard_text)).ratio()
        marker_count = sum(1 for marker in ADAPT_MARKERS if marker in adapted_text.lower())
        if ratio > 0.86:
            errors.append(
                f"{path.relative_to(ROOT)}: trop proche de {standard.name} (similarité {ratio:.0%})"
            )
        if marker_count < 3:
            errors.append(f"{path.relative_to(ROOT)}: adaptations concrètes insuffisantes")
    print(f"Versions aménagées comparées : {checked}")
    print_result("check_differentiation_distinctness", errors)


if __name__ == "__main__":
    main()
