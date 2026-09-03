"""Boîtes de page : format fini A4, fond perdu de 3 mm, onglet à 1 mm.

Défaut mesuré le 2026-09-03 : les deux PDF ne portaient qu'une MediaBox A4, ni
TrimBox ni BleedBox, et l'encre de l'onglet latéral débordait de 1,00 mm HORS
MediaBox — donc rognée par tout viewer et par tout imprimeur.

Décision produit : TrimBox = 210 × 297 mm, BleedBox = TrimBox + 3 mm sur les
quatre côtés, MediaBox contenant la BleedBox.

Piège verrouillé ici : offrir 3 mm de fond perdu ne fait PAS passer l'onglet à
3 mm. Sa géométrie contractuelle (12 mm visibles à l'intérieur du format fini,
1 mm seulement à l'extérieur, page impaire à droite et page paire à gauche)
est mesurée désormais par rapport à la TrimBox, et doit être identique à ce
qu'elle était par rapport à l'ancienne page.
"""

from __future__ import annotations

from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

ROOT = Path(__file__).resolve().parents[1]
CLASS = ROOT / "gabarits/common/nexus-manuel.cls"
BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
PDFS = {name: BUILD / f"MANUEL_1SPE_{name}.pdf" for name in ("eleve", "professeur")}

BP_PER_MM = 72 / 25.4
A4 = (210 * BP_PER_MM, 297 * BP_PER_MM)
BLEED = 3 * BP_PER_MM
TOLERANCE = 0.05  # bp, soit moins de 0,02 mm
TAB_TOTAL_MM = 13.0
TAB_INSIDE_MM = 12.0
TAB_OUTSIDE_MM = 1.0


def _document(variant: str):
    pdf = PDFS[variant]
    if not pdf.exists():
        pytest.skip(f"PDF absent : {pdf}")
    return fitz.open(pdf)


def test_the_bleed_is_declared_in_the_canonical_pipeline() -> None:
    """Aucun post-traitement PDF opaque : le moteur pose les boîtes."""

    source = CLASS.read_text(encoding="utf-8")

    assert r"\newcommand*{\nxFondPerduDim}{3mm}" in source
    assert r"\pdfvariable pageattr\expandafter{\nx@boitesDePage}" in source
    assert "/TrimBox" in source and "/BleedBox" in source
    # \newgeometry et \restoregeometry remettraient \hoffset à zéro.
    assert r"\apptocmd{\newgeometry}{\nxAppliquerFondPerdu}" in source
    assert r"\apptocmd{\restoregeometry}{\nxAppliquerFondPerdu}" in source


def test_the_tab_geometry_is_still_expressed_against_the_finished_format() -> None:
    """12 mm dedans, 1 mm dehors : le fond perdu ne les renégocie pas."""

    source = CLASS.read_text(encoding="utf-8")

    assert "xshift=-12mm" in source
    assert "xshift=12mm" in source
    assert "xshift=1mm" in source
    assert "xshift=-1mm" in source
    assert "xshift=-3mm,yshift" not in source


@pytest.mark.parametrize("variant", sorted(PDFS))
def test_every_page_carries_the_three_boxes(variant: str) -> None:
    with _document(variant) as document:
        for index, page in enumerate(document, start=1):
            trim, bleed, media = page.trimbox, page.bleedbox, page.mediabox

            assert abs(trim.width - A4[0]) < TOLERANCE, index
            assert abs(trim.height - A4[1]) < TOLERANCE, index
            assert abs(bleed.width - (A4[0] + 2 * BLEED)) < TOLERANCE, index
            assert abs(bleed.height - (A4[1] + 2 * BLEED)) < TOLERANCE, index
            # BleedBox = TrimBox élargie de 3 mm sur les quatre côtés.
            assert abs((trim.x0 - bleed.x0) - BLEED) < TOLERANCE, index
            assert abs((bleed.x1 - trim.x1) - BLEED) < TOLERANCE, index
            assert abs((trim.y0 - bleed.y0) - BLEED) < TOLERANCE, index
            assert abs((bleed.y1 - trim.y1) - BLEED) < TOLERANCE, index
            # MediaBox contient la BleedBox.
            assert media.x0 <= bleed.x0 + TOLERANCE, index
            assert media.y0 <= bleed.y0 + TOLERANCE, index
            assert media.x1 >= bleed.x1 - TOLERANCE, index
            assert media.y1 >= bleed.y1 - TOLERANCE, index


def _tab_rectangles(page):
    """Rectangles pleins qui débordent du format fini à la largeur d'onglet."""

    trim = page.trimbox
    found = []
    for drawing in page.get_drawings():
        if not drawing["fill"]:
            continue
        rect = drawing["rect"]
        width_mm = (rect.x1 - rect.x0) / BP_PER_MM
        crosses = rect.x1 > trim.x1 + 0.1 or rect.x0 < trim.x0 - 0.1
        if not crosses or rect.y1 - rect.y0 < 40:
            continue
        if abs(width_mm - TAB_TOTAL_MM) > 0.05:
            continue
        found.append((rect.x0, rect.x1, trim))
    return found


@pytest.mark.parametrize("variant", sorted(PDFS))
def test_the_tab_bleeds_one_millimetre_and_faces_the_right_way(variant: str) -> None:
    observed = {"odd": 0, "even": 0}
    with _document(variant) as document:
        for number, page in enumerate(document, start=1):
            for x0, x1, trim in _tab_rectangles(page):
                outside_right = (x1 - trim.x1) / BP_PER_MM
                inside_right = (trim.x1 - x0) / BP_PER_MM
                outside_left = (trim.x0 - x0) / BP_PER_MM
                inside_left = (x1 - trim.x0) / BP_PER_MM
                if outside_right > 0:
                    assert number % 2 == 1, f"onglet à droite sur page paire {number}"
                    assert abs(outside_right - TAB_OUTSIDE_MM) < 0.05, number
                    assert abs(inside_right - TAB_INSIDE_MM) < 0.05, number
                    observed["odd"] += 1
                else:
                    assert number % 2 == 0, f"onglet à gauche sur page impaire {number}"
                    assert abs(outside_left - TAB_OUTSIDE_MM) < 0.05, number
                    assert abs(inside_left - TAB_INSIDE_MM) < 0.05, number
                    observed["even"] += 1

    assert observed["odd"] > 0 and observed["even"] > 0, observed


@pytest.mark.parametrize("variant", sorted(PDFS))
def test_the_cover_ink_reaches_the_bleed_box(variant: str) -> None:
    """Un aplat de couverture qui s'arrête au format fini laisse un filet blanc."""

    with _document(variant) as document:
        for index in (0, document.page_count - 1):
            page = document[index]
            bleed = page.bleedbox
            covered = [
                drawing
                for drawing in page.get_drawings()
                if drawing["fill"]
                and drawing["rect"].x0 <= bleed.x0 + 0.5
                and drawing["rect"].y0 <= bleed.y0 + 0.5
                and drawing["rect"].x1 >= bleed.x1 - 0.5
                and drawing["rect"].y1 >= bleed.y1 - 0.5
            ]

            assert covered, f"page de couverture {index + 1} sans fond perdu"
