"""Portée de release, registre des bloqueurs, contrôle de toutes les pages.

Trois producteurs, une même exigence : ils ne valent que s'ils peuvent dire
non. Ce module vérifie l'état courant, puis mute les preuves pour s'assurer
qu'un périmètre qui rétrécit, un bloqueur qui se tait ou une page fautive qui
passe sont bien rejetés.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_all_pages_qa as qa  # noqa: E402
import build_1spe_release_blocker_ledger as ledger  # noqa: E402
import build_1spe_release_test_gate as gate  # noqa: E402


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        pytest.skip(f"artefact absent : {path}")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Périmètre de test de la release
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def scope() -> dict[str, Any]:
    return _load(gate.JSON_TARGET)


def test_the_scope_is_a_proof_not_a_pytest_exception(scope: dict[str, Any]) -> None:
    """Aucun test n'est désactivé : le périmètre nomme, il n'exclut pas."""

    assert "aucun test n'est desactive" in scope["this_is_not_a_pytest_exception"]
    conftest = ROOT / "tests" / "conftest.py"
    if conftest.is_file():
        text = conftest.read_text(encoding="utf-8")
        assert "1NSI" not in text, "aucune exclusion 1NSI ne doit vivre dans conftest"


def test_every_module_is_attributed(scope: dict[str, Any]) -> None:
    summary = scope["summary"]
    assert summary["UNKNOWN_SCOPE"] == 0
    assert summary["GATE_MODULES"] + summary["MANUAL_1NSI_EXCLUSIVE_MODULES"] == (
        summary["TEST_MODULES"]
    )
    assert summary["GATE_MODULES"] > summary["MANUAL_1NSI_EXCLUSIVE_MODULES"]


def test_the_shared_runtime_is_read_from_the_engine_not_guessed(
    scope: dict[str, Any],
) -> None:
    """Les fichiers LaTeX partagés viennent du `.fls`, pas d'une liste écrite."""

    assert scope["shared_runtime_evidence"]["latex"].startswith("lignes INPUT")
    shared = scope["SHARED_RUNTIME_USED_BY_1SPE"]
    # La classe et le runtime de marges y sont, sinon la mesure serait vide de
    # sens : ce sont eux que la construction ouvre.
    assert "gabarits/common/nexus-manuel.cls" in shared
    assert "gabarits/common/nexus-charte.sty" in shared
    assert any(name.endswith("nexus-margin-shipout.lua") for name in shared)
    for variant, inputs in scope["latex_inputs_per_variant"].items():
        assert inputs, variant


def test_a_module_that_names_the_manual_never_leaves_the_scope(
    scope: dict[str, Any],
) -> None:
    """Le doute profite au périmètre, jamais à sa réduction."""

    by_module = {row["module"]: row for row in scope["modules"]}
    for module in scope["out_of_gate_modules"]:
        row = by_module[module]
        assert row["mentions_1spe_in_source"] is False, module
        assert row["designated_1spe_paths"] == [], module
        assert row["designated_shared_paths"] == [], module
        assert row["designated_nsi_paths"], module
        assert not module.startswith("Mathematiques/"), module


def test_the_global_suite_status_is_never_called_green_when_red(
    tmp_path: Path,
) -> None:
    capture = tmp_path / "global.log"
    capture.write_text(
        "FAILED NSI/tests/test_1nsi_status_governance.py::test_x\n"
        "1 failed, 10 passed in 1.00s\n",
        encoding="utf-8",
    )

    payload = gate.build(capture, None)

    assert payload["summary"]["GLOBAL_SUPPORTED_SUITE_STATUS"] == "RED"
    assert payload["summary"]["GLOBAL_FAILURES"] == 1
    assert payload["summary"]["FAILURES_1NSI_EXCLUSIVE"] == 1
    assert payload["summary"]["FAILURES_TOUCHING_1SPE"] == 0


def test_a_failure_inside_the_scope_is_counted_against_the_release(
    tmp_path: Path, scope: dict[str, Any]
) -> None:
    """Une mutation : l'échec tombe dans le périmètre, il doit être vu."""

    inside = scope["gate_modules"][0]
    capture = tmp_path / "global.log"
    capture.write_text(
        f"FAILED {inside}::test_x\n1 failed, 10 passed in 1.00s\n", encoding="utf-8"
    )

    payload = gate.build(capture, None)

    assert payload["summary"]["FAILURES_TOUCHING_1SPE"] == 1
    assert payload["summary"]["GLOBAL_SUPPORTED_SUITE_STATUS"] == "RED"


