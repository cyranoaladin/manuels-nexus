"""Tests de l'inventaire canonique des cibles de publication (LOT 0.1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
INVENTORY_JSON = ROOT / "audit/CANONICAL_RELEASE_INVENTORY.json"
BUILDER_SCRIPT = ROOT / "scripts/build_canonical_release_inventory.py"


@pytest.fixture(scope="module")
def inventory() -> dict:
    assert INVENTORY_JSON.is_file(), f"L'artefact {INVENTORY_JSON} doit exister"
    with INVENTORY_JSON.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_canonical_manual_and_pdf_counts(inventory: dict) -> None:
    summary = inventory["summary"]
    assert summary["CANONICAL_MANUALS"] == 6, "La collection compte exactement 6 manuels canoniques"
    assert summary["CANONICAL_PDFS"] == 12, "La collection compte exactement 12 PDF canoniques"
    assert len(inventory["canonical_targets"]) == 12


def test_zero_unregistered_and_zero_missing(inventory: dict) -> None:
    summary = inventory["summary"]
    assert summary["UNREGISTERED_RELEASE_TARGET"] == 0
    assert summary["MISSING_CANONICAL_TARGET"] == 0
    assert summary["AMBIGUOUS_CURRENT_ARTIFACT"] == 0
    assert summary["UNKNOWN"] == 0


def test_all_canonical_targets_have_master_and_pdf_present(inventory: dict) -> None:
    for target in inventory["canonical_targets"]:
        manual = target["manual_id"]
        variant = target["variant"]
        master = ROOT / target["master"]
        pdf = ROOT / target["pdf"]
        assert target["master_present"] is True, f"Master absent pour {manual}:{variant}"
        assert target["pdf_present"] is True, f"PDF absent pour {manual}:{variant}"
        assert master.is_file(), f"Fichier master introuvable sur disque: {master}"
        assert pdf.is_file(), f"Fichier PDF introuvable sur disque: {pdf}"


def test_expected_manual_ids(inventory: dict) -> None:
    expected_ids = {"1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"}
    observed_ids = {t["manual_id"] for t in inventory["canonical_targets"]}
    assert observed_ids == expected_ids


def test_mutation_missing_canonical_target_detected(monkeypatch) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_canonical_release_inventory as mod

    mutated_builds = dict(mod.CANONICAL_BUILDS)
    del mutated_builds["1SPE"]
    monkeypatch.setattr(mod, "CANONICAL_BUILDS", mutated_builds)

    report = mod.build()
    summary = report["summary"]
    assert summary["CANONICAL_MANUALS"] == 5
    assert summary["UNREGISTERED_RELEASE_TARGET"] > 0 or summary["MISSING_CANONICAL_TARGET"] > 0


def test_tex_roots_exact_partition(inventory: dict) -> None:
    summary = inventory["summary"]
    assert summary["TOTAL_TEX_ROOTS"] == 45
    assert summary["CANONICAL_RELEASE_ROOTS"] == 12
    assert summary["EXPLICIT_NON_RELEASE_ROOTS"] == 33
    assert summary["CANONICAL_RELEASE_ROOTS"] + summary["EXPLICIT_NON_RELEASE_ROOTS"] == summary["TOTAL_TEX_ROOTS"]
    assert summary["UNCLASSIFIED_TEX_ROOTS"] == 0
    assert summary["EXTRA_ASSEMBLER_VARIANTS"] == 5
    assert summary["NON_RELEASE_TARGETS"] == 38
