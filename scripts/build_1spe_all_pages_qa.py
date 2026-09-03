#!/usr/bin/env python3
"""Contrôle de toutes les pages des deux variantes 1SPE, sans échantillon.

Un manuel se contrôle page par page, pas par sondage : la page fautive est
toujours celle qu'on n'a pas tirée. Ce producteur ouvre chaque page des deux
variantes et mesure quatre choses, dans le repère de la page composée — le
TrimBox, c'est-à-dire le format fini après coupe :

1. **Encre dans la bande de fond perdu.** Entre le TrimBox et la BleedBox,
   l'encre est imprimée puis rognée : elle doit donc être une décision. Le
   contrat en connaît deux — le millimètre de l'onglet latéral, et les aplats
   qui vont jusqu'au bord du fond perdu (bandeau d'ouverture, couverture).
   Toute autre encre dans cette bande est un débord non décidé.

2. **Encre hors support.** Au-delà de la BleedBox, rien n'est rendu ni
   imprimé : ce n'est pas un défaut d'impression, c'est de l'hygiène de
   fichier. C'est compté et nommé à part, jamais confondu avec le point 1.

3. **Texte trop près du bord.** Un texte à moins de la marge de sécurité du
   trait de coupe est perdu au premier millimètre de dérive de massicot. Les
   éléments qui débordent volontairement sont exclus par la même règle qu'au
   point 1.

4. **Pages sans contenu.** Comptées et nommées, jamais tolérées en silence.

Le rendu n'est pas rastérisé : les boîtes sont lues dans les objets du PDF,
donc à la précision du moteur et non à celle d'un pixel. La rastérisation reste
utile pour l'œil humain, pas pour cette mesure.

Métriques bloquantes : `UNDECLARED_INK_IN_BLEED_BAND`,
`TEXT_INSIDE_SAFETY_MARGIN`. `INK_BEYOND_SUPPORT` est rapportée sans bloquer :
elle ne s'imprime pas.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_ALL_PAGES_QA.json"
MD_TARGET = ROOT / "audit/1SPE_ALL_PAGES_QA.md"
GENERATED_BY = "scripts/build_1spe_all_pages_qa.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")

BP_PER_MM = 72 / 25.4
# Tolérance de mesure. Une borne de boîte et un coin de tracé sont deux nombres
# PDF indépendants, chacun composé par le moteur à trois décimales et repassé
# par la matrice de transformation, elle-même écrite à trois décimales. Plutôt
# que d'empiler ces arrondis, on borne par la plus petite chose qu'une chaîne
# d'impression sache placer : à 2400 points par pouce — la plus haute
# résolution de flashage courante — un point vaut 72/2400 = 0,03 bp. On retient
# 0,05 bp, soit moins de deux points machine et 0,018 mm. Un débord plus petit
# ne peut pas se distinguer du bord de la boîte, sur aucune presse.
MEASUREMENT_TOLERANCE_BP = 0.05
# Marge de sécurité au trait de coupe : le contrat d'onglet place déjà son
# encre visible à 12 mm à l'intérieur du format fini, et le massicot dérive de
# l'ordre du millimètre. Trois millimètres est la valeur du fond perdu, donc
# celle que la chaîne connaît déjà.
SAFETY_MARGIN_MM = 3.0
# L'onglet déborde d'un millimètre hors format fini, par contrat.
TAB_BLEED_MM = 1.0
# Un aplat de fond perdu va jusqu'au bord du support, soit trois millimètres.
FULL_BLEED_MM = 3.0


class QaError(RuntimeError):
    """Une preuve manque : le contrôle ne peut pas conclure."""


def _reject(message: str) -> None:
    raise QaError(message)


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        _reject("PyMuPDF (fitz) est requis pour mesurer les pages")
    return fitz


def _outside(rectangle: Any, box: Any, tolerance: float) -> dict[str, float]:
    """De combien un rectangle sort d'une boîte, côté par côté, en bp."""

    return {
        side: round(value, 5)
        for side, value in (
            ("left", box.x0 - rectangle.x0),
            ("right", rectangle.x1 - box.x1),
            ("top", box.y0 - rectangle.y0),
            ("bottom", rectangle.y1 - box.y1),
        )
        if value > tolerance
    }


