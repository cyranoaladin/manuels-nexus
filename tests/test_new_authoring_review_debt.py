"""Le contenu neuf est du contenu a risque, et il le reste jusqu'a relecture.

Deux cent six objets ont ete ecrits pour remplacer ce que la contamination
avait pris. Leurs blocs VERIFY prouvent une exactitude CALCULABLE ; ils ne
prouvent ni l'adequation au programme, ni la qualite de l'enonce, ni le
niveau, ni le style. Compter un oracle vert comme une revue editoriale
refarait, en plus petit, l'erreur qui a produit le remplissage.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/NEW_AUTHORING_REVIEW_DEBT.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "new_authoring", ROOT / "scripts/build_new_authoring_review_debt.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["new_authoring"] = module
    spec.loader.exec_module(module)
    return module


def test_new_content_is_never_counted_as_reviewed(payload: dict) -> None:
    """Un oracle vert n'est pas une relecture."""

    summary = payload["summary"]
    assert summary["NEW_AUTHORING_REVIEW_PENDING"] == summary["NEW_AUTHORING_OBJECTS"]
    assert payload["human_review_required"] is True
    assert payload["approves_nothing"] is True
    for entry in payload["entries"]:
        assert entry["editorial_review"] == "EDITORIAL_REVIEW_PENDING"


def test_no_new_object_is_declared_approved(payload: dict) -> None:
    """§21 : le contenu neuf ne prend jamais `approved` tout seul."""

    for entry in payload["entries"]:
        assert entry["declared_status"] in {"generated", None}, entry["path"]


def test_every_new_object_carries_an_executed_oracle(payload: dict) -> None:
    summary = payload["summary"]
    assert summary["ORACLE_FAILURES"] == 0
    assert summary["OBJECTS_WITHOUT_ORACLE"] == 0
    assert summary["ORACLE_VERIFIED"] == summary["NEW_AUTHORING_OBJECTS"]


def test_the_new_content_did_not_recreate_the_defect(payload: dict) -> None:
    """Un exercice neuf identique a un autre serait le defaut d'origine
    reintroduit par la main qui le repare."""

    assert payload["summary"]["NEW_AUTHORING_EXACT_CLONES"] == 0
    assert payload["exact_clones"] == []


def test_capacity_proof_is_inherited_through_the_declared_reference(
    payload: dict,
) -> None:
    """Un corrige herite de la preuve de SON exercice, nomme dans son META.

    L'heritage par ressemblance d'identifiant serait le meme raccourci qui a
    laisse passer la contamination.
    """

    assert payload["summary"]["CAPACITY_NOT_PROVEN"] == 0
    par_chemin = {e["path"]: e for e in payload["entries"]}
    for entry in payload["entries"]:
        if entry["role"] != "corriges":
            continue
        if entry["capacity_semantically_proven"] is None:
            continue
        assert entry["declared_capacities"], entry["path"]


def test_every_new_exercise_has_an_answer(payload: dict) -> None:
    assert payload["summary"]["ANSWER_COVERAGE_MISSING"] == 0


def test_the_committed_ledger_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0
