"""Le sommaire canonique réserve la place d'un folio à quatre chiffres.

Défaut mesuré le 2026-09-03 sur les deux variantes du manuel 1SPE : 21
« Overfull \\hbox (0.95421pt too wide) » (10/10 côté élève, 11/11 côté
professeur), tous portés par une entrée de CHAPITRE du sommaire dont le folio
compte trois chiffres. Cause : `nexus-pages-froides.sty` compose ces folios en
`\\nxTocChapPage` (titre gras 10 pt) alors que la boîte qui les reçoit garde
la largeur KOMA par défaut `\\@pnumwidth` = 1,55 em, calculée pour la fonte de
corps. Trois chiffres y mesurent 15,68 pt contre 14,73 pt réservés, soit
exactement 0,95 pt de débordement.

Correction au niveau du LAYOUT canonique : la réserve est mesurée à
l'exécution sur quatre chiffres dans la fonte de folio réelle, et
`\\@tocrmarg` reste solidaire de `\\@pnumwidth`. Les corrections interdites
(réduction de fonte, `\\hspace` local dans les entrées, rustine chapitre par
chapitre) sont verrouillées ici.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COLD_PAGES = ROOT / "gabarits/common/nexus-pages-froides.sty"
BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
LOGS = {
    "eleve": BUILD / "MANUEL_1SPE_eleve.log",
    "professeur": BUILD / "MANUEL_1SPE_professeur.log",
}
OVERFULL = re.compile(r"^Overfull \\hbox", re.MULTILINE)


@pytest.fixture(scope="module")
def cold_pages() -> str:
    return COLD_PAGES.read_text(encoding="utf-8")


def test_the_folio_reserve_is_measured_on_four_digits(cold_pages: str) -> None:
    """Quatre chiffres, mesurés dans la fonte de folio, pas une constante."""

    assert r"\newcommand*{\nxTocFolioGabarit}{8888}" in cold_pages
    assert (
        r"\settowidth{\nxTocFolioWidth}{\nxTocChapPage{\nxTocFolioGabarit}}"
        in cold_pages
    )


def test_the_reserve_replaces_the_koma_default_for_the_whole_toc(
    cold_pages: str,
) -> None:
    """`\\@pnumwidth` et `\\@tocrmarg` bougent ensemble, écart d'un cadratin."""

    assert r"\renewcommand*{\@pnumwidth}{\nxTocFolioWidth}" in cold_pages
    assert r"\renewcommand*{\@tocrmarg}{\nxTocFolioMarge}" in cold_pages
    assert (
        r"\setlength{\nxTocFolioMarge}{\dimexpr\nxTocFolioWidth+1em\relax}"
        in cold_pages
    )


def test_the_chapter_folio_font_is_not_shrunk(cold_pages: str) -> None:
    """La correction interdite « réduire la police » reste interdite."""

    assert (
        r"\newcommand{\nxTocChapPage}[1]{{\titrefont\fontsize{10}{12}\selectfont"
        in cold_pages
    )


def test_the_toc_style_carries_no_local_spacing_patch(cold_pages: str) -> None:
    """Aucun rattrapage local : ni `\\hspace`, ni `\\kern` dans les folios."""

    style = cold_pages.split("SOMMAIRE STYLÉ", 1)[1]
    assert r"\hspace" not in style
    assert r"\kern" not in style


@pytest.mark.parametrize("variant", sorted(LOGS))
def test_the_built_manual_carries_no_overfull_hbox(variant: str) -> None:
    """Cible contractuelle : OVERFULL_HBOX = 0 sur les deux variantes."""

    log = LOGS[variant]
    if not log.exists():
        pytest.skip(f"journal de build absent : {log}")
    offenders = OVERFULL.findall(log.read_text(encoding="utf-8", errors="replace"))

    assert offenders == [], f"{len(offenders)} Overfull \\hbox dans {log.name}"
