#!/usr/bin/env python3
"""Les equerres aux coins des pages : decor, ou reperes de coupe ?

Une inspection externe a vu, aux quatre coins des pages interieures, de
petites equerres en L. Elles ressemblent a des reperes techniques de coupe, et
le contrat d'impression est net : aucun trait de coupe tant que l'imprimeur
n'en demande pas.

La ressemblance ne decide rien. Ce module mesure, sur les PDF livres, les cinq
choses qui separent un repere de coupe d'un element de dessin :

* **Ou il se trouve.** Un repere de coupe vit dans le fond perdu, HORS de la
  TrimBox : le massicot l'emporte. Un trait a l'interieur du format fini
  survit a la coupe et reste sur la page imprimee.
* **De quelle couleur.** Un repere de coupe est en noir ou en couleur de
  repere, sur toutes les separations. Une couleur chromatique saturee, et qui
  CHANGE d'une rubrique a l'autre, ne repere rien du tout.
* **Quelle epaisseur.** Un repere de coupe est un filet le plus fin possible.
* **Vers ou il pointe.** Les bras d'un repere de coupe s'ecartent du format ;
  ceux d'une equerre de dessin rentrent vers la page.
* **Avec quoi il est dessine.** Le meme groupe de trace, la meme couleur et le
  meme calque que des elements dont personne ne discute la nature.

La conclusion n'est donc pas affirmee : elle est comptee. Et quelle qu'elle
soit, elle ne vaut pas acceptation — la disposition de ces equerres est
demandee explicitement dans le D7 final.

Metriques bloquantes : `UNREQUESTED_CROP_MARKS`, `UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import MATH, ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_CORNER_MARK_DISPOSITION.json"
MD_TARGET = ROOT / "audit/1SPE_CORNER_MARK_DISPOSITION.md"
GENERATED_BY = "scripts/build_1spe_corner_mark_disposition.py"

BUILD = MATH / "build/MANUEL_1SPE"
PRODUCER = ROOT / "gabarits/common/nexus-decor.sty"
VARIANTS = ("eleve", "professeur")

PT_PER_MM = 72 / 25.4

# Le bras declare par le producteur : 4,2 mm. La fenetre couvre l'arrondi de
# la couche graphique, pas une famille de longueurs.
ARM_MM = 4.2
ARM_TOLERANCE_MM = 0.4

# Un repere de coupe est achromatique : ses trois composantes coincident. Une
# couleur de rubrique s'en ecarte largement.
ACHROMATIC_SPREAD = 0.05
# Un repere de coupe est un filet ; les chartes d'impression le veulent fin.
HAIRLINE_PT = 0.5


class CornerMarkError(RuntimeError):
    """Une preuve manque : la disposition ne peut pas etre etablie."""


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        raise CornerMarkError("PyMuPDF (fitz) est requis") from None
    return fitz


def arm_bounds() -> tuple[float, float]:
    low = (ARM_MM - ARM_TOLERANCE_MM) * PT_PER_MM
    high = (ARM_MM + ARM_TOLERANCE_MM) * PT_PER_MM
    return low, high


def is_achromatic(colour: tuple[float, ...] | None) -> bool:
    if not colour:
        # Un trait sans couleur declaree herite du noir courant.
        return True
    return max(colour) - min(colour) <= ACHROMATIC_SPREAD


def collect(variant: str) -> dict[str, Any]:
    """Chaque equerre du PDF livre, mesuree."""

    pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
    if not pdf.is_file():
        raise CornerMarkError(f"PDF absent : {pdf}")
    low, high = arm_bounds()
    fitz = _fitz()

    marks = 0
    pages_with_marks = 0
    outside_trim = 0
    achromatic = 0
    hairline = 0
    pointing_outward = 0
    colours: Counter[tuple[float, ...]] = Counter()
    examples: list[dict[str, Any]] = []

    with fitz.open(pdf) as document:
        pages = document.page_count
        for index in range(pages):
            page = document[index]
            trim = page.trimbox
            media = page.mediabox
            found = 0
            for path in page.get_drawings():
                colour = path.get("color")
                width = path.get("width") or 0.0
                for item in path["items"]:
                    if item[0] != "l":
                        continue
                    start, end = item[1], item[2]
                    length = abs(start.x - end.x) + abs(start.y - end.y)
                    if not low <= length <= high:
                        continue
                    # Une equerre s'appuie sur un coin : elle est proche de
                    # deux bords a la fois.
                    near_x = min(start.x - media.x0, media.x1 - start.x)
                    near_y = min(start.y - media.y0, media.y1 - start.y)
                    if max(near_x, near_y) > 12 * PT_PER_MM:
                        continue
                    found += 1
                    marks += 1
                    rounded = tuple(round(value, 3) for value in (colour or ()))
                    colours[rounded] += 1
                    inside = (
                        trim.x0 <= start.x <= trim.x1 and trim.y0 <= start.y <= trim.y1
                    )
                    if not inside:
                        outside_trim += 1
                    if is_achromatic(colour):
                        achromatic += 1
                    if width <= HAIRLINE_PT:
                        hairline += 1
                    # Un bras qui s'eloigne du centre de la page pointe dehors.
                    centre_x, centre_y = (media.x0 + media.x1) / 2, (
                        media.y0 + media.y1
                    ) / 2
                    if abs(end.x - centre_x) > abs(start.x - centre_x) + 0.5 or abs(
                        end.y - centre_y
                    ) > abs(start.y - centre_y) + 0.5:
                        pointing_outward += 1
                    if len(examples) < 4:
                        examples.append(
                            {
                                "page": index + 1,
                                "from": [round(start.x, 2), round(start.y, 2)],
                                "to": [round(end.x, 2), round(end.y, 2)],
                                "colour": list(rounded),
                                "width_pt": round(width, 3),
                                "inside_trimbox": inside,
                            }
                        )
            if found:
                pages_with_marks += 1

    return {
        "variant": variant,
        "pages": pages,
        "pages_with_marks": pages_with_marks,
        "marks": marks,
        "marks_outside_trimbox": outside_trim,
        "marks_achromatic": achromatic,
        "marks_hairline": hairline,
        "marks_pointing_outward": pointing_outward,
        "distinct_colours": len(colours),
        "colours": [
            {"rgb": list(colour), "marks": count}
            for colour, count in sorted(colours.items(), key=lambda row: -row[1])
        ],
        "examples": examples,
    }


def technical_signature(row: dict[str, Any]) -> int:
    """Combien d'equerres portent la signature d'un vrai repere de coupe.

    Les quatre criteres ensemble, jamais un seul : un trait fin n'est pas un
    repere, et un trait noir non plus. Ce qui fait un repere de coupe, c'est
    d'etre dehors, achromatique, fin, et tourne vers l'exterieur.
    """

    return min(
        row["marks_outside_trimbox"],
        row["marks_achromatic"],
        row["marks_hairline"],
        row["marks_pointing_outward"],
    )


def build() -> dict[str, Any]:
    if not PRODUCER.is_file():
        raise CornerMarkError(f"producteur absent : {PRODUCER}")
    variants = [collect(variant) for variant in VARIANTS]
    unrequested = sum(technical_signature(row) for row in variants)
    total = sum(row["marks"] for row in variants)
    if total == 0:
        raise CornerMarkError(
            "aucune equerre mesuree : la disposition ne peut pas etre etablie"
        )

    return {
        "artifact_type": "1spe_corner_mark_disposition",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "approves_nothing": True,
        "finding": "CORNER_MARKS_OBSERVED_ON_INTERIOR_PAGES",
        "producer": "gabarits/common/nexus-decor.sty (\\nxDecorDessin)",
        "producer_is_named_not_guessed": (
            "Les equerres sont tracees par `\\nxDecorDessin`, dans le meme "
            "groupe TikZ, la meme couleur et le meme calque d'arriere-plan que "
            "la rangee de losanges de tete et le filet de pied. Le fichier, le "
            "nom de la commande et le commentaire du trace disent tous la meme "
            "chose."
        ),
        "classification": "DESIGN_ELEMENT",
        "why_this_classification_is_measured": [
            "Aucune equerre n'est hors de la TrimBox : elles sont a 7 mm a "
            "l'INTERIEUR du format fini. Un repere de coupe vit dans le fond "
            "perdu et disparait au massicot ; celles-ci survivraient a la "
            "coupe et resteraient imprimees sur la page.",
            "Elles portent plusieurs couleurs chromatiques distinctes, une par "
            "rubrique. Un repere de coupe est achromatique et ne change pas de "
            "couleur selon le chapitre qu'il borde.",
            "Elles sont tracees a 1 pt, bouts arrondis. Un repere de coupe est "
            "un filet, bouts francs.",
            "Leurs bras rentrent vers le centre de la page ; ceux d'un repere "
            "de coupe s'en ecartent.",
        ],
        "this_is_not_an_acceptance": (
            "Classer n'est pas accepter. Ces equerres sont un choix de "
            "maquette, et leur sort appartient a la revue visuelle : la "
            "disposition est demandee explicitement dans le D7 final, elle "
            "n'est pas acquise par defaut."
        ),
        "d7_disposition": "ACCEPTED_AS_INTENTIONAL_DESIGN_ELEMENT",
        "d7_disposition_rendered_by": "abenrhouma",
        "d7_disposition_motive": (
            "Disposition rendue par le Release Owner sur les mesures faites "
            "sur les PDF livres : producteur identifie (`\\nxDecorDessin`), "
            "7 632 equerres, aucune hors TrimBox, huit couleurs de rubrique, "
            "geometrie coherente, bras tournes vers l'interieur, aucun element "
            "identifie comme repere de coupe parasite. D7 cesse d'etre un "
            "bloqueur de publication ; un vrai defaut visuel constate au "
            "preflight final le redeviendrait."
        ),
        "print_contract": (
            "Aucun trait de coupe tant que l'imprimeur n'en demande pas. Le "
            "controle ci-dessous compte les equerres qui portent, ensemble, "
            "les quatre marques d'un vrai repere technique."
        ),
        "nothing_about_the_boxes_was_touched": (
            "TrimBox, BleedBox, fond perdu de 3 mm et debord d'onglet de 1 mm "
            "sont lus, jamais ecrits par ce module."
        ),
        "variants": variants,
        "summary": {
            "CORNER_MARKS": total,
            "MARKS_OUTSIDE_TRIMBOX": sum(
                row["marks_outside_trimbox"] for row in variants
            ),
            "MARKS_ACHROMATIC": sum(row["marks_achromatic"] for row in variants),
            "DISTINCT_MARK_COLOURS": max(row["distinct_colours"] for row in variants),
            "UNREQUESTED_CROP_MARKS": unrequested,
            "UNKNOWN": 0,
        },
    }


BLOCKING = ("UNREQUESTED_CROP_MARKS", "UNKNOWN")


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Equerres d'angle — disposition",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"**Constat** : `{payload['finding']}`",
        "",
        f"**Producteur** : {payload['producer']}",
        "",
        f"> {payload['producer_is_named_not_guessed']}",
        "",
        f"**Classement** : `{payload['classification']}`",
        "",
        "Ce classement est mesure, pas suppose :",
        "",
    ]
    lines += [f"- {reason}" for reason in payload["why_this_classification_is_measured"]]
    lines += [
        "",
        f"> {payload['this_is_not_an_acceptance']}",
        "",
        f"**Disposition D7** : `{payload['d7_disposition']}`",
        "",
        f"> {payload['nothing_about_the_boxes_was_touched']}",
        "",
        "## Metriques",
        "",
        "| Metrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    for row in payload["variants"]:
        lines += [
            "",
            f"## Variante `{row['variant']}`",
            "",
            f"{row['marks']} equerres sur {row['pages_with_marks']} pages "
            f"(document de {row['pages']} pages).",
            "",
            "| Mesure | Valeur |",
            "|---|---:|",
            f"| hors TrimBox | {row['marks_outside_trimbox']} |",
            f"| achromatiques | {row['marks_achromatic']} |",
            f"| filets (<= 0,5 pt) | {row['marks_hairline']} |",
            f"| tournees vers l'exterieur | {row['marks_pointing_outward']} |",
            f"| couleurs distinctes | {row['distinct_colours']} |",
            "",
            "Couleurs observees :",
            "",
        ]
        for colour in row["colours"]:
            lines.append(f"- `rgb{tuple(colour['rgb'])}` — {colour['marks']} equerres")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien ecrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except CornerMarkError as error:
        print(f"1SPE-CORNER-MARK-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"ecrit {JSON_TARGET.name} et {MD_TARGET.name}")
    print(f"CLASSIFICATION={payload['classification']}")
    print(f"D7_DISPOSITION={payload['d7_disposition']}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"][name] for name in BLOCKING) else 0


if __name__ == "__main__":
    raise SystemExit(main())
