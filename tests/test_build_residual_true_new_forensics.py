from __future__ import annotations

import copy
import importlib.util
import json
from itertools import combinations
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_residual_true_new_forensics.py"
INITIAL_JSON = ROOT / "audit" / "TRUE_NEW_18_FORENSICS.json"
INITIAL_MD = ROOT / "audit" / "TRUE_NEW_18_FORENSICS.md"
INVENTORY = ROOT / "audit" / "INVENTAIRE_COLLECTION.json"
REMOVED_FINGERPRINTS = {
    "265dbdeec1fc2b62",
    "2e189d4bed9a9520",
    "7c204b3da8fcb9a9",
    "e79a0d7257787b02",
    "fac802b8993558c3",
}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_module():
    assert SCRIPT.is_file(), "le générateur résiduel doit exister"
    spec = importlib.util.spec_from_file_location(
        "build_residual_true_new_forensics",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inventory_copy(tmp_path: Path) -> Path:
    target = tmp_path / "INVENTAIRE_COLLECTION.json"
    target.write_bytes(INVENTORY.read_bytes())
    return target


def test_builds_exact_residual_without_mutating_frozen_inputs(tmp_path: Path) -> None:
    module = _load_module()
    frozen_before = {
        INITIAL_JSON: INITIAL_JSON.read_bytes(),
        INITIAL_MD: INITIAL_MD.read_bytes(),
    }

    reports = module.build_reports(ROOT)
    module.write_reports(reports, tmp_path)
    first_bytes = {
        path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())
    }
    module.write_reports(reports, tmp_path)

    assert {path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())} == (
        first_bytes
    )
    assert {path: path.read_bytes() for path in frozen_before} == frozen_before
    assert set(first_bytes) == {
        "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json",
        "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.md",
        "RESIDUAL_TRUE_NEW_FORENSICS.json",
        "RESIDUAL_TRUE_NEW_FORENSICS.md",
    }

    residual = reports["residual_forensics"]
    algebra = reports["residual_algebra"]
    forensic_source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert residual["forensic_source_sha"] == forensic_source_sha
    assert algebra["forensic_source_sha"] == forensic_source_sha
    expected_counts = {
        "TRUE_NEW_INITIAL": 18,
        "FIXED": 0,
        "REMOVED": 5,
        "REVIEW_CLOSED": 0,
        "CONTENT_FINDINGS_FIXED": 5,
        "NEW_AFTER_TRIAGE": 0,
        "RESIDUAL_TRUE_NEW": 13,
    }
    assert residual["counts"] == expected_counts
    assert algebra["counts"] == expected_counts
    assert len(residual["entries"]) == 13
    assert algebra["equalities"] == {
        "initial_still_active_open_debt": True,
        "no_new_after_triage": True,
        "residual_equation": True,
    }
    assert set(algebra["sets"]["REMOVED"]) == REMOVED_FINGERPRINTS
    assert algebra["sets"]["NEW_AFTER_TRIAGE"] == []
    full = algebra["full_current_algebra"]
    # Chaque dette declaree separement est un composant NOMME et disjoint de
    # l'algebre courante, jamais fondu dans le residuel gele des 18. La
    # campagne en ajoute un par chapitre qui cree des objets.
    # 2248 depuis le 2026-08-30 : deux corriges d'evaluation a
    # 1NSI-TYPES-CONSTRUITS et le QCM de TNSI-PROJET, chacun porte par son
    # registre. Chaque terme de l'equation a une autorite contractuelle.
    # 2293 depuis la reconstruction de TSPE-GEOMETRIE-ESPACE : 45 objets que
    # la machine a verifies et qu'aucun humain n'a relus, portes par leur
    # propre registre plutot que fondus dans un terme existant.
    # 2325 depuis la reconstruction couplee 1NSI : 36 objets neufs portes par
    # leur registre. APPROVED_TRANSITION_NEW passe de 9 a 5 : quatre
    # empreintes ont ete SUPERSEDEES par la reecriture des evaluations, et une
    # empreinte que la reecriture a fait disparaitre ne peut plus figurer dans
    # la partition courante.
    assert full["cardinality_equation"] == (
        "2325 = 2121 + 5 + 89 + 13 + 12 + 1 + 2 + 1 + 45 + 36"
    )
    assert full["cardinalities"]["CURRENT_ACTIVE"] == 2325
    assert full["cardinalities"]["APPROVED_TRANSITION_NEW"] == 5
    assert full["cardinalities"]["TRUE_NEW"] == 13
    assert full["cardinalities"]["VARALEA_C6C7_REVIEW_DEBT_12"] == 12
    assert full["cardinalities"]["EXPONENTIELLE_C1_METHOD_REVIEW_DEBT_1"] == 1
    assert full["cardinalities"]["NSI_TC_EVAL_CORRIGES_REVIEW_DEBT_2"] == 2
    assert full["cardinalities"]["TNSI_PROJET_QCM_REVIEW_DEBT_1"] == 1
    assert full["cardinalities"]["TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45"] == 45
    assert full["cardinalities"]["NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT"] == 36
    declared = (
        "VARALEA_C6C7_REVIEW_DEBT_12",
        "EXPONENTIELLE_C1_METHOD_REVIEW_DEBT_1",
        "NSI_TC_EVAL_CORRIGES_REVIEW_DEBT_2",
        "TNSI_PROJET_QCM_REVIEW_DEBT_1",
        "TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45",
        "NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT",
    )
    # La dette de revue se partitionne : aucune intersection deux a deux, y
    # compris avec le residuel gele. Le test n'echantillonnait que deux
    # paires ; une dette comptee deux fois passait donc inapercue.
    partition = {name: set(full["sets"][name]) for name in declared}
    partition["TRUE_NEW"] = set(full["sets"]["TRUE_NEW"])
    for left, right in combinations(sorted(partition), 2):
        assert partition[left].isdisjoint(partition[right]), (left, right)
    assert sum(len(members) for members in partition.values()) == len(
        set().union(*partition.values())
    )
    assert full["equalities"]["current_partition"] is True
    assert full["equalities"]["current_partition_pairwise_disjoint"] is True
    assert full["unknown_count"] == 0

    required = {
        "fingerprint",
        "object_id",
        "path",
        "category",
        "why_legitimate",
        "why_cannot_close",
        "current_review_state",
        "owner",
        "closure_phase",
        "release_acceptance",
        "source_sha",
        "triage_class",
        "reason_created",
        "class_b_eligibility",
    }
    assert all(required <= set(entry) for entry in residual["entries"])
    assert all(
        entry["triage_class"] == "LEGITIMATE_REVIEW_DEBT"
        and entry["current_review_state"]
        == "PENDING_QUALIFIED_OPEN_DEBT"
        and entry["release_acceptance"] is False
        and entry["source_sha"].startswith("sha256:")
        and "qualified=true" in entry["why_cannot_close"]
        for entry in residual["entries"]
    )
    assert all(
        all(value in {"PASS", "NO"} for value in entry["class_b_eligibility"].values())
        for entry in residual["entries"]
    )


