"""Vérifie la filiation BO2026 des quatre contrats Géométrie/Probabilités
migrés en Task 4C (Produit scalaire, Géométrie repérée, Probabilités
conditionnelles, Variables aléatoires).

Cas Variables aléatoires : la loi binomiale B(n,p) n'a pas de support
officiel en 1SPE 2026 (aucun item PROB-VA-* ne la mentionne) — le contrat ne
doit donc plus la citer comme capacité exigible. Les quatre expérimentations
VA-EXP-* (mandatory_content) restent un écart documenté (`gap_task8` dans le
glossaire) : leur ajout est différé à la Task 8, qui devra produire du
contenu réel avant de pouvoir fournir des proof_object_ids non vides."""
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]

GP_CHAPTERS = [
    "1SPE-PRODUIT-SCALAIRE",
    "1SPE-GEOMETRIE-REPEREE",
    "1SPE-PROBA-COND",
    "1SPE-VARIABLES-ALEATOIRES",
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
def gp_contracts():
    return [
        yaml.safe_load((ROOT / "chapitres" / chap / "contrat.yaml").read_text(encoding="utf-8"))
        for chap in GP_CHAPTERS
    ]


@pytest.fixture()
def va_contract():
    return yaml.safe_load(
        (ROOT / "chapitres" / "1SPE-VARIABLES-ALEATOIRES" / "contrat.yaml").read_text(encoding="utf-8")
    )


def test_gp_contract_refs_are_official(gp_contracts, programme):
    official_ids = {item["id"] for item in programme["items"]}
    assert not {
        cap["ref_capacite"]
        for contract in gp_contracts
        for cap in contract["capacites"]
        if cap["ref_capacite"] not in official_ids
    }


def test_all_four_contracts_match_release_schema(gp_contracts, schema):
    for contract in gp_contracts:
        jsonschema.validate(contract, schema)


def test_variables_aleatoires_contract_drops_binomial_law(va_contract):
    labels = " ".join(c["libelle_eleve"].lower() for c in va_contract["capacites"])
    assert "binomial" not in labels
    assert "b(n,p)" not in labels.lower().replace(" ", "")


def test_variables_aleatoires_experimentations_gap_is_documented():
    glossary = json.loads(
        (ROOT / "referentiel" / "capacites_1SPE_VARIABLES_ALEATOIRES.json").read_text(encoding="utf-8")
    )
    assert "VA-EXP-SIMULER" in glossary.get("gap_task8", "")


def test_proof_object_ids_reference_files_that_exist(gp_contracts):
    for contract in gp_contracts:
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


def test_capacites_glossary_cites_bo2026(gp_contracts):
    filenames = {
        "1SPE-PRODUIT-SCALAIRE": "capacites_1SPE_PRODUIT_SCALAIRE.json",
        "1SPE-GEOMETRIE-REPEREE": "capacites_1SPE_GEOMETRIE_REPEREE.json",
        "1SPE-PROBA-COND": "capacites_1SPE_PROBA_COND.json",
        "1SPE-VARIABLES-ALEATOIRES": "capacites_1SPE_VARIABLES_ALEATOIRES.json",
    }
    for chap, filename in filenames.items():
        glossary = json.loads((ROOT / "referentiel" / filename).read_text(encoding="utf-8"))
        assert "2026" in glossary["bo_reference"]
        assert "2019" not in glossary["bo_reference"]
