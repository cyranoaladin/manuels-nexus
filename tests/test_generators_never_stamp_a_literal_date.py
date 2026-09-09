"""Un generateur ne doit pas graver une date de generation litterale.

Une date ecrite en dur est recopiee identique a chaque execution : l'artefact
finit par dater un contenu qu'il n'a pas observe. Le style inventory affichait
ainsi « Généré le: 2026-08-15 » sur un balayage du 9 septembre, et deux
generateurs estampillaient « 2026-08-23 » des mesures courantes.

La provenance se porte par le commit et les empreintes de source observees,
jamais par une constante.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SCRIPTS = sorted((Path(__file__).resolve().parents[1] / "scripts").glob("*.py"))
LITERAL_DATE = re.compile(
    r'"(?:generated_on|generated_at|generation_date|date_generation)"\s*:\s*"20\d\d-\d\d-\d\d"'
    r'|Généré le\s*:?\s*20\d\d-\d\d-\d\d'
)


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_no_generator_stamps_a_literal_generation_date(script: Path) -> None:
    matches = LITERAL_DATE.findall(script.read_text(encoding="utf-8"))
    assert not matches, f"{script.name} grave une date de generation : {matches}"
