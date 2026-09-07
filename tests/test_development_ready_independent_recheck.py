"""Une seconde vérification n'a de valeur que si elle peut contredire.

`DEVELOPMENT_READY = 24/24` est produit par un compteur qui lit des artefacts.
La contre-vérification interroge les moteurs d'assemblage, ouvre les PDF et
ré-exécute les oracles. Ces tests exigent qu'elle sache dire non : un oracle
faux, un PDF tronqué, un chapitre vide ou un désaccord avec le compteur
primaire doivent tous la faire virer au rouge.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_development_ready_independent_recheck as recheck  # noqa: E402


@pytest.fixture(scope="module")
def payload():
    return recheck.build()


# --------------------------------------------------------------------------
# Le constat lui-même
# --------------------------------------------------------------------------
def test_recheck_is_satisfied_at_twenty_four(payload) -> None:
    summary = payload["summary"]
    assert summary["REQUIRED_RELEASE_DELIVERABLES"] == 24
    assert summary["DEVELOPMENT_READY_INDEPENDENT_RECHECK"] == 24
    assert summary["RECHECK_SATISFIED"] is True


def test_recheck_agrees_with_the_primary_counter(payload) -> None:
    agreement = payload["agreement_with_primary"]
    assert agreement["primary_artifact_present"] is True
    assert agreement["DISAGREEMENTS"] == 0
    assert agreement["PRIMARY_DEVELOPMENT_READY"] == \
        agreement["INDEPENDENT_DEVELOPMENT_READY"]


def test_oracles_are_really_re_executed(payload) -> None:
    """Une contre-vérification qui n'exécute rien ne vérifie rien."""
    summary = payload["summary"]
    assert summary["ORACLE_ASSERTIONS_RE_EXECUTED"] > 10_000
    assert summary["ORACLE_FAILURES"] == 0
    assert summary["MISSING_ORACLE"] == 0


def test_the_recheck_approves_nothing(payload) -> None:
    assert payload["summary"]["APPROVES_NOTHING"] is True
    assert "approved" not in json.dumps(payload).lower().split("approves_nothing")[0]


def test_no_release_readiness_is_claimed(payload) -> None:
    """§24 : le rouge de la release reste sain, la contre-vérification n'y touche pas."""
    assert "RELEASE_READY" not in payload["summary"]
    for row in payload["deliverables"]:
        assert "release_ready" not in row
        assert "release_ready_independent" not in row
    assert "ni `RELEASE_READY`" in payload["authority_note"]


# --------------------------------------------------------------------------
# Falsifiabilité : chaque axe doit savoir refuser
# --------------------------------------------------------------------------
def test_a_false_oracle_is_caught() -> None:
    ok, reason, count = recheck._run_verify("x = symbols('x')\nassert x + x == 3 * x")
    assert ok is False
    assert count == 1
    assert "assertion" in reason


def test_a_true_oracle_passes() -> None:
    ok, reason, count = recheck._run_verify("x = symbols('x')\nassert x + x == 2 * x")
    assert (ok, reason, count) == (True, "", 1)


def test_a_block_that_does_not_compile_is_not_a_silent_pass() -> None:
    ok, reason, count = recheck._run_verify("assert (")
    assert ok is False
    assert reason.startswith("SyntaxError")
    assert count == 0


def test_a_truncated_pdf_is_refused(tmp_path) -> None:
    broken = tmp_path / "tronque.pdf"
    broken.write_bytes(b"%PDF-1.5\nrien du tout\n")
    evidence = recheck._pdf_evidence(broken)
    assert evidence["verdict"] is False
    assert evidence["trailer_ok"] is False


def test_an_absent_pdf_is_refused(tmp_path) -> None:
    evidence = recheck._pdf_evidence(tmp_path / "absent.pdf")
    assert evidence["verdict"] is False
    assert evidence["reason"] == "PDF absent"


def test_a_real_pdf_is_accepted(payload) -> None:
    """Le refus doit venir du défaut, pas d'un lecteur qui refuse tout."""
    for row in payload["deliverables"]:
        evidence = row["development_build"]
        assert evidence["verdict"] is True, row["deliverable_id"]
        assert evidence["pages"] > 0
        assert evidence["first_page_has_text"] is True