def page_report(page: Any, number: int) -> dict[str, Any]:
    trim, bleed = page.trimbox, page.mediabox
    if page.bleedbox is not None:
        bleed = page.bleedbox
    drawings = page.get_drawings()
    words = page.get_text("words")

    beyond_support = []
    in_bleed_band = []
    for index, drawing in enumerate(drawings):
        rectangle = drawing["rect"]
        if rectangle.is_empty or rectangle.is_infinite:
            continue
        beyond_bleed = _outside(rectangle, bleed, MEASUREMENT_TOLERANCE_BP)
        if beyond_bleed:
            # Hors support : jamais rendu, jamais imprime. On le nomme et on
            # ne le confond pas avec un debord de fond perdu.
            beyond_support.append(
                {
                    "drawing": index,
                    "rect": [round(value, 3) for value in rectangle],
                    "beyond_mm": {
                        side: round(value / BP_PER_MM, 4)
                        for side, value in beyond_bleed.items()
                    },
                }
            )
            continue
        beyond_trim = _outside(rectangle, trim, MEASUREMENT_TOLERANCE_BP)
        if beyond_trim:
            in_bleed_band.append(
                {
                    "drawing": index,
                    "rect": [round(value, 3) for value in rectangle],
                    "beyond_mm": {
                        side: round(value / BP_PER_MM, 4)
                        for side, value in beyond_trim.items()
                    },
                }
            )

    safety = trim + (
        SAFETY_MARGIN_MM * BP_PER_MM,
        SAFETY_MARGIN_MM * BP_PER_MM,
        -SAFETY_MARGIN_MM * BP_PER_MM,
        -SAFETY_MARGIN_MM * BP_PER_MM,
    )
    text_in_margin = []
    for word in words:
        x0, y0, x1, y1, text = word[0], word[1], word[2], word[3], word[4]
        rectangle = _fitz().Rect(x0, y0, x1, y1)
        beyond = _outside(rectangle, safety, MEASUREMENT_TOLERANCE_BP)
        if beyond:
            text_in_margin.append(
                {
                    "text": text[:40],
                    "rect": [round(value, 3) for value in (x0, y0, x1, y1)],
                    "beyond_mm": {
                        side: round(value / BP_PER_MM, 3)
                        for side, value in beyond.items()
                    },
                }
            )

    body = " ".join(page.get_text().split())
    return {
        "page": number,
        "has_text": bool(body),
        "character_count": len(body),
        "drawing_count": len(drawings),
        "image_count": len(page.get_images()),
        "ink_beyond_support": beyond_support,
        "ink_in_bleed_band": in_bleed_band,
        "text_inside_safety_margin": text_in_margin,
    }


def classify_outside_trim(report: dict[str, Any]) -> tuple[list[Any], list[Any]]:
    """Sépare le débord contractuel du débord non décidé, dans la bande.

    La décision se prend PAR PAGE, pas par tracé. Une page à fond perdu — la
    couverture, une ouverture de chapitre — porte un aplat qui va jusqu'au bord
    du support, et tout ce que cet aplat contient déborde avec lui : les points
    du motif de couverture croisent le trait de coupe de fractions de
    millimètre, et c'est le propre d'un fond perdu. Juger chaque point
    isolément reviendrait à demander à un motif de s'arrêter pile sur la coupe,
    ce qui est exactement ce que le fond perdu existe pour éviter.

    Sur une page ORDINAIRE, en revanche, une seule chose a le droit de
    traverser le trait de coupe : l'onglet latéral, et d'un millimètre. Toute
    autre encre y sera rognée sans que personne l'ait voulu.
    """

    band = report["ink_in_bleed_band"]
    page_bleeds = any(
        any(abs(value - FULL_BLEED_MM) < 0.05 for value in entry["beyond_mm"].values())
        for entry in band
    )
    declared: list[Any] = []
    undeclared: list[Any] = []
    for entry in band:
        values = entry["beyond_mm"].values()
        if all(abs(value - TAB_BLEED_MM) < 0.05 for value in values):
            declared.append({**entry, "reason": "TAB_CONTRACTUAL_1MM_BLEED"})
        elif page_bleeds:
            declared.append({**entry, "reason": "FULL_BLEED_PAGE_ELEMENT"})
        else:
            undeclared.append(entry)
    return declared, undeclared


