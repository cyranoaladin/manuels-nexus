"""Vérifie la filiation BO2026 des six contrats Algèbre/Analyse migrés en
Task 4B (Suites, Second degré, Dérivation locale, Dérivation globale,
Exponentielle, Trigonométrie)."""
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_CHAPTERS = [
    "1SPE-SUITES",
    "1SPE-SECOND-DEGRE",
    "1SPE-DERIVATION-LOCAL",
    "1SPE-DERIVATION-GLOBAL",
    "1SPE-EXPONENTIELLE",
    "1SPE-TRIGONOMETRIE",
]


@pytest.fixture()
def programme():
    return json.loads((ROOT / "referentiel" / "programme_1SPE_2026.json").read_text(encoding="utf-8"))


@pytest.fixture()
def schema():
    return json.loads(
        (ROOT / "schemas" / "contrat_chapitre_1spe_2026.schema.json").read_text(encoding="utf-8")
    )


@pytest.fixture()
def analysis_contracts():
    return [
        yaml.safe_load((ROOT / "chapitres" / chap / "contrat.yaml").read_text(encoding="utf-8"))
        for chap in ANALYSIS_CHAPTERS
    ]


@pytest.fixture()
def trigo_contract():
    return yaml.safe_load(
        (ROOT / "chapitres" / "1SPE-TRIGONOMETRIE" / "contrat.yaml").read_text(encoding="utf-8")
    )


def test_analysis_contract_refs_are_official(analysis_contracts, programme):
    official_ids = {item["id"] for item in programme["items"]}
    assert not {
        cap["ref_capacite"]
        for contract in analysis_contracts
        for cap in contract["capacites"]
        if cap["ref_capacite"] not in official_ids
    }


def test_all_six_contracts_match_release_schema(analysis_contracts, schema):
    for contract in analysis_contracts:
        jsonschema.validate(contract, schema)


def test_trigonometry_contract_has_no_removed_content(trigo_contract):
    labels = " ".join(c["libelle_eleve"] for c in trigo_contract["capacites"])
    assert "formules d'addition" not in labels.lower()
    assert "équations trigonométriques" not in labels.lower()


def test_proof_object_ids_reference_files_that_exist(analysis_contracts):
    """Chaque objet de preuve doit correspondre à un fichier réel du chapitre
    (pas d'identifiant orphelin)."""
    for contract in analysis_contracts:
        chap = contract["chapitre"]
        known_ids = set()
        for tex in (ROOT / "chapitres" / chap).rglob("*.tex"):
            text = tex.read_text(encoding="utf-8", errors="ignore")
            if '"id":' in text:
                start = text.find('"id":')
                frag = text[start:start + 80]
                known_ids.add(frag.split('"')[3])
        for cap in contract["capacites"]:
            for pid in cap["proof_object_ids"]:
                assert pid in known_ids, f"{chap}/{cap['code']}: preuve orpheline {pid}"


def test_capacites_glossary_cites_bo2026(analysis_contracts):
    filenames = {
        "1SPE-SUITES": "capacites_1SPE_SUITES.json",
        "1SPE-SECOND-DEGRE": "capacites_1SPE_SECOND_DEGRE.json",
        "1SPE-DERIVATION-LOCAL": "capacites_1SPE_DERIVATION_LOCAL.json",
        "1SPE-DERIVATION-GLOBAL": "capacites_1SPE_DERIVATION_GLOBAL.json",
        "1SPE-EXPONENTIELLE": "capacites_1SPE_EXPONENTIELLE.json",
        "1SPE-TRIGONOMETRIE": "capacites_1SPE_TRIGONOMETRIE.json",
    }
    for chap, filename in filenames.items():
        glossary = json.loads((ROOT / "referentiel" / filename).read_text(encoding="utf-8"))
        assert "2026" in glossary["bo_reference"]
        assert "2019" not in glossary["bo_reference"]
