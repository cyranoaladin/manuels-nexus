"""Le plan d'ecriture prescrit des fonctions, jamais des effectifs.

C'est la difference entre « il manque une situation de transfert a la
capacite C4 » et « il faut deux exercices de plus » : la premiere phrase dit
ce que l'eleve ne peut pas faire, la seconde remplit un compteur. Le mandat
refuse explicitement la seconde.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "audit/EXERCISE_DIVERSITY_BLUEPRINT.json"
VERDICTS = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "diversity_blueprint", ROOT / "scripts/build_exercise_diversity_blueprint.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["diversity_blueprint"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(BLUEPRINT.read_text(encoding="utf-8"))


def test_no_entry_is_written_for_a_counter(payload: dict) -> None:
    interdits = {"increase_count", "satisfy_diversity_metric"}
    for chapitre in payload["chapters"]:
        for entree in chapitre["blueprint"]:
            assert entree["AUTHORING_REASON"] not in interdits
            assert len(entree["AUTHORING_REASON"]) > 40, entree["PEDAGOGICAL_GAP_ID"]


def test_no_entry_prescribes_a_number_of_exercises(payload: dict) -> None:
    """Un motif qui compte des exercices est un quota, meme bien redige."""

    quota = re.compile(
        r"\b(?:deux|trois|quatre|cinq|dix|cinquante|\d+)\s+"
        r"(?:nouveaux?\s+)?(?:exercices?|objets?)",
        re.I,
    )
    for chapitre in payload["chapters"]:
        for entree in chapitre["blueprint"]:
            assert not quota.search(entree["AUTHORING_REASON"]), (
                entree["PEDAGOGICAL_GAP_ID"], entree["AUTHORING_REASON"]
            )


def test_every_entry_answers_a_real_gap(payload: dict) -> None:
    """Une entree de plan sans lacune correspondante serait du remplissage."""

    verdicts = json.loads(VERDICTS.read_text(encoding="utf-8"))
    lacunes = {
        (row["CHAPTER_ID"], analyse["CAPACITY_ID"])
        for row in verdicts["chapters"]
        for analyse in row["per_capacity"]
        if analyse["REAL_DIVERSITY_GAP"]
    }
    for chapitre in payload["chapters"]:
        for entree in chapitre["blueprint"]:
            assert (chapitre["CHAPTER_ID"], entree["CAPACITY_ID"]) in lacunes


def test_a_sufficient_capacity_never_enters_the_plan(payload: dict) -> None:
    verdicts = json.loads(VERDICTS.read_text(encoding="utf-8"))
    suffisantes = {
        (row["CHAPTER_ID"], analyse["CAPACITY_ID"])
        for row in verdicts["chapters"]
        for analyse in row["per_capacity"]
        if not analyse["REAL_DIVERSITY_GAP"]
    }
    planifiees = {
        (chapitre["CHAPTER_ID"], entree["CAPACITY_ID"])
        for chapitre in payload["chapters"]
        for entree in chapitre["blueprint"]
    }
    assert not (planifiees & suffisantes)


def test_the_prescribed_role_is_one_the_capacity_lacks(payload: dict) -> None:
    for chapitre in payload["chapters"]:
        for entree in chapitre["blueprint"]:
            assert entree["EXERCISE_ROLE"] not in entree["CURRENT_FUNCTIONS"], (
                entree["PEDAGOGICAL_GAP_ID"]
            )


def test_a_capacity_already_served_asks_for_at_most_one_object(payload: dict) -> None:
    """Une capacite deja pourvue ne reclame qu'UNE fonction manquante.

    Seule une capacite sans aucun exercice en reclame deux -- le geste de
    base et un registre de transfert -- parce qu'il n'y a rien a completer.
    """

    for chapitre in payload["chapters"]:
        par_capacite: dict[str, int] = {}
        for entree in chapitre["blueprint"]:
            par_capacite[entree["CAPACITY_ID"]] = (
                par_capacite.get(entree["CAPACITY_ID"], 0) + 1
            )
            if entree["CURRENT_EXERCISES"] > 0:
                assert par_capacite[entree["CAPACITY_ID"]] == 1, (
                    chapitre["CHAPTER_ID"], entree["CAPACITY_ID"]
                )


def test_a_project_assessed_chapter_gets_no_exercise_plan(payload: dict) -> None:
    """Ses capacites n'ont pas d'exercice par decision, pas par manque."""

    verdicts = json.loads(VERDICTS.read_text(encoding="utf-8"))
    projets = {
        row["CHAPTER_ID"] for row in verdicts["chapters"]
        if row["ASSESSMENT_MODE"] == "PROJECT_ASSESSMENT"
    }
    assert projets
    assert not projets & {c["CHAPTER_ID"] for c in payload["chapters"]}


def test_the_committed_plan_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0
