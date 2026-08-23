"""Régression globale contre trois corruptions LaTeX tronquant l'antislash."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapitres"


def test_aucune_commande_latex_connue_ne_perd_son_antislash() -> None:
    corruptions = []
    pattern = re.compile(r"(?m)^[ \t]*(?:eq|ormalfont|ewline)\b")
    for path in sorted(CHAPTERS.rglob("*.tex")):
        text = path.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            line = text[: match.start()].count("\n") + 1
            corruptions.append(f"{path.relative_to(ROOT)}:{line}:{match.group(0).strip()}")
    assert corruptions == []
