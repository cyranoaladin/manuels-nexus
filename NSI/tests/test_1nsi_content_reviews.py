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
CURRENT_ALLOWED_FILES = {
    "NSI/tests/test_1nsi_content_reviews.py",
    "scripts/review_1nsi_content.py",
    "audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
    "audit/schemas/v1/1nsi-content-review.schema.json",
    "audit/sources/1nsi/programme-premiere-nsi.pdf",
    "audit/sources/1nsi/legifrance-arrete-17-janvier-2019.html",
    "audit/sources/1nsi/eduscol-programmes-nsi.html",
}
REVIEW_OUTPUTS = {
    "audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml",
    "audit/1NSI_CONTENT_REVIEWS.json",
    "audit/1NSI_CONTENT_REVIEW_SUMMARY.md",
}
REVIEW_RUNS = {
    f"audit/reviews/1nsi/runs/2026-08-10-{name}.yaml"
    for name in (
        "contracts",
        "algorithms",
        "systems-web",
        "language-project",
        "data-basics-tables",
        "types-construits",
    )
}
ALLOWED_FILES = CURRENT_ALLOWED_FILES | REVIEW_OUTPUTS | REVIEW_RUNS
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


def _fact(
    source: dict,
    observation: str,
    *,
    fact_type: str = "source_statement",
    root: Path = ROOT,
) -> dict:
    path = root / source["path"]
    return {
        "path": source["path"],
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": _excerpt_digest(path),
        "fact_type": fact_type,
        "observation": observation,
    }


def _finding(
    source: dict,
    *,
    reviewer_id: str = "independent-reviewer",
    provenance: dict | None = None,
    root: Path = ROOT,
) -> dict:
    refs = source.get("capacity_refs", [])
    if provenance is None:
        provenance = {
            "reviewer_id": reviewer_id,
            "review_run_id": "unit-review-run",
            "reviewer_model": "unit-reviewer-model",
            "integrator_id": "integrator",
        }
    return {
        "id": source["id"],
        "scope": source["scope"],
        "chapter": source["chapter"],
        "source_path": source["path"],
        "source_status": source["status"],
        "capacity_refs": refs,
        "provenance": copy.deepcopy(provenance),
        "dimensions": {
            "scientific": {
                "verdict": "pass",
                "justification": "Le fait scientifique ancre a ete examine dans cette fixture.",
                "facts": [
                    _fact(
                        source,
                        f"Constat scientifique propre a {source['id']}.",
                        root=root,
                    )
                ],
                "anomaly_ids": [],
            },
            "pedagogical": {
                "verdict": "pass",
                "justification": "Le fait pedagogique ancre a ete examine dans cette fixture.",
                "facts": [
                    _fact(
                        source,
                        f"Constat pedagogique propre a {source['id']}.",
                        root=root,
                    )
                ],
                "anomaly_ids": [],
            },
        },
        "anomalies": [],
    }


def _git(root: Path, *args: str, input_text: str | None = None) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        input=input_text,
    ).stdout.strip()


def _review_run_receipt(
    policy: dict,
    sources: list[dict],
    root: Path,
    *,
    review_run_id: str,
    reviewer_id: str,
    reviewer_model: str,
) -> dict:
    scopes = {source["scope"] for source in sources}
    assert len(scopes) == 1
    reviews = []
    for source in sources:
        finding = _finding(source, root=root)
        reviews.append({
            "id": source["id"],
            "chapter": source["chapter"],
            "scope": source["scope"],
            "payload": {
                "dimensions": finding["dimensions"],
                "anomalies": finding["anomalies"],
            },
        })
    return {
        "artifact_type": "1nsi_review_run",
        "schema_version": 1,
        "manual": "1NSI",
        "review_run_id": review_run_id,
        "reviewer_id": reviewer_id,
        "reviewer_model": reviewer_model,
        "protocol_digest": policy["protocol_digest"],
        "reviewed_at": "2026-08-10T12:00:00+00:00",
        "assignment": {
            "scope": scopes.pop(),
            "chapters": sorted({source["chapter"] for source in sources}),
            "source_ids": sorted(source["id"] for source in sources),
        },
        "reviews": reviews,
    }


