from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator, FormatChecker
import pytest


ROOT = Path(__file__).resolve().parents[1]
PROGRAMME_PATH = ROOT / "referentiel" / "programme_1SPE_2026.json"
SCHEMA_PATH = ROOT / "schemas" / "programme_1spe_2026.schema.json"
CHECKER_PATH = ROOT / "scripts" / "check_programme_1spe_2026.py"
ATTESTATION_PATH = (
    ROOT / "validations" / "release-1spe" / "programme-1spe-2026.attestation.json"
)
ATTESTATION_SCHEMA_PATH = (
    ROOT / "schemas" / "programme_1spe_2026.attestation.schema.json"
)
REVIEW_PATH = ROOT / "validations" / "release-1spe" / "revue-programme.md"
REGISTRY_PATH = ROOT / "sources" / "registry.yaml"
COMPLIANCE_PATH = ROOT / "referentiel" / "CONFORMITE_BO2026.md"
SOURCE_PATH = ROOT / "sources" / "BO2026_1SPE_specialite.pdf"
TEXT_PATH = ROOT / "sources" / "txt" / "BO2026_1SPE_specialite.txt"
PLAN_PATH = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-26-finalisation-manuel-1spe-bat.md"
)
EXPECTED_PDF_SHA256 = (
    "5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08"
)
EXPECTED_COUNTS = {
    ("contenu", "mandatory_content"): 42,
    ("contenu", "contextual_guidance"): 5,
    ("capacite", "mandatory_content"): 44,
    ("demonstration", "prescribed_teaching"): 11,
    ("algorithme", "mandatory_content"): 4,
    ("algorithme", "prescribed_teaching"): 11,
    ("approfondissement", "optional_extension"): 17,
    ("transversal", "mandatory_content"): 8,
    ("transversal", "prescribed_teaching"): 29,
    ("transversal", "contextual_guidance"): 4,
}
OBJECTIVE_COVERAGE = {
    "OBJ-COV-SUITES-TAUX-FIXE": {
        "covered_by_item_ids": {"ALG-SUI-CONT-004", "ALG-SUI-CAP-005"},
        "assigned_chapters": {"1SPE-SUITES"},
        "coverage_kind": "required_learning_outcome",
    },
    "OBJ-COV-SD-COMPLETION-CARRE": {
        "covered_by_item_ids": {"ALG-SD-CONT-002"},
        "assigned_chapters": {"1SPE-SECOND-DEGRE"},
        "coverage_kind": "required_learning_outcome",
    },
    "OBJ-COV-SD-FACTORISATION-DIRECTE": {
        "covered_by_item_ids": {"ALG-SD-CAP-003"},
        "assigned_chapters": {"1SPE-SECOND-DEGRE"},
        "coverage_kind": "required_learning_outcome",
    },
    "OBJ-COV-DERIVEE-GRAPHIQUE": {
        "covered_by_item_ids": {
            "ANA-DERLOC-CONT-001",
            "ANA-DERLOC-CONT-003",
        },
        "assigned_chapters": {"1SPE-DERIVATION-LOCAL"},
        "coverage_kind": "required_introduction_modality",
    },
    "OBJ-COV-DERIVEE-ALGEBRIQUE": {
        "covered_by_item_ids": {"ANA-DERLOC-CAP-001"},
        "assigned_chapters": {"1SPE-DERIVATION-LOCAL"},
        "coverage_kind": "required_introduction_modality",
    },
    "OBJ-COV-DERIVEE-NUMERIQUE": {
        "covered_by_item_ids": {
            "ANA-DERLOC-CONT-004",
            "ANA-DERLOC-CAP-005",
        },
        "assigned_chapters": {"1SPE-DERIVATION-LOCAL"},
        "coverage_kind": "required_introduction_modality",
    },
}
EXACT_SECTION_ANCHORS = {
    "ANA-DERLOC-ALG-001": ("Exemple d’algorithme", "Démonstrations"),
    "ANA-VAR-ALG-001": ("Exemple d’algorithme", "Capacités attendues"),
    "ANA-EXP-ALG-001": ("Exemple d’algorithme", "Capacités attendues"),
    "ANA-EXP-ALG-002": ("Exemple d’algorithme", "Capacités attendues"),
    "PROB-COND-ALG-001": ("Exemple d’algorithme", "Capacités attendues"),
    "ANA-TRIG-ALG-001": ("Exemple d’algorithme", "Démonstration"),
    "OBJ-PROB-UNIVERS-BORNE-001": (
        "Variables aléatoires réelles",
        "Approfondissements possibles",
    ),
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
        "mandatory_content",
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


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def swap_content_obligation_classes(value: dict) -> None:
    mandatory = next(
        item
        for item in value["items"]
        if item["type"] == "contenu"
        and item["obligation_class"] == "mandatory_content"
    )
    contextual = next(
        item
        for item in value["items"]
        if item["type"] == "contenu"
        and item["obligation_class"] == "contextual_guidance"
    )
    mandatory["obligation_class"], contextual["obligation_class"] = (
        contextual["obligation_class"],
        mandatory["obligation_class"],
    )


def swap_chapter_assignments(value: dict) -> None:
    first = value["items"][10]
    second = value["items"][100]
    first["assigned_chapters"], second["assigned_chapters"] = (
        second["assigned_chapters"],
        first["assigned_chapters"],
    )


def swap_citation_anchors(value: dict) -> None:
    fields = (
        "bo_page",
        "bo_quote",
        "bo_section",
        "bo_occurrence",
        "bo_offset",
    )
    first = value["items"][0]
    second = value["items"][1]
    for field in fields:
        first[field], second[field] = second[field], first[field]


def run_checker(
    tmp_path: Path,
    *,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
    **overrides: Path,
) -> subprocess.CompletedProcess[str]:
    paths = {
        "programme": PROGRAMME_PATH,
        "schema": SCHEMA_PATH,
        "source": SOURCE_PATH,
        "text": TEXT_PATH,
        "attestation": ATTESTATION_PATH,
        "attestation-schema": ATTESTATION_SCHEMA_PATH,
        "review": REVIEW_PATH,
        "registry": REGISTRY_PATH,
        "compliance": COMPLIANCE_PATH,
    }
    paths.update(overrides)
    command = [sys.executable, str(CHECKER_PATH)]
    for option, path in paths.items():
        command.extend((f"--{option}", str(path)))
    return subprocess.run(
        command,
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
        env=env,
        timeout=timeout,
    )


def write_refreshed_attestation(
    tmp_path: Path,
    *,
    programme_path: Path = PROGRAMME_PATH,
    compliance_path: Path = COMPLIANCE_PATH,
) -> Path:
    attestation = json.loads(ATTESTATION_PATH.read_text(encoding="utf-8"))
    attestation["programme_sha256"] = hashlib.sha256(
        programme_path.read_bytes()
    ).hexdigest()
    attestation["compliance_sha256"] = hashlib.sha256(
        compliance_path.read_bytes()
    ).hexdigest()
    path = tmp_path / "attestation.json"
    path.write_text(
        json.dumps(attestation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def test_checker_never_certifies_a_two_line_temporary_review(tmp_path: Path) -> None:
    review = tmp_path / "review.md"
    review.write_text(
        "Statut : `approved`\n"
        "SHA-256 du référentiel revu : "
        f"`{hashlib.sha256(PROGRAMME_PATH.read_bytes()).hexdigest()}`\n",
        encoding="utf-8",
    )

    result = run_checker(tmp_path, review=review)

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert "review" in report["noncanonical_inputs"]
    assert report["review_errors"]


@pytest.mark.parametrize(
    "mutation",
    [
        swap_content_obligation_classes,
        swap_chapter_assignments,
        swap_citation_anchors,
    ],
)
def test_checker_never_certifies_coordinated_semantic_and_review_mutations(
    tmp_path: Path,
    mutation,
) -> None:
    programme = json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))
    mutation(programme)
    altered_programme = tmp_path / "programme.json"
    altered_programme.write_text(
        json.dumps(programme, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    attestation = write_refreshed_attestation(
        tmp_path,
        programme_path=altered_programme,
    )
    review_text = REVIEW_PATH.read_text(encoding="utf-8")
    review_text = review_text.replace(
        hashlib.sha256(PROGRAMME_PATH.read_bytes()).hexdigest(),
        hashlib.sha256(altered_programme.read_bytes()).hexdigest(),
    ).replace(
        hashlib.sha256(ATTESTATION_PATH.read_bytes()).hexdigest(),
        hashlib.sha256(attestation.read_bytes()).hexdigest(),
    )
    review = tmp_path / "review.md"
    review.write_text(review_text, encoding="utf-8")

    result = run_checker(
        tmp_path,
        programme=altered_programme,
        attestation=attestation,
        review=review,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert {"programme", "attestation", "review"} <= set(
        report["noncanonical_inputs"]
    )


def test_checker_never_certifies_refreshed_compliance_without_new_review(
    tmp_path: Path,
) -> None:
    compliance = tmp_path / "CONFORMITE_BO2026.md"
    compliance.write_text(
        COMPLIANCE_PATH.read_text(encoding="utf-8") + "\nAltération.\n",
        encoding="utf-8",
    )
    attestation = write_refreshed_attestation(
        tmp_path,
        compliance_path=compliance,
    )

    result = run_checker(
        tmp_path,
        compliance=compliance,
        attestation=attestation,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert {"compliance", "attestation"} <= set(report["noncanonical_inputs"])
    assert report["review_errors"]


@pytest.mark.parametrize(
    ("option", "report_name", "canonical"),
    [
        ("programme", "programme", PROGRAMME_PATH),
        ("schema", "schema", SCHEMA_PATH),
        ("source", "source", SOURCE_PATH),
        ("text", "text", TEXT_PATH),
        ("attestation", "attestation", ATTESTATION_PATH),
        (
            "attestation-schema",
            "attestation_schema",
            ATTESTATION_SCHEMA_PATH,
        ),
        ("review", "review", REVIEW_PATH),
        ("registry", "registry", REGISTRY_PATH),
        ("compliance", "compliance", COMPLIANCE_PATH),
    ],
)
def test_checker_never_certifies_a_noncanonical_input_path(
    tmp_path: Path,
    option: str,
    report_name: str,
    canonical: Path,
) -> None:
    copied = tmp_path / canonical.name
    copied.write_bytes(canonical.read_bytes())

    result = run_checker(tmp_path, **{option: copied})

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert report["noncanonical_inputs"] == [report_name]


@pytest.mark.parametrize(
    ("option", "report_name", "canonical"),
    [
        ("programme", "programme", PROGRAMME_PATH),
        ("schema", "schema", SCHEMA_PATH),
        ("source", "source", SOURCE_PATH),
        ("text", "text", TEXT_PATH),
        ("attestation", "attestation", ATTESTATION_PATH),
        (
            "attestation-schema",
            "attestation_schema",
            ATTESTATION_SCHEMA_PATH,
        ),
        ("review", "review", REVIEW_PATH),
        ("registry", "registry", REGISTRY_PATH),
        ("compliance", "compliance", COMPLIANCE_PATH),
    ],
)
def test_checker_rejects_every_symlink_alias_of_a_canonical_input(
    tmp_path: Path,
    option: str,
    report_name: str,
    canonical: Path,
) -> None:
    alias = tmp_path / f"alias-{canonical.name}"
    alias.symlink_to(canonical)

    result = run_checker(tmp_path, **{option: alias})

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert report["noncanonical_inputs"] == [report_name]


def test_noncanonical_input_is_review_required_even_on_early_read_error(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-programme.json"

    result = run_checker(tmp_path, programme=missing)

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert report["noncanonical_inputs"] == ["programme"]
    assert report["schema_errors"]


def write_fake_pdftotext(tmp_path: Path, body: str) -> tuple[Path, dict[str, str]]:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake = fake_bin / "pdftotext"
    fake.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    fake.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = str(fake_bin)
    return fake, env


def test_checker_rejects_pdftotext_below_minimum_poppler_version(
    tmp_path: Path,
) -> None:
    _, env = write_fake_pdftotext(
        tmp_path,
        "if [ \"$1\" = \"-v\" ]; then\n"
        "  echo 'pdftotext version 23.01.0' >&2\n"
        "  exit 0\n"
        "fi\n"
        "exec /usr/bin/pdftotext \"$@\"\n",
    )

    result = run_checker(tmp_path, env=env)

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "needs_fix"
    assert any("version Poppler" in error for error in report["errors"])


def test_checker_bounds_a_blocking_pdftotext_version_probe(tmp_path: Path) -> None:
    _, env = write_fake_pdftotext(
        tmp_path,
        "if [ \"$1\" = \"-v\" ]; then\n"
        "  /bin/sleep 10\n"
        "  exit 0\n"
        "fi\n"
        "exec /usr/bin/pdftotext \"$@\"\n",
    )

    result = run_checker(tmp_path, env=env, timeout=4)

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "needs_fix"
    assert any("version" in error for error in report["errors"])


def test_checker_bounds_a_blocking_pdftotext_extraction(tmp_path: Path) -> None:
    _, env = write_fake_pdftotext(
        tmp_path,
        "if [ \"$1\" = \"-v\" ]; then\n"
        "  echo 'pdftotext version 24.02.0' >&2\n"
        "  exit 0\n"
        "fi\n"
        "/bin/sleep 10\n",
    )

    result = run_checker(tmp_path, env=env, timeout=4)

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "needs_fix"
    assert any("pdftotext" in error for error in report["errors"])


def test_checker_rejects_a_fake_pdftotext_from_path(tmp_path: Path) -> None:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    (fake_bin / "pdftotext").symlink_to("/bin/echo")
    env = os.environ.copy()
    env["PATH"] = str(fake_bin)

    result = run_checker(tmp_path, env=env)

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "needs_fix"
    assert any("version" in error for error in report["errors"])


def test_checker_uses_private_source_snapshot_and_allowlisted_environment(
    tmp_path: Path,
) -> None:
    observed_input = tmp_path / "observed-input.txt"
    observed_env = tmp_path / "observed-env.txt"
    _, env = write_fake_pdftotext(
        tmp_path,
        "if [ \"$1\" = \"-v\" ]; then\n"
        "  echo 'pdftotext version 24.02.0' >&2\n"
        "  exit 0\n"
        "fi\n"
        f"printf '%s' \"$2\" > '{observed_input}'\n"
        f"printf '%s|%s|%s|%s' \"$LANG\" \"$LC_ALL\" \"$TZ\" "
        f"\"$UNTRUSTED_MARKER\" > '{observed_env}'\n"
        "exec /usr/bin/pdftotext \"$@\"\n",
    )
    env["UNTRUSTED_MARKER"] = "must-not-leak"

    result = run_checker(tmp_path, env=env)

    assert result.returncode == 0, result.stderr
    snapshot = Path(observed_input.read_text(encoding="utf-8"))
    assert snapshot != SOURCE_PATH.resolve()
    assert not snapshot.exists()
    assert observed_env.read_text(encoding="utf-8") == "C|C|UTC|"


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


def test_machine_attestation_is_closed_and_pins_the_exact_semantic_state(
    programme: dict,
) -> None:
    attestation_schema = json.loads(
        ATTESTATION_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    attestation = json.loads(ATTESTATION_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(attestation_schema)
    Draft202012Validator(attestation_schema).validate(attestation)
    assert attestation["compliance_path"] == "referentiel/CONFORMITE_BO2026.md"
    assert attestation["compliance_sha256"] == hashlib.sha256(
        COMPLIANCE_PATH.read_bytes()
    ).hexdigest()
    assert attestation["programme_sha256"] == hashlib.sha256(
        PROGRAMME_PATH.read_bytes()
    ).hexdigest()
    assert attestation["schema_sha256"] == hashlib.sha256(
        SCHEMA_PATH.read_bytes()
    ).hexdigest()
    assert attestation["source_pdf_sha256"] == EXPECTED_PDF_SHA256
    assert attestation["source_text_sha256"] == hashlib.sha256(
        TEXT_PATH.read_bytes()
    ).hexdigest()
    assert attestation["registry_sha256"] == hashlib.sha256(
        REGISTRY_PATH.read_bytes()
    ).hexdigest()
    assert attestation["item_count"] == 175
    assert attestation["item_ids_sha256"] == canonical_sha256(
        [item["id"] for item in programme["items"]]
    )
    assert attestation["matrix_sha256"] == canonical_sha256(
        programme["expected_cardinalities"]
    )


def test_checker_requires_review_when_the_compliance_document_changes(
    tmp_path: Path,
) -> None:
    altered_compliance = tmp_path / "CONFORMITE_BO2026.md"
    altered_compliance.write_text(
        COMPLIANCE_PATH.read_text(encoding="utf-8") + "\nAltération non revue.\n",
        encoding="utf-8",
    )
    current_programme_sha256 = hashlib.sha256(
        PROGRAMME_PATH.read_bytes()
    ).hexdigest()
    current_review = tmp_path / "review.md"
    current_review.write_text(
        "Statut : `approved`\n\n"
        "SHA-256 du référentiel revu : "
        f"`{current_programme_sha256}`\n",
        encoding="utf-8",
    )

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
            "--compliance",
            str(altered_compliance),
            "--review",
            str(current_review),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert report["attestation_errors"] == ["compliance_sha256"]
    assert report["review_errors"]
    assert set(report["noncanonical_inputs"]) == {"compliance", "review"}


def test_programme_matches_closed_schema(programme: dict, schema: dict) -> None:
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(programme)


def test_every_program_item_is_traceable(programme: dict) -> None:
    for item in programme["items"]:
        assert item["bo_page"] >= 1
        assert item["bo_quote"].strip()
        assert item["bo_section"].strip()
        assert item["bo_occurrence"] >= 1
        assert item["bo_offset"] >= 0
        assert item["source_sha256"] == EXPECTED_PDF_SHA256
        assert item["obligation_class"] in {
            "mandatory_content",
            "prescribed_teaching",
            "optional_extension",
            "contextual_guidance",
        }


def test_canonical_ambiguous_sections_use_the_exact_nearest_heading(
    programme: dict,
) -> None:
    by_id = {item["id"]: item for item in programme["items"]}
    assert {
        item_id: by_id[item_id]["bo_section"]
        for item_id in EXACT_SECTION_ANCHORS
    } == {
        item_id: expected_and_old[0]
        for item_id, expected_and_old in EXACT_SECTION_ANCHORS.items()
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


def test_taxonomy_matches_the_approved_compliance_gate(programme: dict) -> None:
    capacities = [item for item in programme["items"] if item["type"] == "capacite"]
    thematic_algorithms = [
        item
        for item in programme["items"]
        if item["type"] == "algorithme" and item["id"] not in EXPERIMENT_IDS
    ]
    assert len(capacities) == 44
    assert all(
        item["obligation_class"] == "mandatory_content" for item in capacities
    )
    assert len(thematic_algorithms) == 11
    assert all(
        item["obligation_class"] == "prescribed_teaching"
        for item in thematic_algorithms
    )


def test_compliance_document_matches_taxonomy_matrix_and_objective_gate() -> None:
    text = COMPLIANCE_PATH.read_text(encoding="utf-8")
    assert "| Capacités attendues | `capacite` | `mandatory_content` |" in text
    assert (
        "| Exemples d’algorithmes | `algorithme` | "
        "`prescribed_teaching` |"
    ) in text
    assert "| Expérimentations | `algorithme` | `mandatory_content` |" in text
    for row in (
        "| `capacite` | `mandatory_content` | 44 |",
        "| `algorithme` | `prescribed_teaching` | 11 |",
        "| `algorithme` | `mandatory_content` | 4 |",
    ):
        assert row in text
    assert "preuve de couverture explicite" in text
    for coverage_id in OBJECTIVE_COVERAGE:
        assert f"`{coverage_id}`" in text


def test_objective_prescriptions_have_explicit_machine_readable_coverage(
    programme: dict,
) -> None:
    by_id = {item["id"]: item for item in programme["items"]}
    coverage = {
        entry["id"]: entry for entry in programme["objective_coverage"]
    }
    assert coverage.keys() == OBJECTIVE_COVERAGE.keys()
    for coverage_id, expected in OBJECTIVE_COVERAGE.items():
        entry = coverage[coverage_id]
        assert entry["bo_page"] >= 1
        assert entry["bo_quote"].strip()
        assert entry["bo_section"] == "Objectifs"
        assert entry["bo_occurrence"] >= 1
        assert entry["bo_offset"] >= 0
        assert set(entry["covered_by_item_ids"]) == expected["covered_by_item_ids"]
        assert set(entry["assigned_chapters"]) == expected["assigned_chapters"]
        assert entry["coverage_kind"] == expected["coverage_kind"]
        assert entry["release_gate"] is True
        assert expected["covered_by_item_ids"] <= by_id.keys()
        assert all(
            set(by_id[item_id]["assigned_chapters"]) & expected["assigned_chapters"]
            for item_id in expected["covered_by_item_ids"]
        )


def test_release_plan_gates_every_objective_in_both_manual_variants() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    task_4d = plan.split("### Task 4D:", 1)[1].split("### Task 5:", 1)[0]
    task_18 = plan.split("### Task 18:", 1)[1].split("### Task 19:", 1)[0]
    task_20 = plan.split("### Task 20:", 1)[1]
    required_scope = (
        "100 % des entrées `objective_coverage` dont `release_gate=true`"
    )

    assert required_scope in " ".join(task_4d.split())
    assert "`manual_object_ids`" in task_4d
    assert "`assigned_chapters`" in task_4d
    assert required_scope in " ".join(task_18.split())
    assert (
        "`student_folios` et `teacher_folios` non vides"
        in " ".join(task_18.split())
    )
    assert required_scope in " ".join(task_20.split())
    assert (
        "`student_folios` et `teacher_folios` non vides"
        in " ".join(task_20.split())
    )


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("covered_by_item_ids", ["ALG-SUI-CONT-004"]),
        ("assigned_chapters", ["1SPE-SECOND-DEGRE"]),
        ("coverage_kind", "required_introduction_modality"),
        ("release_gate", False),
    ],
)
def test_checker_rejects_every_mutated_objective_coverage_dimension(
    tmp_path: Path,
    field: str,
    invalid_value,
) -> None:
    programme = json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))
    coverage = next(
        entry
        for entry in programme["objective_coverage"]
        if entry["id"] == "OBJ-COV-SUITES-TAUX-FIXE"
    )
    coverage[field] = invalid_value
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
    assert "OBJ-COV-SUITES-TAUX-FIXE" in report["objective_coverage_errors"]


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


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: (
            value["items"][0].__setitem__(
                "bo_quote", value["items"][1]["bo_quote"]
            ),
            value["items"][0].__setitem__(
                "bo_page", value["items"][1]["bo_page"]
            ),
            value["items"][0].__setitem__(
                "bo_section", value["items"][1]["bo_section"]
            ),
            value["items"][0].__setitem__(
                "bo_occurrence", value["items"][1]["bo_occurrence"]
            ),
            value["items"][0].__setitem__(
                "bo_offset", value["items"][1]["bo_offset"]
            ),
        ),
        swap_content_obligation_classes,
        swap_chapter_assignments,
        lambda value: value["items"][20].__setitem__(
            "theme", "Thème sémantiquement altéré"
        ),
    ],
)
def test_attestation_blocks_semantic_mutations_even_when_counts_are_preserved(
    tmp_path: Path,
    mutation,
) -> None:
    programme = json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))
    mutation(programme)
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
            "--attestation",
            str(ATTESTATION_PATH),
            "--review",
            str(REVIEW_PATH),
            "--registry",
            str(REGISTRY_PATH),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "review_required"
    assert report["noncanonical_inputs"] == ["programme"]
    assert report["attestation_errors"]


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


@pytest.mark.parametrize("field", ["bo_occurrence", "bo_section"])
def test_checker_rejects_a_wrong_positional_citation_anchor(
    tmp_path: Path,
    field: str,
) -> None:
    programme = json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))
    item = programme["items"][0]
    if field == "bo_occurrence":
        item[field] = item[field] + 1
    else:
        item[field] = "Contenus"
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
    assert item["id"] in report["orphan_quotes"]


