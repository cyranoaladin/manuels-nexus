"""Un blocage produit doit pouvoir être levé par du travail produit.

Quarante motifs disaient `PRODUCT_P1` alors qu'ils constataient l'absence
d'un reçu de build final — que le protocole interdit de produire avant le
gel. Ces tests exigent que la reclassification se fasse SUR PREUVE : un
livrable requis sans build de développement valide doit rester un blocage
produit, et le dire.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_build_blocker_classification as builds  # noqa: E402

ARTEFACT = ROOT / "audit/BUILD_BLOCKER_CLASSIFICATION.json"
RAW_REASONS = ROOT / "audit/RELEASE_RAW_REASONS.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTEFACT.read_text(encoding="utf-8"))


def test_every_build_reason_is_classified_exactly_once(payload: dict) -> None:
    resume = payload["summary"]
    assert resume["CLASSES_SUM_EQUALS_TOTAL"] is True
    assert (
        resume["DEVELOPMENT_BUILD_BLOCKERS"]
        + resume["FINAL_RELEASE_BUILD_EVIDENCE_BLOCKERS"]
        + resume["OPTIONAL_NOT_APPROVED_BLOCKERS"]
        == resume["BUILD_REASONS_TOTAL"]
    )
    identifiants = [ligne["reason_id"] for ligne in payload["reasons"]]
    assert len(identifiants) == len(set(identifiants))


def test_the_taxonomy_agrees_with_the_evidence(payload: dict) -> None:
    assert payload["summary"]["BUILD_BLOCKER_MISCLASSIFICATION"] == 0
    for ligne in payload["reasons"]:
        assert ligne["declared_taxonomy"] == ligne["expected_taxonomy"], ligne["reason_id"]


def test_development_build_blockers_are_zero_when_all_deliverables_build(
    payload: dict,
) -> None:
    """§21 : zéro si les vingt-quatre livrables ont un build de développement."""
    readiness = json.loads(
        (ROOT / "audit/RELEASE_DELIVERABLE_READINESS.json").read_text(encoding="utf-8")
    )
    if readiness["summary"]["DEVELOPMENT_BUILD_PASS"] == readiness["summary"][
        "REQUIRED_RELEASE_DELIVERABLES"
    ]:
        assert payload["summary"]["DEVELOPMENT_BUILD_BLOCKERS"] == 0


def test_a_required_deliverable_without_a_build_stays_a_product_blocker(
    monkeypatch, tmp_path,
) -> None:
    """Le refus doit venir de la preuve : on retire un PDF, la classe change."""
    import build_development_ready_independent_recheck as recheck

    reel = recheck._engine_pdf_path

    def absent(manuel: str, variante: str):
        if (manuel, variante) == ("1SPE", "eleve"):
            return tmp_path / "MANUEL_1SPE_eleve.pdf"
        return reel(manuel, variante)

    monkeypatch.setattr(recheck, "_engine_pdf_path", absent)
    verdict = builds.classification_for("1SPE", "manuel_eleve")
    assert verdict["required"] is True
    assert verdict["DEVELOPMENT_BUILD_EXISTS"] is False
    assert verdict["CLASSIFICATION"] == "DEVELOPMENT_BUILD"
    assert verdict["expected_taxonomy"] == "PRODUCT_P1"


def test_a_passing_build_without_a_final_receipt_is_certification(
    payload: dict,
) -> None:
    finaux = [
        ligne for ligne in payload["reasons"]
        if ligne["CLASSIFICATION"] == "FINAL_RELEASE_BUILD_EVIDENCE"
    ]
    assert finaux
    for ligne in finaux:
        assert ligne["required"] is True
        assert ligne["DEVELOPMENT_BUILD_EXISTS"] is True
        assert ligne["DEVELOPMENT_BUILD_PASS"] is True
        assert ligne["FINAL_RELEASE_RECEIPT_EXISTS"] is False
        assert ligne["expected_taxonomy"] == "CERTIFICATION_BLOCKER"


def test_an_optional_deliverable_is_a_scope_matter_not_a_product_debt(
    payload: dict,
) -> None:
    optionnels = [
        ligne for ligne in payload["reasons"]
        if ligne["CLASSIFICATION"] == "OPTIONAL_DELIVERABLE_NOT_APPROVED"
    ]
    for ligne in optionnels:
        assert ligne["required"] is False
        assert ligne["requirement_status"] == "PROPOSED_NOT_APPROVED"
        assert ligne["expected_taxonomy"] == "RELEASE_POLICY_BLOCKER"


def test_the_reclassification_produced_no_final_receipt(payload: dict) -> None:
    """§7 : on ne reconstruit toujours pas les reçus finaux."""
    assert all(
        ligne["FINAL_RELEASE_RECEIPT_EXISTS"] is False
        for ligne in payload["reasons"]
    )
    assert "APPROVES_NOTHING" in payload["summary"]


def test_each_build_root_carries_a_single_taxonomy() -> None:
    reasons = json.loads(RAW_REASONS.read_text(encoding="utf-8"))
    par_racine: dict[str, set[str]] = {}
    for entree in reasons["raw_reasons"]:
        par_racine.setdefault(entree["root_cause_id"], set()).add(entree["category"])
    for racine, taxonomies in par_racine.items():
        assert len(taxonomies) == 1, (racine, taxonomies)