def _reseal_review_receipt(sealed_review: dict, receipt: dict) -> None:
    path = sealed_review["receipt_path"]
    path.write_text(
        yaml.safe_dump(receipt, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    root = sealed_review["root"]
    _git(root, "add", path.relative_to(root).as_posix())
    _git(root, "commit", "-q", "-m", "reseal review receipt")
    sealed_review["provenance"]["review_receipt_sha256"] = _sha(path)
    sealed_review["provenance"]["sealing_commit_sha"] = _git(root, "rev-parse", "HEAD")


@pytest.fixture
def sealed_review(tmp_path, policy):
    chapter = tmp_path / "NSI" / "chapitres" / "1NSI-UNIT"
    contract_path = chapter / "contrat.yaml"
    receipt_path = tmp_path / "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml"
    object_paths = [
        chapter / "exercices" / "1NSI-UNIT-EX-001.tex",
        chapter / "exercices" / "1NSI-UNIT-EX-002.tex",
    ]
    contract_path.parent.mkdir(parents=True)
    receipt_path.parent.mkdir(parents=True)
    object_paths[0].parent.mkdir(parents=True)
    contract_path.write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\ncapacites: []\n", encoding="utf-8"
    )
    sources = []
    for index, path in enumerate(object_paths, start=1):
        object_id = f"1NSI-UNIT-EX-{index:03d}"
        path.write_text(
            f'% META: {{"id":"{object_id}","chapitre":"1NSI-UNIT",'
            '"type_objet":"exercice","status":"verified"}}\n'
            f"Contenu unitaire {index}.\n",
            encoding="utf-8",
        )
        sources.append(
            {
                "id": object_id,
                "scope": "object",
                "chapter": "1NSI-UNIT",
                "path": path.relative_to(tmp_path).as_posix(),
                "status": "verified",
                "type": "exercice",
                "capacity_refs": [],
                "metadata": {},
                "source_sha256": _sha(path),
            }
        )
    receipt = _review_run_receipt(
        policy,
        sources,
        tmp_path,
        review_run_id="unit-review-run",
        reviewer_id="independent-reviewer",
        reviewer_model="unit-reviewer-model",
    )
    receipt_path.write_text(
        yaml.safe_dump(receipt, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Nexus Tests")
    _git(tmp_path, "config", "user.email", "nexus-tests@example.invalid")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "seal review receipt")
    sealing_commit = _git(tmp_path, "rev-parse", "HEAD")
    provenance = {
        "reviewer_id": "independent-reviewer",
        "review_run_id": "unit-review-run",
        "reviewer_model": "unit-reviewer-model",
        "integrator_id": "integrator",
        "review_receipt_path": receipt_path.relative_to(tmp_path).as_posix(),
        "review_receipt_sha256": _sha(receipt_path),
        "sealing_commit_sha": sealing_commit,
    }
    return {
        "root": tmp_path,
        "policy": copy.deepcopy(policy),
        "sources": sources,
        "provenance": provenance,
        "receipt_path": receipt_path,
        "receipt": receipt,
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
    assert policy["review_dimensions"] == ["scientific", "pedagogical"]
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


@pytest.mark.parametrize(
    "mutation",
    ["decision", "verdicts", "prohibited_transitions", "review_dimensions", "capacity_matrix"],
)
def test_protocol_digest_seals_every_governance_rule(
    policy, review_module, mutation
) -> None:
    mutated = copy.deepcopy(policy)
    if mutation == "decision":
        mutated["decision"]["release_acceptance"] = True
    elif mutation == "verdicts":
        mutated["verdicts"].reverse()
    elif mutation == "prohibited_transitions":
        mutated["prohibited_transitions"].append("silently_approved")
    elif mutation == "review_dimensions":
        mutated["review_dimensions"].reverse()
    else:
        mutated["capacity_matrix"][0]["programme_anchor"] += " Mutation de test."

    assert review_module.compute_protocol_digest(ROOT, mutated) != policy["protocol_digest"]


def test_protocol_payload_contains_exactly_eight_source_records(policy, review_module) -> None:
    records = review_module._protocol_records(policy)
    assert len(records) == 8
    assert {record["path"] for record in records} == {
        *(item["snapshot_path"] for item in policy["official_sources"]),
        *(item["path"] for item in policy["contractual_documents"]),
    }


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
    review_module.verify_scope(ROOT, policy, changed_paths=sorted(REVIEW_OUTPUTS | REVIEW_RUNS))
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
            "review_receipt_path": "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml",
            "review_receipt_sha256": digest,
            "sealing_commit_sha": "1" * 40,
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
    assert set(schema["$defs"]["provenance"]["required"]) == {
        "reviewer_id",
        "review_run_id",
        "reviewer_model",
        "integrator_id",
        "review_receipt_path",
        "review_receipt_sha256",
        "sealing_commit_sha",
    }

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


def test_review_run_receipt_schema_is_closed_and_validates_yaml(sealed_review) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    receipt_schema = schema["$defs"]["review_run_receipt"]
    assert receipt_schema["additionalProperties"] is False
    assert receipt_schema["properties"]["assignment"]["additionalProperties"] is False
    review_schema = receipt_schema["properties"]["reviews"]["items"]
    assert review_schema["additionalProperties"] is False
    assert set(review_schema["required"]) == {"id", "chapter", "scope", "payload"}
    assert review_schema["properties"]["payload"]["additionalProperties"] is False
    wrapper = {
        "$schema": schema["$schema"],
        "$ref": "#/$defs/review_run_receipt",
        "$defs": schema["$defs"],
    }
    Draft202012Validator.check_schema(wrapper)
    parsed = yaml.safe_load(sealed_review["receipt_path"].read_text(encoding="utf-8"))
    Draft202012Validator(wrapper).validate(parsed)


def test_accepts_finding_with_git_sealed_review_receipt(sealed_review, review_module) -> None:
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )

    validated = review_module.validate_findings(
        [finding],
        [source],
        sealed_review["root"],
        sealed_review["policy"],
        require_complete=True,
    )

    assert validated[0]["provenance"] == sealed_review["provenance"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("run", "review_run_id"),
        ("reviewer", "reviewer_id"),
        ("model", "reviewer_model"),
        ("protocol", "protocol_digest"),
        ("source_not_assigned", "source non assignee"),
        ("review_absent", "review absente"),
        ("review_duplicated", "review dupliquee"),
        ("assignment_chapter", "chapitre d'affectation"),
        ("assignment_scope", "scope d'affectation"),
        ("review_chapter", "chapitre de review"),
        ("review_scope", "scope de review"),
        ("schema_extra", "schema du recu"),
    ],
)
def test_rejects_review_receipt_not_bound_to_current_finding(
    sealed_review, review_module, mutation, message
) -> None:
    receipt = copy.deepcopy(sealed_review["receipt"])
    source = sealed_review["sources"][0]
    if mutation == "run":
        receipt["review_run_id"] = "another-run"
    elif mutation == "reviewer":
        receipt["reviewer_id"] = "another-reviewer"
    elif mutation == "model":
        receipt["reviewer_model"] = "another-model"
    elif mutation == "protocol":
        receipt["protocol_digest"] = "sha256:" + "0" * 64
    elif mutation == "source_not_assigned":
        receipt["assignment"]["source_ids"].remove(source["id"])
    elif mutation == "review_absent":
        receipt["reviews"] = [
            review for review in receipt["reviews"] if review["id"] != source["id"]
        ]
    elif mutation == "review_duplicated":
        receipt["reviews"].append(copy.deepcopy(receipt["reviews"][0]))
    elif mutation == "assignment_chapter":
        receipt["assignment"]["chapters"] = ["1NSI-OTHER"]
    elif mutation == "assignment_scope":
        receipt["assignment"]["scope"] = "contract"
    elif mutation == "review_chapter":
        receipt["reviews"][0]["chapter"] = "1NSI-OTHER"
    elif mutation == "review_scope":
        receipt["reviews"][0]["scope"] = "contract"
    else:
        receipt["unexpected"] = "forbidden"
    _reseal_review_receipt(sealed_review, receipt)
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )

    with pytest.raises(review_module.ReviewValidationError, match=message):
        review_module.validate_findings(
            [finding],
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("path", "recu de revue"),
        ("extra_run_path", "recu de revue"),
        ("digest", "digest du recu"),
        ("commit", "commit de scellement"),
        ("not_in_commit", "absent du commit"),
        ("not_ancestor", "ancetre"),
        ("worktree_drift", "octets du recu"),
    ],
)
def test_rejects_unsealed_review_receipt(
    sealed_review, review_module, mutation, message
) -> None:
    root = sealed_review["root"]
    provenance = copy.deepcopy(sealed_review["provenance"])
    if mutation == "path":
        provenance["review_receipt_path"] = "audit/1NSI_CONTENT_REVIEWS.json"
    elif mutation == "extra_run_path":
        path = root / "audit/reviews/1nsi/runs/2026-08-10-unplanned.yaml"
        path.write_text("run_id: unplanned\n", encoding="utf-8")
        _git(root, "add", path.relative_to(root).as_posix())
        _git(root, "commit", "-q", "-m", "seal unplanned receipt")
        provenance["review_receipt_path"] = path.relative_to(root).as_posix()
        provenance["review_receipt_sha256"] = _sha(path)
        provenance["sealing_commit_sha"] = _git(root, "rev-parse", "HEAD")
        sealed_review["policy"]["allowlist"].append(provenance["review_receipt_path"])
    elif mutation == "digest":
        provenance["review_receipt_sha256"] = "sha256:" + "0" * 64
    elif mutation == "commit":
        provenance["sealing_commit_sha"] = "0" * 40
    elif mutation == "not_in_commit":
        path = root / "audit/reviews/1nsi/runs/2026-08-10-algorithms.yaml"
        path.write_text("run_id: not-committed\n", encoding="utf-8")
        provenance["review_receipt_path"] = path.relative_to(root).as_posix()
        provenance["review_receipt_sha256"] = _sha(path)
    elif mutation == "not_ancestor":
        tree = _git(root, "rev-parse", "HEAD^{tree}")
        provenance["sealing_commit_sha"] = _git(
            root, "commit-tree", tree, input_text="unrelated seal\n"
        )
    else:
        sealed_review["receipt_path"].write_text("run_id: modified\n", encoding="utf-8")

    source = sealed_review["sources"][0]
    finding = _finding(source, provenance=provenance, root=root)
    with pytest.raises(review_module.ReviewValidationError, match=message):
        review_module.validate_findings(
            [finding], [source], root, sealed_review["policy"], require_complete=True
        )


