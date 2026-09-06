"""Vérification indépendante du contenu ajouté pour l'exigence 2026 C7.

Tout authoring doit être vérifié, pas seulement relu. Les blocs
`% BEGIN-VERIFY` des cinq objets sont extraits du `.tex` lui-même et exécutés :
la propriété générale est prouvée symboliquement, les exemples numériques sont
recalculés, et l'appariement exercice/corrigé est contrôlé.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dimension_mathematics as maths  # noqa: E402

CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE"
OBJECTS = {
    "cours": "cours/16_C7_somme_produit_racines.tex",
    "EX-101": "exercices/1SPE-SECDEG-EX-101.tex",
    "EX-102": "exercices/1SPE-SECDEG-EX-102.tex",
    "CO-101": "corriges/1SPE-SECDEG-CO-101.tex",
    "CO-102": "corriges/1SPE-SECDEG-CO-102.tex",
}
PAIRS = (("EX-101", "CO-101"), ("EX-102", "CO-102"))


def _meta(relative: str) -> dict:
    first = (CHAPTER / relative).read_text(encoding="utf-8").split("\n", 1)[0]
    return json.loads(first[len("% META:"):])


@pytest.mark.parametrize("name,relative", sorted(OBJECTS.items()))
def test_every_new_object_passes_its_own_oracle(name: str, relative: str) -> None:
    block = maths.VERIFY_BLOCK.search((CHAPTER / relative).read_text(encoding="utf-8"))
    assert block, f"{name}: aucun bloc % BEGIN-VERIFY"
    program = maths.extract_program(block.group(1))
    assertions = [line for line in program if line.strip().startswith("assert")]
    assert assertions, f"{name}: bloc sans assertion"
    ok, detail = maths._run_assertions(program)
    assert ok, f"{name}: {detail}"


def test_the_general_property_is_proved_symbolically() -> None:
    """Les exemples numériques ne suffisent pas : la propriété est générale."""
    from sympy import expand, simplify, symbols

    x, a, x1, x2 = symbols("x a x1 x2")
    developed = expand(a * (x - x1) * (x - x2))
    assert simplify(developed.coeff(x, 1) + a * (x1 + x2)) == 0
    assert simplify(developed.coeff(x, 0) - a * x1 * x2) == 0


def test_two_roots_do_not_determine_the_function() -> None:
    """Le point que vise l'exigence 2026 : a reste libre."""
    from sympy import Rational, symbols

    x = symbols("x")
    for coefficient in (1, -3, Rational(1, 2), 7):
        candidate = coefficient * (x - 2) * (x - 3)
        assert candidate.subs(x, 2) == 0 and candidate.subs(x, 3) == 0
        assert candidate.expand() != (x - 2) * (x - 3).expand() or coefficient == 1


@pytest.mark.parametrize("exercise,correction", PAIRS)
def test_no_exercise_correction_drift(exercise: str, correction: str) -> None:
    exercise_meta = _meta(OBJECTS[exercise])
    correction_meta = _meta(OBJECTS[correction])
    assert correction_meta["exercice_ref"] == exercise_meta["id"]
    assert exercise_meta["corrige_tex"].endswith(Path(OBJECTS[correction]).name)
    assert sorted(exercise_meta["capacites_codes"]) == sorted(
        correction_meta["capacites_codes"]
    )
    assert sorted(exercise_meta["capacites"]) == sorted(correction_meta["capacites"])


def test_the_new_objects_declare_the_2026_capacity() -> None:
    for name in ("EX-101", "CO-101"):
        assert "1SPE-SECOND-DEGRE-2026-C2" in _meta(OBJECTS[name])["capacites"]
    assert _meta(OBJECTS["cours"])["capacites_codes"] == ["C7"]


def test_no_object_claims_a_human_approved_status() -> None:
    """Aucun agent n'écrit `approved` : le statut reste réservé à l'humain."""
    for relative in OBJECTS.values():
        assert _meta(relative)["status"] == "generated"


def test_the_official_requirement_is_now_covered() -> None:
    import build_dimension_regulation as regulation

    uncovered = [
        finding["target"] for finding in regulation.build()["findings"]
        if finding["code"] == "OFFICIAL_REQUIREMENT_UNCOVERED"
    ]
    assert "1SPE::1SPE-SECOND-DEGRE-2026-C2" not in uncovered
    assert uncovered == []