def test_check_reuses_frozen_source_sha_only_for_report_only_commits(
    tmp_path: Path,
) -> None:
    module = _load_module()
    repo = tmp_path / "repo"
    audit = repo / "audit"
    audit.mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "source")
    source_sha = _git(repo, "rev-parse", "HEAD")

    for names in module.OUTPUT_NAMES.values():
        (audit / names["json"]).write_text(
            json.dumps({"forensic_source_sha": source_sha}) + "\n",
            encoding="utf-8",
        )
        (audit / names["md"]).write_text("report\n", encoding="utf-8")
    _git(repo, "add", "audit")
    _git(repo, "commit", "-m", "reports")

    assert module._forensic_source_sha_for_check(repo, audit) == source_sha

    (repo / "source.txt").write_text("changed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sources modifiées depuis le gel"):
        module._forensic_source_sha_for_check(repo, audit)

    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    (repo / "untracked-object.yaml").write_text("new: object\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sources modifiées depuis le gel"):
        module._forensic_source_sha_for_check(repo, audit)


def test_build_revalidates_source_snapshot_after_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    repo = tmp_path / "repo"
    audit = repo / "audit"
    audit.mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "source")
    source_sha = _git(repo, "rev-parse", "HEAD")

    def mutate_during_build(*args, **kwargs):
        (repo / "late-object.yaml").write_text("late: object\n", encoding="utf-8")
        return {}

    monkeypatch.setattr(module, "build_reports", mutate_during_build)
    with pytest.raises(ValueError, match="sources modifiées depuis le gel"):
        module._build_reports_with_stable_source(repo, audit, source_sha)


