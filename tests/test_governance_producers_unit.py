"""Tests unitaires des producteurs de gouvernance, en cours de processus.

Ces producteurs etaient exerces uniquement par leur CLI en sous-processus :
leur comportement etait verifie, mais aucune ligne n'etait mesuree, et
audit/COVERAGE_TRAJECTORY.md pose explicitement qu'« une execution non mesuree
ne vaut pas preuve de couverture ».

Chaque test ci-dessous verifie une propriete reelle -- determinisme, exclusion
des observations volatiles, non-auto-reference, regle de variante, contrat CLI,
mode d'echec. Aucun n'appelle une fonction dans le seul but d'en marquer les
lignes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def freeze_binding():
    return _load("freeze_binding_unit", "build_1spe_suites_current_freeze_binding.py")


@pytest.fixture(scope="module")
def gap_metrics():
    return _load("qcm_gap_metrics_unit", "build_qcm_gap_metrics.py")


@pytest.fixture(scope="module")
def debt_algebra():
    return _load("debt_algebra_unit", "build_debt_set_algebra_reconciliation.py")


@pytest.fixture(scope="module")
def qcm_reference_debt():
    return _load("qcm_reference_debt_unit", "build_qcm_reference_debt_metrics.py")


@pytest.fixture(scope="module")
def binding_payload(freeze_binding):
    return freeze_binding.build_binding()


# ------------------------------------------- liaison courante du gel --------


def test_the_binding_reports_the_frozen_identity_and_passes_every_check(
    freeze_binding, binding_payload
) -> None:
    assert binding_payload["freeze_source_sha"] == (
        "c667f12b1792f31981b6b5894c8c604df1bce634"
    )
    assert binding_payload["freeze_object_count"] == 161
    assert binding_payload["current_object_count"] == 161
    assert binding_payload["binding_state"] == freeze_binding.BINDING_CURRENT
    for check in (
        "object_blob_identity_pass",
        "semantic_identity_pass",
        "programme_authority_identity_pass",
        "variant_semantic_identity_pass",
    ):
        assert binding_payload[check] is True, check
    # Le TeX genere du QCM est un artefact de RENDU, pas une source semantique :
    # la campagne diacritiques a change ses octets sans toucher une seule
    # question du JSON canonique. Sa derive est signalee a part et n'entre pas
    # dans le verdict de fraicheur du gel.
    assert binding_payload["findings"] == {
        "missing_objects": [],
        "modified_objects": [],
        "supplementary_objects": [],
        "covered_source_drift": [],
        "render_artifact_drift": [
            "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/qcm/1SPE-SUITES-QCM.tex"
        ],
        "programme_authority_drift": [],
    }
    assert binding_payload["render_evidence_state"] == "RENDER_CHANGED"
    assert binding_payload["qcm_semantic_authority"].endswith("1SPE-SUITES-QCM.json")
    assert binding_payload["qcm_render_artifact"].endswith("1SPE-SUITES-QCM.tex")


def test_the_content_projection_ignores_commit_metadata(freeze_binding) -> None:
    """Un blob Git ou un commit d'origine ne sont pas du contenu."""

    rows = [
        {
            "object_id": "OBJ-1",
            "object_type": "exercice",
            "path": "a/b.tex",
            "source_kind": "TEX_META",
            "status": "draft",
            "source_sha256": "a" * 64,
            "git_blob_sha1": "1" * 40,
            "source_commit_sha": "2" * 40,
        }
    ]
    other = [dict(rows[0], git_blob_sha1="9" * 40, source_commit_sha="8" * 40)]
    changed = [dict(rows[0], source_sha256="b" * 64)]

    assert freeze_binding._content_projection(rows) == freeze_binding._content_projection(other)
    assert freeze_binding._content_projection(rows) != freeze_binding._content_projection(changed)


def test_the_content_projection_is_order_independent(freeze_binding) -> None:
    first = {"object_id": "B", "object_type": "t", "path": "p2", "source_kind": "k",
             "status": "s", "source_sha256": "b" * 64}
    second = {"object_id": "A", "object_type": "t", "path": "p1", "source_kind": "k",
              "status": "s", "source_sha256": "a" * 64}

    assert freeze_binding._content_projection([first, second]) == (
        freeze_binding._content_projection([second, first])
    )


def test_the_stable_projection_drops_exactly_the_volatile_observations(
    freeze_binding, binding_payload
) -> None:
    """Publier le rapport ne doit pas perimer le rapport."""

    stable = freeze_binding.stable_projection(binding_payload)
    dropped = set(binding_payload) - set(stable)

    assert dropped == set(freeze_binding.VOLATILE_OBSERVATION_FIELDS)
    assert "current_repository_sha" in dropped
    assert "current_branch" in dropped
    moved = dict(binding_payload)
    moved["current_repository_sha"] = "0" * 40
    moved["current_branch"] = {"value": "autre", "binding": "INFORMATIONAL_ONLY"}
    assert freeze_binding.stable_projection(moved) == stable


