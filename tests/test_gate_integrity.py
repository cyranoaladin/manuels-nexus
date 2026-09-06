"""L'integrite des gates de release, prouvee par mutation reelle.

Un gate vert ne vaut que si le rouge est atteignable. Chaque test injecte donc
un defaut dans la source ou dans la preuve, reconstruit, et exige le rouge.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
AUDIT_JSON = ROOT / "audit/GATE_INTEGRITY_AUDIT.json"
PROVENANCE_JSON = ROOT / "audit/PROOF_PROVENANCE_MAP.json"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate_audit():
    return _load("gate_integrity", "scripts/audit_gate_integrity.py")


@pytest.fixture(scope="module")
def report(gate_audit):
    payload, _ = gate_audit.audit(ROOT)
    return payload


def test_no_release_metric_is_hardcoded(report):
    offenders = report["hardcoded_release_metrics"]
    assert offenders == [], f"metriques affirmees au lieu d'etre mesurees: {offenders}"


def test_no_required_evidence_is_optional(report):
    offenders = report["optional_required_evidence"]
    assert offenders == [], f"preuve obligatoire rendue optionnelle: {offenders}"


def test_no_evidence_is_loaded_then_ignored(report):
    offenders = report["loaded_but_unused_evidence"]
    assert offenders == [], f"preuve chargee puis jamais lue: {offenders}"


def test_no_gate_test_is_tautological(report):
    offenders = report["tautological_gate_tests"]
    assert offenders == [], f"assertion entre constantes: {offenders}"


def test_every_release_metric_has_a_provenance_chain(gate_audit):
    provenance = gate_audit.build_provenance_map(ROOT)
    untraced = [e for e in provenance["entries"] if e["source_kind"] == "UNTRACED"]
    assert untraced == [], f"metriques sans chaine de provenance: {untraced}"
    for entry in provenance["entries"]:
        if entry["source_kind"] == "DERIVED_FROM_EVIDENCE":
            assert entry["input_artifacts"], entry["metric"]
            assert entry["producers"], entry["metric"]


# --- Mutations : le detecteur doit voir ce qu'il pretend voir -----------------


def _mutated_tree(source: str) -> ast.AST:
    return ast.parse(source)


def test_mutation_a_hardcoded_metric_is_detected(gate_audit):
    source = 'REPORT = {"TOTAL_P0_OPEN": 0, "PREFLIGHT_ALL_TARGETS": "PASS"}\n'
    found = gate_audit.scan_hardcoded_metrics("mutant.py", _mutated_tree(source))
    metrics = {f["metric"] for f in found}
    assert metrics == {"TOTAL_P0_OPEN", "PREFLIGHT_ALL_TARGETS"}


def test_mutation_a_derived_metric_is_not_flagged(gate_audit):
    source = 'REPORT = {"TOTAL_P0_OPEN": len(findings)}\n'
    assert gate_audit.scan_hardcoded_metrics("mutant.py", _mutated_tree(source)) == []


def test_mutation_an_optional_required_evidence_is_detected(gate_audit):
    source = (
        "def build():\n"
        "    debt = 0\n"
        "    if path.is_file():\n"
        "        debt += 1\n"
        "    return debt\n"
    )
    found = gate_audit.scan_optional_required_evidence("mutant.py", _mutated_tree(source))
    assert found, "une preuve absente traitee comme zero doit etre signalee"


def test_mutation_an_explicitly_handled_absence_is_not_flagged(gate_audit):
    source = (
        "def build():\n"
        "    debt = 0\n"
        "    if path.is_file():\n"
        "        debt += 1\n"
        "    else:\n"
        "        debt = FAIL\n"
        "    return debt\n"
    )
    assert gate_audit.scan_optional_required_evidence("mutant.py", _mutated_tree(source)) == []


def test_mutation_a_tautological_assertion_is_detected(gate_audit):
    source = "def test_x():\n    assert 1289 + 134 == 1423\n"
    found = gate_audit.scan_tautological_tests("mutant.py", _mutated_tree(source))
    assert len(found) == 1


def test_mutation_a_real_assertion_is_not_flagged(gate_audit):
    source = "def test_x():\n    assert summary['TOTAL'] == 1423\n"
    assert gate_audit.scan_tautological_tests("mutant.py", _mutated_tree(source)) == []


def test_mutation_loaded_but_unused_evidence_is_detected(gate_audit):
    source = (
        "def build():\n"
        "    debt = json.load(handle)\n"
        "    return 0\n"
    )
    found = gate_audit.scan_loaded_but_unused("mutant.py", _mutated_tree(source), source)
    assert [f["variable"] for f in found] == ["debt"]


# --- Mutations : les gates produits doivent virer au rouge --------------------


def test_mutation_missing_evidence_key_blocks_the_debt_gate(tmp_path):
    """Retirer une cle d'une preuve doit bloquer, jamais valoir zero defaut."""

    debt_module = _load("zero_debt_mutation", "scripts/build_zero_technical_debt.py")
    parity = json.loads(
        (ROOT / "audit/PARITY_BAREMES_VALIDATION.json").read_text(encoding="utf-8")
    )
    baseline = debt_module.audit_technical_debt(ROOT)
    assert baseline["product_debt_summary"]["EVIDENCE_DEBT_OPEN"] == 0

    stripped = dict(parity)
    stripped["summary"] = {
        k: v for k, v in parity["summary"].items() if k != "TEACHER_CONTENT_LEAK_IN_STUDENT"
    }
    mutant_root = tmp_path / "root"
    (mutant_root / "audit").mkdir(parents=True)
    for artifact in (ROOT / "audit").glob("*.json"):
        (mutant_root / "audit" / artifact.name).write_text(
            artifact.read_text(encoding="utf-8"), encoding="utf-8"
        )
    (mutant_root / "audit" / "PARITY_BAREMES_VALIDATION.json").write_text(
        json.dumps(stripped), encoding="utf-8"
    )

    mutated = debt_module.audit_technical_debt(mutant_root)
    assert mutated["product_debt_summary"]["EVIDENCE_DEBT_OPEN"] >= 1
    assert mutated["all_product_debts_zero"] is False
    assert any(
        "TEACHER_CONTENT_LEAK_IN_STUDENT" in entry
        for entry in mutated["missing_or_malformed_evidence"]
    )


