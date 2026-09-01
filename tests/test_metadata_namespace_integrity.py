"""Un prerequis n'est pas une capacite, et le champ le dit ou il ment."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)


@pytest.fixture(scope="module")
def guard():
    spec = importlib.util.spec_from_file_location(
        "metadata_namespace_integrity",
        ROOT / "scripts/metadata_namespace_integrity.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = {
    "chapitre": "X-CHAP",
    "capacites": [
        {"code": "C1", "ref_capacite": "P-REF-01"},
        {"code": "C2", "ref_capacite": "P-REF-02"},
    ],
    "prerequis": [{"code": "R1"}, {"code": "R2"}],
}


@pytest.fixture(scope="module")
def scope(guard):
    return guard.namespaces(CONTRACT, "X-CHAP")


def _meta(**fields):
    return {"id": "X-OBJ", "chapitre": "X-CHAP", "type_objet": "remediation", **fields}


# -- A : un prerequis declare comme capacite ---------------------------------


def test_a_prerequisite_in_the_capacity_field_is_a_violation(guard, scope) -> None:
    found = guard.object_violations(_meta(capacites_codes=["R1"]), scope)
    assert [row["kind"] for row in found] == [guard.PREREQUISITE_IN_CAPACITY_FIELD]
    assert found[0]["value"] == "R1"


# -- B : le meme prerequis, dans son champ ----------------------------------


def test_b_a_prerequisite_in_its_own_field_is_accepted(guard, scope) -> None:
    assert guard.object_violations(_meta(prerequis_testes=["R1", "R2"]), scope) == []


# -- C : une capacite locale dans le champ des capacites ---------------------


def test_c_a_scoped_capacity_in_the_capacity_field_is_accepted(guard, scope) -> None:
    assert guard.object_violations(_meta(capacites_codes=["C1"]), scope) == []
    assert guard.object_violations(_meta(capacites=["P-REF-01"]), scope) == []
    assert guard.object_violations(_meta(capacites_codes=["X-CHAP-C1"]), scope) == []


# -- D : une capacite dans le champ des prerequis ----------------------------


def test_d_a_capacity_in_the_prerequisite_field_is_a_violation(guard, scope) -> None:
    found = guard.object_violations(_meta(prerequis_testes=["C1"]), scope)
    assert [row["kind"] for row in found] == [guard.CAPACITY_IN_PREREQUISITE_FIELD]


# -- E : melange, la violation ne porte QUE sur la valeur fautive ------------


def test_e_a_mixed_field_only_flags_the_offending_value(guard, scope) -> None:
    found = guard.object_violations(_meta(capacites_codes=["C1", "R1"]), scope)
    assert len(found) == 1, "C1 est legitime et ne doit pas etre signale"
    assert found[0]["value"] == "R1"
    assert found[0]["kind"] == guard.PREREQUISITE_IN_CAPACITY_FIELD


# -- F : un code inconnu echoue ferme, dans les deux champs ------------------


def test_f_an_unknown_code_fails_closed_in_either_field(guard, scope) -> None:
    assert [row["kind"] for row in guard.object_violations(
        _meta(capacites_codes=["ZZ9"]), scope
    )] == [guard.UNKNOWN_CODE_IN_CAPACITY_FIELD]
    assert [row["kind"] for row in guard.object_violations(
        _meta(prerequis_testes=["ZZ9"]), scope
    )] == [guard.UNKNOWN_CODE_IN_PREREQUISITE_FIELD]


# -- G : un meme jeton dans deux champs exclusifs ----------------------------


def test_g_the_same_token_in_two_exclusive_fields_is_a_violation(guard) -> None:
    """Si un contrat declarait reellement le meme code des deux cotes, la
    resolution devrait etre pleinement qualifiee -- pas un choix arbitraire.
    Tant que le contrat ne l'etablit pas, le porter dans les deux champs est
    une ambiguite, et elle se signale."""
    contract = {
        "chapitre": "Y-CHAP",
        "capacites": [{"code": "C1", "ref_capacite": "P-REF-01"}],
        "prerequis": [{"code": "C1"}],
    }
    scope = guard.namespaces(contract, "Y-CHAP")
    meta = {
        "id": "Y-OBJ",
        "chapitre": "Y-CHAP",
        "capacites_codes": ["C1"],
        "prerequis_testes": ["C1"],
    }
    kinds = [row["kind"] for row in guard.object_violations(meta, scope)]
    assert guard.SAME_CODE_IN_MUTUALLY_EXCLUSIVE_FIELDS in kinds


# -- La regle ne doit pas dependre de la FORME du code -----------------------


def test_the_rule_never_infers_a_namespace_from_the_shape_of_the_code(guard) -> None:
    """Un chapitre dont une CAPACITE s'appelle `R1` reste legitime.

    Une regle du type `code.startswith("R")` marcherait sur le corpus
    d'aujourd'hui et mentirait ici.
    """
    contract = {
        "chapitre": "Z-CHAP",
        "capacites": [{"code": "R1", "ref_capacite": "P-REF-09"}],
        "prerequis": [{"code": "C9"}],
    }
    scope = guard.namespaces(contract, "Z-CHAP")
    assert guard.object_violations(
        {"id": "Z", "chapitre": "Z-CHAP", "capacites_codes": ["R1"]}, scope
    ) == []
    assert [
        row["kind"]
        for row in guard.object_violations(
            {"id": "Z", "chapitre": "Z-CHAP", "capacites_codes": ["C9"]}, scope
        )
    ] == [guard.PREREQUISITE_IN_CAPACITY_FIELD]


# -- Le depot reel -----------------------------------------------------------


def test_the_collection_declares_every_identity_in_its_own_namespace(guard) -> None:
    violations = guard.scan(CORPORA)
    summary: dict[str, int] = {}
    for row in violations:
        summary[row["kind"]] = summary.get(row["kind"], 0) + 1
    assert violations == [], (
        f"violations de namespace dans le corpus publiable : {summary}"
    )