def measure(variant: str) -> dict[str, Any]:
    pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
    if not pdf.is_file():
        _reject(f"PDF absent : {relative(pdf)}")
    fitz = _fitz()
    pages: list[dict[str, Any]] = []
    with fitz.open(pdf) as document:
        for index in range(document.page_count):
            report = page_report(document[index], index + 1)
            declared, undeclared = classify_outside_trim(report)
            report["bleed_band_declared"] = declared
            report["bleed_band_undeclared"] = undeclared
            pages.append(report)
    return {
        "variant": variant,
        "pdf_path": relative(pdf),
        "page_count": len(pages),
        "pages_inspected": len(pages),
        "coverage": "100%",
        "pages": pages,
        "INK_BEYOND_SUPPORT": sum(len(page["ink_beyond_support"]) for page in pages),
        "UNDECLARED_INK_IN_BLEED_BAND": sum(
            len(page["bleed_band_undeclared"]) for page in pages
        ),
        "DECLARED_INK_IN_BLEED_BAND": sum(
            len(page["bleed_band_declared"]) for page in pages
        ),
        "TEXT_INSIDE_SAFETY_MARGIN": sum(
            len(page["text_inside_safety_margin"]) for page in pages
        ),
        "PAGES_WITHOUT_TEXT": [
            page["page"] for page in pages if not page["has_text"]
        ],
    }


def build() -> dict[str, Any]:
    variants = [measure(variant) for variant in VARIANTS]
    return {
        "artifact_type": "1spe_all_pages_qa",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "sampling": "aucun : toutes les pages des deux variantes sont ouvertes",
        "frame": "page composee (TrimBox), format fini apres coupe",
        "measurement_tolerance_bp": MEASUREMENT_TOLERANCE_BP,
        "safety_margin_mm": SAFETY_MARGIN_MM,
        "variants": variants,
        "summary": {
            "PAGES_INSPECTED": sum(row["pages_inspected"] for row in variants),
            "INK_BEYOND_SUPPORT": sum(row["INK_BEYOND_SUPPORT"] for row in variants),
            "UNDECLARED_INK_IN_BLEED_BAND": sum(
                row["UNDECLARED_INK_IN_BLEED_BAND"] for row in variants
            ),
            "DECLARED_INK_IN_BLEED_BAND": sum(
                row["DECLARED_INK_IN_BLEED_BAND"] for row in variants
            ),
            "TEXT_INSIDE_SAFETY_MARGIN": sum(
                row["TEXT_INSIDE_SAFETY_MARGIN"] for row in variants
            ),
            "PAGES_WITHOUT_TEXT": sum(
                len(row["PAGES_WITHOUT_TEXT"]) for row in variants
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Contrôle de toutes les pages — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Échantillonnage : {payload['sampling']}.",
        f"Repère : {payload['frame']}.",
        f"Tolérance de mesure : {payload['measurement_tolerance_bp']} bp.",
        f"Marge de sécurité au trait de coupe : {payload['safety_margin_mm']} mm.",
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
            f"- PDF : `{row['pdf_path']}`",
            f"- pages inspectées : {row['pages_inspected']} / {row['page_count']}",
            f"- encre hors support, jamais imprimée : "
            f"{row['INK_BEYOND_SUPPORT']}",
            f"- débord de fond perdu contractuel : "
            f"{row['DECLARED_INK_IN_BLEED_BAND']}",
            f"- débord de fond perdu non décidé : "
            f"{row['UNDECLARED_INK_IN_BLEED_BAND']}",
            f"- texte dans la marge de sécurité : "
            f"{row['TEXT_INSIDE_SAFETY_MARGIN']}",
            f"- pages sans texte : {row['PAGES_WITHOUT_TEXT'] or 'aucune'}",
        ]
        offenders = [
            page
            for page in row["pages"]
            if page["bleed_band_undeclared"]
            or page["ink_beyond_support"]
            or page["text_inside_safety_margin"]
        ]
        if offenders:
            lines += [
                "",
                "| Page | Hors support | Fond perdu non décidé | Texte en marge |",
                "|---:|---:|---:|---:|",
            ]
            for page in offenders[:60]:
                lines.append(
                    f"| {page['page']} | {len(page['ink_beyond_support'])} | "
                    f"{len(page['bleed_band_undeclared'])} | "
                    f"{len(page['text_inside_safety_margin'])} |"
                )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except QaError as error:
        print(f"1SPE-ALL-PAGES-QA-ERROR: {error}", file=sys.stderr)
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
    # `INK_BEYOND_SUPPORT` n'est pas bloquante : ce qui sort du support n'est
    # ni rendu ni imprime. Elle reste rapportee, et nommee.
    blocking = ("UNDECLARED_INK_IN_BLEED_BAND", "TEXT_INSIDE_SAFETY_MARGIN")
    return 1 if any(payload["summary"][name] for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
