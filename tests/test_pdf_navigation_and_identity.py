"""Le PDF publié porte des signets et une identité, pas un fichier anonyme.

Défaut mesuré le 2026-09-03 : aucun `hyperref` n'était chargé. Les deux PDF
sortaient avec zéro signet, zéro lien et un dictionnaire Info entièrement vide
(`title`, `author`, `subject`, `keywords`), alors qu'AGENTS.md exige « signets,
liens, métadonnées et polices incorporées » pour tout PDF final.

Correction dans la classe canonique : hyperref est chargé en fin de classe,
les signets recopient exactement les entrées du sommaire (chapitres puis
grandes sections), et les métadonnées sont dérivées des mêmes données
éditoriales que la couverture — donc distinctes d'une variante à l'autre.
"""

from __future__ import annotations

from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

ROOT = Path(__file__).resolve().parents[1]
CLASS = ROOT / "gabarits/common/nexus-manuel.cls"
BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
TITLES = {
    "eleve": "Mathématiques Première spécialité — Édition Élève — 2026-2027",
    "professeur": (
        "Mathématiques Première spécialité — Édition Professeur — 2026-2027"
    ),
}
PDFS = {name: BUILD / f"MANUEL_1SPE_{name}.pdf" for name in TITLES}
PUBLISHER_UTF16 = "FEFF004E00650078007500730020005200E9007500730073006900740065"


@pytest.fixture(scope="module")
def class_source() -> str:
    return CLASS.read_text(encoding="utf-8")


def _document(variant: str):
    pdf = PDFS[variant]
    if not pdf.exists():
        pytest.skip(f"PDF absent : {pdf}")
    return fitz.open(pdf)


def test_hyperref_is_loaded_by_the_canonical_class(class_source: str) -> None:
    assert "]{hyperref}" in class_source
    assert r"\RequirePackage{bookmark}" in class_source
    assert "bookmarks=true" in class_source


def test_a_hand_written_chapter_entry_gets_a_fresh_anchor(class_source: str) -> None:
    """Sinon le signet d'une page liminaire pointe le chapitre précédent."""

    assert r"\newif\ifnxAncreChapitreFraiche" in class_source
    assert r"\ifnxAncreChapitreFraiche\else\phantomsection\fi" in class_source
    assert r"\global\nxAncreChapitreFraichetrue" in class_source


def test_the_metadata_are_derived_not_hard_coded(class_source: str) -> None:
    assert r"pdftitle={\nxTitrePdf}" in class_source
    assert r"pdfauthor={\nxMarqueEditeur}" in class_source
    assert "pdflang={fr-FR}" in class_source
    assert PUBLISHER_UTF16 in class_source
    # /PTEX.FullBanner publierait la distribution et la machine de build.
    assert r"\pdfvariable suppressoptionalinfo=1" in class_source


@pytest.mark.parametrize("variant", sorted(TITLES))
def test_the_built_pdf_carries_its_own_title_and_publisher(variant: str) -> None:
    with _document(variant) as document:
        metadata = document.metadata or {}

        assert metadata["title"] == TITLES[variant]
        assert metadata["author"] == "Nexus Réussite"
        assert metadata["subject"].strip()
        assert metadata["keywords"].strip()
        assert document.xref_get_key(document.pdf_catalog(), "Lang") == (
            "string",
            "fr-FR",
        )


def test_the_two_variants_do_not_share_the_same_identity() -> None:
    titles = set()
    for variant in TITLES:
        with _document(variant) as document:
            titles.add((document.metadata or {}).get("title"))

    assert len(titles) == 2


@pytest.mark.parametrize("variant", sorted(TITLES))
def test_no_metadata_leaks_the_build_environment(variant: str) -> None:
    forbidden = ("/tmp", "/home/", "draft", "brouillon", ".run", "Users")
    with _document(variant) as document:
        values = " ".join(
            str(value) for value in (document.metadata or {}).values()
        )

    for needle in forbidden:
        assert needle.lower() not in values.lower(), needle


@pytest.mark.parametrize("variant", sorted(TITLES))
def test_the_outline_mirrors_the_manual_structure(variant: str) -> None:
    with _document(variant) as document:
        outline = document.get_toc()
        page_count = document.page_count

    assert outline, "aucun signet"
    levels = {level for level, _, _ in outline}
    assert levels <= {1, 2}, f"profondeur de signet inattendue : {levels}"
    assert sum(1 for level, _, _ in outline if level == 1) >= 10

    for level, title, page in outline:
        assert title.strip(), "signet sans libellé"
        assert 1 <= page <= page_count, f"destination cassée : {title!r} -> {page}"

    assert len(set(outline)) == len(outline), "signets en doublon"


@pytest.mark.parametrize("variant", sorted(TITLES))
def test_every_chapter_bookmark_lands_on_its_own_page(variant: str) -> None:
    """Une destination fausse est un signet dont la page ignore son titre."""

    with _document(variant) as document:
        offenders = []
        for level, title, page in document.get_toc():
            if level != 1:
                continue
            text = " ".join(document[page - 1].get_text().split())
            needle = " ".join(title.split())
            if needle not in text:
                offenders.append((title, page))

    assert offenders == [], f"destinations douteuses : {offenders}"


@pytest.mark.parametrize("variant", sorted(TITLES))
def test_the_pdf_carries_navigation_links(variant: str) -> None:
    with _document(variant) as document:
        links = sum(len(page.get_links()) for page in document)

    assert links > 0
