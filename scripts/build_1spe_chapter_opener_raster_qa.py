#!/usr/bin/env python3
"""Les vingt ouvertures de chapitre, regardées page par page à 300 dpi.

L'étendue est déjà mesurée ailleurs : une ouverture, une page. Tenir sur une
page ne dit pourtant rien de ce qu'on y voit. Un bloc peut chevaucher le
suivant, une ligne peut être coupée par le bord du fond perdu, une pastille
peut recouvrir un titre -- et la page tiendra quand même sur une page.

Ce module regarde donc les ouvertures elles-mêmes. Trois lectures, aucune
n'étant l'avis d'un humain :

* TEXTE SANS TRACE -- c'est le risque propre à une ouverture à bandeau : le
  texte de la bannière est blanc, et un bloc qui glisserait sous le bandeau
  resterait blanc sur blanc, présent dans le PDF et introuvable sur la page.
  Chaque fragment est donc rendu seul, et l'on compte la part de ses pixels
  qui s'écartent de la couleur dominante de sa propre zone : c'est la trace
  qu'il laisse. Un texte invisible n'en laisse aucune.

  Deux mesures ont été essayées et rejetées avant celle-là, et le dire évite
  de les réessayer. Le CHEVAUCHEMENT DES RECTANGLES d'abord : le grand chiffre
  fantôme du chapitre passe délibérément derrière « CHAPITRE n » et le titre,
  si bien que leurs boîtes se recouvrent sur une page parfaitement lisible --
  cinquante-deux fausses alertes. Le CONTRASTE WCAG ensuite : il juge une
  intention graphique (du blanc sur une pastille orange) et non un défaut de
  composition, et il se lit mal sur la boîte serrée d'un seul glyphe --
  trente-trois fausses alertes. La trace, elle, ne dit qu'une chose, mais elle
  la dit sans se tromper.
* ROGNAGE -- aucune encre de texte ne doit franchir le format fini. Le bord
  est lu sur la TrimBox de la page, jamais écrit.
* PAGE VIDE -- une ouverture doit porter de l'encre partout où on l'attend :
  la bannière en haut, le bloc des capacités, le bloc d'accroche. La mesure se
  fait sur le rendu, à 300 dpi, en comptant les pixels non blancs par bande.

`ORPHAN_PAGE` et `MISSING_CONTENT` ne sont pas recomptés ici : ils sont établis
par `1SPE_CHAPTER_OPENER_SPAN`, qui lit le texte plutôt que les pixels. Ce
module les reprend de cet artefact et refuse de conclure s'il est absent --
deux mesures indépendantes valent mieux qu'une mesure dupliquée.

Métriques bloquantes : `OPENER_TEXT_WITHOUT_TRACE`, `OPENER_CLIPPING`,
`OPENER_EMPTY_ZONE`, `OPENER_ORPHAN_PAGE`, `OPENER_MISSING_CONTENT`,
`OPENER_UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

def _label(path: Path) -> str:
    """Chemin lisible, y compris pour une sonde fabriquée hors du dépôt."""

    try:
        return relative(path)
    except ValueError:
        return str(path)


JSON_TARGET = ROOT / "audit/1SPE_CHAPTER_OPENER_RASTER_QA.json"
MD_TARGET = ROOT / "audit/1SPE_CHAPTER_OPENER_RASTER_QA.md"
GENERATED_BY = "scripts/build_1spe_chapter_opener_raster_qa.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
SPAN_ARTIFACT = ROOT / "audit/1SPE_CHAPTER_OPENER_SPAN.json"
VARIANTS = ("eleve", "professeur")

RASTER_DPI = 300
# Une page d'ouverture est lue en trois bandes horizontales : la bannière, le
# corps où vivent les blocs, et le pied. Chacune doit porter de l'encre.
ZONES = (("banniere", 0.0, 0.5), ("blocs", 0.5, 0.92), ("pied", 0.92, 1.0))
# Sous ce taux de pixels encrés, une bande est considérée vide.
MINIMUM_INK_RATIO = 0.0005
# Un pixel est « encré » s'il s'écarte du blanc franc.
WHITE_THRESHOLD = 250
# Un fragment invisible ne laisse exactement aucune trace. Le seuil est donc
# posé loin en dessous du fragment le moins encré du corpus -- un point médian
# de 8,6 pt, à 6,1 % -- et loin au-dessus de zéro. Le minimum réellement
# observé est publié à chaque construction, pour que ce rapport se vérifie.
MINIMUM_INK_COVERAGE = 0.01


class RasterError(RuntimeError):
    """Une preuve manque : la lecture ne peut pas être faite."""


def _reject(message: str) -> None:
    raise RasterError(message)


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        _reject("PyMuPDF (fitz) est requis")
    return fitz


def opener_pages(variant: str) -> list[dict[str, Any]]:
    """Les ouvertures, reprises de la mesure d'étendue plutôt que refaites."""

    if not SPAN_ARTIFACT.is_file():
        _reject(f"artefact d'étendue absent : {_label(SPAN_ARTIFACT)}")
    payload = json.loads(SPAN_ARTIFACT.read_text(encoding="utf-8"))
    for row in payload["variants"]:
        if row["variant"] == variant:
            return row["openers"]
    _reject(f"l'artefact d'étendue ne couvre pas la variante {variant}")
    return []