def test_mutation_a_bareme_defect_turns_the_bareme_gate_red(tmp_path):
    """Un total de bareme fausse dans la source doit etre vu."""

    parity_module = _load(
        "parity_mutation", "scripts/build_parity_baremes_validation.py"
    )
    subject = ROOT / "NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/evaluations/TNSI-HIST-EVAL-A.tex"
    original = subject.read_text(encoding="utf-8")
    assert "Ex. 1 : 10 pts" in original

    clean_root = tmp_path / "clean"
    target = clean_root / subject.relative_to(ROOT)
    target.parent.mkdir(parents=True)
    target.write_text(original, encoding="utf-8")
    assert parity_module.audit_baremes(clean_root)["total_mismatch"] == []

    mutant_root = tmp_path / "mutant"
    target = mutant_root / subject.relative_to(ROOT)
    target.parent.mkdir(parents=True)
    target.write_text(original.replace("Ex. 1 : 10 pts", "Ex. 1 : 9 pts", 1), encoding="utf-8")
    assert parity_module.audit_baremes(mutant_root)["total_mismatch"] != []


def test_mutation_a_statement_drift_turns_the_parity_gate_red(tmp_path):
    """Un corrige rattache au mauvais enonce doit etre vu, pas devine."""

    parity = json.loads(
        (ROOT / "audit/PARITY_BAREMES_VALIDATION.json").read_text(encoding="utf-8")
    )
    drift = parity["statement_drift"]
    assert isinstance(drift, list)
    # La mesure existe et est reliee a des paires nommees, pas a une constante.
    for entry in drift:
        assert entry["exercise_label"] != entry["correction_targets"]
        assert (ROOT / "NSI" / entry["exercise"]).is_file() or (
            ROOT / "Mathematiques/manuel-maths" / entry["exercise"]
        ).is_file()


def test_committed_gate_integrity_audit_matches_the_producer(gate_audit):
    """Le rapport commite doit etre celui que le producteur recalcule."""

    payload, provenance = gate_audit.audit(ROOT)
    assert AUDIT_JSON.is_file()
    committed = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    assert committed["summary"] == payload["summary"]
    assert PROVENANCE_JSON.is_file()
    committed_prov = json.loads(PROVENANCE_JSON.read_text(encoding="utf-8"))
    assert committed_prov["summary"] == provenance["summary"]
