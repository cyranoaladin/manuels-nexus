"""Tests du registre des avertissements de dependances et de l'epinglage.

Le registre ne doit jamais deviner un avertissement : il les lit dans une
capture reelle de sortie pytest. Il ne doit pas non plus declarer l'epinglage
reproductible tant que l'environnement local diverge de l'ensemble epingle.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dependency_warning_ledger as ledger  # noqa: E402

LEDGER_PATH = ROOT / "audit" / "DEPENDENCY_WARNING_AND_PINNING_LEDGER.json"
CAPTURE_PATH = ROOT / "audit" / "DEPENDENCY_WARNING_CAPTURE.txt"


def _ledger() -> dict:
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def test_every_pinned_package_is_reported() -> None:
    report = _ledger()["pinning"]
    assert report["pinned_package_count"] == len(ledger.pinned_requirements())
    assert (
        report["match_count"] + report["drift_count"] + report["absent_count"]
        == report["pinned_package_count"]
    )


def test_pinned_requirements_are_all_exact() -> None:
    """Un fichier d'epinglage ne contient que des `==`."""

    for line in (ROOT / "requirements-ci-audit.txt").read_text(
        encoding="utf-8"
    ).splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            assert "==" in stripped, stripped


def test_unbounded_declarations_are_all_listed() -> None:
    declared = _ledger()["unbounded_declarations"]
    assert declared, "NSI/requirements.txt porte des declarations non bornees"
    for entry in declared:
        assert "==" not in entry["requirement"]
        assert entry["bound"] in {"lower_only", "none"}


def test_warnings_are_read_from_a_real_capture_not_invented() -> None:
    """Le registre doit decrire LA capture commitee, pas une autre.

    L'inclusion seule laissait passer un registre bati sur une capture
    anterieure : il gardait des avertissements que le depot ne portait plus, et
    l'empreinte declaree ne designait aucun fichier present. Une preuve qui
    nomme une source introuvable ne prouve rien.
    """
    import hashlib

    warnings = _ledger()["pytest_warnings"]
    assert warnings["source_capture_sha256"], "aucune capture source declaree"
    assert warnings["count"] == len(warnings["warnings"])

    empreinte = "sha256:" + hashlib.sha256(CAPTURE_PATH.read_bytes()).hexdigest()
    assert warnings["source_capture_sha256"] == empreinte, (
        "le registre declare une capture qui n'est pas celle du depot"
    )

    parsed = ledger.parse_pytest_warnings(CAPTURE_PATH)
    identity = lambda item: (item["location"], item["line"], item["message"])  # noqa: E731
    assert {identity(item) for item in parsed} == {identity(item) for item in warnings["warnings"]}


def test_a_post_summary_warning_is_distinguished_from_the_summary_ones() -> None:
    """Un avertissement emis apres le resume doit rester visible comme tel.

    L'assertion etait inconditionnelle : elle exigeait qu'un tel avertissement
    existe toujours, ce qui la rendait rouge des que l'environnement cessait
    d'en emettre -- et verte, a l'inverse, tant qu'un registre perime en
    conservait un. Ce qui doit tenir est le classement : si la capture en
    contient un, le registre le distingue du resume.
    """
    parsed = ledger.parse_pytest_warnings(CAPTURE_PATH)
    attendus = {item["phase"] for item in parsed}
    phases = {item["phase"] for item in _ledger()["pytest_warnings"]["warnings"]}
    assert phases == attendus, (
        "le registre ne classe pas les avertissements comme la capture les presente"
    )
    if "post_summary" in attendus:
        assert "post_summary" in phases


def test_every_warning_carries_an_owner() -> None:
    for warning in _ledger()["pytest_warnings"]["warnings"]:
        assert warning["owner"] in {"project", "upstream"}


def test_the_ledger_changes_nothing() -> None:
    report = _ledger()
    assert report["read_only"] is True
    assert report["closure_planned_before"] == "FINAL_SOURCE_SHA"


def test_ci_installs_the_pinned_set_with_no_deps_and_checks_it() -> None:
    for policy in _ledger()["workflow_install_policy"]:
        assert policy["installs_pinned_requirements"], policy["workflow"]
        assert policy["uses_no_deps"], policy["workflow"]
        assert policy["runs_pip_check"], policy["workflow"]