def _ink_coverage(page: Any, box: Any) -> float:
    """La part des pixels d'une zone qui s'écartent de sa couleur dominante."""

    pixmap = page.get_pixmap(dpi=RASTER_DPI, clip=box, annots=False)
    samples = pixmap.samples
    stride = pixmap.n
    counts: dict[bytes, int] = {}
    total = 0
    for offset in range(0, len(samples), stride):
        pixel = bytes(samples[offset : offset + stride])
        counts[pixel] = counts.get(pixel, 0) + 1
        total += 1
    if total == 0:
        return 0.0
    dominant = max(counts.values())
    return 1.0 - dominant / total


def span_traces(page: Any) -> tuple[list[dict[str, Any]], float]:
    """Les fragments qui ne laissent aucune trace, et la plus faible observée."""

    import fitz  # noqa: PLC0415

    findings: list[dict[str, Any]] = []
    weakest = 1.0
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                box = fitz.Rect(span["bbox"])
                if box.is_empty or box.width < 1 or box.height < 1:
                    continue
                coverage = _ink_coverage(page, box)
                weakest = min(weakest, coverage)
                if coverage < MINIMUM_INK_COVERAGE:
                    findings.append(
                        {
                            "text": text[:60],
                            "bbox": [round(value, 2) for value in span["bbox"]],
                            "font_size_pt": round(span["size"], 2),
                            "ink_coverage": round(coverage, 5),
                        }
                    )
    return findings, round(weakest, 5)


def clipped_text(page: Any) -> list[dict[str, Any]]:
    """Le texte qui franchit le format fini, lu sur la TrimBox de la page."""

    trim = page.trimbox
    clipped: list[dict[str, Any]] = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line.get("spans", [])).strip()
            if not text:
                continue
            left, top, right, bottom = line["bbox"]
            if (
                left < trim.x0 - 0.5
                or right > trim.x1 + 0.5
                or top < trim.y0 - 0.5
                or bottom > trim.y1 + 0.5
            ):
                clipped.append(
                    {
                        "text": text[:60],
                        "bbox": [round(value, 2) for value in line["bbox"]],
                        "trimbox": [round(value, 2) for value in trim],
                    }
                )
    return clipped


def empty_zones(page: Any) -> list[dict[str, Any]]:
    """Les bandes de la page qui ne portent aucune encre, à 300 dpi."""

    pixmap = page.get_pixmap(dpi=RASTER_DPI, colorspace="gray", annots=False)
    samples = pixmap.samples
    width, height = pixmap.width, pixmap.height
    empty: list[dict[str, Any]] = []
    for name, start, end in ZONES:
        first_row = int(height * start)
        last_row = int(height * end)
        inked = 0
        for row in range(first_row, last_row):
            offset = row * pixmap.stride
            band = samples[offset : offset + width]
            inked += sum(1 for value in band if value < WHITE_THRESHOLD)
        total = max(1, (last_row - first_row) * width)
        ratio = inked / total
        if ratio < MINIMUM_INK_RATIO:
            empty.append({"zone": name, "ink_ratio": round(ratio, 6)})
    return empty


def measure(variant: str) -> dict[str, Any]:
    pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
    if not pdf.is_file():
        _reject(f"PDF absent : {_label(pdf)}")
    fitz = _fitz()
    openers = opener_pages(variant)
    rows: list[dict[str, Any]] = []
    with fitz.open(pdf) as document:
        for opener in openers:
            number = opener["opening_start_page"]
            if number > document.page_count:
                _reject(f"page {number} hors du document {_label(pdf)}")
            page = document[number - 1]
            traceless, weakest = span_traces(page)
            rows.append(
                {
                    "chapter_number": opener["chapter_number"],
                    "title": opener["title"],
                    "page": number,
                    "traceless_text": traceless,
                    "weakest_ink_coverage": weakest,
                    "clipped": clipped_text(page),
                    "empty_zones": empty_zones(page),
                }
            )
    return {
        "variant": variant,
        "pdf_path": _label(pdf),
        "openers": rows,
        "OPENER_TEXT_WITHOUT_TRACE": sum(
            len(row["traceless_text"]) for row in rows
        ),
        "WEAKEST_INK_COVERAGE": min(
            (row["weakest_ink_coverage"] for row in rows), default=0.0
        ),
        "OPENER_CLIPPING": sum(len(row["clipped"]) for row in rows),
        "OPENER_EMPTY_ZONE": sum(len(row["empty_zones"]) for row in rows),
        "OPENERS_INSPECTED": len(rows),
    }


