"""`approved` dans un META n'est pas une approbation, et 50 n'est pas une loi.

Deux verites de gouvernance, chacune verifiable : d'ou vient un statut, et
d'ou vient un nombre. Les confondre avec des faits acquis a coute neuf cents
objets.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APPROVAL = ROOT / "audit/CONTAMINATED_APPROVAL_AUDIT.json"
POLICY = ROOT / "audit/FIFTY_EXERCISES_POLICY_ORIGIN.json"


def _module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def approvals() -> dict:
    return json.loads(APPROVAL.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def test_every_contaminated_approval_is_classified(approvals: dict) -> None:
    summary = approvals["summary"]
    assert summary["UNKNOWN_APPROVAL_PROVENANCE"] == 0
    assert summary["CLASSES_SUM_EQUALS_TOTAL"] is True


def test_a_defect_qualification_is_never_read_as_an_approval(
    approvals: dict,
) -> None:
    """464 dispositions nomment ces objets -- toutes qualifient un DEFAUT.

    Les lire comme des approbations transformerait une dette ouverte en feu
    vert.
    """

    # Le compteur tombe a zero une fois les objets contamines retires : ce
    # n'est pas la preuve qui disparait, c'est la population.
    if approvals["records"]:
        assert approvals["summary"]["DEFECT_QUALIFICATIONS_FOUND"] > 0
    for record in approvals["records"]:
        for preuve in record["approval_evidence"]:
            assert preuve["qualifies_a_defect"] is False


def test_no_contaminated_approval_may_be_reused(approvals: dict) -> None:
    """Approuver un exercice d'analyse n'approuve pas son remplacant."""

    assert approvals["summary"]["CONTAMINATED_APPROVAL_REUSED_FOR_NEW_CONTENT"] == 0
    for record in approvals["records"]:
        assert record["reusable_for_replacement_content"] is False
        assert record["invalidated_status"] == "HISTORICAL_INVALIDATED_BY_CONTAMINATION"


def test_the_previous_status_is_preserved_not_erased(approvals: dict) -> None:
    for record in approvals["records"]:
        assert record["declared_status"]
        assert "introduced_commit" in record


def test_the_committed_approval_audit_matches_the_producer() -> None:
    assert _module("approval_audit", "scripts/build_contaminated_approval_audit.py").main(
        ["--check"]
    ) == 0


def test_no_release_gate_enforces_fifty_exercises(policy: dict) -> None:
    """Le nombre n'est impose par aucun test ni aucun producteur bloquant."""

    assert policy["summary"]["RELEASE_GATES_ENFORCING_FIFTY"] == 0
    assert policy["release_gates_enforcing_fifty"] == []


def test_the_prior_human_directive_is_reported_not_hidden(policy: dict) -> None:
    """Une directive humaine anterieure existe : on la remonte telle quelle.

    La taire pour justifier de ne pas ecrire serait aussi malhonnete que de
    fabriquer du volume pour la satisfaire.
    """

    owner = [
        trace for trace in policy["traces"]
        if trace["classification"] == "EXPLICIT_RELEASE_OWNER_REQUIREMENT"
    ]
    assert owner, "la directive du prompt de mission doit rester visible"
    assert all(trace["verified_in_tree"] for trace in owner)
    # Depuis la decision du 2026-09-07, le statut canonique est nomme par le
    # Release Owner lui-meme ; la directive reste visible et non appliquee.
    assert policy["summary"]["FIFTY_EXERCISES_RELEASE_REQUIREMENT"] == (
        "SUPERSEDED_EDITORIAL_VOLUME_TARGET"
    )
    assert policy["summary"]["HISTORICAL_REQUIREMENT_EXISTED"] is True
    assert "jamais la cible" in policy["current_authority"]


def test_the_committed_policy_origin_matches_the_producer() -> None:
    assert _module(
        "policy_origin", "scripts/build_fifty_exercises_policy_origin.py"
    ).main(["--check"]) == 0