@pytest.mark.parametrize(
    ("dimension_name", "verdict"),
    [
        ("scientific", "human_confirmation_required"),
        ("pedagogical", "not_applicable"),
    ],
)
def test_dimension_with_anomaly_requires_issue_verdict(
    sealed_review, review_module, dimension_name, verdict
) -> None:
    source = sealed_review["sources"][0]
    finding = _finding(
        source,
        provenance=sealed_review["provenance"],
        root=sealed_review["root"],
    )
    anomaly_id = "1NSI-REV-UNIT-DIMENSION"
    finding["dimensions"][dimension_name]["verdict"] = verdict
    finding["dimensions"][dimension_name]["anomaly_ids"] = [anomaly_id]
    finding["anomalies"] = [{
        "id": anomaly_id,
        "severity": "P1",
        "dimension": dimension_name,
        "fact": copy.deepcopy(finding["dimensions"][dimension_name]["facts"][0]),
        "consequence": "Consequence dimensionnelle de test.",
        "expected_action": "Action dimensionnelle de test.",
    }]

    with pytest.raises(review_module.ReviewValidationError, match="verdict issue"):
        review_module.validate_findings(
            [finding],
            [source],
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


def _approved_release_fixture(policy) -> tuple[dict, dict]:
    approved_policy = copy.deepcopy(policy)
    approved_policy["decision"].update({
        "publication_approval": True,
        "human_confirmation_required": False,
        "release_acceptance": True,
    })
    entry = _schema_entry(0)
    entry["publication_approval"] = True
    entry["human_confirmation_required"] = False
    document = {
        "publication_approval": True,
        "human_confirmation_required": False,
        "entries": [entry],
    }
    return approved_policy, document


def test_release_gate_can_pass_only_fully_approved_clean_document(policy, review_module) -> None:
    approved_policy, document = _approved_release_fixture(policy)
    assert review_module.release_gate_allows(document, approved_policy) is True


@pytest.mark.parametrize(
    "blocker",
    [
        "policy_publication_false",
        "policy_human_confirmation",
        "document_publication_false",
        "document_human_confirmation",
        "entry_publication_false",
        "entry_human_confirmation",
        "entry_anomaly",
        "entry_issue",
        "entry_human_verdict",
    ],
)
def test_release_gate_rejects_every_document_or_entry_blocker(
    policy, review_module, blocker
) -> None:
    approved_policy, document = _approved_release_fixture(policy)
    entry = document["entries"][0]
    if blocker == "policy_publication_false":
        approved_policy["decision"]["publication_approval"] = False
    elif blocker == "policy_human_confirmation":
        approved_policy["decision"]["human_confirmation_required"] = True
    elif blocker == "document_publication_false":
        document["publication_approval"] = False
    elif blocker == "document_human_confirmation":
        document["human_confirmation_required"] = True
    elif blocker == "entry_publication_false":
        entry["publication_approval"] = False
    elif blocker == "entry_human_confirmation":
        entry["human_confirmation_required"] = True
    elif blocker == "entry_anomaly":
        entry["anomalies"] = [{"id": "1NSI-REV-RELEASE"}]
    elif blocker == "entry_issue":
        entry["dimensions"]["scientific"]["verdict"] = "issue"
    else:
        entry["dimensions"]["pedagogical"]["verdict"] = "human_confirmation_required"

    assert review_module.release_gate_allows(document, approved_policy) is False


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("digest_supplied", "digest"),
        ("verdict_without_evidence", "preuve"),
        ("pass_with_issue", "verdict issue"),
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
def test_reject_invalid_finding(
    sealed_review, review_module, mutation, message
) -> None:
    root = sealed_review["root"]
    policy = sealed_review["policy"]
    source = sealed_review["sources"][0]
    finding = _finding(source, provenance=sealed_review["provenance"], root=root)
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
        outside = root / "outside.txt"
        outside.write_text("preuve hors graphe\n", encoding="utf-8")
        fact = finding["dimensions"]["scientific"]["facts"][0]
        fact["path"] = "outside.txt"
        fact["excerpt_sha256"] = _excerpt_digest(outside)
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
            root,
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


def test_rejects_normalized_duplicate_observations(sealed_review, review_module) -> None:
    selected = sealed_review["sources"]
    findings = [
        _finding(
            item,
            provenance=sealed_review["provenance"],
            root=sealed_review["root"],
        )
        for item in selected
    ]
    findings[0]["dimensions"]["scientific"]["facts"][0]["observation"] = "Meme fait ancre."
    findings[1]["dimensions"]["scientific"]["facts"][0]["observation"] = "  meme   FAIT ancre "
    with pytest.raises(review_module.ReviewValidationError, match="observation"):
        review_module.validate_findings(
            findings,
            selected,
            sealed_review["root"],
            sealed_review["policy"],
            require_complete=True,
        )


def test_generate_register_is_deterministic_with_fixture(sealed_review, review_module) -> None:
    selected = sealed_review["sources"]
    findings = [
        _finding(
            item,
            provenance=sealed_review["provenance"],
            root=sealed_review["root"],
        )
        for item in selected
    ]
    first = review_module.generate_register(
        findings,
        sealed_review["root"],
        sealed_review["policy"],
        sources=selected,
        require_complete=True,
    )
    second = review_module.generate_register(
        copy.deepcopy(findings),
        sealed_review["root"],
        sealed_review["policy"],
        sources=selected,
        require_complete=True,
    )
    assert first == second
    assert first["publication_approval"] is False
    assert first["human_confirmation_required"] is True
    assert len(first["entries"]) == 2
    assert all(SHA256.fullmatch(entry["dependency_digest"]) for entry in first["entries"])


@pytest.mark.parametrize(
    "dependency_class",
    [
        "protocol",
        "source",
        "contract",
        "linked_objects",
        "help",
        "correction",
        "receipt",
        "python",
    ],
)
def test_real_dependency_mutation_changes_required_class_digest(
    tmp_path, policy, review_module, dependency_class
) -> None:
    chapter = tmp_path / "NSI/chapitres/1NSI-UNIT"
    paths = {
        "source": chapter / "exercices/1NSI-UNIT-EX-001.tex",
        "contract": chapter / "contrat.yaml",
        "linked_objects": chapter / "exercices/1NSI-UNIT-LINKED.tex",
        "help": chapter / "methodes/1NSI-UNIT-HELP.tex",
        "correction": chapter / "corriges/1NSI-UNIT-CORR.tex",
        "receipt": chapter / "validations/1NSI-UNIT-EX-001.execution.json",
        "python": chapter / "code/example.py",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["contract"].write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\ncapacites: []\n", encoding="utf-8"
    )
    paths["source"].write_text(
        '% META: {"id":"1NSI-UNIT-EX-001","chapitre":"1NSI-UNIT",'
        '"type_objet":"exercice","status":"verified"}\n'
        "Code publie : \\texttt{code/example.py}.\n",
        encoding="utf-8",
    )
    paths["linked_objects"].write_text("Objet lie.\n", encoding="utf-8")
    paths["help"].write_text("Aide liee.\n", encoding="utf-8")
    paths["correction"].write_text("Corrige lie.\n", encoding="utf-8")
    paths["receipt"].write_text(
        json.dumps({"verdict": "pass", "details": {"checks": []}}), encoding="utf-8"
    )
    paths["python"].write_text("print(42)\n", encoding="utf-8")

    def source_record(object_id: str, key: str, object_type: str, metadata: dict) -> dict:
        path = paths[key]
        return {
            "id": object_id,
            "scope": "object",
            "chapter": "1NSI-UNIT",
            "path": path.relative_to(tmp_path).as_posix(),
            "status": "verified",
            "type": object_type,
            "capacity_refs": [],
            "metadata": metadata,
            "source_sha256": _sha(path),
        }

    source = source_record(
        "1NSI-UNIT-EX-001",
        "source",
        "exercice",
        {"corrige_tex": paths["correction"].relative_to(tmp_path / "NSI").as_posix()},
    )
    sources = [
        source,
        source_record(
            "1NSI-UNIT-LINKED",
            "linked_objects",
            "exercice",
            {"exercice_ref": source["id"]},
        ),
        source_record(
            "1NSI-UNIT-HELP",
            "help",
            "coup_de_pouce",
            {"exercice_ref": source["id"]},
        ),
        source_record(
            "1NSI-UNIT-CORR",
            "correction",
            "corrige",
            {"exercice_ref": source["id"]},
        ),
    ]
    mutable_policy = copy.deepcopy(policy)
    before = review_module.dependency_class_digests(
        source, sources, tmp_path, mutable_policy
    )
    before_aggregate = review_module.aggregate_dependency_digest(before)

    if dependency_class == "protocol":
        mutable_policy["protocol_digest"] = "sha256:" + "f" * 64
    else:
        paths[dependency_class].write_text(
            paths[dependency_class].read_text(encoding="utf-8") + "mutation\n",
            encoding="utf-8",
        )

    after = review_module.dependency_class_digests(
        source, sources, tmp_path, mutable_policy
    )
    assert after[dependency_class] != before[dependency_class]
    assert review_module.aggregate_dependency_digest(after) != before_aggregate


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


@pytest.mark.parametrize(
    ("object_id", "receipt_stem"),
    [
        ("1NSI-TC-TD1", "07_td1_station_meteo"),
        ("1NSI-TC-TD2", "07_td2_classement_esport"),
    ],
)
def test_receipt_resolution_uses_real_source_stem_for_td(
    sources, review_module, object_id, receipt_stem
) -> None:
    source = next(item for item in sources if item["id"] == object_id)
    manifest = review_module.dependency_manifest(source, sources, ROOT)

    assert manifest["receipt"] == [{
        "path": (
            "NSI/chapitres/1NSI-TYPES-CONSTRUITS/validations/"
            f"{receipt_stem}.execution.json"
        ),
        "sha256": _sha(
            ROOT
            / "NSI/chapitres/1NSI-TYPES-CONSTRUITS/validations"
            / f"{receipt_stem}.execution.json"
        ),
    }]
    observation = review_module.execution_observation(source, ROOT)
    assert observation["receipt_sha256"] == manifest["receipt"][0]["sha256"]
    assert "missing_receipt" not in observation["anomalies"]


def test_receipt_resolution_rejects_distinct_id_and_stem_candidates(
    tmp_path, review_module
) -> None:
    chapter = tmp_path / "NSI/chapitres/1NSI-UNIT"
    source_path = chapter / "cours/source-stem.tex"
    validations = chapter / "validations"
    source_path.parent.mkdir(parents=True)
    validations.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        "chapitre: 1NSI-UNIT\nstatut: draft\ncapacites: []\n", encoding="utf-8"
    )
    source_path.write_text(
        '% META: {"id":"META-ID","chapitre":"1NSI-UNIT",'
        '"type_objet":"cours","status":"verified"}\n'
        "% BEGIN-TRACE\n% print(2)\n% EXPECTED\n% 2\n% END-TRACE\n",
        encoding="utf-8",
    )
    for name in ("META-ID", "source-stem"):
        (validations / f"{name}.execution.json").write_text(
            json.dumps({"verdict": "pass", "details": {"checks": []}}),
            encoding="utf-8",
        )
    source = {
        "id": "META-ID",
        "scope": "object",
        "chapter": "1NSI-UNIT",
        "path": source_path.relative_to(tmp_path).as_posix(),
        "status": "verified",
        "type": "cours",
        "capacity_refs": [],
        "metadata": {},
    }

    with pytest.raises(review_module.ReviewValidationError, match="candidats de recu"):
        review_module.dependency_manifest(source, [source], tmp_path)


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
    assert divergent["anomalies"] == ["execution_receipt_diverged"]

    receipt_path.unlink()
    missing = review_module.execution_observation(source, tmp_path)
    assert missing["matches_receipt"] is False
    assert missing["anomalies"] == ["missing_receipt"]

    source_path.write_text(
        source_path.read_text(encoding="utf-8").replace("% 2\n% END-TRACE", "% 3\n% END-TRACE"),
        encoding="utf-8",
    )
    failed = review_module.execution_observation(source, tmp_path)
    assert failed["fresh_verdict"] == "fail"
    assert failed["anomalies"] == ["fresh_execution_failed"]


