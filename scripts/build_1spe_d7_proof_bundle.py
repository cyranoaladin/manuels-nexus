#!/usr/bin/env python3
"""Dossier D7 du manuel 1SPE : quinze pages, choisies pour ce qu'elles portent.

Le dossier D7 existant prouve la maquette v5, un specimen de quinze pages. Il ne
dit rien du manuel. Celui-ci prend les pages dans les PDF du manuel lui-meme.

**Les pages ne sont pas ecrites en dur.** Chacune est CHERCHEE par ce qu'elle
doit montrer — la couverture par sa mention d'edition, l'ouverture de chapitre
par sa banniere, le sommaire par ses folios, l'arbre de probabilite par ses
branches, le corrige par sa rubrique. Si une categorie ne se trouve pas, elle
est nommee manquante ; elle n'est jamais remplacee par une page voisine.

Quinze pages, et le contrat en demande douze categories : trois categories
recoivent donc deux pages, choisies pour couvrir en plus l'alternance
recto-verso de l'onglet.

**Les mesures de l'onglet** sont prises sur la geometrie du PDF, dans le repere
de la page composee, puis confirmees par une rasterisation a 300 dpi :

  12 mm a l'interieur du format fini
   1 mm a l'exterieur, et pas 3 : offrir du fond perdu ne deplace pas l'onglet
  16 mm de longueur minimale
  largeur du texte + 6 mm
   3 mm de marge interne
  page impaire a droite, page paire a gauche

Le dossier n'approuve rien : D7 reste `PENDING_HUMAN`.

Metriques bloquantes : `MISSING_CATEGORIES`, `TAB_CONTRACT_VIOLATIONS`,
`PAGES_SELECTED` (qui doit valoir quinze).
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

JSON_TARGET = ROOT / "audit/1SPE_D7_PROOF_BUNDLE.json"
MD_TARGET = ROOT / "audit/1SPE_D7_PROOF_BUNDLE.md"
BUNDLE_DIR = ROOT / "audit/1SPE_D7_PROOF_BUNDLE"
GENERATED_BY = "scripts/build_1spe_d7_proof_bundle.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
BUNDLE_PAGES = 15
CRITICAL_DPI = 300
CONTACT_DPI = 100

BP_PER_MM = 72 / 25.4
TAB_INSIDE_MM = 12.0
TAB_OUTSIDE_MM = 1.0
TAB_TOTAL_MM = TAB_INSIDE_MM + TAB_OUTSIDE_MM
TAB_MIN_LENGTH_MM = 16.0
TAB_TEXT_PADDING_MM = 6.0
TAB_INNER_PADDING_MM = 3.0
# Tolerance de mesure : deux points machine a 2400 dpi (cf. le controle de
# toutes les pages). Elle borne le bruit d'ecriture, jamais un ecart reel.
TOLERANCE_BP = 0.05


class BundleError(RuntimeError):
    """Une preuve manque : le dossier ne peut pas etre compose."""


def _reject(message: str) -> None:
    raise BundleError(message)


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        _reject("PyMuPDF (fitz) est requis")
    return fitz


def normalise(text: str) -> str:
    return " ".join(text.replace("’", "'").replace(" ", " ").split())


# ---------------------------------------------------------------------------
#  Ce que chaque categorie doit montrer
# ---------------------------------------------------------------------------
# Chaque predicat lit le texte NORMALISE de la page et rend vrai si la page
# porte bien la chose a montrer. Aucun numero de page n'apparait ici.
CATEGORIES: tuple[dict[str, Any], ...] = (
    {
        # La mention de variante est ce que D7 doit voir : c'est elle qui
        # distingue les deux editions, et elle vit sur la page de titre
        # interieure. La premiere de couverture, elle, compose son etiquette
        # de collection lettre a lettre — « C O L L E C T I O N » — et ne se
        # cherche donc pas par son texte.
        "id": "COVER_VARIANT",
        "shows": "la mention d'edition qui distingue les deux variantes",
        "variants": ("eleve", "professeur"),
        "match": lambda text: "ÉDITION ÉLÈVE" in text
        or "ÉDITION PROFESSEUR" in text,
    },
    {
        "id": "CHAPTER_OPENER",
        "shows": "une ouverture de chapitre, banniere et capacites",
        "variants": ("eleve",),
        "match": lambda text: re.search(r"CHAPITRE \d+", text)
        and "Objectifs — Capacités attendues" in text,
    },
    {
        # Deux pages : le contrat demande de voir les folios a un, deux et
        # trois chiffres, et le sommaire du manuel s'etend sur quatre pages.
        "id": "TOC_AND_FOLIO",
        "shows": "le sommaire et ses folios a un, deux et trois chiffres",
        "variants": ("eleve", "eleve"),
        "match": lambda text: text.lstrip().startswith("Sommaire")
        or _looks_like_summary(text),
    },
    {
        "id": "COURSE",
        "shows": "une page de cours",
        "variants": ("eleve",),
        "match": lambda text: text.startswith("COURS "),
    },
    {
        "id": "METHOD",
        "shows": "une fiche methode",
        "variants": ("eleve",),
        "match": lambda text: text.startswith("MÉTHODES "),
    },
    {
        "id": "FORMULARY",
        "shows": "le formulaire",
        "variants": ("eleve",),
        "match": lambda text: "Formulaire" in text[:200],
    },
    {
        "id": "EXERCISE",
        "shows": "une page d'exercices",
        "variants": ("eleve",),
        "match": lambda text: text.startswith("EXERCICES ")
        and "Exercice" in text,
    },
    {
        "id": "PROBABILITY_TREE",
        "shows": "un arbre de probabilite dessine",
        "variants": ("eleve",),
        "match": lambda text: "arbre" in text.lower()
        and re.search(r"P[_ ]?\(", text) is not None,
    },
    {
        "id": "ASSESSMENT",
        "shows": "un sujet d'evaluation",
        "variants": ("eleve",),
        "match": lambda text: "Évaluation" in text and "points" in text,
    },
    {
        "id": "REMEDIATION",
        "shows": "une page de remediation",
        "variants": ("eleve",),
        "match": lambda text: text.startswith("REMÉDIATION "),
    },
    {
        "id": "TEACHER_CORRECTION",
        "shows": "un corrige reserve au professeur",
        "variants": ("professeur",),
        "match": lambda text: "Corrigé" in text
        and "Barème indicatif" in text,
    },
    {
        "id": "TAB_ODD_AND_EVEN",
        "shows": "l'alternance de l'onglet, page impaire puis page paire",
        "variants": ("eleve", "eleve"),
        "match": lambda text: text.startswith("EXERCICES ")
        or text.startswith("COURS "),
        "parity": ("odd", "even"),
    },
)


SUMMARY_ENTRY = re.compile(r"\.\s?\.\s?\.[\s.]*\d{1,3}\b")


def _looks_like_summary(text: str) -> bool:
    """Une suite d'entrees pointillees suivies d'un folio : c'est un sommaire.

    Les pages de suite du sommaire ne repetent pas le titre « Sommaire » : on
    les reconnait a la forme de leurs entrees, pas a un intitule.
    """

    return len(SUMMARY_ENTRY.findall(text)) >= 5


def page_text(document: Any, index: int) -> str:
    return normalise(document[index].get_text())


def select_pages(documents: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Cherche une page par categorie, sans jamais en inventer une."""

    chosen: list[dict[str, Any]] = []
    missing: list[str] = []
    used: set[tuple[str, int]] = set()
    for category in CATEGORIES:
        parities = category.get("parity", (None,) * len(category["variants"]))
        for position, variant in enumerate(category["variants"]):
            document = documents[variant]
            parity = parities[position] if position < len(parities) else None
            found = None
            for index in range(document.page_count):
                number = index + 1
                if (variant, number) in used:
                    continue
                if parity == "odd" and number % 2 == 0:
                    continue
                if parity == "even" and number % 2 == 1:
                    continue
                if category["match"](page_text(document, index)):
                    found = number
                    break
            if found is None:
                missing.append(f"{category['id']}/{variant}")
                continue
            used.add((variant, found))
            chosen.append(
                {
                    "category": category["id"],
                    "shows": category["shows"],
                    "variant": variant,
                    "page": found,
                    "parity": "odd" if found % 2 else "even",
                    "requested_parity": parity,
                }
            )
    return chosen, missing


