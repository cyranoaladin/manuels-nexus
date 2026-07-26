from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator
import pytest


ROOT = Path(__file__).resolve().parents[1]
PROGRAMME_PATH = ROOT / "referentiel" / "programme_1SPE_2026.json"
SCHEMA_PATH = ROOT / "schemas" / "programme_1spe_2026.schema.json"
CHECKER_PATH = ROOT / "scripts" / "check_programme_1spe_2026.py"
SOURCE_PATH = ROOT / "sources" / "BO2026_1SPE_specialite.pdf"
TEXT_PATH = ROOT / "sources" / "txt" / "BO2026_1SPE_specialite.txt"
EXPECTED_PDF_SHA256 = (
    "5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08"
)
EXPECTED_COUNTS = {
    ("contenu", "mandatory_content"): 42,
    ("contenu", "contextual_guidance"): 5,
    ("capacite", "prescribed_teaching"): 44,
    ("demonstration", "prescribed_teaching"): 11,
    ("algorithme", "mandatory_content"): 4,
    ("algorithme", "contextual_guidance"): 11,
    ("approfondissement", "optional_extension"): 17,
    ("transversal", "mandatory_content"): 8,
    ("transversal", "prescribed_teaching"): 29,
    ("transversal", "contextual_guidance"): 4,
}
OFFICIAL_DOMAINS = {
    "Algèbre",
    "Analyse",
    "Géométrie",
    "Probabilités et statistiques",
}
EXPERIMENT_IDS = {
    "VA-EXP-SIMULER",
    "VA-EXP-FONCTION-MOYENNE",
    "VA-EXP-DISTANCE-MOYENNE-ESPERANCE",
    "VA-EXP-PROPORTION-2SIGMA",
}
OBJECTIVE_BOUNDARIES = {
    "OBJ-ALG-SUITES-BORNE-001": (
        "contenu",
        "contextual_guidance",
        5,
        "aucune connaissance spécifique à leur sujet n’est au programme",
    ),
    "OBJ-ALG-LIMITE-BORNE-001": (
        "contenu",
        "contextual_guidance",
        5,
        "Toute formalisation est exclue",
    ),
    "OBJ-ALG-SD-BORNE-001": (
        "contenu",
        "contextual_guidance",
        5,
        "Le calcul effectif de la forme canonique dans le cas général n’est pas un attendu du programme",
    ),
    "OBJ-ANA-DERIVEE-BORNE-001": (
        "contenu",
        "contextual_guidance",
        7,
        "On n’en donne pas de définition formelle",
    ),
    "OBJ-GEO-VECTEURS-PRESC-001": (
        "capacite",
        "prescribed_teaching",
        9,
        "Les élèves doivent conserver une pratique du calcul vectoriel en géométrie non repérée",
    ),
    "OBJ-PROB-UNIVERS-BORNE-001": (
        "contenu",
        "contextual_guidance",
        10,
        "Le programme ne considère que des univers finis et des variables aléatoires réelles",
    ),
}


@pytest.fixture(scope="module")
def programme() -> dict:
    return json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def counts_by_type_and_class(programme: dict) -> dict[tuple[str, str], int]:
    return dict(
        Counter(
            (item["type"], item["obligation_class"])
            for item in programme["items"]
        )
    )


def test_schema_is_closed_recursively(schema: dict) -> None:
    Draft202012Validator.check_schema(schema)

    def visit(node: object) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)


def test_programme_matches_closed_schema(programme: dict, schema: dict) -> None:
    Draft202012Validator(schema).validate(programme)


def test_every_program_item_is_traceable(programme: dict) -> None:
    for item in programme["items"]:
        assert item["bo_page"] >= 1
        assert item["bo_quote"].strip()
        assert item["source_sha256"] == EXPECTED_PDF_SHA256
        assert item["obligation_class"] in {
            "mandatory_content",
            "prescribed_teaching",
            "optional_extension",
            "contextual_guidance",
        }


