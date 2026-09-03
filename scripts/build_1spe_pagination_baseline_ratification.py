#!/usr/bin/env python3
"""Ratification de la baseline visuelle de pagination 1SPE : preuves, pas dires.

La décision humaine est une donnée : elle vit dans
`audit/HUMAN_DECISION_1SPE_VISUAL_BASELINE_PAGINATION_*.json`. Ce producteur
n'approuve rien ; il CONFRONTE chaque valeur déclarée à une mesure faite sur
les PDF eux-mêmes.

Deux états sont comparés, et les deux sont lus, jamais supposés :

* l'état **avant** : les PDF versionnés au parent du commit de correction,
  relus par `git show` — l'historique est la seule source de l'avant ;
* l'état **après** : les PDF de `build/` au HEAD courant.

Quatre familles de preuves :

1. **Folio de chapitre.** La page d'ouverture d'un chapitre est localisée par
   son CONTENU rendu — la bannière porte « CHAPITRE n » et le bloc
   « Objectifs — Capacités attendues » — puis confrontée à la destination du
   signet et au folio du sommaire. L'oracle qui comparait le sommaire au
   signet ne pouvait rien voir : les deux descendent du même
   `\\addcontentsline`, ils étaient faux ensemble. Celui-ci est indépendant.

2. **Conservation du contenu.** Le texte de chaque page est dépouillé de son
   mobilier — pied de page, folio, onglet de rubrique — les pages de sommaire
   sont écartées, et les deux flux ainsi obtenus doivent être IDENTIQUES,
   caractère pour caractère. C'est la preuve que le changement n'a ni perdu,
   ni dupliqué, ni réordonné quoi que ce soit.

3. **Pages blanches.** Aucune page ne doit être vide sans raison. Les pages
   quasi vides sont comptées à part et nommées : une page qui ne porte que
   « Temps estimés » est un défaut de mise en page, pas une page blanche.

4. **Compteurs déclarés.** Pages et folios faux, avant et après, doivent être
   exactement ceux que la décision annonce.

Métriques bloquantes : `REFUTED_CLAIMS`, `CHAPTER_OPENING_FALSE_FOLIO_AFTER`,
`MISSING_CONTENT`, `DUPLICATED_CONTENT`, `UNEXPECTED_REORDERING`,
`UNINTENTIONAL_BLANK_PAGE`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_PAGINATION_BASELINE_RATIFICATION.json"
MD_TARGET = ROOT / "audit/1SPE_PAGINATION_BASELINE_RATIFICATION.md"
DOCKET_GLOB = "HUMAN_DECISION_1SPE_VISUAL_BASELINE_PAGINATION_*.json"
DOCKET_TYPE = "human_decision_visual_baseline_pagination"
GENERATED_BY = "scripts/build_1spe_pagination_baseline_ratification.py"

FOOTER = "NEXUS RÉUSSITE"
# La rubrique est composée deux fois par page : en capitales dans l'onglet
# latéral, puis en casse d'usage dans l'en-tête. C'est du mobilier de page :
# il suit sa page, et le suivre est précisément l'effet autorisé.
RUBRICS = (
    "Ouverture",
    "Remédiation",
    "Méthodes",
    "Exercices",
    "Cours",
    "Auto-évaluation",
    "Corrigés",
    "Formulaire",
    "Sommaire",
    "Mémo Python",
    "Avant-propos",
    "Mode d'emploi",
    "Plan du manuel",
    "Diagnostic",
    "Entraînement",
    "Transfert",
    "Réactivation",
    "Preuve de maîtrise",
    "Guidage",
    "Exemple expert",
    "Orientation",
)
CHAPTER_BANNER = re.compile(r"CHAPITRE (\d+)")
OBJECTIVES = "Objectifs — Capacités attendues"
# En dessous de ce nombre de caractères utiles, une page ne porte plus de
# contenu : elle est quasi vide, et il faut la nommer.
NEARLY_EMPTY_CHARACTERS = 120


class RatificationError(RuntimeError):
    """Une valeur déclarée est réfutée, ou une preuve est inaccessible."""


def _reject(message: str) -> None:
    raise RatificationError(message)


def _fitz() -> Any:
    try:
        import fitz
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        _reject("PyMuPDF (fitz) est requis pour mesurer les PDF")
    return fitz


def _git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, check=False
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalise(text: str) -> str:
    return " ".join(text.replace("’", "'").replace(" ", " ").split())


def dehyphenate(title: str) -> str:
    """Recolle une césure de fin de ligne dans un titre composé.

    La bannière compose le titre du chapitre dans un nœud de largeur fixe :
    « Probabilités conditionnelles et indépendance » y devient « Probabilités
    condition- nelles et indépendance ». Le sommaire, lui, tient sur une seule
    ligne. Sans ce recollage l'oracle déclarerait un folio faux là où il n'y a
    qu'une césure. Aucun titre de chapitre ne doit porter de trait d'union
    propre pour que le recollage soit sûr : le producteur le vérifie.
    """

    return re.sub(r"-\s+", "", normalise(title))


def page_body(page: Any) -> str:
    """Le texte utile d'une page : sans pied, sans folio, sans onglet."""

    raw = page.get_text().replace("’", "'").replace(" ", " ")
    lines = [line.strip() for line in raw.splitlines()]
    kept = [
        line
        for line in lines
        if line and line != FOOTER and not re.fullmatch(r"\d{1,4}", line)
    ]
    body = " ".join(" ".join(kept).split())
    for rubric in RUBRICS:
        doubled = f"{rubric.upper()} {rubric}"
        if body.startswith(doubled):
            return body[len(doubled) :].strip()
        if body.startswith(rubric.upper() + " "):
            return body[len(rubric.upper()) + 1 :].strip()
    return body