def test_a_missing_fls_makes_the_scope_unprovable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sans la trace d'ouverture du moteur, la portée LaTeX serait vide."""

    monkeypatch.setattr(
        gate, "FLS_FILES", (Path("Mathematiques/manuel-maths/build/absent.fls"),)
    )

    with pytest.raises(gate.GateError, match="absent"):
        gate.build(None, None)


# ---------------------------------------------------------------------------
#  Registre des bloqueurs
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def blockers() -> dict[str, Any]:
    return _load(ledger.JSON_TARGET)


def test_the_ledger_only_holds_what_can_reach_the_1spe_release(
    blockers: dict[str, Any],
) -> None:
    allowed = {
        "1SPE_RELEASE_BLOCKER",
        "1SPE_SHARED_RELEASE_BLOCKER",
        "HUMAN_DECISION_PENDING",
        "OTHER_MANUAL_SCOPE_DEBT",
    }
    surfaces = {
        "1SPE_SEMANTIC_CONTENT",
        "1SPE_MACHINE_PROOF",
        "1SPE_HUMAN_REVIEW",
        "1SPE_BUILD",
        "1SPE_STYLE_RENDER",
        "1SPE_PRINT_ARTIFACT",
    }
    for row in blockers["blockers"]:
        assert row["scope"] in allowed, row["blocker_id"]
        assert row["surface"] in surfaces, row["blocker_id"]
        assert row["meaning"].strip(), row["blocker_id"]
    assert blockers["approves_nothing"] is True


def test_every_observed_finding_carries_an_executable_check(
    blockers: dict[str, Any],
) -> None:
    """Un constat sans vérification serait une affirmation, pas une preuve."""

    docket = _load(ledger.DOCKET)
    declared = {row["blocker_id"] for row in docket["observed_findings"]}
    assert declared <= set(ledger.CHECKS), declared - set(ledger.CHECKS)
    for row in blockers["blockers"]:
        if row["blocker_id"] in declared:
            assert row["state"] in {"OPEN", "RESOLVED"}, row


def test_a_derived_blocker_closes_when_its_metric_reaches_zero() -> None:
    """Le registre suit le producteur : rien n'y reste par inertie."""

    rows = {row["blocker_id"]: row for row in ledger.derived_blockers()}
    closed = [row for row in rows.values() if row["state"] == "CLOSED"]
    assert closed, "aucun bloqueur ferme : le mecanisme ne serait pas eprouve"
    for row in closed:
        assert row["observed"] in (0, False, [], "")


def test_a_missing_producer_artifact_is_unverifiable_not_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ledger,
        "DERIVED_SOURCES",
        (
            {
                "artifact": "audit/DOES_NOT_EXIST.json",
                "metric": "ANYTHING",
                "blocker_id": "FIXTURE",
                "scope": "1SPE_RELEASE_BLOCKER",
                "surface": "1SPE_MACHINE_PROOF",
                "meaning": "fixture",
                "closes_with": "MACHINE",
            },
        ),
    )

    rows = ledger.derived_blockers()

    assert rows[0]["state"] == "UNVERIFIABLE"
    assert "absent" in rows[0]["reason"]


# ---------------------------------------------------------------------------
#  Contrôle de toutes les pages
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def pages() -> dict[str, Any]:
    return _load(qa.JSON_TARGET)


def test_no_page_is_sampled_away(pages: dict[str, Any]) -> None:
    assert pages["sampling"].startswith("aucun")
    for row in pages["variants"]:
        assert row["pages_inspected"] == row["page_count"]
        assert row["coverage"] == "100%"
        assert row["page_count"] > 300, row["variant"]


def test_every_bleed_in_the_band_is_contractual(pages: dict[str, Any]) -> None:
    """Entre le format fini et le fond perdu, l'encre s'imprime : elle se décide."""

    assert pages["summary"]["UNDECLARED_INK_IN_BLEED_BAND"] == 0
    # Le contrôle serait vide de sens si rien ne débordait : l'onglet et les
    # aplats d'ouverture débordent, par contrat.
    assert pages["summary"]["DECLARED_INK_IN_BLEED_BAND"] > 0
    for row in pages["variants"]:
        reasons = {
            entry["reason"]
            for page in row["pages"]
            for entry in page["bleed_band_declared"]
        }
        assert reasons <= {"TAB_CONTRACTUAL_1MM_BLEED", "FULL_BLEED_PAGE_ELEMENT"}