def test_rejects_any_unexpected_active_unqualified_fingerprint(
    tmp_path: Path,
) -> None:
    module = _load_module()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    inventory["anomaly_qualifications"]["ffffffffffffffff"] = {
        "blocking": True,
        "categories": ["blocking_statuses"],
        "category": "blocking_statuses",
        "disposition": "open_debt",
        "fingerprint": "ffffffffffffffff",
        "occurrence_count": 1,
        "qualified": False,
        "raw_identities": ["f" * 64],
    }
    mutated = tmp_path / "inventory-extra.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="ensemble actif non qualifié inattendu",
    ):
        module.build_reports(ROOT, inventory_path=mutated)


def test_rejects_a_qualified_residual_that_stops_blocking_release(
    tmp_path: Path,
) -> None:
    module = _load_module()
    inventory = copy.deepcopy(json.loads(INVENTORY.read_text(encoding="utf-8")))
    initial = json.loads(INITIAL_JSON.read_text(encoding="utf-8"))
    fingerprint = next(
        entry["fingerprint"]
        for entry in initial["entries"]
        if entry["triage_class"] == "LEGITIMATE_REVIEW_DEBT"
    )
    qualification = inventory["anomaly_qualifications"][fingerprint]
    qualification["blocking"] = False
    qualification["release_blocking"] = False
    mutated = tmp_path / "inventory-non-blocking.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(ValueError, match="non bloquante ou clôturée"):
        module.build_reports(ROOT, inventory_path=mutated)


def test_projects_a_review_closed_initial_fingerprint(
    tmp_path: Path,
) -> None:
    module = _load_module()
    inventory = copy.deepcopy(
        json.loads(INVENTORY.read_text(encoding="utf-8"))
    )
    initial = json.loads(INITIAL_JSON.read_text(encoding="utf-8"))
    fingerprint = next(
        entry["fingerprint"]
        for entry in initial["entries"]
        if entry["triage_class"] == "LEGITIMATE_REVIEW_DEBT"
    )
    inventory["anomaly_qualifications"].pop(fingerprint)
    mutated = tmp_path / "inventory-review-closed.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    reports = module.build_reports(ROOT, inventory_path=mutated)
    assert reports["residual_forensics"]["counts"]["REVIEW_CLOSED"] == 1
    assert reports["residual_forensics"]["counts"]["RESIDUAL_TRUE_NEW"] == 12


def test_projects_a_fixed_initial_fingerprint(tmp_path: Path) -> None:
    module = _load_module()
    inventory = copy.deepcopy(json.loads(INVENTORY.read_text(encoding="utf-8")))
    initial = json.loads(INITIAL_JSON.read_text(encoding="utf-8"))
    fingerprint = next(
        entry["fingerprint"]
        for entry in initial["entries"]
        if entry["triage_class"] == "FIX_NOW"
    )
    inventory["anomaly_qualifications"].pop(fingerprint)
    mutated = tmp_path / "inventory-fixed.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    reports = module.build_reports(ROOT, inventory_path=mutated)
    counts = reports["residual_forensics"]["counts"]
    assert counts["FIXED"] == 1
    assert counts["CONTENT_FINDINGS_FIXED"] == 5
    assert counts["RESIDUAL_TRUE_NEW"] == 12
