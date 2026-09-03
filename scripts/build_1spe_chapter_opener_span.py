#!/usr/bin/env python3
"""Étendue des ouvertures de chapitre 1SPE : une ouverture, une page.

Invariant contractuel : `opening_start_page == opening_end_page` pour les dix
chapitres, dans les deux variantes. Une ouverture qui déborde sur une seconde
page est un échec, même si la seconde page ne porte que vingt-neuf caractères
de temps estimé — surtout dans ce cas.

Le débordement ne produit AUCUN avertissement : `\\vfill` avale la coupure, le
journal LaTeX reste muet et `Overfull = 0` reste vrai. Il ne se voit que sur la
page rendue, et c'est pourquoi il se mesure ici.

Comment l'étendue est mesurée, sans jamais écrire un numéro de page :

* la page d'OUVERTURE est celle qui porte la bannière — « CHAPITRE n » et le
  bloc « Objectifs — Capacités attendues » ;
* la page suivante n'appartient à l'ouverture que si elle porte un bloc que la
  bannière a PERDU. La rubrique « Ouverture » ne suffit pas : la section
  d'ouverture du chapitre — le contrat, « ce que tu vas savoir faire » — la
  porte elle aussi, et c'est du contenu à part entière. Les confondre ferait
  crier au débordement sur une mise en page saine.

Chaque ouverture doit en outre porter, sur SA page, tout ce que le contrat lui
demande : le titre, les capacités, l'accroche et les temps estimés.

Métriques bloquantes : `MULTI_PAGE_OPENERS`, `OPENER_MISSING_CONTENT`,
`OPENERS_FOUND` (qui doit valoir dix par variante).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_CHAPTER_OPENER_SPAN.json"
MD_TARGET = ROOT / "audit/1SPE_CHAPTER_OPENER_SPAN.md"
GENERATED_BY = "scripts/build_1spe_chapter_opener_span.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")
EXPECTED_OPENERS = 10

BANNER = re.compile(r"CHAPITRE (\d+)")
OBJECTIVES = "Objectifs — Capacités attendues"
OPENER_RUBRIC = "OUVERTURE"
# Ce que l'ouverture doit porter, sur sa propre page.
REQUIRED_CONTENT = {
    "capacities": lambda text: "▶" in text or "C1" in text,
    "hook": lambda text: "À RETENIR" in text or "RETENIR" in text,
    "estimated_time": lambda text: "Temps estimés" in text
    or "Temps estimé" in text,
}


class SpanError(RuntimeError):
    """Une preuve manque : l'étendue ne peut pas être établie."""


def _reject(message: str) -> None:
    raise SpanError(message)


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        _reject("PyMuPDF (fitz) est requis")
    return fitz


def normalise(text: str) -> str:
    return " ".join(text.replace("’", "'").replace(" ", " ").split())


def dehyphenate(title: str) -> str:
    return re.sub(r"-\s+", "", normalise(title))


def opener_spans(document: Any) -> list[dict[str, Any]]:
    """Les ouvertures et leur étendue réelle, en pages."""

    pages = [normalise(document[index].get_text()) for index in range(document.page_count)]
    rows: list[dict[str, Any]] = []
    for index, text in enumerate(pages):
        banner = BANNER.search(text)
        if banner is None or OBJECTIVES not in text:
            continue
        start = index + 1
        title = dehyphenate(text[banner.end() :].split("Objectifs")[0].strip())
        # Ce que la page de banniere ne porte pas, elle l'a rejete.
        missing = [
            name for name, holds in REQUIRED_CONTENT.items() if not holds(text)
        ]
        # Une page qui suit n'appartient au debordement que si elle porte un
        # bloc que la banniere a perdu. La rubrique « Ouverture » ne suffit
        # PAS : la section d'ouverture du chapitre -- le contrat, « ce que tu
        # vas savoir faire » -- la porte aussi, et c'est du contenu a part
        # entiere. Les confondre ferait crier au debordement sur une mise en
        # page saine.
        end = start
        moved: list[str] = []
        cursor = index + 1
        while cursor < len(pages) and missing:
            following = pages[cursor]
            if not following.startswith(OPENER_RUBRIC) or OBJECTIVES in following:
                break
            carried = [
                name
                for name in missing
                if REQUIRED_CONTENT[name](following)
            ]
            if not carried:
                break
            moved.extend(carried)
            missing = [name for name in missing if name not in carried]
            end = cursor + 1
            cursor += 1
        rows.append(
            {
                "chapter_number": int(banner.group(1)),
                "title": title,
                "opening_start_page": start,
                "opening_end_page": end,
                "page_span": end - start + 1,
                "single_page": start == end,
                "missing_on_the_opening_page": sorted(set(missing) | set(moved)),
                "pushed_to_the_overflow_page": moved,
            }
        )
    return rows


