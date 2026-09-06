"""Les livrets auxiliaires maths sont des produits, pas des extraits bruts.

Quatre des six assemblages manquants se dérivaient des sources déjà présentes :
l'assembleur savait parcourir les chapitres, poser les ouvertures et marquer les
rubriques ; il lui manquait la déclaration des variantes. Ces tests vérifient
que l'ajout n'a rien changé aux manuels existants et que les livrets sont
réellement structurés.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "Mathematiques/manuel-maths/scripts"))

import inventory_assembly as ia  # noqa: E402
import assemble_manuel as assembler  # noqa: E402

ASSEMBLER = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
AUXILIARY = ("methodes", "remediation")
MATHS_MANUALS = ("1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES")


def test_the_assembler_still_satisfies_its_declaration_contract() -> None:
    analysis = ia.analyze_assembler(ASSEMBLER)
    assert ia.validate_analysis(ASSEMBLER, analysis) == []


def test_the_four_variants_are_statically_resolvable() -> None:
    analysis = ia.analyze_assembler(ASSEMBLER)
    assert analysis["variants"] == ["eleve", "methodes", "professeur", "remediation"]


def test_variant_orders_cover_exactly_the_declared_variants() -> None:
    assert set(assembler.VARIANT_ORDERS) == set(assembler.VARIANTS)
    assert set(assembler.ELEVE_VARIANTS) <= set(assembler.VARIANTS)
    assert "eleve" in assembler.ELEVE_VARIANTS


def test_the_student_and_teacher_orders_still_match_order() -> None:
    """L'ajout des livrets ne doit pas déplacer un seul objet des manuels."""
    reference = [tuple(rule) for rule in assembler.ORDER]
    for variant in ("eleve", "professeur"):
        assert [tuple(rule) for rule in assembler.VARIANT_ORDERS[variant]] == reference


@pytest.mark.parametrize("manual", MATHS_MANUALS)
@pytest.mark.parametrize("variant", AUXILIARY)
def test_each_auxiliary_booklet_selects_only_its_own_rubric(manual, variant) -> None:
    directory = {"methodes": "methodes", "remediation": "remediation"}[variant]
    collected = 0
    for chapter in assembler.MANUAL_CHAPTERS[manual]:
        chapter_dir = assembler.ROOT / "chapitres" / chapter
        if not chapter_dir.exists():
            continue
        files = assembler.collect_chapter(chapter_dir, variant)
        collected += len(files)
        assert all(path.parent.name == directory for path in files), chapter
        assert len(set(files)) == len(files), f"doublon dans {chapter}"
    assert collected > 0, f"{manual}/{variant} ne collecte aucun objet"


@pytest.mark.parametrize("variant", AUXILIARY)
def test_an_auxiliary_booklet_never_carries_a_correction(variant) -> None:
    for manual in MATHS_MANUALS:
        for chapter in assembler.MANUAL_CHAPTERS[manual]:
            chapter_dir = assembler.ROOT / "chapitres" / chapter
            if not chapter_dir.exists():
                continue
            for path in assembler.collect_chapter(chapter_dir, variant):
                assert "corriges" not in path.parts


def test_an_unknown_variant_is_still_refused() -> None:
    chapter_dir = assembler.ROOT / "chapitres" / "1SPE-SECOND-DEGRE"
    with pytest.raises(assembler.AssemblyError):
        assembler.collect_chapter(chapter_dir, "livret_inconnu")


# --- Déclaration dans l'inventaire -------------------------------------------

def _declared() -> set[str]:
    inventory = json.loads(
        (ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )
    return {a["assembly_id"] for a in inventory["declared_assemblies"]}


@pytest.mark.parametrize("manual", MATHS_MANUALS)
@pytest.mark.parametrize("variant", AUXILIARY)
def test_the_auxiliary_assembly_is_declared(manual, variant) -> None:
    assert f"math:manual:{manual}:{variant}" in _declared()


def test_the_twelve_canonical_manual_assemblies_are_still_declared() -> None:
    declared = _declared()
    for manual in MATHS_MANUALS:
        for variant in ("eleve", "professeur"):
            assert f"math:manual:{manual}:{variant}" in declared
    for manual in ("1NSI", "TNSI"):
        for variant in ("eleve", "professeur"):
            assert f"nsi:manual:{manual}:{variant}" in declared


def test_the_two_ece_banks_remain_content_gaps() -> None:
    """Le créneau `ece` est déclaré par l'assembleur NSI, le contenu n'existe pas."""
    import build_deliverable_assembly_forensics as forensics

    payload = forensics.build()
    still_missing = [
        record["deliverable_id"] for record in payload["deliverables"]
        if not record["assembly_declared"]
    ]
    assert sorted(still_missing) == ["TNSI::banque_ecrite", "TNSI::banque_pratique"]
    assert payload["summary"]["NEW_MASTERS_WRITTEN"] == 0
    assert not any((ROOT / "NSI/chapitres" / c / "ece").exists()
                   for c in ("TNSI-ALGORITHMIQUE", "TNSI-BASES-DE-DONNEES"))