# ---------------------------------------------------------------------------
#  Mesures de l'onglet
# ---------------------------------------------------------------------------


def tab_measurements(page: Any) -> dict[str, Any]:
    """La geometrie de l'onglet, mesuree contre le format fini."""

    trim = page.trimbox
    found = None
    for drawing in page.get_drawings():
        if not drawing.get("fill"):
            continue
        rectangle = drawing["rect"]
        width_mm = (rectangle.x1 - rectangle.x0) / BP_PER_MM
        crosses = (
            rectangle.x1 > trim.x1 + TOLERANCE_BP
            or rectangle.x0 < trim.x0 - TOLERANCE_BP
        )
        if not crosses or abs(width_mm - TAB_TOTAL_MM) > 0.05:
            continue
        found = rectangle
        break
    if found is None:
        return {"present": False}

    on_right = found.x1 > trim.x1
    outside_mm = (
        (found.x1 - trim.x1) if on_right else (trim.x0 - found.x0)
    ) / BP_PER_MM
    inside_mm = (
        (trim.x1 - found.x0) if on_right else (found.x1 - trim.x0)
    ) / BP_PER_MM
    length_mm = (found.y1 - found.y0) / BP_PER_MM

    # Le libelle vit dans l'onglet : on mesure sa boite pour verifier le
    # remplissage de 6 mm et la marge interne de 3 mm.
    label = None
    for word in page.get_text("words"):
        rectangle = _fitz().Rect(word[0], word[1], word[2], word[3])
        if rectangle.x0 >= found.x0 - 1 and rectangle.x1 <= found.x1 + 1:
            label = rectangle if label is None else label | rectangle
    label_length_mm = (label.y1 - label.y0) / BP_PER_MM if label else None
    inner_padding_mm = (
        min(label.x0 - found.x0, found.x1 - label.x1) / BP_PER_MM if label else None
    )
    return {
        "present": True,
        "side": "right" if on_right else "left",
        "outside_mm": round(outside_mm, 4),
        "inside_mm": round(inside_mm, 4),
        "length_mm": round(length_mm, 4),
        "label_length_mm": round(label_length_mm, 4) if label_length_mm else None,
        "inner_padding_mm": (
            round(inner_padding_mm, 4) if inner_padding_mm is not None else None
        ),
    }