def test_official_experiments_are_present_and_mandatory(programme: dict) -> None:
    by_id = {item["id"]: item for item in programme["items"]}
    assert EXPERIMENT_IDS <= by_id.keys()
    assert all(
        by_id[item_id]["type"] == "algorithme"
        and by_id[item_id]["obligation_class"] == "mandatory_content"
        for item_id in EXPERIMENT_IDS
    )


def test_expected_cardinalities_are_exact(programme: dict) -> None:
    assert len(programme["items"]) == 175
    assert counts_by_type_and_class(programme) == EXPECTED_COUNTS


def test_prescriptive_objective_boundaries_are_traceable(programme: dict) -> None:
    by_id = {item["id"]: item for item in programme["items"]}
    assert OBJECTIVE_BOUNDARIES.keys() <= by_id.keys()
    for item_id, expected in OBJECTIVE_BOUNDARIES.items():
        item = by_id[item_id]
        assert (
            item["type"],
            item["obligation_class"],
            item["bo_page"],
        ) == expected[:3]
        assert expected[3] in item["bo_quote"]
        assert item["editorial_verdict"] == "included"


def test_selection_policy_includes_only_prescriptive_objective_sentences(
    programme: dict,
) -> None:
    assert programme["selection_policy"] == {
        "objective_paragraphs": (
            "include_explicit_prescriptions_and_scope_boundaries"
        ),
        "excluded_objective_material": [
            "descriptive_context",
            "history_of_mathematics",
        ],
    }


def test_ids_are_unique_at_runtime(programme: dict) -> None:
    ids = [item["id"] for item in programme["items"]]
    assert len(ids) == len(set(ids))


def test_only_four_official_thematic_domains_are_modelled(programme: dict) -> None:
    assert set(programme["thematic_domains"]) == OFFICIAL_DOMAINS
    assert {
        item["domain"]
        for item in programme["items"]
        if item["domain_kind"] == "thematic"
    } == OFFICIAL_DOMAINS
    assert all(
        item["domain"] not in OFFICIAL_DOMAINS
        for item in programme["items"]
        if item["domain_kind"] == "transversal"
    )


def test_checker_accepts_the_canonical_programme_from_an_unrelated_cwd(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--programme",
            str(PROGRAMME_PATH),
            "--schema",
            str(SCHEMA_PATH),
            "--source",
            str(SOURCE_PATH),
            "--text",
            str(TEXT_PATH),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "certified"
    assert report["orphan_quotes"] == []
    assert report["item_count"] == 175
    assert report["source_sha256"] == EXPECTED_PDF_SHA256


def test_checker_rejects_a_quote_on_the_wrong_page(tmp_path: Path) -> None:
    programme = json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))
    programme["items"][0]["bo_page"] = 11
    altered = tmp_path / "programme.json"
    altered.write_text(
        json.dumps(programme, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--programme",
            str(altered),
            "--schema",
            str(SCHEMA_PATH),
            "--source",
            str(SOURCE_PATH),
            "--text",
            str(TEXT_PATH),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert programme["items"][0]["id"] in report["orphan_quotes"]


def test_checker_rejects_duplicate_and_unjustified_distributed_assignments(
    tmp_path: Path,
) -> None:
    programme = json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))
    programme["items"][1]["id"] = programme["items"][0]["id"]
    programme["items"][2]["assigned_chapters"] = [
        "1SPE-SUITES",
        "1SPE-SECOND-DEGRE",
    ]
    programme["items"][2]["distribution_justification"] = "   "
    altered = tmp_path / "programme.json"
    altered.write_text(
        json.dumps(programme, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--programme",
            str(altered),
            "--schema",
            str(SCHEMA_PATH),
            "--source",
            str(SOURCE_PATH),
            "--text",
            str(TEXT_PATH),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["duplicate_ids"]
    assert report["unjustified_distributions"]


def test_canonical_text_hash_is_recorded(programme: dict) -> None:
    actual = hashlib.sha256(TEXT_PATH.read_bytes()).hexdigest()
    assert programme["source"]["text_sha256"] == actual