def test_the_variant_partition_follows_the_teacher_only_rule(freeze_binding) -> None:
    rows = [
        {"object_id": "CO-1", "path": "chap/corriges/CO-1.tex"},
        {"object_id": "EV-A", "path": "chap/evaluations/EV-A-corrige.tex"},
        {"object_id": "EX-1", "path": "chap/exercices/EX-1.tex"},
    ]
    partition = freeze_binding._variant_partition(rows)

    assert partition["teacher_only"] == ["CO-1", "EV-A"]
    assert partition["student_visible"] == ["EX-1"]
    assert freeze_binding._is_teacher_only("x/corriges/y.tex") is True
    assert freeze_binding._is_teacher_only("x/exercices/y.tex") is False


def test_the_markdown_render_never_leaks_a_sha_or_a_branch_name(
    freeze_binding, binding_payload
) -> None:
    rendered = freeze_binding.render_md(binding_payload)

    assert binding_payload["current_repository_sha"] not in rendered
    assert binding_payload["current_branch"]["value"] not in rendered
    assert "INFORMATIONAL_ONLY" in rendered
    assert str(binding_payload["freeze_object_count"]) in rendered
    assert freeze_binding.render_md(binding_payload) == rendered  # deterministe


def test_the_json_render_is_deterministic_and_sorted(freeze_binding, binding_payload) -> None:
    once = freeze_binding.render_json(binding_payload)

    assert once == freeze_binding.render_json(binding_payload)
    assert once.endswith("\n")
    assert json.loads(once) == binding_payload


def test_the_check_cli_agrees_with_the_committed_artifact(freeze_binding) -> None:
    assert freeze_binding.main(["--check"]) == 0


# ------------------------------------------------ metriques de lacune QCM ---


def test_the_gap_metrics_declare_their_real_inputs(gap_metrics) -> None:
    inputs = gap_metrics._source_inputs()
    declared = {row["path"] for row in inputs}

    assert inputs, "la provenance doit nommer ses entrees"
    assert all(row["sha256"].startswith("sha256:") for row in inputs)
    assert any(path.endswith("-QCM.json") for path in declared)
    assert any(path.endswith("contrat.yaml") for path in declared)
    assert "audit/QCM_GAP_METRICS.json" not in declared  # non auto-referent


def test_the_gap_metrics_digest_changes_only_with_its_inputs(gap_metrics) -> None:
    inputs = gap_metrics._source_inputs()
    before = gap_metrics._source_digest(inputs)
    mutated = [dict(inputs[0], sha256="sha256:" + "0" * 64), *inputs[1:]]

    assert gap_metrics._source_digest(inputs) == before
    assert gap_metrics._source_digest(mutated) != before


def test_the_observed_sha_is_a_constat_not_a_freshness_condition(gap_metrics) -> None:
    observed = gap_metrics._observed_source_sha()

    assert len(observed) == 40
    assert int(observed, 16) >= 0


def test_the_gap_metrics_report_matches_the_committed_artifact(gap_metrics) -> None:
    """Les quatre grandeurs doivent etre reproduites, pas seulement executees."""

    committed = json.loads(
        (ROOT / "audit" / "QCM_GAP_METRICS.json").read_text(encoding="utf-8")
    )
    report = gap_metrics.build_report()

    assert report["inventory"] == committed["inventory"]
    for metric in (
        "UNIQUE_CAPACITY_IDS_WITHOUT_ANY_QCM",
        "CHAPTER_CAPACITY_PAIRS_WITHOUT_ANY_QCM",
        "MANDATORY_ASSESSED_CAPACITY_PAIRS_WITHOUT_QCM",
        "REQUIRED_DISTRACTOR_WITHOUT_DIAGNOSTIC",
    ):
        assert report[metric]["count"] == committed[metric]["count"], metric
    assert report["PEDAGOGICALLY_REQUIRED_QCM_GAPS"]["objective"] == 0


# --------------------------------------------- rendus des autres ledgers ----


def test_the_debt_algebra_markdown_states_the_wrong_subtraction(debt_algebra) -> None:
    payload = debt_algebra.build_reconciliation()
    rendered = debt_algebra.render_md(payload)

    assert "6541 - 5371" in rendered
    assert "RESOLVED_ARCHIVE_ALL_GENERATIONS" in rendered
    assert debt_algebra.render_md(payload) == rendered
    assert debt_algebra.main(["--check"]) == 0


def test_the_qcm_reference_debt_markdown_separates_the_two_metrics(
    qcm_reference_debt,
) -> None:
    payload = qcm_reference_debt.build_metrics()
    rendered = qcm_reference_debt.render_md(payload)

    assert "TSPE_BROKEN_REMEDIATION_REFERENCES" in rendered
    assert "GLOBAL_DISTRACTORS_MISSING_DIAGNOSTIC_OR_REFERENCE" in rendered
    assert qcm_reference_debt.main(["--check"]) == 0


def test_the_reference_resolver_rejects_a_target_that_does_not_exist(
    qcm_reference_debt,
) -> None:
    targets = {"M": {"M1"}, "C": {"C1"}, "R": {"C1"}}

    assert qcm_reference_debt._resolves("M", "1", targets) is True
    assert qcm_reference_debt._resolves("M", "9", targets) is False
    assert qcm_reference_debt._resolves("C", "1", targets) is True
    assert qcm_reference_debt._resolves("C", "4", targets) is False
    assert qcm_reference_debt._resolves("R", "1", targets) is True
