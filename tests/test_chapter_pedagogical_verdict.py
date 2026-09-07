"""La revue pedagogique derive ses verdicts, elle ne les affirme pas.

Le nombre d'exercices ne dit rien : c'est la lecon du remplissage. Ce que ce
producteur mesure, ce sont les quatre couvertures que le critere qualitatif
exige -- application directe, variation, raisonnement, synthese -- lues sur
les competences et les parcours que chaque exercice DECLARE.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "pedagogical_verdict", ROOT / "scripts/build_chapter_pedagogical_verdict.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["pedagogical_verdict"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_every_chapter_receives_a_verdict(payload: dict) -> None:
    assert payload["summary"]["CHAPTERS_AUDITED"] == 14
    for row in payload["chapters"]:
        assert row["PEDAGOGICAL_VERDICT"] in {
            "STRONG", "ADEQUATE", "WEAK", "UNUSABLE"
        }


def test_the_verdict_is_the_worst_axis_not_an_average(payload: dict) -> None:
    """Une moyenne noierait un axe faible dans cinq axes forts.

    Un chapitre dont les corriges manquent n'est pas « globalement adequat » :
    il est inutilisable sur ce point, et c'est ce point qui decide.
    """

    ordre = {"STRONG": 3, "ADEQUATE": 2, "WEAK": 1, "UNUSABLE": 0}
    axes = (
        "COURSE_COMPLETENESS", "EXERCISE_DIVERSITY", "DIFFICULTY_PROGRESSION",
        "CORRECTION_QUALITY", "ASSESSMENT_QUALITY", "REMEDIATION",
    )
    for row in payload["chapters"]:
        attendu = min((row[axe] for axe in axes), key=lambda v: ordre[v])
        assert row["PEDAGOGICAL_VERDICT"] == attendu, row["CHAPTER_ID"]


def test_full_coverage_alone_never_earns_a_strong_verdict(producer) -> None:
    """Une capacite servie par un seul exercice n'est pas entrainee.

    C'est la regle qui empeche de relire « chaque capacite a un exercice »
    comme « le chapitre est riche ».
    """

    for row in json.loads(ARTIFACT.read_text(encoding="utf-8"))["chapters"]:
        direct, total = row["coverage"]["DIRECT_APPLICATION_COVERAGE"].split("/")
        variation, _ = row["coverage"]["VARIATION_COVERAGE"].split("/")
        if int(direct) == int(total) and int(variation) < int(total) * 0.5:
            assert row["EXERCISE_DIVERSITY"] in {"WEAK", "UNUSABLE"}, row["CHAPTER_ID"]


def test_the_weak_chapters_are_named_with_their_uncovered_capacities(
    payload: dict,
) -> None:
    """Un verdict sans la liste de ce qui manque n'est pas actionnable."""

    for row in payload["chapters"]:
        if row["PEDAGOGICAL_VERDICT"] in {"WEAK", "UNUSABLE"}:
            manques = row["uncovered"]
            assert any(manques.values()), row["CHAPTER_ID"]


def test_the_committed_verdict_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0