def test_ink_beyond_the_support_is_named_and_never_confused_with_a_bleed(
    pages: dict[str, Any],
) -> None:
    """Au-delà du support rien n'est rendu : c'est de l'hygiène, pas un défaut."""

    assert "INK_BEYOND_SUPPORT" in pages["summary"]
    for row in pages["variants"]:
        for page in row["pages"]:
            for entry in page["ink_beyond_support"]:
                assert entry["beyond_mm"], entry
                # Un même tracé n'est jamais compté dans les deux familles.
                assert entry["drawing"] not in {
                    other["drawing"] for other in page["ink_in_bleed_band"]
                }


def test_the_measurement_tolerance_is_a_machine_dot(pages: dict[str, Any]) -> None:
    """0,05 bp : moins de deux points à 2400 dpi, la plus fine des presses."""

    assert pages["measurement_tolerance_bp"] == qa.MEASUREMENT_TOLERANCE_BP
    machine_dot_bp = 72 / 2400
    assert qa.MEASUREMENT_TOLERANCE_BP < 2 * machine_dot_bp
    # Et bien au-dessous du vingtième de millimètre : une dérive réelle de mise
    # en page, qui vaut des millimètres, ne peut pas s'y cacher.
    assert qa.MEASUREMENT_TOLERANCE_BP < 0.05 * qa.BP_PER_MM
    assert qa.MEASUREMENT_TOLERANCE_BP / qa.BP_PER_MM < 0.02


# ---------------------------------------------------------------------------
#  Mutations du contrôle de pages : il doit savoir dire non
# ---------------------------------------------------------------------------


def _report(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"ink_in_bleed_band": []}
    base.update(overrides)
    return base


def _band(**beyond: float) -> dict[str, Any]:
    return {"drawing": 0, "rect": [0, 0, 1, 1], "beyond_mm": beyond}


def test_the_tab_bleed_of_one_millimetre_is_recognised_as_contractual() -> None:
    declared, undeclared = qa.classify_outside_trim(
        _report(ink_in_bleed_band=[_band(right=1.0)])
    )

    assert undeclared == []
    assert [row["reason"] for row in declared] == ["TAB_CONTRACTUAL_1MM_BLEED"]


def test_a_full_bleed_page_carries_its_pattern_with_it() -> None:
    """Un aplat va au bord ; ce qu'il contient déborde avec lui."""

    declared, undeclared = qa.classify_outside_trim(
        _report(ink_in_bleed_band=[_band(left=3.0, top=3.0), _band(left=0.16)])
    )

    assert undeclared == []
    assert [row["reason"] for row in declared] == [
        "FULL_BLEED_PAGE_ELEMENT",
        "FULL_BLEED_PAGE_ELEMENT",
    ]


def test_the_same_overhang_on_an_ordinary_page_is_undeclared() -> None:
    """Sans aplat de fond perdu, seul l'onglet traverse le trait de coupe.

    C'est la même mesure — 0,16 mm — et elle change de verdict avec la page :
    la décision porte sur la page, pas sur le tracé.
    """

    declared, undeclared = qa.classify_outside_trim(
        _report(ink_in_bleed_band=[_band(left=0.16)])
    )

    assert declared == []
    assert len(undeclared) == 1


def test_an_ink_overhang_that_is_neither_is_undeclared() -> None:
    declared, undeclared = qa.classify_outside_trim(
        _report(ink_in_bleed_band=[_band(right=2.1)])
    )

    assert declared == []
    assert len(undeclared) == 1


def test_an_overhang_below_the_engine_precision_is_not_reported() -> None:
    """Deux points machine à 2400 dpi : sous cette borne, rien n'est mesurable."""

    fitz = pytest.importorskip("fitz")
    box = fitz.Rect(0, 0, 100, 100)
    inside = fitz.Rect(0, 0, 100 + qa.MEASUREMENT_TOLERANCE_BP / 2, 100)
    outside = fitz.Rect(0, 0, 100 + qa.MEASUREMENT_TOLERANCE_BP * 4, 100)

    assert qa._outside(inside, box, qa.MEASUREMENT_TOLERANCE_BP) == {}
    assert "right" in qa._outside(outside, box, qa.MEASUREMENT_TOLERANCE_BP)
