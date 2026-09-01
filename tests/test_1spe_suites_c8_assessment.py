"""C8 doit etre EVALUEE, pas seulement enseignee.

1SPE-SUITES declare huit capacites. Ses deux devoirs ecrits n'en evaluaient
que sept : C8 -- « reconnaitre intuitivement une limite finie, une limite
infinie ou une absence de limite » -- n'apparaissait nulle part. Le bareme
totalisait pourtant 20 points et toutes les autres verifications passaient :
un total juste ne prouve pas que les bonnes capacites sont couvertes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATIONS = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/evaluations"
VERSIONS = ("A", "B")


def _text(name: str) -> str:
    return (EVALUATIONS / name).read_text(encoding="utf-8")


def _meta(name: str) -> dict:
    return json.loads(_text(name).split("META:", 1)[1].split("\n", 1)[0])


def test_both_written_assessments_evaluate_c8() -> None:
    for version in VERSIONS:
        subject = _text(f"1SPE-SUITES-EV-{version}.tex")
        assert "C8" in subject, version
        assert _meta(f"1SPE-SUITES-EV-{version}.tex")["capacites_codes"][-1] == "C8"
        correction = _meta(f"1SPE-SUITES-EV-{version}-corrige.tex")
        assert correction["capacites_codes"][-1] == "C8"


def test_the_total_stays_twenty_points_in_both_versions() -> None:
    for version in VERSIONS:
        subject = _text(f"1SPE-SUITES-EV-{version}.tex")
        per_exercise = [
            int(value)
            for value in re.findall(
                r"Exercice \d+ \\ifnxVersionProfesseur\\hfill \((\d+) points\)", subject
            )
        ]
        per_question = [
            int(value)
            for value in re.findall(r"\((\d+) pts? — ", subject)
        ]
        assert sum(per_exercise) == 20, version
        assert sum(per_question) == 20, version


def test_c8_carries_the_same_weight_in_a_and_b() -> None:
    """Comparabilite A/B : meme capacite, meme poids, meme geste."""
    weights = []
    for version in VERSIONS:
        subject = _text(f"1SPE-SUITES-EV-{version}.tex")
        block = subject.split("$w_n =", 1)[1]
        weights.append(re.search(r"\((\d+) pts? — ([^)]*)\)", block).groups())
    assert weights[0] == weights[1], weights


def test_the_c8_question_cannot_be_answered_by_monotonicity_alone() -> None:
    """Le piege scientifique a eviter.

    « La suite est croissante donc elle tend vers l'infini » est faux. Les
    deux suites proposees sont croissantes et se comportent differemment :
    l'eleve doit donc regarder autre chose que le sens de variation.
    """
    for version in VERSIONS:
        subject = _text(f"1SPE-SUITES-EV-{version}.tex")
        assert "toutes les deux croissantes" in subject, version
        assert "et non du seul fait que la suite est croissante" in subject, version

        correction = _text(f"1SPE-SUITES-EV-{version}-corrige.tex")
        assert "la croissance seule ne permet donc pas de conclure" in correction
        assert "croît sans borne" in correction
        assert "se rapproche de la valeur finie" in correction


def test_no_formal_limit_apparatus_is_required_at_this_level() -> None:
    """Programme de Premiere : reconnaissance intuitive, pas de formalisme."""
    forbidden = ("epsilon", "\\varepsilon", "pour tout A >", "definition formelle de la limite")
    for version in VERSIONS:
        for name in (f"1SPE-SUITES-EV-{version}.tex", f"1SPE-SUITES-EV-{version}-corrige.tex"):
            lowered = _text(name).lower()
            for token in forbidden:
                assert token.lower() not in lowered, (name, token)