def test_an_empty_chapter_makes_the_content_axis_fail(monkeypatch) -> None:
    original = recheck._engine_objects

    def crevasse(manual: str, variant: str):
        collected = original(manual, variant)
        first = sorted(collected)[0]
        collected[first] = []
        return collected

    monkeypatch.setattr(recheck, "_engine_objects", crevasse)
    inventory = json.loads(
        (ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    axis = recheck._content_axis(
        "TCOMPL", "eleve", "math:manual:TCOMPL:eleve", inventory)
    assert axis["verdict"] is False
    assert axis["chapters_uncovered"]


def test_a_wrong_declared_output_name_makes_the_target_axis_fail() -> None:
    axis = recheck._build_target_axis("TCOMPL", "eleve", "MANUEL_AUTRE_eleve.pdf")
    assert axis["verdict"] is False


def test_the_documented_naming_normalisation_is_not_a_defect() -> None:
    """Le périmètre écrit `TSPE_2026_2027`, le moteur `TSPE_2026-2027`."""
    axis = recheck._build_target_axis(
        "TSPE_2026_2027", "eleve", "MANUEL_TSPE_2026_2027_eleve.pdf")
    assert axis["verdict"] is True
    assert axis["naming_normalisation_applied"] is True
    assert axis["engine_output"] == "MANUEL_TSPE_2026-2027_eleve.pdf"


def test_an_unknown_variant_makes_the_assembly_axis_fail() -> None:
    inventory = json.loads(
        (ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    axis = recheck._assembly_axis(
        "TCOMPL", "affiches", "math:manual:TCOMPL:affiches", inventory)
    assert axis["verdict"] is False
    assert axis["variant_known_to_engine"] is False


def test_an_unmapped_programme_atom_makes_the_programme_axis_fail() -> None:
    matrix = {"chapters": [{
        "manual": "TCOMPL",
        "chapter": "TCOMPL-FICTIF",
        "programme": {"status": "GAP", "missing": 2, "wrong_year": 0},
        "pedagogical_role_coverage": {"missing": 0},
    }]}
    axis = recheck._programme_axis("TCOMPL", matrix)
    assert axis["verdict"] is False
    assert axis["unmapped_official_atoms"] == 2


def test_a_real_pedagogical_gap_makes_the_programme_axis_fail() -> None:
    """§22 : une lacune pédagogique réelle est un défaut de programme."""
    matrix = {"chapters": [{
        "manual": "TCOMPL",
        "chapter": "TCOMPL-FICTIF",
        "programme": {"status": "COMPLETE", "missing": 0, "wrong_year": 0},
        "pedagogical_role_coverage": {"missing": 3},
    }]}
    axis = recheck._programme_axis("TCOMPL", matrix)
    assert axis["verdict"] is False
    assert axis["real_pedagogical_gaps"] == 3


def test_a_disagreement_with_the_primary_is_reported(monkeypatch, tmp_path) -> None:
    primary = {
        "summary": {"DEVELOPMENT_READY": 1},
        "deliverables": [{"deliverable_id": "TCOMPL::manuel_eleve",
                          "development_ready": True,
                          "axes": {"content": True}}],
    }
    fake = tmp_path / "primaire.json"
    fake.write_text(json.dumps(primary), encoding="utf-8")
    monkeypatch.setattr(recheck, "PRIMARY", fake)
    agreement = recheck._agreement([{
        "deliverable_id": "TCOMPL::manuel_eleve",
        "development_ready_independent": False,
        "axes": {"content": False},
    }])
    assert agreement["DISAGREEMENTS"] == 1
    assert agreement["disagreements"][0]["primary"] is True


# --------------------------------------------------------------------------
# Indépendance du chemin de preuve
# --------------------------------------------------------------------------
def test_the_recheck_does_not_read_the_dimension_artifacts() -> None:
    """Relire `DIMENSION_*.json` referait le constat primaire, pas un second."""
    source = (ROOT / "scripts/build_development_ready_independent_recheck.py") \
        .read_text(encoding="utf-8")
    body = source.split('"""', 2)[2]
    assert "DIMENSION_MATHEMATICS" not in body
    assert "DIMENSION_REGULATION" not in body


def test_the_recheck_does_not_reuse_the_primary_verdicts_to_conclude() -> None:
    """Le compteur primaire n'est ouvert qu'après conclusion, pour comparer."""
    source = (ROOT / "scripts/build_development_ready_independent_recheck.py") \
        .read_text(encoding="utf-8")
    conclusion = source.split("def _agreement")[0]
    assert "PRIMARY.read_text" not in conclusion


def test_the_transversal_apparatus_is_not_counted_as_a_divergence(payload) -> None:
    """Un avant-propos déclaré par l'assemblage n'est pas un objet de chapitre."""
    assert payload["summary"]["INVENTORY_DIVERGENCE_DELIVERABLES"] == 0
    maths = [row for row in payload["deliverables"]
             if row["deliverable_id"] == "1SPE::manuel_eleve"][0]
    assert maths["content"]["declared_outside_chapters"]
    for path in maths["content"]["declared_outside_chapters"]:
        assert "/chapitres/" not in path