def summary_pages(document: Any) -> set[int]:
    """Les pages du sommaire composé, en numérotation physique 1..n."""

    outline = document.get_toc()
    if not outline:
        _reject("le PDF ne porte aucun signet")
    first = next(
        (
            index
            for index in range(document.page_count)
            if document[index].get_text().lstrip().startswith("Sommaire")
        ),
        None,
    )
    if first is None:
        _reject("aucune page de sommaire trouvée dans le PDF")
    following = min(
        (page for _level, _title, page in outline if page > first + 1),
        default=first + 2,
    )
    return set(range(first + 1, following))


def chapter_openings(document: Any) -> list[dict[str, Any]]:
    """Les ouvertures de chapitre, localisées par leur contenu rendu."""

    openings: list[dict[str, Any]] = []
    for index in range(document.page_count):
        text = normalise(document[index].get_text())
        banner = CHAPTER_BANNER.search(text)
        if banner is None or OBJECTIVES not in text:
            continue
        tail = text[banner.end() :]
        title = dehyphenate(tail.split("Objectifs")[0].strip())
        openings.append(
            {
                "chapter_number": int(banner.group(1)),
                "title": title,
                "opening_page": index + 1,
            }
        )
    return openings


def toc_folios(document: Any) -> dict[str, int]:
    """Le folio que le sommaire IMPRIME pour chaque entrée de niveau 1."""

    pages = sorted(summary_pages(document))
    printed = normalise("\n".join(document[page - 1].get_text() for page in pages))
    folios: dict[str, int] = {}
    cursor = 0
    for level, title, _page in document.get_toc():
        if level != 1:
            continue
        needle = normalise(title)
        position = printed.find(needle, cursor)
        if position < 0:
            continue
        cursor = position + len(needle)
        digits = re.search(r"(\d+)", printed[cursor : cursor + 220])
        if digits is not None:
            folios[dehyphenate(title)] = int(digits.group(1))
    return folios


def bookmark_pages(document: Any) -> dict[str, int]:
    return {
        dehyphenate(title): page
        for level, title, page in document.get_toc()
        if level == 1
    }


def blank_and_nearly_empty(document: Any) -> dict[str, list[int]]:
    """Pages sans contenu, et pages qui n'en portent presque plus."""

    blank: list[int] = []
    nearly: list[int] = []
    for index in range(document.page_count):
        page = document[index]
        body = page_body(page)
        if body:
            if len(body) < NEARLY_EMPTY_CHARACTERS:
                nearly.append(index + 1)
            continue
        has_ink = bool(page.get_drawings()) or bool(page.get_images())
        if has_ink:
            nearly.append(index + 1)
        else:
            blank.append(index + 1)
    return {"blank_pages": blank, "nearly_empty_pages": nearly}