@pytest.mark.parametrize(
    ("item_id", "expected_and_old"),
    EXACT_SECTION_ANCHORS.items(),
)
def test_checker_rejects_the_previous_inexact_section_heading(
    tmp_path: Path,
    item_id: str,
    expected_and_old: tuple[str, str],
) -> None:
    programme = json.loads(PROGRAMME_PATH.read_text(encoding="utf-8"))
    item = next(item for item in programme["items"] if item["id"] == item_id)
    item["bo_section"] = expected_and_old[1]
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
    assert report["orphan_quotes"] == [item_id]


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


@pytest.mark.parametrize(
    ("mutation", "expected_fragment"),
    [
        (lambda value: value["items"][0].__setitem__("bo_quote", "   "), "bo_quote"),
        (lambda value: value["source"].__setitem__("title", "   "), "title"),
        (
            lambda value: value["source"].__setitem__("bo_url", "not a URI"),
            "bo_url",
        ),
        (
            lambda value: value["source"].__setitem__("pdf_url", "relative/path"),
            "pdf_url",
        ),
        (
            lambda value: next(
                item
                for item in value["items"]
                if item["editorial_verdict"] == "excluded_with_rationale"
            ).__setitem__("editorial_rationale", "   "),
            "editorial_rationale",
        ),
    ],
)
def test_schema_rejects_blank_editorial_fields_and_invalid_uris(
    programme: dict,
    schema: dict,
    mutation,
    expected_fragment: str,
) -> None:
    altered = json.loads(json.dumps(programme))
    mutation(altered)

    errors = list(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(altered)
    )

    assert errors
    assert expected_fragment in " ".join(
        "/".join(str(part) for part in error.absolute_path)
        for error in errors
    )
