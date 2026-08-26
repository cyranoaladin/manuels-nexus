"""Régressions du contrat LaTeX du chapitre 1SPE-SUITES."""

from __future__ import annotations

import re
from pathlib import Path


CHAPTER = Path(__file__).resolve().parents[1] / "chapitres" / "1SPE-SUITES"


def source(relative_path: str) -> str:
    text = (CHAPTER / relative_path).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", text)


def test_cours_limites_n_utilise_pas_un_environnement_absent_du_build_chapitre() -> None:
    limits_course = source("cours/17_C8_limites_intuitives.tex")

    assert r"\begin{remarqueV}" not in limits_course
    assert r"\end{remarqueV}" not in limits_course
    assert r"\erreurFrequente{" in limits_course