@pytest.mark.parametrize(
    ("anomaly_code", "severity", "dimension"),
    [
        ("fresh_execution_failed", "P0", "scientific"),
        ("missing_receipt", "P1", "traceability"),
        ("execution_receipt_diverged", "P1", "traceability"),
    ],
)
def test_execution_anomaly_severity_matches_failure_class(
    sealed_review, review_module, anomaly_code, severity, dimension
) -> None:
    anomaly = review_module._execution_anomaly(
        sealed_review["sources"][0],
        {"anomalies": [anomaly_code]},
        sealed_review["root"],
    )
    assert anomaly["severity"] == severity
    assert anomaly["dimension"] == dimension


def test_generate_register_marks_receipt_divergence_as_p1_traceability(
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
    review_receipt = tmp_path / "audit/reviews/1nsi/runs/2026-08-10-contracts.yaml"
    review_receipt.parent.mkdir(parents=True)
    review_receipt.write_text(
        yaml.safe_dump(
            _review_run_receipt(
                policy,
                [source],
                tmp_path,
                review_run_id="unit-run",
                reviewer_id="independent-reviewer",
                reviewer_model="unit-model",
            ),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Nexus Tests")
    _git(tmp_path, "config", "user.email", "nexus-tests@example.invalid")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "seal execution review")
    before = receipt_path.read_bytes()
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
            "review_receipt_path": review_receipt.relative_to(tmp_path).as_posix(),
            "review_receipt_sha256": _sha(review_receipt),
            "sealing_commit_sha": _git(tmp_path, "rev-parse", "HEAD"),
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
    assert entry["dimensions"]["scientific"]["verdict"] == "pass"
    assert entry["dimensions"]["scientific"]["anomaly_ids"] == []
    assert entry["anomalies"][0]["severity"] == "P1"
    assert entry["anomalies"][0]["dimension"] == "traceability"
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
