"""Gardes de contenu : identite semantique EX/CO, et anti-remplissage.

Les deux defauts historiques sont rejoues ici. Le premier gate doit voir un
corrige rattache au mauvais enonce ; le second doit voir un commit
d'infrastructure qui introduit du contenu pedagogique par recopie.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BINDING_JSON = ROOT / "audit/EX_CO_SEMANTIC_BINDING.json"

#: Le commit qui a rempli 986 slots vides sous un intitule de charte LaTeX.
FILLER_COMMIT = "533d19198eb7810699a41a7b5275744691420859"
EXERCISE_CYCLE = 5
CORRECTION_CYCLE = 6


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def binding_module():
    return _load("ex_co_binding", "scripts/build_ex_co_semantic_binding.py")


@pytest.fixture(scope="module")
def provenance_module():
    return _load("content_provenance", "scripts/check_content_provenance.py")


@pytest.fixture(scope="module")
def binding():
    assert BINDING_JSON.is_file()
    return json.loads(BINDING_JSON.read_text(encoding="utf-8"))


# --- Identite semantique enonce / corrige ------------------------------------


def test_every_correction_resolves_its_declared_statement(binding):
    assert binding["summary"]["UNRESOLVED_CORRECTION_TARGETS"] == 0


def test_no_correction_answers_another_statement(binding):
    assert binding["summary"]["STUDENT_TEACHER_STATEMENT_DRIFT"] == 0


def test_each_binding_carries_the_statement_digest(binding):
    for entry in binding["bindings"]:
        assert entry["corrects_statement_digest"]
        assert entry["corrects_statement_digest"] == entry["statement_semantic_digest"]


def test_the_digest_covers_questions_numbers_and_code(binding_module, tmp_path):
    """Deux enonces qui ne different que par un nombre ont deux digests."""

    def write(name: str, value: str) -> Path:
        path = tmp_path / name
        path.write_text(
            "% META: {}\n"
            "\\begin{exercice}{EX-1}{1}{10}\n"
            "\\begin{enumerate}\n"
            f"  \\item Calculer l'aire pour x = {value}.\n"
            "  \\item Conclure.\n"
            "\\end{enumerate}\n"
            "\\end{exercice}\n",
            encoding="utf-8",
        )
        return path

    first = binding_module.statement_semantic_digest(write("a.tex", "12"), {})
    second = binding_module.statement_semantic_digest(write("b.tex", "13"), {})
    assert first["question_count"] == 2
    assert first["digest"] != second["digest"], "un nombre different doit changer le digest"


def test_question_order_is_part_of_the_identity(binding_module, tmp_path):
    def write(name: str, first: str, second: str) -> Path:
        path = tmp_path / name
        path.write_text(
            "% META: {}\n"
            "\\begin{exercice}{EX-1}{1}{10}\n"
            "\\begin{enumerate}\n"
            f"  \\item {first}\n  \\item {second}\n"
            "\\end{enumerate}\n"
            "\\end{exercice}\n",
            encoding="utf-8",
        )
        return path

    a = binding_module.statement_semantic_digest(write("a.tex", "Calculer.", "Conclure."), {})
    b = binding_module.statement_semantic_digest(write("b.tex", "Conclure.", "Calculer."), {})
    assert a["digest"] != b["digest"], "l'ordre des questions fait partie de l'identite"


def test_fixture_the_historical_cycle_mismatch_is_a_drift():
    """Periode 5 pour les enonces, periode 6 pour les corriges."""

    slots = range(1, 51)
    statement = {n: f"EX-{((n - 1) % EXERCISE_CYCLE) + 1:03d}" for n in slots}
    correction = {n: f"EX-{((n - 1) % CORRECTION_CYCLE) + 1:03d}" for n in slots}
    drifted = [n for n in slots if statement[n] != correction[n]]
    assert len(drifted) == 40
    assert min(drifted) == 6


# --- Anti-remplissage ---------------------------------------------------------


def _has_commit(revision: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=ROOT, capture_output=True,
    ).returncode == 0


@pytest.mark.skipif(not _has_commit(FILLER_COMMIT), reason="historique tronque")
def test_the_guard_sees_the_historical_filler_commit(provenance_module):
    """Le defaut historique doit etre rouge, sinon la garde ne garde rien."""

    report = provenance_module.inspect(ROOT, f"{FILLER_COMMIT}^", FILLER_COMMIT)
    assert report["passed"] is False
    codes = {finding["code"] for finding in report["findings"]}
    assert "SYNTHETIC_FILLER_CONTAMINATION" in codes
    assert "MASS_CONTENT_MUTATION_REQUIRES_EXPLICIT_CONTENT_PROVENANCE" in codes
    assert report["duplicated_count"] > 500


def test_the_guard_accepts_a_removal_only_change(provenance_module):
    """Retirer des copies ne doit pas etre confondu avec en ajouter."""

    head = subprocess.run(
        ["git", "log", "--format=%H", "-1", "--grep", "1NSI-CANONICAL-RECOVERY"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    if not head:
        pytest.skip("commit de recuperation absent")
    report = provenance_module.inspect(ROOT, f"{head}^", head)
    assert report["passed"] is True
    assert report["duplicated_count"] == 0


def test_a_non_content_prefix_may_still_touch_a_few_objects(provenance_module):
    """La garde vise l'ampleur et la nature, pas toute retouche."""

    assert provenance_module.MASS_OBJECT_THRESHOLD >= 10
    assert "[LATEX]" in provenance_module.NON_CONTENT_PREFIXES
    assert "[MATH]" not in provenance_module.NON_CONTENT_PREFIXES


def test_committed_binding_matches_the_producer(binding_module, binding):
    recomputed = binding_module.build(ROOT)
    assert recomputed["summary"] == binding["summary"]