def measure(variant: str) -> dict[str, Any]:
    pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
    if not pdf.is_file():
        _reject(f"PDF absent : {relative(pdf)}")
    fitz = _fitz()
    with fitz.open(pdf) as document:
        rows = opener_spans(document)
        page_count = document.page_count
    return {
        "variant": variant,
        "pdf_path": relative(pdf),
        "page_count": page_count,
        "openers": rows,
        "OPENERS_FOUND": len(rows),
        "MULTI_PAGE_OPENERS": sum(1 for row in rows if not row["single_page"]),
        "OPENER_MISSING_CONTENT": sum(
            len(row["missing_on_the_opening_page"]) for row in rows
        ),
    }


def build() -> dict[str, Any]:
    variants = [measure(variant) for variant in VARIANTS]
    return {
        "artifact_type": "1spe_chapter_opener_span",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "invariant": "opening_start_page == opening_end_page pour les dix chapitres",
        "why_it_is_invisible_otherwise": (
            "\\vfill avale la coupure : le journal LaTeX reste muet et "
            "Overfull = 0 reste vrai. Le defaut ne se voit que sur la page rendue."
        ),
        "no_page_number_is_written_down": True,
        "variants": variants,
        "summary": {
            "OPENERS_FOUND": sum(row["OPENERS_FOUND"] for row in variants),
            "OPENERS_EXPECTED": EXPECTED_OPENERS * len(VARIANTS),
            "MULTI_PAGE_OPENERS": sum(row["MULTI_PAGE_OPENERS"] for row in variants),
            "SINGLE_PAGE_OPENERS": sum(
                sum(1 for opener in row["openers"] if opener["single_page"])
                for row in variants
            ),
            "OPENER_MISSING_CONTENT": sum(
                row["OPENER_MISSING_CONTENT"] for row in variants
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Étendue des ouvertures de chapitre — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Invariant : {payload['invariant']}.",
        "",
        "> " + payload["why_it_is_invisible_otherwise"],
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    for row in payload["variants"]:
        lines += [
            "",
            f"## Variante `{row['variant']}` — {row['page_count']} pages",
            "",
            "| Ch. | Titre | Début | Fin | Pages | Une seule page | Manquant |",
            "|---:|---|---:|---:|---:|---|---|",
        ]
        for opener in row["openers"]:
            lines.append(
                f"| {opener['chapter_number']} | {opener['title']} | "
                f"{opener['opening_start_page']} | {opener['opening_end_page']} | "
                f"{opener['page_span']} | "
                f"{'oui' if opener['single_page'] else '**NON**'} | "
                f"{', '.join(opener['missing_on_the_opening_page']) or '—'} |"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except SpanError as error:
        print(f"1SPE-CHAPTER-OPENER-SPAN-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {relative(JSON_TARGET)} et {relative(MD_TARGET)}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    summary = payload["summary"]
    if summary["OPENERS_FOUND"] != summary["OPENERS_EXPECTED"]:
        print("OPENERS_FOUND_IS_NOT_THE_EXPECTED_COUNT=1")
        return 1
    return (
        1
        if summary["MULTI_PAGE_OPENERS"] or summary["OPENER_MISSING_CONTENT"]
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
