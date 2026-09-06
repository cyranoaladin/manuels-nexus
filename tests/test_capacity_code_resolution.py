"""Les codes locaux de chapitre doivent être résolus vers les capacités officielles.

Un objet de cours porte typiquement `capacites_codes: ["C1", "C2"]` et laisse
`capacites` à null ; la correspondance vers `T-STRUCT-01A` vit dans le
`contrat.yaml` du chapitre. Ne pas la suivre faisait déclarer non couvertes dix
capacités que le manuel enseigne réellement — un défaut de producteur pris pour
une lacune de contenu.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dimension_regulation as regulation  # noqa: E402
import build_tnsi_curricular_coverage as tnsi  # noqa: E402

CHAPTER = ROOT / "NSI/chapitres/TNSI-STRUCTURES-DONNEES"


@pytest.mark.parametrize("module", [regulation, tnsi], ids=["regulation", "tnsi"])
def test_chapter_contract_maps_local_codes_to_official_capacities(module) -> None:
    mapping = module.chapter_code_map(CHAPTER)
    assert mapping["C1"] == ["T-STRUCT-01A"]
    assert mapping["C2"] == ["T-STRUCT-01B"]
    assert mapping["C3"] == ["T-STRUCT-01C"]
    assert mapping["C8"] == ["T-STRUCT-03C"]


@pytest.mark.parametrize("module", [regulation, tnsi], ids=["regulation", "tnsi"])
def test_a_local_code_may_cover_several_official_capacities(module) -> None:
    """Le programme 2026 scinde le second degré : un code local en couvre deux."""
    mapping = module.chapter_code_map(
        ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE"
    )
    assert mapping["C4"] == [
        "1SPE-SECOND-DEGRE-2026-C1",
        "1SPE-SECOND-DEGRE-2026-C3",
    ]
    assert mapping["C3"] == ["1SPE-SECOND-DEGRE-2026-D1"]


@pytest.mark.parametrize("module", [regulation, tnsi], ids=["regulation", "tnsi"])
def test_a_missing_contract_yields_no_mapping(module, tmp_path: Path) -> None:
    assert module.chapter_code_map(tmp_path) == {}


@pytest.mark.parametrize("module", [regulation, tnsi], ids=["regulation", "tnsi"])
def test_an_unreadable_contract_yields_no_mapping(module, tmp_path: Path) -> None:
    (tmp_path / "contrat.yaml").write_text("capacites: [oops\n", encoding="utf-8")
    assert module.chapter_code_map(tmp_path) == {}


def test_every_chapter_contract_declares_its_official_references() -> None:
    """Sans cette table, la conformité réglementaire n'est pas calculable."""
    contracts = sorted(ROOT.glob("NSI/chapitres/*/contrat.yaml")) + sorted(
        ROOT.glob("Mathematiques/manuel-maths/chapitres/*/contrat.yaml")
    )
    assert len(contracts) == 52
    without = [c.parent.name for c in contracts if not regulation.chapter_code_map(c.parent)]
    assert without == [], f"contrats sans ref_capacite : {without}"


def test_tnsi_official_capacities_are_fully_covered_once_codes_are_resolved() -> None:
    payload = tnsi.build()
    summary = payload["summary"]
    assert summary["OFFICIAL_CAPACITIES_UNCOVERED"] == 0
    assert summary["OFFICIAL_CAPACITIES_COVERED"] == summary["OFFICIAL_CAPACITIES_TOTAL"] == 61