def content_stream(document: Any) -> str:
    skip = summary_pages(document)
    parts = [
        page_body(document[index])
        for index in range(document.page_count)
        if (index + 1) not in skip
    ]
    return " ".join(part for part in parts if part)


def opener_overflow(document: Any, openings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Une ouverture de chapitre qui ne tient pas sur sa page.

    La macro pose `\\thispagestyle{empty}` : l'ouverture est une page pleine
    bannière, sans onglet ni folio. Quand son contenu — objectifs, accroche,
    temps estimés — dépasse la place laissée sous la bannière, la fin bascule
    sur la page suivante, qui reprend l'onglet « Ouverture » et un folio.
    `\\vfill` avale le débordement : le journal LaTeX reste muet, et le défaut
    ne se voit que sur la page rendue. C'est pourquoi il est mesuré ici.
    """

    rows = []
    for opening in openings:
        page = opening["opening_page"]
        if page >= document.page_count:
            continue
        following = normalise(document[page].get_text())
        if not following.startswith(RUBRICS[0].upper()):
            continue
        body = page_body(document[page])
        rows.append(
            {
                "chapter_number": opening["chapter_number"],
                "title": opening["title"],
                "opening_page": page,
                "overflow_page": page + 1,
                "overflow_characters": len(body),
                "overflow_is_nearly_empty": len(body) < NEARLY_EMPTY_CHARACTERS,
                "overflow_body": body[:160],
            }
        )
    return rows


def measure(path: Path) -> dict[str, Any]:
    fitz = _fitz()
    with fitz.open(path) as document:
        openings = chapter_openings(document)
        folios = toc_folios(document)
        bookmarks = bookmark_pages(document)
        rows = []
        for opening in openings:
            key = opening["title"]
            rows.append(
                {
                    **opening,
                    "toc_printed_folio": folios.get(key),
                    "bookmark_destination": bookmarks.get(key),
                    "folio_is_wrong": folios.get(key) != opening["opening_page"],
                    "bookmark_is_wrong": bookmarks.get(key)
                    != opening["opening_page"],
                }
            )
        return {
            "page_count": document.page_count,
            "bookmark_count": len(document.get_toc()),
            "summary_pages": sorted(summary_pages(document)),
            "chapter_openings": rows,
            "chapter_opening_false_folio": sum(
                1 for row in rows if row["folio_is_wrong"]
            ),
            "chapter_opening_false_bookmark": sum(
                1 for row in rows if row["bookmark_is_wrong"]
            ),
            "content_stream_sha256": hashlib.sha256(
                content_stream(document).encode("utf-8")
            ).hexdigest(),
            "content_stream_length": len(content_stream(document)),
            "chapter_titles_carry_no_own_hyphen": all(
                "-" not in row["title"] for row in rows
            ),
            "opener_overflow": opener_overflow(document, openings),
            **blank_and_nearly_empty(document),
        }


def docket_paths() -> list[Path]:
    return sorted((ROOT / "audit").glob(DOCKET_GLOB))


def load_docket() -> dict[str, Any]:
    paths = docket_paths()
    if not paths:
        _reject("aucune décision humaine de baseline de pagination trouvée")
    if len(paths) > 1:
        _reject(
            "plusieurs décisions concurrentes : "
            + ", ".join(relative(path) for path in paths)
        )
    payload = json.loads(paths[0].read_text(encoding="utf-8"))
    if payload.get("artifact_type") != DOCKET_TYPE:
        _reject(f"{relative(paths[0])} n'est pas un docket de baseline de pagination")
    payload["docket_path"] = relative(paths[0])
    return payload


def pdf_at(revision: str, tracked_path: str, destination: Path) -> None:
    """Un PDF relu dans l'historique, a la revision demandee."""

    result = _git("show", f"{revision}:{tracked_path}")
    if result.returncode != 0:
        _reject(
            f"impossible de relire {tracked_path} a {revision} : "
            + result.stderr.decode("utf-8", "replace").strip()
        )
    destination.write_bytes(result.stdout)


def compare(
    variant: str,
    before: dict[str, Any],
    after: dict[str, Any],
    docket: dict[str, Any],
) -> dict[str, Any]:
    superseded = docket["superseded_baseline"]
    candidate = docket["ratified_candidate"]
    claims: list[dict[str, Any]] = []

    def claim(name: str, declared: Any, observed: Any) -> None:
        claims.append(
            {
                "claim": name,
                "declared": declared,
                "observed": observed,
                "verdict": "CONFIRMED" if declared == observed else "REFUTED",
            }
        )

    claim(
        f"{variant}_page_count_before",
        superseded[f"{variant_key(variant)}_page_count"],
        before["page_count"],
    )
    claim(
        f"{variant}_page_count_after",
        candidate[f"{variant_key(variant)}_page_count"],
        after["page_count"],
    )
    claim(
        f"{variant}_wrong_chapter_folios_before",
        superseded[f"{variant_key(variant)}_wrong_chapter_folios"],
        before["chapter_opening_false_folio"],
    )
    claim(
        f"{variant}_wrong_chapter_folios_after",
        candidate[f"{variant_key(variant)}_wrong_chapter_folios"],
        after["chapter_opening_false_folio"],
    )

    by_number_before = {
        row["chapter_number"]: row for row in before["chapter_openings"]
    }
    boundaries = []
    for row in after["chapter_openings"]:
        number = row["chapter_number"]
        earlier = by_number_before.get(number)
        boundaries.append(
            {
                "chapter_number": number,
                "title": row["title"],
                "opening_page_before": earlier and earlier["opening_page"],
                "opening_page_after": row["opening_page"],
                "propagated_delta": (
                    row["opening_page"] - earlier["opening_page"]
                    if earlier
                    else None
                ),
                "toc_folio_before": earlier and earlier["toc_printed_folio"],
                "toc_folio_after": row["toc_printed_folio"],
                "folio_was_wrong_before": earlier and earlier["folio_is_wrong"],
                "folio_is_wrong_after": row["folio_is_wrong"],
                "bookmark_is_wrong_after": row["bookmark_is_wrong"],
            }
        )

    content_conserved = (
        before["content_stream_sha256"] == after["content_stream_sha256"]
    )
    documented = {
        entry["page"]: entry for entry in docket.get("documented_blank_pages", [])
    }
    blank_rows = [
        {
            "page": page,
            "reason": documented.get(page, {}).get("reason", "UNDOCUMENTED"),
            "mechanism": documented.get(page, {}).get("mechanism"),
            "documented": page in documented,
            "already_blank_before": page in set(before["blank_pages"]),
        }
        for page in after["blank_pages"]
    ]
    # Une raison déclarée pour une page qui n'est plus blanche est une
    # déclaration périmée : elle compte comme réfutation.
    stale_reasons = sorted(set(documented) - set(after["blank_pages"]))
    overflow_after = after["opener_overflow"]
    return {
        "variant": variant,
        "before": before,
        "after": after,
        "claims": claims,
        "chapter_boundaries": boundaries,
        "REFUTED_CLAIMS": sum(1 for row in claims if row["verdict"] == "REFUTED"),
        "CHAPTER_OPENING_FALSE_FOLIO_BEFORE": before["chapter_opening_false_folio"],
        "CHAPTER_OPENING_FALSE_FOLIO_AFTER": after["chapter_opening_false_folio"],
        "CHAPTER_OPENING_FALSE_BOOKMARK_AFTER": after[
            "chapter_opening_false_bookmark"
        ],
        # Le flux dépouillé est identique ou il ne l'est pas. Une perte, un
        # doublon et un réordonnancement changent tous les trois ce condensat ;
        # aucun des trois ne peut donc se cacher derrière les deux autres.
        "CONTENT_STREAM_CONSERVED": content_conserved,
        "MISSING_CONTENT": 0 if content_conserved else 1,
        "DUPLICATED_CONTENT": 0 if content_conserved else 1,
        "UNEXPECTED_REORDERING": 0 if content_conserved else 1,
        "blank_pages": blank_rows,
        "stale_blank_page_reasons": stale_reasons,
        "UNINTENTIONAL_BLANK_PAGE": sum(
            1 for row in blank_rows if not row["documented"]
        ),
        "STALE_BLANK_PAGE_REASONS": len(stale_reasons),
        "DOCUMENTED_BLANK_PAGE": sum(1 for row in blank_rows if row["documented"]),
        "NEARLY_EMPTY_PAGES_BEFORE": len(before["nearly_empty_pages"]),
        "NEARLY_EMPTY_PAGES_AFTER": len(after["nearly_empty_pages"]),
        "CHAPTER_TITLES_CARRY_NO_OWN_HYPHEN": after[
            "chapter_titles_carry_no_own_hyphen"
        ],
        # Défaut nommé, distinct de la décision ratifiée : il préexiste, il a
        # empiré, et il attend une décision éditoriale.
        "chapter_opener_overflow": overflow_after,
        "CHAPTER_OPENER_OVERFLOW_BEFORE": len(before["opener_overflow"]),
        "CHAPTER_OPENER_OVERFLOW_AFTER": len(overflow_after),
        "CHAPTER_OPENER_ORPHAN_PAGE_BEFORE": sum(
            1 for row in before["opener_overflow"] if row["overflow_is_nearly_empty"]
        ),
        "CHAPTER_OPENER_ORPHAN_PAGE_AFTER": sum(
            1 for row in overflow_after if row["overflow_is_nearly_empty"]
        ),
    }


def variant_key(variant: str) -> str:
    return {"eleve": "student", "professeur": "teacher"}[variant]


def build(temporary: Path) -> dict[str, Any]:
    docket = load_docket()
    commit = docket["change_commit"]
    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        _reject(f"le commit de correction {commit} est introuvable")

    variants = []
    for entry in docket["variants"]:
        variant = entry["variant"]
        tracked = entry["pdf_path"]
        current = ROOT / tracked
        if not current.is_file():
            _reject(f"PDF courant absent : {tracked}")
        # La ratification porte sur UN changement, celui du commit declare. Ses
        # deux etats sont donc relus dans l'historique, et la preuve reste vraie
        # quels que soient les changements autorises qui suivront. Le build
        # COURANT est mesure a part, et on lui demande de tenir encore les
        # proprietes ratifiees -- pas d'etre le meme fichier.
        earlier = temporary / f"before-{variant}.pdf"
        later = temporary / f"after-{variant}.pdf"
        pdf_at(f"{commit}^", tracked, earlier)
        pdf_at(commit, tracked, later)
        row = compare(variant, measure(earlier), measure(later), docket)
        row["pdf_path"] = tracked
        row["ratified_after_commit"] = commit
        current_measure = measure(current)
        row["current_build"] = {
            "pdf_sha256": sha256_file(current),
            "page_count": current_measure["page_count"],
            "chapter_opening_false_folio": current_measure[
                "chapter_opening_false_folio"
            ],
            "chapter_opening_false_bookmark": current_measure[
                "chapter_opening_false_bookmark"
            ],
            "blank_pages": current_measure["blank_pages"],
            "nearly_empty_pages": current_measure["nearly_empty_pages"],
            "opener_overflow": current_measure["opener_overflow"],
            "content_stream_length": current_measure["content_stream_length"],
            "content_stream_sha256": current_measure["content_stream_sha256"],
            "still_carries_the_ratified_page_count": (
                current_measure["page_count"] == row["after"]["page_count"]
            ),
            "still_carries_no_false_chapter_folio": (
                current_measure["chapter_opening_false_folio"] == 0
            ),
            "content_stream_identical_to_ratified_build": (
                current_measure["content_stream_sha256"]
                == row["after"]["content_stream_sha256"]
            ),
        }
        variants.append(row)

    summary = {
        "REFUTED_CLAIMS": sum(row["REFUTED_CLAIMS"] for row in variants),
        "CHAPTER_OPENING_FALSE_FOLIO_AFTER": sum(
            row["CHAPTER_OPENING_FALSE_FOLIO_AFTER"] for row in variants
        ),
        "CHAPTER_OPENING_FALSE_BOOKMARK_AFTER": sum(
            row["CHAPTER_OPENING_FALSE_BOOKMARK_AFTER"] for row in variants
        ),
        "MISSING_CONTENT": sum(row["MISSING_CONTENT"] for row in variants),
        "DUPLICATED_CONTENT": sum(row["DUPLICATED_CONTENT"] for row in variants),
        "UNEXPECTED_REORDERING": sum(
            row["UNEXPECTED_REORDERING"] for row in variants
        ),
        "UNINTENTIONAL_BLANK_PAGE": sum(
            row["UNINTENTIONAL_BLANK_PAGE"] for row in variants
        ),
        "CURRENT_BUILD_LOST_THE_RATIFIED_PAGE_COUNT": sum(
            0 if row["current_build"]["still_carries_the_ratified_page_count"] else 1
            for row in variants
        ),
        "CURRENT_BUILD_FALSE_CHAPTER_FOLIO": sum(
            row["current_build"]["chapter_opening_false_folio"] for row in variants
        ),
        "CURRENT_BUILD_DIFFERS_FROM_THE_RATIFIED_ONE": sum(
            0
            if row["current_build"]["content_stream_identical_to_ratified_build"]
            else 1
            for row in variants
        ),
        "STALE_BLANK_PAGE_REASONS": sum(
            row["STALE_BLANK_PAGE_REASONS"] for row in variants
        ),
        "DOCUMENTED_BLANK_PAGE": sum(
            row["DOCUMENTED_BLANK_PAGE"] for row in variants
        ),
        "CHAPTER_TITLES_CARRY_NO_OWN_HYPHEN": all(
            row["CHAPTER_TITLES_CARRY_NO_OWN_HYPHEN"] for row in variants
        ),
        "NEARLY_EMPTY_PAGES_AFTER": sum(
            row["NEARLY_EMPTY_PAGES_AFTER"] for row in variants
        ),
        "CHAPTER_OPENER_OVERFLOW_BEFORE": sum(
            row["CHAPTER_OPENER_OVERFLOW_BEFORE"] for row in variants
        ),
        "CHAPTER_OPENER_OVERFLOW_AFTER": sum(
            row["CHAPTER_OPENER_OVERFLOW_AFTER"] for row in variants
        ),
        "CHAPTER_OPENER_ORPHAN_PAGE_BEFORE": sum(
            row["CHAPTER_OPENER_ORPHAN_PAGE_BEFORE"] for row in variants
        ),
        "CHAPTER_OPENER_ORPHAN_PAGE_AFTER": sum(
            row["CHAPTER_OPENER_ORPHAN_PAGE_AFTER"] for row in variants
        ),
    }
    return {
        "artifact_type": "1spe_pagination_baseline_ratification",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "decision_id": docket["decision_id"],
        "decision_ref": docket["decision_ref"],
        "docket_path": docket["docket_path"],
        "change_commit": commit,
        "ratified_mechanism": docket["ratified_mechanism"],
        "refused_mechanism": docket["refused_mechanism"],
        "content_approval": docket["content_approval"],
        "d7_approval": docket["d7_approval"],
        "publication_approval": docket["publication_approval"],
        "page_counts_are_pinned": docket["page_counts_are_pinned"],
        "authorized_change_class": docket["authorized_change_class"],
        "variants": variants,
        "summary": summary,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Ratification de la baseline visuelle de pagination — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Décision : [`{payload['decision_id']}`]({payload['docket_path']})",
        f"Commit de correction : `{payload['change_commit']}`",
        f"Mécanisme ratifié : `{payload['ratified_mechanism']}` — "
        f"refusé : `{payload['refused_mechanism']}`",
        "",
        "## Portée",
        "",
        "| Portée | État |",
        "|---|---|",
        f"| `CONTENT_APPROVAL` | {str(payload['content_approval']).lower()} |",
        f"| `D7_APPROVAL` | {str(payload['d7_approval']).lower()} |",
        f"| `PUBLICATION_APPROVAL` | "
        f"{str(payload['publication_approval']).lower()} |",
        f"| Compteurs de pages épinglés | "
        f"{str(payload['page_counts_are_pinned']).lower()} |",
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
            f"- pages : {row['before']['page_count']} → "
            f"{row['after']['page_count']} au commit ratifié",
            f"- build courant : {row['current_build']['page_count']} pages, "
            f"`sha256:{row['current_build']['pdf_sha256'][:16]}…`, "
            f"{row['current_build']['chapter_opening_false_folio']} folio faux, "
            f"identique au build ratifié : "
            f"{str(row['current_build']['content_stream_identical_to_ratified_build']).lower()}",
            f"- folios de chapitre faux : "
            f"{row['CHAPTER_OPENING_FALSE_FOLIO_BEFORE']} → "
            f"{row['CHAPTER_OPENING_FALSE_FOLIO_AFTER']}",
            f"- flux de contenu dépouillé conservé : "
            f"{str(row['CONTENT_STREAM_CONSERVED']).lower()} "
            f"({row['after']['content_stream_length']} caractères)",
            f"- pages blanches : {row['after']['blank_pages'] or 'aucune'}",
            f"- pages quasi vides : {row['NEARLY_EMPTY_PAGES_BEFORE']} → "
            f"{row['NEARLY_EMPTY_PAGES_AFTER']} "
            f"({row['after']['nearly_empty_pages'] or 'aucune'})",
            "",
            "### Valeurs déclarées confrontées",
            "",
            "| Affirmation | Déclaré | Observé | Verdict |",
            "|---|---:|---:|---|",
        ]
        for entry in row["claims"]:
            lines.append(
                f"| `{entry['claim']}` | {entry['declared']} | "
                f"{entry['observed']} | {entry['verdict']} |"
            )
        lines += [
            "",
            "### Frontières de chapitre",
            "",
            "| Ch. | Titre | Ouverture avant | Ouverture après | Δ | "
            "Folio avant | Folio après | Faux avant | Faux après |",
            "|---:|---|---:|---:|---:|---:|---:|---|---|",
        ]
        for entry in row["chapter_boundaries"]:
            lines.append(
                f"| {entry['chapter_number']} | {entry['title']} | "
                f"{entry['opening_page_before']} | "
                f"{entry['opening_page_after']} | "
                f"{entry['propagated_delta']:+d} | "
                f"{entry['toc_folio_before']} | {entry['toc_folio_after']} | "
                f"{'oui' if entry['folio_was_wrong_before'] else 'non'} | "
                f"{'oui' if entry['folio_is_wrong_after'] else 'non'} |"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="mesurer sans écrire ; sortie 1 si une valeur déclarée est réfutée",
    )
    arguments = parser.parse_args(argv)

    import tempfile

    try:
        with tempfile.TemporaryDirectory(prefix="nexus-pagination-") as directory:
            payload = build(Path(directory))
    except RatificationError as error:
        print(f"1SPE-PAGINATION-RATIFICATION-ERROR: {error}", file=sys.stderr)
        return 2

    blocking = {
        name: payload["summary"][name]
        for name in (
            "REFUTED_CLAIMS",
            "CHAPTER_OPENING_FALSE_FOLIO_AFTER",
            "CHAPTER_OPENING_FALSE_BOOKMARK_AFTER",
            "MISSING_CONTENT",
            "DUPLICATED_CONTENT",
            "UNEXPECTED_REORDERING",
            "UNINTENTIONAL_BLANK_PAGE",
            "STALE_BLANK_PAGE_REASONS",
            "CURRENT_BUILD_LOST_THE_RATIFIED_PAGE_COUNT",
            "CURRENT_BUILD_FALSE_CHAPTER_FOLIO",
        )
    }
    if not payload["summary"]["CHAPTER_TITLES_CARRY_NO_OWN_HYPHEN"]:
        # Le recollage des cesures suppose qu'aucun titre ne porte de trait
        # d'union propre. Si un chapitre en gagne un, l'oracle de folio doit
        # etre revu avant d'etre cru.
        blocking["CHAPTER_TITLE_HYPHEN_BREAKS_THE_FOLIO_ORACLE"] = 1
    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {relative(JSON_TARGET)} et {relative(MD_TARGET)}")
    for name, value in blocking.items():
        print(f"{name}={value}")
    return 1 if any(blocking.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
