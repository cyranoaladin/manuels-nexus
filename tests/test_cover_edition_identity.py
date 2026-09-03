"""La variante d'édition est nommée sur la couverture et la page de titre.

Défaut mesuré le 2026-09-03 : rien, dans les deux PDF publiés, ne distinguait
l'exemplaire élève de l'exemplaire professeur — ni la première de couverture,
ni une page de titre (il n'en existait aucune), ni les métadonnées. Deux
fichiers de 357 et 629 pages portaient la même identité.

Correction : la variante devient une donnée du producteur canonique. Un seul
booléen, `\\ifnxVersionProfesseur`, alimente `\\nxMentionVariante` (capitales,
sans interlettrage pour rester extractible) et `\\nxLibelleVariante` (casse
éditoriale). Aucun appel de la collection ne répète « élève » ou
« professeur ».

Décision produit associée FIRST_PRINT_EDITION_NO_ISBN : ce premier tirage ne
porte AUCUNE mention d'ISBN — ni numéro, ni « à attribuer », ni « sans ISBN ».
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLASS = ROOT / "gabarits/common/nexus-manuel.cls"
COVER = ROOT / "gabarits/common/nexus-couverture.sty"
BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
PDFS = {
    "eleve": (BUILD / "MANUEL_1SPE_eleve.pdf", "ÉDITION ÉLÈVE", "ÉDITION PROFESSEUR"),
    "professeur": (
        BUILD / "MANUEL_1SPE_professeur.pdf",
        "ÉDITION PROFESSEUR",
        "ÉDITION ÉLÈVE",
    ),
}
# Sources réellement publiées : la classe et les styles canoniques, plus les
# fragments assemblés dans le manuel.
PUBLISHED_SOURCES = (
    *sorted((ROOT / "gabarits/common").glob("*.sty")),
    *sorted((ROOT / "gabarits/common").glob("*.cls")),
    *sorted((ROOT / "gabarits/common").glob("*.tex")),
    *sorted((ROOT / "Mathematiques/manuel-maths/transversal").glob("*.tex")),
)


def _composed(source: str) -> str:
    """Le source réellement composé : les commentaires TeX ne sont pas publiés.

    La provenance de la décision produit (FIRST_PRINT_EDITION_NO_ISBN) doit
    rester lisible dans le style ; ce qui ne doit plus exister, c'est une
    mention composée.
    """

    return "\n".join(
        line.split("%", 1)[0] if not line.lstrip().startswith("%") else ""
        for line in source.splitlines()
    )


def _pdf_text(pdf: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        errors="replace",
        check=True,
        timeout=180,
    )
    return completed.stdout


def test_the_variant_label_derives_from_the_single_variant_boolean() -> None:
    source = CLASS.read_text(encoding="utf-8")

    assert (
        r"\ifnxVersionProfesseur ÉDITION PROFESSEUR\else ÉDITION ÉLÈVE\fi" in source
    )
    assert (
        r"\ifnxVersionProfesseur Édition Professeur\else Édition Élève\fi" in source
    )


def test_the_cover_and_the_title_page_share_that_single_label() -> None:
    """Deux emplacements, une seule source : pas d'argument dupliqué."""

    cover = _composed(COVER.read_text(encoding="utf-8"))
    occurrences = cover.count(r"\nxMentionVariante")

    assert occurrences == 2, "la mention doit venir du même producteur canonique"
    assert r"\newcommand{\nxPageTitreInterieure}[3]" in cover
    assert r"\nxPageTitreInterieure{#2}{#3}{#5}" in cover


def test_no_published_source_mentions_an_isbn() -> None:
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in PUBLISHED_SOURCES
        if re.search(
            r"ISBN", _composed(path.read_text(encoding="utf-8")), re.IGNORECASE
        )
    ]

    assert offenders == []


@pytest.mark.parametrize("variant", sorted(PDFS))
def test_the_built_pdf_names_its_own_edition_twice(variant: str) -> None:
    """Une fois en première de couverture, une fois en page de titre."""

    pdf, expected, forbidden = PDFS[variant]
    if not pdf.exists():
        pytest.skip(f"PDF absent : {pdf}")
    text = _pdf_text(pdf)

    assert text.count(expected) >= 2, f"{expected} attendu deux fois dans {pdf.name}"
    assert forbidden not in text


@pytest.mark.parametrize("variant", sorted(PDFS))
def test_the_built_pdf_carries_no_isbn_at_all(variant: str) -> None:
    pdf = PDFS[variant][0]
    if not pdf.exists():
        pytest.skip(f"PDF absent : {pdf}")

    assert re.search(r"ISBN", _pdf_text(pdf), re.IGNORECASE) is None
