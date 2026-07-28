"""Valide le schéma de contrat de chapitre spécifique au millésime 1SPE 2026.

Ce schéma est une variante STRICTE de schemas/contrat_chapitre.schema.json,
propre à la collection 1SPE alignée sur le programme BO 2026 : il n'est pas
partagé avec TSPE, qui continue d'utiliser le schéma générique.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "contrat_chapitre_1spe_2026.schema.json"


@pytest.fixture()
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_contract_schema_requires_official_lineage(schema):
    capacity = schema["$defs"]["capacity"]
    assert {
        "ref_capacite", "obligation_class",
        "proof_object_ids", "transversal_ids",
    } <= set(capacity["required"])
    assert schema["additionalProperties"] is False


def test_capacity_obligation_class_matches_referentiel_vocabulary(schema):
    capacity = schema["$defs"]["capacity"]
    enum = set(capacity["properties"]["obligation_class"]["enum"])
    referentiel = json.loads(
        (ROOT / "referentiel" / "programme_1SPE_2026.json").read_text(encoding="utf-8")
    )
    observed = {item["obligation_class"] for item in referentiel["items"]}
    assert observed <= enum


def test_capacity_forbids_additional_properties(schema):
    assert schema["$defs"]["capacity"]["additionalProperties"] is False


def test_capacity_proof_object_ids_and_transversal_ids_are_string_arrays(schema):
    capacity = schema["$defs"]["capacity"]
    assert capacity["properties"]["proof_object_ids"]["type"] == "array"
    assert capacity["properties"]["proof_object_ids"]["items"]["type"] == "string"
    assert capacity["properties"]["transversal_ids"]["type"] == "array"
    assert capacity["properties"]["transversal_ids"]["items"]["type"] == "string"
