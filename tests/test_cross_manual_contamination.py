"""La population canonique de la contamination se recalcule et se defend.

Un registre qui affirme un nombre sans le rederiver n'est qu'une opinion. Ces
tests verifient que la population se reconstruit depuis les sources, que la
lignee n'est jamais inventee, et que la source d'un groupe n'est pas condamnee
parce qu'on l'a recopiee ailleurs.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/CROSS_MANUAL_CONTAMINATION.json"
MATRIX = ROOT / "audit/CROSS_MANUAL_CONTAMINATION_MATRIX.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "cmc", ROOT / "scripts/build_cross_manual_contamination.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["cmc"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def matrix() -> dict:
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def test_the_committed_population_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_the_normalisation_is_proven_in_both_directions(payload: dict) -> None:
    proof = payload["normalization_proof"]
    assert proof["CLONE_NORMALIZATION_FALSE_POSITIVES"] == 0
    assert proof["CLONE_NORMALIZATION_FALSE_NEGATIVES"] == 0
    assert payload["CURRENT_CLONE_LEDGER_USES_CORRECT_NORMALIZATION"] is True


def test_every_reported_number_is_recomputed_or_explained(payload: dict) -> None:
    """Aucun nombre repris : chaque ecart vient d'une definition nommee."""

    reconciliation = payload["reconciliation"]
    assert reconciliation["UNEXPLAINED_DELTAS"] == []
    for row in reconciliation["metrics"]:
        assert row["recomputed_now"] is not None
        if not row["agrees"]:
            assert row["definitional_difference"], row["metric"]


def test_the_whole_collection_is_scanned(payload: dict) -> None:
    assert payload["summary"]["UNSCANNED_CANONICAL_CHAPTERS"] == 0
    assert payload["unscanned_canonical_chapters"] == []


def test_a_lineage_is_never_invented(payload: dict) -> None:
    """Quand l'historique ne tranche pas, on ne designe pas d'original.

    Six groupes de satellites et un groupe de corriges arrivent chacun dans un
    seul commit : l'ordre des chemins ne prouverait rien, et designer le
    premier par ordre alphabetique fabriquerait une lignee.
    """

    for group in payload["groups"]:
        if group["lineage_status"] == "CANONICAL_SOURCE_OBJECT":
            assert group["lineage_rule"] in {
                "EARLIEST_INTRODUCTION",
                "CORRECTION_FOLLOWS_ITS_EXERCISE",
            }
            assert group["canonical_source"]["introduced_commit"]
        else:
            assert group["canonical_source"] is None
            assert group["lineage_rule"] in {
                "ALL_MEMBERS_INTRODUCED_BY_THE_SAME_COMMIT",
                "ALL_MEMBERS_ANSWER_CONTAMINATED_EXERCISES",
                "EARLIEST_INTRODUCTION_IS_A_TIE",
                "COMMIT_ORDER_UNAVAILABLE",
                "NO_INTRODUCTION_RECORDED",
            }


def test_the_canonical_source_is_never_counted_as_contaminated(
    payload: dict, matrix: dict
) -> None:
    """Un corps n'est pas illegitime chez lui parce qu'on l'a copie ailleurs."""

    sources = {
        group["canonical_source"]["path"]
        for group in payload["groups"]
        if group["canonical_source"]
    }
    contamines = {
        row["OBJECT_PATH"] for row in matrix["rows"] if not row["IS_CANONICAL_SOURCE"]
    }
    assert sources & contamines == set()
    assert len(contamines) == payload["summary"]["CROSS_MANUAL_CONTAMINATION_OBJECTS"]


def test_the_matrix_names_every_column_the_decision_requires(matrix: dict) -> None:
    exigees = {
        "SOURCE_BODY_DIGEST", "ORIGINAL_LINEAGE", "TARGET_MANUAL",
        "TARGET_CHAPTER", "OBJECT_ID", "OBJECT_TYPE", "CAPACITY", "STATUS",
        "INTRODUCED_COMMIT",
    }
    assert exigees <= set(matrix["columns"])
    for row in matrix["rows"]:
        for colonne in exigees:
            assert colonne in row


def test_the_finding_stays_a_publication_blocker(payload: dict) -> None:
    """Ne pas le reclassifier en gouvernance : l'eleve le voit sur la page."""

    assert payload["finding"] == "CROSS_MANUAL_PEDAGOGICAL_CONTAMINATION"
    assert payload["publication_blocker"] is True
    assert payload["approves_nothing"] is True
    assert payload["root_cause_id"] == "533d1919_SYNTHETIC_CROSS_MANUAL_FILLER"


def test_a_contaminated_object_is_never_its_own_lineage(payload: dict) -> None:
    for group in payload["groups"]:
        source = group["canonical_source"]
        if not source:
            continue
        assert sum(
            1 for m in group["members"] if m["path"] == source["path"]
        ) == 1