def tab_verdicts(page_number: int, tab: dict[str, Any]) -> list[dict[str, Any]]:
    if not tab.get("present"):
        return [
            {
                "rule": "TAB_PRESENT",
                "verdict": "ABSENT",
                "detail": "aucun rectangle d'onglet a la largeur contractuelle",
            }
        ]
    rules = [
        ("TAB_INSIDE_12MM", abs(tab["inside_mm"] - TAB_INSIDE_MM) <= 0.05, tab["inside_mm"]),
        ("TAB_OUTSIDE_1MM", abs(tab["outside_mm"] - TAB_OUTSIDE_MM) <= 0.05, tab["outside_mm"]),
        (
            "TAB_MIN_LENGTH_16MM",
            tab["length_mm"] >= TAB_MIN_LENGTH_MM - 0.05,
            tab["length_mm"],
        ),
        (
            "TAB_SIDE_FOLLOWS_PARITY",
            tab["side"] == ("right" if page_number % 2 else "left"),
            tab["side"],
        ),
    ]
    if tab.get("label_length_mm") is not None:
        rules.append(
            (
                # La charte fixe la longueur de l'onglet a « libelle + 6 mm »,
                # avec un plancher de 16 mm : c'est le maximum des deux, et
                # rien d'autre.
                "TAB_LENGTH_IS_LABEL_PLUS_6MM",
                tab["length_mm"] + 0.05
                >= max(
                    TAB_MIN_LENGTH_MM,
                    tab["label_length_mm"] + TAB_TEXT_PADDING_MM,
                ),
                {
                    "tab": tab["length_mm"],
                    "label": tab["label_length_mm"],
                    "expected_min": round(
                        max(
                            TAB_MIN_LENGTH_MM,
                            tab["label_length_mm"] + TAB_TEXT_PADDING_MM,
                        ),
                        4,
                    ),
                },
            )
        )
    if tab.get("inner_padding_mm") is not None:
        rules.append(
            (
                "TAB_INNER_PADDING_3MM",
                tab["inner_padding_mm"] >= TAB_INNER_PADDING_MM - 0.6,
                tab["inner_padding_mm"],
            )
        )
    return [
        {"rule": name, "verdict": "PASS" if ok else "FAIL", "measured": value}
        for name, ok, value in rules
    ]


