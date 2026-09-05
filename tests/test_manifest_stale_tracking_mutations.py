"""Mutation testing for build manifest dependency graph and stale tracking.

Verifies strict invariants required by Release Owner:
1. Mutating exclusive source of manual A stales A but leaves B fresh (no cross-contamination).
2. Mutating shared dependency (nexus-manuel.cls) stales all consuming manuals.
3. Mutating curriculum authority of manual B does not stale manual A.
4. Mutating non-applicable future curriculum does not stale any 2026-2027 manual.
5. Mutating or substituting output PDF triggers immediate PDF_HASH_MISMATCH.
6. Altering page count triggers immediate PAGE_COUNT_MISMATCH.
7. Mutating build reproducibility parameters triggers immediate STALE_CONFIG_CHANGED.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.manifest_dependency_graph import (
    build_canonical_dependency_graph,
    evaluate_target_freshness,
    COMMON_CLASS_PATH,
    REPRODUCIBILITY_CONFIG_PATH,
)


@pytest.fixture(scope="module")
def dependency_graph():
    return build_canonical_dependency_graph(ROOT)


@pytest.fixture
def mock_clean_receipt_factory(dependency_graph):
    """Produces a clean, matching receipt for any canonical target."""
    def _create(target_id: str):
        target = dependency_graph[target_id]
        dep_digests: dict[str, str] = {}
        for dep in target.all_dependencies:
            dep_path = ROOT / dep
            if dep_path.is_file():
                dep_digests[dep] = "sha256:" + hashlib.sha256(dep_path.read_bytes()).hexdigest()
            else:
                dep_digests[dep] = "sha256:" + "0" * 64

        pdf_path = ROOT / target.pdf
        if pdf_path.is_file():
            pdf_sha = "sha256:" + hashlib.sha256(pdf_path.read_bytes()).hexdigest()
            from scripts.inventory_collection import _page_count_with_pdfinfo, _page_count_with_python
            res = _page_count_with_pdfinfo(pdf_path); pages = res[0] if isinstance(res, tuple) else (res or 100)
        else:
            pdf_sha = "sha256:" + "f" * 64
            pages = 100

        repro_cfg = {}
        repro_path = ROOT / REPRODUCIBILITY_CONFIG_PATH
        if repro_path.is_file():
            raw_cfg = json.loads(repro_path.read_text(encoding="utf-8"))
            repro_cfg["source_commit"] = raw_cfg.get("source_commit")
            repro_cfg["source_date_epoch"] = raw_cfg.get("source_date_epoch")

        return {
            "manual": target.manual_id,
            "variant": target.variant,
            "pdf_path": target.pdf,
            "pdf_sha256": pdf_sha,
            "page_count": pages,
            "dependency_digests": dep_digests,
            "reproducibility": repro_cfg,
        }
    return _create


def test_dependency_graph_covers_all_twelve_targets(dependency_graph):
    assert len(dependency_graph) == 12
    expected_targets = {
        "1SPE_eleve", "1SPE_professeur",
        "TSPE_2026_2027_eleve", "TSPE_2026_2027_professeur",
        "TCOMPL_eleve", "TCOMPL_professeur",
        "TEXPERTES_eleve", "TEXPERTES_professeur",
        "1NSI_eleve", "1NSI_professeur",
        "TNSI_eleve", "TNSI_professeur",
    }
    assert set(dependency_graph.keys()) == expected_targets


def test_clean_receipt_evaluates_as_fresh(dependency_graph, mock_clean_receipt_factory):
    target_1spe = dependency_graph["1SPE_eleve"]
    receipt = mock_clean_receipt_factory("1SPE_eleve")

    eval_result = evaluate_target_freshness(
        ROOT,
        target_1spe,
        receipt,
        inspect_pdf=True,
    )
    assert eval_result.is_fresh is True
    assert eval_result.status == "FRESH_CURRENT"


def test_mutation_exclusive_source_stales_target_a_not_target_b(dependency_graph, mock_clean_receipt_factory):
    """Mutating 1SPE exclusive source must stale 1SPE, but keep TSPE and 1NSI fresh."""
    target_1spe = dependency_graph["1SPE_eleve"]
    target_tspe = dependency_graph["TSPE_2026_2027_eleve"]
    target_1nsi = dependency_graph["1NSI_eleve"]

    receipt_1spe = mock_clean_receipt_factory("1SPE_eleve")
    receipt_tspe = mock_clean_receipt_factory("TSPE_2026_2027_eleve")
    receipt_1nsi = mock_clean_receipt_factory("1NSI_eleve")

    mutated_source = target_1spe.exclusive_sources[0]
    assert mutated_source not in target_tspe.all_dependencies
    assert mutated_source not in target_1nsi.all_dependencies

    simulated_digests = {mutated_source: "sha256:deadbeef" + "0" * 56}

    eval_1spe = evaluate_target_freshness(
        ROOT, target_1spe, receipt_1spe,
        current_file_digests=simulated_digests,
        inspect_pdf=False,
    )
    eval_tspe = evaluate_target_freshness(
        ROOT, target_tspe, receipt_tspe,
        current_file_digests=simulated_digests,
        inspect_pdf=False,
    )
    eval_1nsi = evaluate_target_freshness(
        ROOT, target_1nsi, receipt_1nsi,
        current_file_digests=simulated_digests,
        inspect_pdf=False,
    )

    assert eval_1spe.is_fresh is False
    assert eval_1spe.status == "STALE_EXCLUSIVE_SOURCE_MODIFIED"
    assert eval_1spe.stale_file == mutated_source

    assert eval_tspe.is_fresh is True
    assert eval_tspe.status == "FRESH_CURRENT"

    assert eval_1nsi.is_fresh is True
    assert eval_1nsi.status == "FRESH_CURRENT"


def test_mutation_shared_class_stales_all_manuals(dependency_graph, mock_clean_receipt_factory):
    """Mutating nexus-manuel.cls must stale every single canonical target."""
    simulated_digests = {COMMON_CLASS_PATH: "sha256:mutatedcommonclass" + "0" * 46}

    for target_id, target in dependency_graph.items():
        receipt = mock_clean_receipt_factory(target_id)
        eval_res = evaluate_target_freshness(
            ROOT, target, receipt,
            current_file_digests=simulated_digests,
            inspect_pdf=False,
        )
        assert eval_res.is_fresh is False, f"Target {target_id} was not staled by common class mutation"
        assert eval_res.status == "STALE_SHARED_DEPENDENCY_MODIFIED"
        assert eval_res.stale_file == COMMON_CLASS_PATH


def test_mutation_curriculum_authority_stales_only_applicable_manual(dependency_graph, mock_clean_receipt_factory):
    """Mutating TCOMPL authority file must stale TCOMPL but keep 1SPE and TSPE fresh."""
    target_1spe = dependency_graph["1SPE_eleve"]
    target_tcompl = dependency_graph["TCOMPL_eleve"]

    tcompl_authority = target_tcompl.programme_authority_file
    assert tcompl_authority is not None
    assert tcompl_authority not in target_1spe.all_dependencies

    simulated_digests = {tcompl_authority: "sha256:mutatedcurriculum" + "0" * 47}

    receipt_1spe = mock_clean_receipt_factory("1SPE_eleve")
    receipt_tcompl = mock_clean_receipt_factory("TCOMPL_eleve")

    eval_1spe = evaluate_target_freshness(
        ROOT, target_1spe, receipt_1spe,
        current_file_digests=simulated_digests,
        inspect_pdf=False,
    )
    eval_tcompl = evaluate_target_freshness(
        ROOT, target_tcompl, receipt_tcompl,
        current_file_digests=simulated_digests,
        inspect_pdf=False,
    )

    assert eval_tcompl.is_fresh is False
    assert eval_tcompl.status == "STALE_PROGRAMME_AUTHORITY_MODIFIED"
    assert eval_tcompl.stale_file == tcompl_authority

    assert eval_1spe.is_fresh is True
    assert eval_1spe.status == "FRESH_CURRENT"


def test_mutation_future_year_curriculum_does_not_stale_any_2026_manual(dependency_graph, mock_clean_receipt_factory):
    """Mutating a 2027+ decree (MENE2602919A) does not belong to 2026-2027 and stales nothing."""
    future_curriculum_path = "docs/programme_maths_1spe_2027_MENE2602919A.pdf"
    simulated_digests = {future_curriculum_path: "sha256:futurecurriculum" + "0" * 48}

    for target_id, target in dependency_graph.items():
        receipt = mock_clean_receipt_factory(target_id)
        eval_res = evaluate_target_freshness(
            ROOT, target, receipt,
            current_file_digests=simulated_digests,
            inspect_pdf=False,
        )
        assert eval_res.is_fresh is True, f"Target {target_id} was incorrectly staled by future curriculum"
        assert eval_res.status == "FRESH_CURRENT"


def test_pdf_substitution_or_byte_drift_detected_immediately(dependency_graph, mock_clean_receipt_factory):
    """Mutating recorded pdf hash or replacing pdf must trigger PDF_HASH_MISMATCH."""
    target_1spe = dependency_graph["1SPE_eleve"]
    receipt = mock_clean_receipt_factory("1SPE_eleve")
    receipt["pdf_sha256"] = "sha256:0123456789abcdef" + "0" * 48

    eval_res = evaluate_target_freshness(
        ROOT, target_1spe, receipt,
        inspect_pdf=True,
    )
    assert eval_res.is_fresh is False
    assert eval_res.status == "PDF_HASH_MISMATCH"


def test_page_count_alteration_detected_immediately(dependency_graph, mock_clean_receipt_factory):
    """Altering recorded page count must trigger PAGE_COUNT_MISMATCH."""
    target_1spe = dependency_graph["1SPE_eleve"]
    receipt = mock_clean_receipt_factory("1SPE_eleve")
    receipt["page_count"] = receipt["page_count"] + 10

    eval_res = evaluate_target_freshness(
        ROOT, target_1spe, receipt,
        inspect_pdf=True,
    )
    assert eval_res.is_fresh is False
    assert eval_res.status == "PAGE_COUNT_MISMATCH"


def test_reproducibility_config_drift_stales_target(dependency_graph, mock_clean_receipt_factory):
    """Altering source_commit or source_date_epoch stales target."""
    target_1spe = dependency_graph["1SPE_eleve"]
    receipt = mock_clean_receipt_factory("1SPE_eleve")
    receipt["reproducibility"]["source_commit"] = "0000000000000000000000000000000000000000"

    eval_res = evaluate_target_freshness(
        ROOT, target_1spe, receipt,
        inspect_pdf=False,
    )
    assert eval_res.is_fresh is False
    assert eval_res.status == "STALE_CONFIG_CHANGED"
