"""Contrats réglementaires minimaux de la collection 2026-2027."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/programmes/PROGRAMMES_2026_2027.yaml"
MATH_SOURCES = ROOT / "Mathematiques/manuel-maths/sources/SOURCES.md"
TSPE_TEXT = ROOT / "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt"
PERIMETER = ROOT / "Mathematiques/manuel-maths/docs/10_perimetre_terminale.md"
ROADMAP = ROOT / "ROADMAP_TERMINALE.md"
ASSEMBLER = ROOT / "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
README = ROOT / "README.md"
CORRECT_TSPE_NOR = "MENE1921246A"
STMG_NOR = "MENE1921262A"
TNSI_NOR = "MENE1921247A"
CORRECT_TSPE_BO = "BO spécial n° 8 du 25 juillet 2019"
CORRECT_TSPE_URL = "https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm"
CORRECT_TSPE_TEXT_PATH = (
    "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt"
)
CORRECT_TSPE_TEXT_SHA256 = (
    "65eb5a55df14a2b3025a96db72fbcb1d917b55e8da7feb13669e28b903712210"
)
CORRECT_PROGRAMME_VERSION = "2019"
CORRECT_APPLICATION_DATE = "2020-09-01"
CORRECT_SOURCES_BO = "BO special n 8 du 25-07-2019"
CORRECT_SOURCES_APPLICATION = "Rentree 2020"
CORRECT_TSPE_PDF_SHA256 = (
    "eb8369e7c1611e90f51491fecc5a7c2081a9c57f9c7fbb08d0414677b56ce16f"
)


def _assert_official_tspe_source(source: dict[str, object]) -> None:
    assert source["reference_bo"] == CORRECT_TSPE_BO
    assert source["arrete"] == CORRECT_TSPE_NOR
    assert source["url"] == CORRECT_TSPE_URL
    assert source["fichier"] == CORRECT_TSPE_TEXT_PATH
    assert source["sha256"] == CORRECT_TSPE_TEXT_SHA256


def test_p0_tspe_registry_uses_the_complete_official_reference() -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    source = registry["sources"]["SRC-BO2019-TSPE"]
    manuals = [
        item
        for item in registry["manuels"]
        if item["manual_id"] == "TSPE_2026_2027"
    ]
    assert len(manuals) == 1
    assert manuals[0]["programme_source"] == "SRC-BO2019-TSPE"
    assert manuals[0]["programme_version"] == CORRECT_PROGRAMME_VERSION
    assert manuals[0]["date_application"] == CORRECT_APPLICATION_DATE
    _assert_official_tspe_source(source)


def test_p0_tspe_sources_table_uses_the_official_mathematics_nor() -> None:
    lines = MATH_SOURCES.read_text(encoding="utf-8").splitlines()
    rows = [line for line in lines if "`BO2019_TSPE_specialite.pdf`" in line]
    assert len(rows) == 1
    row = rows[0]
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    assert cells == [
        "`BO2019_TSPE_specialite.pdf`",
        CORRECT_TSPE_NOR,
        CORRECT_SOURCES_BO,
        CORRECT_SOURCES_APPLICATION,
        f"`{CORRECT_TSPE_PDF_SHA256}`",
    ]


def test_p0_tspe_tracked_extract_keeps_the_archived_digest() -> None:
    assert TSPE_TEXT.is_file()
    digest = hashlib.sha256(TSPE_TEXT.read_bytes()).hexdigest()
    assert digest == CORRECT_TSPE_TEXT_SHA256


def test_p0_tspe_active_documents_use_the_mathematics_nor() -> None:
    expectations = (
        (
            ROADMAP,
            "Maths specialite Terminale (TSPE) | 2019, arrete MENE1921246A",
            "Maths specialite Terminale (TSPE) | 2019, arrete MENE1921262A",
        ),
        (
            PERIMETER,
            "arrete du 19-07-2019, MENE1921246A",
            "arrete du 19-07-2019, MENE1921247A",
        ),
        (
            ASSEMBLER,
            "programme 2019 MENE1921246A",
            "programme 2019 MENE1921247A",
        ),
    )
    for path, expected, stale in expectations:
        text = path.read_text(encoding="utf-8")
        assert expected in text, path
        assert stale not in text, path
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "NSI Terminale (TNSI) | 2019, arrete MENE1921247A" in roadmap


def test_p0_tspe_readme_reports_the_current_fixed_provenance() -> None:
    text = README.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    audited_begin = "<!-- BEGIN CURRENT AUDITED STATE -->"
    audited_end = "<!-- END CURRENT AUDITED STATE -->"
    programmes_begin = "## Programmes officiels 2026-2027"
    programmes_end = "## Enrichissements hors programme"
    historic_p0 = (
        "4. **Provenance TSPE.** Le registre porte `MENE1921262A` (STMG) au lieu de\n"
        "   `MENE1921246A` (spécialité mathématiques)."
    )
    closure = "La provenance TSPE est corrigée et n'est plus un P0 ouvert."
    post_audit_update = f"**Actualisation post-audit — Wave 0.**\n\n{closure}"

    assert text.count(audited_begin) == 1
    assert text.count(audited_end) == 1
    before_audit, remainder = text.split(audited_begin, maxsplit=1)
    audited_state, after_audit = remainder.split(audited_end, maxsplit=1)
    outside_audit = before_audit + after_audit
    programmes = before_audit.split(programmes_begin, maxsplit=1)[1].split(
        programmes_end, maxsplit=1
    )[0]

    assert CORRECT_TSPE_URL in text
    assert "Registre et table des sources alignés" in text
    assert (
        "Le registre canonique et la table des sources attribuent désormais à "
        "TSPE le NOR `MENE1921246A`" in normalized
    )
    assert "Le registre courant attribue encore à TSPE" not in text
    assert historic_p0 in audited_state
    assert closure not in audited_state
    assert post_audit_update in outside_audit
    assert post_audit_update in programmes


@pytest.mark.parametrize("wrong_nor", [STMG_NOR, TNSI_NOR])
def test_p0_tspe_contract_rejects_another_terminal_nor(wrong_nor: str) -> None:
    fixture = {
        "reference_bo": CORRECT_TSPE_BO,
        "arrete": wrong_nor,
        "url": CORRECT_TSPE_URL,
        "fichier": CORRECT_TSPE_TEXT_PATH,
        "sha256": CORRECT_TSPE_TEXT_SHA256,
    }
    with pytest.raises(AssertionError):
        _assert_official_tspe_source(fixture)
