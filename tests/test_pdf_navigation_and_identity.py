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

import re
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
    # Le sommaire du manuel descend jusqu'aux sous-sections de cours ; les
    # signets le recopient, sans jamais aller plus bas.
    assert levels <= {1, 2, 3}, f"profondeur de signet inattendue : {levels}"
    assert sum(1 for level, _, _ in outline if level == 1) >= 10
    # Pas un signet par micro-objet : aucun exercice, aucune définition,
    # aucune figure n'écrit d'entrée de sommaire, donc aucun n'est signet.
    assert len(outline) < page_count // 3, "signets trop nombreux pour un sommaire"
    micro = [
        title
        for _, title, _ in outline
        if re.match(r"(Exercice|Corrigé|Figure|Définition|Théorème)\s+\d", title)
    ]
    assert micro == [], micro

    for level, title, page in outline:
        assert title.strip(), "signet sans libellé"
        assert 1 <= page <= page_count, f"destination cassée : {title!r} -> {page}"

    entries = [tuple(entry) for entry in outline]
    assert len(set(entries)) == len(entries), "signets en doublon"


def _normalise(text: str) -> str:
    return " ".join(text.replace("’", "'").replace(" ", " ").split())


@pytest.mark.parametrize("variant", sorted(TITLES))
def test_the_outline_repeats_the_printed_summary(variant: str) -> None:
    """Contrat : le signet renvoie à la page que le sommaire imprime.

    On lit le sommaire composé dans le PDF lui-même et on confronte, entrée
    par entrée et dans l'ordre du document, son folio à la page de destination
    du signet. Une destination fausse est un signet qui ne mène pas où le
    sommaire annonce.

    Les entrées dont le titre porte des mathématiques ne sont pas comparables
    par le texte (le sommaire compose « 𝑡↦e^{𝑎𝑡} » en glyphes de fonte
    mathématique, le signet porte la traduction Unicode « t↦eat ») : elles
    sont comptées à part, et restent une minorité.
    """

    with _document(variant) as document:
        outline = document.get_toc()
        first = next(
            index
            for index in range(document.page_count)
            if document[index].get_text().lstrip().startswith("Sommaire")
        )
        after = min(page for _, _, page in outline if page > first + 1)
        summary = _normalise(
            "\n".join(document[i].get_text() for i in range(first, after - 1))
        )

    cursor = 0
    mismatched = []
    unlocated = []
    for _level, title, page in outline:
        needle = _normalise(title)
        position = summary.find(needle, cursor)
        if position < 0:
            unlocated.append(title)
            continue
        cursor = position + len(needle)
        folio = re.search(r"(\d+)", summary[cursor : cursor + 220])
        if folio is None or int(folio.group(1)) != page:
            mismatched.append((title, page, folio and folio.group(1)))

    assert mismatched == [], f"signets en desaccord avec le sommaire : {mismatched}"
    assert len(unlocated) <= len(outline) // 10, unlocated


@pytest.mark.parametrize("variant", sorted(TITLES))
def test_the_pdf_carries_navigation_links(variant: str) -> None:
    with _document(variant) as document:
        links = sum(len(page.get_links()) for page in document)

    assert links > 0
