"""Contrats réglementaires minimaux de la collection 2026-2027."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/programmes/PROGRAMMES_2026_2027.yaml"
MATH_SOURCES = ROOT / "Mathematiques/manuel-maths/sources/SOURCES.md"
CORRECT_TSPE_NOR = "MENE1921246A"
STMG_NOR = "MENE1921262A"


def test_p0_tspe_registry_uses_the_official_mathematics_nor() -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    source = registry["sources"]["SRC-BO2019-TSPE"]
    manuals = [
        item
        for item in registry["manuels"]
        if item["manual_id"] == "TSPE_2026_2027"
    ]

    assert len(manuals) == 1
    manual = manuals[0]
    assert manual["programme_source"] == "SRC-BO2019-TSPE"
    assert source["arrete"] == CORRECT_TSPE_NOR
    assert source["arrete"] != STMG_NOR


def test_p0_tspe_sources_table_uses_the_official_mathematics_nor() -> None:
    lines = MATH_SOURCES.read_text(encoding="utf-8").splitlines()
    rows = [
        line for line in lines if "`BO2019_TSPE_specialite.pdf`" in line
    ]

    assert len(rows) == 1
    row = rows[0]
    assert CORRECT_TSPE_NOR in row
    assert STMG_NOR not in row
