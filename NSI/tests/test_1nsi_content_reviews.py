"""Contrat executable du protocole de revue scientifique et pedagogique 1NSI."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "review_1nsi_content.py"
POLICY_PATH = ROOT / "audit" / "1NSI_CONTENT_REVIEW_POLICY.yaml"
SCHEMA_PATH = ROOT / "audit" / "schemas" / "v1" / "1nsi-content-review.schema.json"
BASE_SHA = "867e10503044688a0b8cee3847647562dce6db45"
PDF_SHA256 = "7ca9a32e1823be6c1120cb0417324c3cb01688d1d194c7614a88ea851ccc60b0"
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
ALLOWED_FILES = {
    "NSI/tests/test_1nsi_content_reviews.py",
    "scripts/review_1nsi_content.py",
    "audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
    "audit/schemas/v1/1nsi-content-review.schema.json",
    "audit/sources/1nsi/programme-premiere-nsi.pdf",
    "audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html",
    "audit/sources/1nsi/eduscol-programmes-nsi.html",
}
CONTRACTUAL_DOCUMENTS = {
    "NSI/docs/01_conception_manuel.md",
    "NSI/docs/02_workflow_production.md",
    "NSI/docs/05_conventions_latex.md",
    "docs/codex/QUALITY_GATES.md",
    "docs/codex/ISSUE_REGISTER_TEMPLATE.md",
}
CANONICAL_PDFS = {
    f"NSI/build/MANUEL_1NSI/MANUEL_1NSI_{variant}.pdf"
    for variant in (
        "amenagee",
        "eleve",
        "evaluations",
        "methodes",
        "professeur",
        "projets",
        "remediation",
    )
}


@pytest.fixture(scope="module")
def review_module():
    if not MODULE_PATH.is_file():
        return None
    spec = importlib.util.spec_from_file_location("review_1nsi_content", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def policy():
    if not POLICY_PATH.is_file():
        return None
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sources(review_module):
    if review_module is None:
        return None
    return review_module.discover_sources(ROOT)


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _contract_refs() -> set[tuple[str, str]]:
    refs = set()
    for path in sorted((ROOT / "NSI" / "chapitres").glob("1NSI-*/contrat.yaml")):
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        refs.update(
            (contract["chapitre"], capacity["ref_capacite"])
            for capacity in contract["capacites"]
        )
    return refs


def _excerpt_digest(path: Path, start: int = 1, end: int = 1) -> str:
    lines = path.read_bytes().splitlines(keepends=True)
    return "sha256:" + hashlib.sha256(b"".join(lines[start - 1 : end])).hexdigest()


def _fact(source: dict, observation: str, *, fact_type: str = "source_statement") -> dict:
    path = ROOT / source["path"]
    return {
        "path": source["path"],
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": _excerpt_digest(path),
        "fact_type": fact_type,
        "observation": observation,
    }


def _finding(source: dict, *, reviewer_id: str = "independent-reviewer") -> dict:
    refs = source.get("capacity_refs", [])
    return {
        "id": source["id"],
        "scope": source["scope"],
        "chapter": source["chapter"],
        "source_path": source["path"],
        "source_status": source["status"],
        "capacity_refs": refs,
        "provenance": {
            "reviewer_id": reviewer_id,
            "review_run_id": "unit-review-run",
            "reviewer_model": "unit-reviewer-model",
            "integrator_id": "integrator",
        },
        "dimensions": {
            "scientific": {
                "verdict": "pass",
                "justification": "Le fait scientifique ancre a ete examine dans cette fixture.",
                "facts": [_fact(source, f"Constat scientifique propre a {source['id']}.")],
                "anomaly_ids": [],
            },
            "pedagogical": {
                "verdict": "pass",
                "justification": "Le fait pedagogique ancre a ete examine dans cette fixture.",
                "facts": [_fact(source, f"Constat pedagogique propre a {source['id']}.")],
                "anomaly_ids": [],
            },
        },
        "anomalies": [],
    }


def test_policy_closes_manual_decision_and_verdicts(policy) -> None:
    assert policy is not None, "la politique de revue doit etre creee"
    assert policy["artifact_type"] == "1nsi_content_review_policy"
    assert policy["manual"] == "1NSI"
    assert policy["decision"]["date"] == "2026-08-10"
    assert policy["decision"]["publication_approval"] is False
    assert policy["decision"]["human_confirmation_required"] is True
    assert policy["decision"]["release_acceptance"] is False
    assert policy["verdicts"] == [
        "pass",
        "issue",
        "not_applicable",
        "human_confirmation_required",
    ]
    assert set(policy["prohibited_transitions"]) == {"approved", "ready", "rejected"}
    assert set(policy["allowlist"]) == ALLOWED_FILES


def test_policy_pins_official_and_contractual_sources(policy, review_module) -> None:
    assert policy is not None, "la politique de revue doit etre creee"
    assert review_module is not None, "le generateur de revue doit etre cree"
    official = policy["official_sources"]
    assert len(official) == 3
    assert {item["kind"] for item in official} == {
        "official_programme_pdf",
        "legifrance_consolidated_text",
        "eduscol_programme_page",
    }
    assert {item["consulted_on"] for item in official} == {"2026-08-10"}
    for item in official:
        snapshot = ROOT / item["snapshot_path"]
        assert snapshot.is_file()
        assert item["sha256"] == _sha(snapshot)
        assert item["url"].startswith("https://")
        assert item["capture_status"] == "content"
        if snapshot.suffix == ".html":
            html = snapshot.read_text(encoding="utf-8")
            assert "Attention Required!" not in html
            assert "Vérification de sécurité en cours" not in html
    assert "Arrêté du 17 janvier 2019" in (
        ROOT / "audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html"
    ).read_text(encoding="utf-8")
    assert "Programme en vigueur" in (
        ROOT / "audit/sources/1nsi/eduscol-programmes-nsi.html"
    ).read_text(encoding="utf-8")
    programme = next(item for item in official if item["kind"] == "official_programme_pdf")
    assert programme["sha256"] == f"sha256:{PDF_SHA256}"

    local = policy["contractual_documents"]
    assert {item["path"] for item in local} == CONTRACTUAL_DOCUMENTS
    assert all(item["sha256"] == _sha(ROOT / item["path"]) for item in local)
    assert SHA256.fullmatch(policy["protocol_digest"])
    assert review_module.compute_protocol_digest(ROOT, policy) == policy["protocol_digest"]


def test_policy_matrix_covers_every_contract_reference_once(policy) -> None:
    assert policy is not None, "la politique de revue doit etre creee"
    rows = policy["capacity_matrix"]
    observed = [(row["chapter"], row["ref"]) for row in rows]
    assert len(observed) == len(set(observed))
    assert set(observed) == _contract_refs()
    assert all(row["programme_section"] and row["programme_anchor"] for row in rows)
    assert all(row["classification"] in {
        "official_capacity",
        "local_reference",
        "transversal_enrichment",
    } for row in rows)

    local = {row["ref"] for row in rows if row["classification"] == "local_reference"}
    enrichments = {
        row["ref"] for row in rows if row["classification"] == "transversal_enrichment"
    }
    assert local == {f"1NSI-TYPES-CONSTRUITS-C{i}" for i in range(1, 6)}
    assert enrichments == {
        "BO-PREAMBULE-DEMARCHE-DE-PROJET",
        "BO-PREAMBULE-COMPETENCES-METHODE",
        "BO-PREAMBULE-COMPETENCES-ORALES",
    }
    assert all(
        row["human_confirmation_required"] is (row["classification"] != "official_capacity")
        for row in rows
    )


def test_protocol_mutation_invalidates_all_dependency_digests(policy, sources, review_module) -> None:
    original = [
        review_module.compute_dependency_digest(source, sources, ROOT, policy)
        for source in sources
    ]
    mutated = copy.deepcopy(policy)
    mutated["protocol_digest"] = "sha256:" + "0" * 64
    changed = [
        review_module.compute_dependency_digest(source, sources, ROOT, mutated)
        for source in sources
    ]
    assert len(original) == 349
    assert all(before != after for before, after in zip(original, changed, strict=True))


def test_discover_sources_is_exact_and_1nsi_only(sources) -> None:
    assert sources is not None, "le generateur de revue doit etre cree"
    assert len(sources) == 349
    assert len({item["id"] for item in sources}) == 349
    assert Counter(item["scope"] for item in sources) == {"object": 339, "contract": 10}
    assert Counter(item["status"] for item in sources if item["scope"] == "object") == {
        "verified": 163,
        "needs_review": 169,
        "manual_review": 7,
    }
    assert Counter(item["status"] for item in sources if item["scope"] == "contract") == {
        "draft": 10
    }
    assert all(item["path"].startswith("NSI/chapitres/1NSI-") for item in sources)
    assert all("TNSI" not in item["id"] + item["chapter"] + item["path"] for item in sources)
    assert all(SHA256.fullmatch(item["source_sha256"]) for item in sources)
    assert all(item["source_sha256"] == _sha(ROOT / item["path"]) for item in sources)


def test_scope_guard_pins_exact_sources_and_immutable_surfaces(policy, sources, review_module) -> None:
    guard = policy["scope_guard"]
    assert guard["implementation_base_sha"] == BASE_SHA
    assert guard["sources"] == [
        {"id": item["id"], "path": item["path"], "status": item["status"]}
        for item in sources
    ]
    assert guard["build_manifest"] == {
        "path": "audit/BUILD_MANIFEST.json",
        "sha256": _sha(ROOT / "audit/BUILD_MANIFEST.json"),
    }
    assert {item["path"] for item in guard["canonical_pdfs"]} == CANONICAL_PDFS
    assert all(item["sha256"] == _sha(ROOT / item["path"]) for item in guard["canonical_pdfs"])
    assert guard["tnsi_tracked_files_count"] == 261
    assert SHA256.fullmatch(guard["tnsi_tracked_files_digest"])
    review_module.verify_scope(ROOT, policy)


@pytest.mark.parametrize("surface", ["source_path", "source_status", "manifest", "pdf", "tnsi"])
def test_verify_scope_rejects_every_guard_drift(policy, review_module, surface) -> None:
    mutated = copy.deepcopy(policy)
    guard = mutated["scope_guard"]
    if surface == "source_path":
        guard["sources"][0]["path"] += ".moved"
    elif surface == "source_status":
        guard["sources"][0]["status"] = "approved"
    elif surface == "manifest":
        guard["build_manifest"]["sha256"] = "sha256:" + "0" * 64
    elif surface == "pdf":
        guard["canonical_pdfs"][0]["sha256"] = "sha256:" + "0" * 64
    else:
        guard["tnsi_tracked_files_digest"] = "sha256:" + "0" * 64
    with pytest.raises(review_module.ReviewValidationError, match="scope"):
        review_module.verify_scope(ROOT, mutated)


def test_verify_scope_rejects_changed_path_outside_allowlist(policy, review_module) -> None:
    review_module.verify_scope(ROOT, policy, changed_paths=sorted(ALLOWED_FILES))
    with pytest.raises(review_module.ReviewValidationError, match="allowlist"):
        review_module.verify_scope(
            ROOT,
            policy,
            changed_paths=["NSI/chapitres/TNSI-ALGORITHMIQUE/contrat.yaml"],
        )


def _schema_entry(index: int) -> dict:
    digest = "sha256:" + f"{index + 1:064x}"[-64:]
    fact = {
        "path": f"NSI/chapitres/1NSI-TEST/cours/OBJ-{index:03d}.tex",
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": digest,
        "fact_type": "source_statement",
        "observation": f"Observation specifique {index}.",
    }
    dimension = {
        "verdict": "pass",
        "justification": f"Justification specifique {index}.",
        "facts": [fact],
        "anomaly_ids": [],
    }
    return {
        "id": f"1NSI-TEST-{index:03d}",
        "scope": "object",
        "chapter": "1NSI-TEST",
        "source_path": fact["path"],
        "source_status": "needs_review",
        "source_sha256": digest,
        "contract_path": "NSI/chapitres/1NSI-TEST/contrat.yaml",
        "capacity_refs": [],
        "protocol_digest": digest,
        "dependency_digest": digest,
        "dependency_digests": {
            key: digest
            for key in (
                "protocol",
                "source",
                "contract",
                "linked_objects",
                "help",
                "correction",
                "receipt",
                "python",
            )
        },
        "provenance": {
            "reviewer_id": "independent-reviewer",
            "review_run_id": "unit-run",
            "reviewer_model": "unit-model",
            "integrator_id": "integrator",
        },
        "dimensions": {
            "scientific": copy.deepcopy(dimension),
            "pedagogical": copy.deepcopy(dimension),
        },
        "anomalies": [],
        "execution_observation": None,
        "publication_approval": False,
        "human_confirmation_required": True,
    }


def test_schema_is_closed_and_requires_exactly_349_entries() -> None:
    assert SCHEMA_PATH.is_file(), "le schema de revue doit etre cree"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["entries"]["minItems"] == 349
    assert schema["properties"]["entries"]["maxItems"] == 349
    assert schema["$defs"]["entry"]["additionalProperties"] is False
    assert schema["$defs"]["fact"]["additionalProperties"] is False
    assert schema["$defs"]["provenance"]["additionalProperties"] is False

    document = {
        "artifact_type": "1nsi_content_reviews",
        "schema_version": 1,
        "manual": "1NSI",
        "protocol_digest": "sha256:" + "1" * 64,
        "publication_approval": False,
        "human_confirmation_required": True,
        "entries": [_schema_entry(index) for index in range(349)],
    }
    Draft202012Validator(schema).validate(document)


def test_schema_rejects_approval_and_unknown_properties() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    document = {
        "artifact_type": "1nsi_content_reviews",
        "schema_version": 1,
        "manual": "1NSI",
        "protocol_digest": "sha256:" + "1" * 64,
        "publication_approval": True,
        "human_confirmation_required": True,
        "entries": [_schema_entry(index) for index in range(349)],
        "unexpected": "forbidden",
    }
    errors = list(Draft202012Validator(schema).iter_errors(document))
    assert len(errors) >= 2


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("digest_supplied", "digest"),
        ("verdict_without_evidence", "preuve"),
        ("pass_with_issue", "pass"),
        ("tnsi_path", "TNSI"),
        ("approval", "approval"),
        ("unknown_ref", "reference"),
        ("reviewer_integrator", "integrateur"),
        ("incomplete_provenance", "provenance"),
        ("bad_excerpt_digest", "extrait"),
        ("evidence_outside_graph", "dependances"),
        ("unknown_field", "champ inconnu"),
    ],
)
def test_reject_invalid_finding(policy, sources, review_module, mutation, message) -> None:
    source = next(item for item in sources if item["scope"] == "object")
    finding = _finding(source)
    if mutation == "digest_supplied":
        finding["source_sha256"] = source["source_sha256"]
    elif mutation == "verdict_without_evidence":
        finding["dimensions"]["scientific"]["facts"] = []
    elif mutation == "pass_with_issue":
        finding["dimensions"]["scientific"]["anomaly_ids"] = ["1NSI-REV-UNIT"]
        finding["anomalies"] = [{
            "id": "1NSI-REV-UNIT",
            "severity": "P0",
            "dimension": "scientific",
            "fact": finding["dimensions"]["scientific"]["facts"][0],
            "consequence": "Consequence de test.",
            "expected_action": "Action de test.",
        }]
    elif mutation == "tnsi_path":
        finding["source_path"] = "NSI/chapitres/TNSI-ALGORITHMIQUE/contrat.yaml"
    elif mutation == "approval":
        finding["publication_approval"] = True
    elif mutation == "unknown_ref":
        finding["capacity_refs"] = ["UNKNOWN-CAPACITY"]
    elif mutation == "reviewer_integrator":
        finding["provenance"]["reviewer_id"] = "integrator"
    elif mutation == "incomplete_provenance":
        finding["provenance"].pop("reviewer_model")
    elif mutation == "evidence_outside_graph":
        fact = finding["dimensions"]["scientific"]["facts"][0]
        fact["path"] = "AGENTS.md"
        fact["excerpt_sha256"] = _excerpt_digest(ROOT / "AGENTS.md")
    elif mutation == "unknown_field":
        finding["approved"] = True
    else:
        finding["dimensions"]["scientific"]["facts"][0]["excerpt_sha256"] = (
            "sha256:" + "0" * 64
        )
    with pytest.raises(review_module.ReviewValidationError, match=message):
        review_module.validate_findings(
            [finding],
            [source],
            ROOT,
            policy,
            require_complete=True,
        )


def test_rejects_missing_and_duplicate_findings(policy, sources, review_module) -> None:
    selected = [item for item in sources if item["scope"] == "object"][:2]
    with pytest.raises(review_module.ReviewValidationError, match="manquante"):
        review_module.validate_findings(
            [_finding(selected[0])], selected, ROOT, policy, require_complete=True
        )
    with pytest.raises(review_module.ReviewValidationError, match="doublon"):
        review_module.validate_findings(
            [_finding(selected[0]), _finding(selected[0])],
            selected,
            ROOT,
            policy,
            require_complete=True,
        )


def test_rejects_normalized_duplicate_observations(policy, sources, review_module) -> None:
    selected = [
        item
        for item in sources
        if item["scope"] == "object" and item["chapter"] == sources[0]["chapter"]
    ][:2]
    findings = [_finding(item) for item in selected]
    findings[0]["dimensions"]["scientific"]["facts"][0]["observation"] = "Meme fait ancre."
    findings[1]["dimensions"]["scientific"]["facts"][0]["observation"] = "  meme   FAIT ancre "
    with pytest.raises(review_module.ReviewValidationError, match="observation"):
        review_module.validate_findings(
            findings, selected, ROOT, policy, require_complete=True
        )


def test_generate_register_is_deterministic_with_fixture(policy, sources, review_module) -> None:
    selected = [item for item in sources if item["scope"] == "object"][:2]
    findings = [_finding(item) for item in selected]
    first = review_module.generate_register(
        findings, ROOT, policy, sources=selected, require_complete=True
    )
    second = review_module.generate_register(
        copy.deepcopy(findings), ROOT, policy, sources=selected, require_complete=True
    )
    assert first == second
    assert first["publication_approval"] is False
    assert first["human_confirmation_required"] is True
    assert len(first["entries"]) == 2
    assert all(SHA256.fullmatch(entry["dependency_digest"]) for entry in first["entries"])


def test_dependency_digest_changes_for_every_required_class(review_module) -> None:
    class_digests = {
        key: "sha256:" + f"{index:064x}"[-64:]
        for index, key in enumerate(
            (
                "protocol",
                "source",
                "contract",
                "linked_objects",
                "help",
                "correction",
                "receipt",
                "python",
            ),
            start=1,
        )
    }
    baseline = review_module.aggregate_dependency_digest(class_digests)
    for key in class_digests:
        mutated = dict(class_digests)
        mutated[key] = "sha256:" + "f" * 64
        assert review_module.aggregate_dependency_digest(mutated) != baseline, key


def test_dependency_graph_contains_bidirectional_help_correction_and_receipt(sources, review_module) -> None:
    exercise = next(item for item in sources if item["id"] == "1NSI-TC-EX-001")
    manifest = review_module.dependency_manifest(exercise, sources, ROOT)
    assert set(manifest) == {
        "source",
        "contract",
        "linked_objects",
        "help",
        "correction",
        "receipt",
        "python",
    }
    assert any(item["path"].endswith("1NSI-TC-EX-001-CDP.tex") for item in manifest["help"])
    assert any(item["path"].endswith("1NSI-TC-CO-001.tex") for item in manifest["correction"])
    assert any(item["path"].endswith("1NSI-TC-EX-001.execution.json") for item in manifest["receipt"])
    linked_paths = {item["path"] for item in manifest["linked_objects"]}
    assert {item["path"] for item in manifest["help"]} <= linked_paths
    assert {item["path"] for item in manifest["correction"]} <= linked_paths


def test_dependency_graph_detects_declared_python_file(tmp_path, review_module) -> None:
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    source_path = chapter / "cours" / "1NSI-UNIT-COURS-C1.tex"
    python_path = chapter / "code" / "example.py"
    contract_path = chapter / "contrat.yaml"
    source_path.parent.mkdir(parents=True)
    python_path.parent.mkdir(parents=True)
    contract_path.write_text("chapitre: 1NSI-UNIT\nstatut: draft\n", encoding="utf-8")
    python_path.write_text("print(42)\n", encoding="utf-8")
    source_path.write_text(
        '% META: {"id":"1NSI-UNIT-COURS-C1","chapitre":"1NSI-UNIT",'
        '"type_objet":"cours","status":"needs_review"}\n'
        "Code publie : \\texttt{code/example.py}.\n",
        encoding="utf-8",
    )
    source = {
        "id": "1NSI-UNIT-COURS-C1",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "needs_review",
        "type": "cours",
        "metadata": {},
    }
    manifest = review_module.dependency_manifest(source, [source], tmp_path)
    assert manifest["python"] == [{
        "path": python_path.relative_to(tmp_path).as_posix(),
        "sha256": _sha(python_path),
    }]


def test_execution_observation_reruns_without_writing_receipt(tmp_path, review_module) -> None:
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    source_path = chapter / "exercices" / "1NSI-UNIT-EX-001.tex"
    receipt_path = chapter / "validations" / "1NSI-UNIT-EX-001.execution.json"
    source_path.parent.mkdir(parents=True)
    receipt_path.parent.mkdir(parents=True)
    source_path.write_text(
        '% META: {"id":"1NSI-UNIT-EX-001","chapitre":"1NSI-UNIT",'
        '"type_objet":"exercice","status":"verified"}\n'
        "% BEGIN-TRACE\n% print(1 + 1)\n% EXPECTED\n% 2\n% END-TRACE\n",
        encoding="utf-8",
    )
    receipt = {
        "objet_id": "1NSI-UNIT-EX-001",
        "gate": "sympy",
        "verdict": "pass",
        "details": {
            "checks": [{"type": "trace", "index": 0, "pass": True, "detail": ""}]
        },
        "reviewer": "verify_python.py",
        "created_at": "2026-08-10T00:00:00+00:00",
    }
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    before = receipt_path.read_bytes()
    source = {
        "id": "1NSI-UNIT-EX-001",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "verified",
    }

    observation = review_module.execution_observation(source, tmp_path)

    assert observation["fresh_verdict"] == "pass"
    assert observation["receipt_verdict"] == "pass"
    assert observation["matches_receipt"] is True
    assert observation["anomalies"] == []
    assert SHA256.fullmatch(observation["check_digest"])
    assert receipt_path.read_bytes() == before

    receipt["details"]["checks"][0]["pass"] = False
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    divergent = review_module.execution_observation(source, tmp_path)
    assert divergent["matches_receipt"] is False
    assert divergent["anomalies"]


def test_generate_register_promotes_receipt_divergence_to_scientific_issue(
    tmp_path, policy, review_module
) -> None:
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    source_path = chapter / "exercices" / "1NSI-UNIT-EX-001.tex"
    receipt_path = chapter / "validations" / "1NSI-UNIT-EX-001.execution.json"
    source_path.parent.mkdir(parents=True)
    receipt_path.parent.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\n", encoding="utf-8"
    )
    source_path.write_text(
        '% META: {"id":"1NSI-UNIT-EX-001","chapitre":"1NSI-UNIT",'
        '"type_objet":"exercice","status":"verified"}\n'
        "% BEGIN-TRACE\n% print(1 + 1)\n% EXPECTED\n% 2\n% END-TRACE\n",
        encoding="utf-8",
    )
    receipt_path.write_text(
        json.dumps({
            "verdict": "pass",
            "details": {
                "checks": [{"type": "trace", "index": 0, "pass": False, "detail": "old"}]
            },
        }),
        encoding="utf-8",
    )
    before = receipt_path.read_bytes()
    source = {
        "id": "1NSI-UNIT-EX-001",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "verified",
        "type": "exercice",
        "capacity_refs": [],
        "metadata": {},
        "source_sha256": _sha(source_path),
    }
    fact = {
        "path": source["path"],
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": _excerpt_digest(source_path),
        "fact_type": "source_statement",
        "observation": "Observation de fixture propre a l'objet unitaire.",
    }
    finding = {
        "id": source["id"],
        "scope": source["scope"],
        "chapter": source["chapter"],
        "source_path": source["path"],
        "source_status": source["status"],
        "capacity_refs": [],
        "provenance": {
            "reviewer_id": "independent-reviewer",
            "review_run_id": "unit-run",
            "reviewer_model": "unit-model",
            "integrator_id": "integrator",
        },
        "dimensions": {
            "scientific": {
                "verdict": "pass",
                "justification": "Fixture scientifique initialement sans anomalie.",
                "facts": [copy.deepcopy(fact)],
                "anomaly_ids": [],
            },
            "pedagogical": {
                "verdict": "pass",
                "justification": "Fixture pedagogique initialement sans anomalie.",
                "facts": [{**fact, "observation": "Observation pedagogique unitaire."}],
                "anomaly_ids": [],
            },
        },
        "anomalies": [],
    }

    document = review_module.generate_register(
        [finding], tmp_path, policy, sources=[source], require_complete=True
    )

    entry = document["entries"][0]
    assert entry["dimensions"]["scientific"]["verdict"] == "issue"
    assert entry["dimensions"]["scientific"]["anomaly_ids"]
    assert entry["anomalies"][0]["severity"] == "P0"
    assert entry["execution_observation"]["matches_receipt"] is False
    assert receipt_path.read_bytes() == before


def test_cli_exposes_required_modes(policy, review_module) -> None:
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    for flag in (
        "--findings",
        "--output-json",
        "--output-summary",
        "--check",
        "--verify-scope",
        "--release-gate",
    ):
        assert flag in result.stdout
    assert review_module.main(["--verify-scope"]) == 0
    assert review_module.main(["--release-gate"]) != 0