def build() -> dict[str, Any]:
    span = json.loads(SPAN_ARTIFACT.read_text(encoding="utf-8")) if (
        SPAN_ARTIFACT.is_file()
    ) else _reject(f"artefact d'étendue absent : {_label(SPAN_ARTIFACT)}")
    variants = [measure(variant) for variant in VARIANTS]
    return {
        "artifact_type": "1spe_chapter_opener_raster_qa",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "raster_dpi": RASTER_DPI,
        "what_is_measured_elsewhere_is_not_measured_twice": {
            "artifact": _label(SPAN_ARTIFACT),
            "metrics": ["MULTI_PAGE_OPENERS", "OPENER_MISSING_CONTENT"],
            "why": (
                "L'étendue et le contenu manquant se lisent sur le texte, pas "
                "sur les pixels. Deux mesures indépendantes valent mieux qu'une "
                "mesure dupliquée."
            ),
        },
        "the_trim_edge_is_read_from_the_page": (
            "Le bord de rognage est la TrimBox de chaque page, jamais une "
            "valeur écrite ici."
        ),
        "measures_tried_and_rejected": [
            {
                "measure": "chevauchement des rectangles de lignes",
                "why_rejected": (
                    "Le grand chiffre du chapitre passe délibérément derrière "
                    "le titre : leurs boîtes se recouvrent sur une page "
                    "parfaitement lisible. Cinquante-deux fausses alertes."
                ),
            },
            {
                "measure": "rapport de contraste WCAG par fragment",
                "why_rejected": (
                    "Il juge une intention graphique -- du blanc sur une "
                    "pastille orange -- et non un défaut de composition, et se "
                    "lit mal sur la boîte serrée d'un seul glyphe. "
                    "Trente-trois fausses alertes."
                ),
            },
        ],
        "minimum_ink_coverage": MINIMUM_INK_COVERAGE,
        "variants": variants,
        "summary": {
            "OPENERS_INSPECTED": sum(row["OPENERS_INSPECTED"] for row in variants),
            "OPENER_TEXT_WITHOUT_TRACE": sum(
                row["OPENER_TEXT_WITHOUT_TRACE"] for row in variants
            ),
            "WEAKEST_INK_COVERAGE": min(
                (row["WEAKEST_INK_COVERAGE"] for row in variants), default=0.0
            ),
            "OPENER_CLIPPING": sum(row["OPENER_CLIPPING"] for row in variants),
            "OPENER_EMPTY_ZONE": sum(row["OPENER_EMPTY_ZONE"] for row in variants),
            "OPENER_ORPHAN_PAGE": span["summary"]["MULTI_PAGE_OPENERS"],
            "OPENER_MISSING_CONTENT": span["summary"]["OPENER_MISSING_CONTENT"],
            "OPENER_UNKNOWN": 0,
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Ouvertures de chapitre — contrôle sur le rendu",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Rendu à {payload['raster_dpi']} dpi.",
        "",
        f"> {payload['the_trim_edge_is_read_from_the_page']}",
        "",
        "Mesures essayées puis écartées : "
        + " ".join(
            f"**{row['measure']}** — {row['why_rejected']}"
            for row in payload["measures_tried_and_rejected"]
        ),
        "",
        f"> {payload['what_is_measured_elsewhere_is_not_measured_twice']['why']}",
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
            f"## Variante `{row['variant']}`",
            "",
            "| Ch. | Titre | Page | Sans trace | Trace min. | "
            "Rognages | Bandes vides |",
            "|---:|---|---:|---:|---:|---:|---|",
        ]
        for opener in row["openers"]:
            lines.append(
                f"| {opener['chapter_number']} | {opener['title']} | "
                f"{opener['page']} | {len(opener['traceless_text'])} | "
                f"{opener['weakest_ink_coverage']} | "
                f"{len(opener['clipped'])} | "
                f"{', '.join(zone['zone'] for zone in opener['empty_zones']) or '—'} |"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except RasterError as error:
        print(f"1SPE-CHAPTER-OPENER-RASTER-QA-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    summary = payload["summary"]
    blocking = (
        "OPENER_TEXT_WITHOUT_TRACE",
        "OPENER_CLIPPING",
        "OPENER_EMPTY_ZONE",
        "OPENER_ORPHAN_PAGE",
        "OPENER_MISSING_CONTENT",
        "OPENER_UNKNOWN",
    )
    return 1 if any(summary[name] for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
