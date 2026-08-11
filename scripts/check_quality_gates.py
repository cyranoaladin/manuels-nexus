#!/usr/bin/env python3
"""Run the documented blocking QA core.

The repository still keeps many historical `check_*` scripts for metrics and
diagnostics. This aggregate gate is intentionally limited to the documented
blocking core in `qa_gate_policy.md`; broad counting checks remain callable
directly but are no longer treated as proof of pedagogical validation.
"""

from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

CORE_CHECKS: list[list[str]] = [
    ["-m", "scripts.check_git_clean"],
    ["-m", "scripts.check_repo_topology"],
    ["-m", "scripts.check_audit_folder_policy"],
    ["-m", "scripts.check_content_tree_policy"],
    ["-m", "scripts.check_rag_config"],
    ["-m", "scripts.rag_smoke_test"],
    ["-m", "scripts.rag_diagnose_search_timeout"],
    ["-m", "scripts.check_rag_collection_policy"],
    ["-m", "scripts.check_rag_golden_examples_policy"],
    ["-m", "scripts.check_rag_metadata_canonical_fields"],
    ["-m", "scripts.check_no_secret_file_mutation_policy"],
    ["-m", "scripts.check_agents_governance"],
    ["-m", "scripts.check_skills_governance"],
    ["-m", "scripts.check_metadata"],
    ["-m", "scripts.check_links"],
    ["-m", "scripts.check_no_private_data"],
    ["-m", "scripts.check_no_committed_secrets"],
    ["-m", "scripts.check_no_placeholders_docs"],
    ["-m", "scripts.check_no_placeholders_code"],
    ["-m", "scripts.check_no_build_artifacts_in_index"],
    ["-m", "scripts.check_uploaded_archive_policy"],
    ["-m", "scripts.check_program_coverage"],
    ["-m", "scripts.generate_coverage_gap_action_plan"],
    ["-m", "scripts.check_coverage_gap_action_plan"],
    ["-m", "scripts.check_sources_catalog"],
    ["-m", "scripts.check_sources_catalog_schema"],
    ["-m", "scripts.generate_pedagogical_indexes"],
    ["-m", "scripts.check_pedagogical_indexes"],
    ["-m", "scripts.check_makefile_audit_policy"],
    ["-m", "scripts.check_reports_policy"],
    ["-m", "scripts.check_substance_anchors"],
    ["-m", "scripts.check_status_promotion_guard"],
    ["-m", "scripts.check_contract_substance_quality"],
    ["-m", "scripts.check_differentiation_distinctness"],
    ["-m", "scripts.check_rendered_unit_artifacts", "--unit", "P05"],
    ["-m", "scripts.check_drive_enrichment_traceability_portable"],
    ["-m", "scripts.check_drive_action_plan_completeness"],
    ["-m", "scripts.check_no_coverage_from_sheets_only"],
    ["-m", "scripts.run_python_tests"],
]

INDICATIVE_CHECKS: list[list[str]] = [
    ["-m", "scripts.check_required_sections"],
    ["-m", "scripts.check_document_depth"],
    ["-m", "scripts.check_document_style"],
]


def remove_python_caches() -> None:
    for path in ROOT.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)


def run_check(command: list[str], env: dict[str, str], indicative: bool = False) -> int:
    label = " ".join(command)
    suffix = " (indicatif)" if indicative else ""
    print(f"== {label}{suffix} ==")
    command_env = env
    if command in (["-m", "scripts.rag_smoke_test"], ["-m", "scripts.rag_diagnose_search_timeout"]) and "RAG_ENV_FILE" not in env:
        command_env = env.copy()
        command_env["RAG_ENV_FILE"] = str(ROOT / ".env.rag.audit-core-missing")
    return subprocess.run([PYTHON, *command], cwd=ROOT, env=command_env).returncode


def main() -> None:
    failures: list[str] = []
    indicative_failures: list[str] = []
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    remove_python_caches()
    try:
        for command in CORE_CHECKS:
            if run_check(command, env) != 0:
                failures.append(" ".join(command))
        for command in INDICATIVE_CHECKS:
            if run_check(command, env, indicative=True) != 0:
                indicative_failures.append(" ".join(command))
        if failures:
            print("check_quality_gates: KO")
            for item in failures:
                print(f"- {item}")
            raise SystemExit(1)
        if indicative_failures:
            print("Gates indicatifs non bloquants en échec:")
            for item in indicative_failures:
                print(f"- {item}")
        print("check_quality_gates: PASS")
    finally:
        remove_python_caches()


if __name__ == "__main__":
    main()
