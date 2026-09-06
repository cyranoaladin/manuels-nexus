"""Tests de parite eleve/professeur, etancheite et baremes (LOT 4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "audit/PARITY_BAREMES_VALIDATION.json"
SCRIPT_PATH = ROOT / "scripts/build_parity_baremes_validation.py"


@pytest.fixture(scope="module")
def parity_report() -> dict:
    assert REPORT_PATH.is_file(), f"L'artefact {REPORT_PATH} doit exister"
    with REPORT_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_zero_student_without_correction_and_zero_orphan(parity_report: dict) -> None:
    summary = parity_report["summary"]
    assert summary["STUDENT_WITHOUT_CORRECTION"] == 0
    assert summary["ORPHAN_TEACHER_CORRECTION"] == 0
    assert summary["TOTAL_EXERCISES"] == summary["TOTAL_CORRECTIONS"]
    # Pas de plancher de volume : un seuil sur le nombre d'exercices ferait de
    # la suppression des copies synthetiques une regression, et donnerait au
    # remplissage une raison de rester. La bijection est l'invariant, pas la
    # densite ; le volume descend legitimement quand des clones disparaissent.
    assert summary["TOTAL_EXERCISES"] > 0


def test_zero_teacher_content_leak_in_student(parity_report: dict) -> None:
    summary = parity_report["summary"]
    assert summary["TEACHER_CONTENT_LEAK_IN_STUDENT"] == 0
    assert summary["STUDENT_PDFS_AUDITED"] == 6


def test_baremes_zero_ambiguity_and_zero_mismatch(parity_report: dict) -> None:
    summary = parity_report["summary"]
    assert summary["BAREME_SCOPE_AMBIGUOUS"] == 0
    assert summary["BAREME_TOTAL_MISMATCH"] == 0
    assert summary["BAREME_DUPLICATE_ALLOCATION"] == 0
    assert summary["BAREME_MISSING_REQUIRED_QUESTION"] == 0
    assert summary["TEACHER_MISSING_REQUIRED_CONTENT"] == 0


def test_mutation_student_leak_detected(monkeypatch) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_parity_baremes_validation as mod

    real_run = mod.subprocess.run
    def mutated_run(cmd, *args, **kwargs):
        res = real_run(cmd, *args, **kwargs)
        if "pdftotext" in cmd:
            # Inject a simulated teacher correction leak
            import subprocess
            return subprocess.CompletedProcess(
                cmd,
                0,
                stdout=res.stdout + "\nCorrigé officiel de l'exercice\n",
                stderr=res.stderr
            )
        return res

    monkeypatch.setattr(mod.subprocess, "run", mutated_run)
    report = mod.validate_parity_and_baremes()
    assert report["summary"]["TEACHER_CONTENT_LEAK_IN_STUDENT"] > 0
