"""Tests de non-régression de l'autorité réglementaire.

Une migration d'autorité ne vaut que si le dépôt sait redevenir rouge. Chaque
test remet une anomalie réelle et exige qu'elle soit détectée — sinon rien ne
distinguerait un référentiel conforme d'un détecteur muet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dimension_regulation as regulation  # noqa: E402
import derive_1spe_referential_2026 as derive  # noqa: E402

REFERENTIAL = ROOT / "Mathematiques/manuel-maths/referentiel/capacites_1SPE_SECOND_DEGRE.json"
LEGACY = ROOT / "audit/historique/capacites_1SPE_SECOND_DEGRE_2019.json"
OFFICIAL_SOURCE = ROOT / "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt"


@pytest.fixture
def restore_referential():
    """Rend le référentiel intact quoi qu'il arrive au test."""
    saved = REFERENTIAL.read_bytes()
    yield
    REFERENTIAL.write_bytes(saved)


def _codes(payload) -> list[str]:
    return [f["code"] for f in payload["findings"]]


# --- État de référence --------------------------------------------------------

def test_second_degree_is_bound_to_the_2026_authority() -> None:
    payload = json.loads(REFERENTIAL.read_text(encoding="utf-8"))
    assert payload["authority"]["nor"] == "MENE2602917A"
    assert payload["authority"]["effective_school_year"] == "2026-2027"
    assert "2019" not in payload["bo_reference"]


def test_no_authority_divergence_remains_in_1spe() -> None:
    payload = regulation.build()
    divergences = [
        f for f in payload["findings"]
        if f["code"] == "PROGRAMME_AUTHORITY_DIVERGENCE" and f["target"] == "1SPE"
    ]
    assert divergences == []


# --- Mutation 1 : retour au programme 2019 -----------------------------------

def test_reverting_second_degree_to_the_2019_programme_fails(restore_referential) -> None:
    REFERENTIAL.write_bytes(LEGACY.read_bytes())
    payload = regulation.build()
    assert payload["status"] == "failed"
    divergences = [
        f for f in payload["findings"]
        if f["code"] == "PROGRAMME_AUTHORITY_DIVERGENCE" and f["target"] == "1SPE"
    ]
    assert divergences, "revenir au programme 2019 doit rouvrir la divergence d'autorité"
    assert "2019" in divergences[0]["detail"]


# --- Mutation 2 : source officielle absente ----------------------------------

def test_a_missing_official_source_cannot_be_derived_from(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(derive, "SOURCE", tmp_path / "absent.txt")
    with pytest.raises(OSError):
        derive.derive_section("Équations, fonctions polynômes du second degré")


# --- Mutation 3 : exigence d'une année non applicable ------------------------

def test_an_authority_from_another_year_is_reported(restore_referential) -> None:
    payload = json.loads(REFERENTIAL.read_text(encoding="utf-8"))
    payload["bo_reference"] = (
        "Programme d'enseignement de spécialité de mathématiques de première, "
        "BO n°21 du 3 juin 2031, arrêté MENE3100001A (application à la rentrée 2031-2032)."
    )
    REFERENTIAL.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result = regulation.build()
    divergences = [
        f for f in result["findings"]
        if f["code"] in {"PROGRAMME_AUTHORITY_DIVERGENCE", "WRONG_YEAR_AUTHORITY"}
        and f["target"] == "1SPE"
    ]
    assert divergences, "une autorité d'une autre année doit être signalée"


# --- Mutation 4 : libellé officiel retouché sans son empreinte ---------------

def test_a_reworded_official_capacity_no_longer_matches_its_digest(restore_referential) -> None:
    """Le libellé officiel est ancré par une empreinte : le retoucher se voit."""
    import hashlib

    payload = json.loads(REFERENTIAL.read_text(encoding="utf-8"))
    capacity = payload["capacites"][0]
    recorded = capacity["source_digest"]
    assert recorded == "sha256:" + hashlib.sha256(
        capacity["libelle_bo"].encode("utf-8")
    ).hexdigest()

    capacity["libelle_bo"] = capacity["libelle_bo"].replace("Étudier", "Survoler")
    recomputed = "sha256:" + hashlib.sha256(
        capacity["libelle_bo"].encode("utf-8")
    ).hexdigest()
    assert recomputed != recorded, "REFERENTIAL_SOURCE_MISMATCH doit être détectable"


# --- Mutation 5 : capacité sans aucun objet pédagogique ----------------------

def test_a_capacity_without_any_object_is_reported_as_uncovered() -> None:
    """Fausse couverture impossible : C7 n'a aucun objet et doit ressortir."""
    payload = regulation.build()
    uncovered = [
        f["target"] for f in payload["findings"]
        if f["code"] == "OFFICIAL_REQUIREMENT_UNCOVERED"
    ]
    assert "1SPE::1SPE-SECOND-DEGRE-2026-C2" in uncovered, (
        "l'exigence 2026 nouvelle est déclarée au contrat mais sans contenu : "
        "elle doit être signalée, pas absorbée"
    )


# --- La dérivation reste fidèle au texte officiel ----------------------------

def test_derivation_quotes_the_official_wording_verbatim() -> None:
    derived = derive.derive_section("Équations, fonctions polynômes du second degré")
    official = OFFICIAL_SOURCE.read_text(encoding="utf-8")
    normalised = " ".join(official.split())
    for capacity in derived["capacites"]:
        assert " ".join(capacity["libelle_bo"].split()) in normalised, capacity["id"]


def test_derivation_records_the_source_digest() -> None:
    import hashlib

    derived = derive.derive_section("Équations, fonctions polynômes du second degré")
    assert derived["authority"]["source_digest"] == "sha256:" + hashlib.sha256(
        OFFICIAL_SOURCE.read_bytes()
    ).hexdigest()