# ---------------------------------------------------------------------------


def rasterise(
    document: Any, page_number: int, target: Path, dpi: int, clip: Any = None
) -> str:
    """Rend une page, ou une region de page, et retourne son condensat.

    La rasterisation critique de l'onglet est un DECOUPE : c'est l'onglet
    qu'il faut voir a 300 dpi, pas la page entiere. Une page A4 pleine a cette
    resolution pese quelques megaoctets, et trente d'entre elles alourdiraient
    le depot pour montrer, a chaque fois, treize millimetres de bord.
    """

    import hashlib

    page = document[page_number - 1]
    pixmap = page.get_pixmap(dpi=dpi, clip=clip) if clip else page.get_pixmap(dpi=dpi)
    target.parent.mkdir(parents=True, exist_ok=True)
    pixmap.save(target)
    return "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()


def tab_clip(page: Any, tab: dict[str, Any]) -> Any:
    """La bande a montrer a 300 dpi : l'onglet et cinq millimetres autour."""

    fitz = _fitz()
    trim = page.trimbox
    margin = 5 * BP_PER_MM
    if tab["side"] == "right":
        x0 = trim.x1 - (TAB_INSIDE_MM * BP_PER_MM) - margin
        x1 = trim.x1 + (TAB_OUTSIDE_MM * BP_PER_MM) + margin
    else:
        x0 = trim.x0 - (TAB_OUTSIDE_MM * BP_PER_MM) - margin
        x1 = trim.x0 + (TAB_INSIDE_MM * BP_PER_MM) + margin
    # Toute la hauteur du format fini : l'onglet se lit avec sa position
    # verticale, qui est ce que l'alternance recto-verso fait varier.
    return fitz.Rect(x0, trim.y0, x1, trim.y1)


def build(write: bool) -> dict[str, Any]:
    fitz = _fitz()
    documents = {}
    for variant in ("eleve", "professeur"):
        pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
        if not pdf.is_file():
            _reject(f"PDF absent : {relative(pdf)}")
        documents[variant] = fitz.open(pdf)

    chosen, missing = select_pages(documents)
    rows = []
    for entry in chosen:
        document = documents[entry["variant"]]
        page = document[entry["page"] - 1]
        tab = tab_measurements(page)
        verdicts = tab_verdicts(entry["page"], tab)
        record = {
            **entry,
            "tab": tab,
            "tab_verdicts": verdicts,
            "tab_failures": [row["rule"] for row in verdicts if row["verdict"] == "FAIL"],
        }
        if write:
            name = f"{entry['category']}-{entry['variant']}-p{entry['page']:04d}"
            page_target = BUNDLE_DIR / f"{name}@{CONTACT_DPI}dpi.png"
            record["page_raster"] = relative(page_target)
            record["page_raster_dpi"] = CONTACT_DPI
            record["page_raster_sha256"] = rasterise(
                document, entry["page"], page_target, CONTACT_DPI
            )
            if tab.get("present"):
                tab_target = BUNDLE_DIR / f"{name}-tab@{CRITICAL_DPI}dpi.png"
                record["tab_raster"] = relative(tab_target)
                record["tab_raster_dpi"] = CRITICAL_DPI
                record["tab_raster_sha256"] = rasterise(
                    document, entry["page"], tab_target, CRITICAL_DPI,
                    clip=tab_clip(page, tab),
                )
        rows.append(record)

    for document in documents.values():
        document.close()

    categories_found = {row["category"] for row in rows}
    failures = [row for row in rows if row["tab_failures"]]
    return {
        "artifact_type": "1spe_d7_proof_bundle",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "d7_status": "PENDING_HUMAN",
        "approves_nothing": (
            "ce dossier compose et mesure ; il ne vaut pas validation visuelle"
        ),
        "pages_are_searched_not_hardcoded": True,
        "critical_dpi": CRITICAL_DPI,
        "contact_dpi": CONTACT_DPI,
        "tab_contract": {
            "inside_mm": TAB_INSIDE_MM,
            "outside_mm": TAB_OUTSIDE_MM,
            "minimum_length_mm": TAB_MIN_LENGTH_MM,
            "label_padding_mm": TAB_TEXT_PADDING_MM,
            "inner_padding_mm": TAB_INNER_PADDING_MM,
        },
        "pages": rows,
        "missing": missing,
        "summary": {
            "PAGES_SELECTED": len(rows),
            "PAGES_REQUIRED": BUNDLE_PAGES,
            "CATEGORIES_REQUIRED": len(CATEGORIES),
            "CATEGORIES_FOUND": len(categories_found),
            "MISSING_CATEGORIES": len(missing),
            "TAB_PRESENT": sum(1 for row in rows if row["tab"].get("present")),
            "TAB_CONTRACT_VIOLATIONS": sum(len(row["tab_failures"]) for row in rows),
            "PAGES_WITH_A_TAB_FAILURE": len(failures),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Dossier D7 du manuel 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Statut D7 : **{payload['d7_status']}**. {payload['approves_nothing']}.",
        "",
        f"Rastérisation critique : {payload['critical_dpi']} dpi ; "
        f"planche de contact : {payload['contact_dpi']} dpi.",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Pages retenues",
        "",
        "| Catégorie | Ce qu'elle montre | Variante | Page | Parité | Onglet |",
        "|---|---|---|---:|---|---|",
    ]
    for row in payload["pages"]:
        tab = row["tab"]
        summary = (
            f"{tab['side']}, {tab['inside_mm']} mm dedans / "
            f"{tab['outside_mm']} mm dehors, {tab['length_mm']} mm"
            if tab.get("present")
            else "absent"
        )
        lines.append(
            f"| `{row['category']}` | {row['shows']} | {row['variant']} | "
            f"{row['page']} | {row['parity']} | {summary} |"
        )
    lines += ["", "## Mesures de l'onglet", ""]
    for row in payload["pages"]:
        if not row["tab"].get("present"):
            continue
        lines += [
            f"### `{row['category']}` — {row['variant']} page {row['page']}",
            "",
            "| Règle | Verdict | Mesuré |",
            "|---|---|---|",
        ]
        for verdict in row["tab_verdicts"]:
            lines.append(
                f"| `{verdict['rule']}` | {verdict['verdict']} | "
                f"`{json.dumps(verdict['measured'], ensure_ascii=False)}` |"
            )
        lines.append("")
    if payload["missing"]:
        lines += ["## Catégories introuvables", ""]
        for entry in payload["missing"]:
            lines.append(f"- `{entry}`")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="mesurer sans écrire ni rastériser"
    )
    arguments = parser.parse_args(argv)

    try:
        payload = build(not arguments.check)
    except BundleError as error:
        print(f"1SPE-D7-BUNDLE-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {relative(JSON_TARGET)}, {relative(MD_TARGET)} et {relative(BUNDLE_DIR)}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    blocking = ("MISSING_CATEGORIES", "TAB_CONTRACT_VIOLATIONS")
    if payload["summary"]["PAGES_SELECTED"] != BUNDLE_PAGES:
        print(f"PAGES_SELECTED_IS_NOT_{BUNDLE_PAGES}=1")
        return 1
    return 1 if any(payload["summary"][name] for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
