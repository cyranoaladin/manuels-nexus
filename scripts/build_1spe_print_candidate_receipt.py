#!/usr/bin/env python3
"""Le reçu des candidats d'impression 1SPE, dérivé et non plus écrit à la main.

L'artefact qui portait ce nom était une saisie manuelle datant d'une campagne
antérieure : 357 et 629 pages, zéro signet, aucune TrimBox, métadonnées vides,
couvertures indiscernables. Tout cela est corrigé depuis, mais le fichier, lui,
ne pouvait pas le savoir : rien ne le produisait, donc rien ne le rafraîchissait.
Un reçu qui ne peut pas se périmer ne prouve rien, et celui-là bloquait la
release en décrivant un manuel qui n'existe plus.

Il est désormais DÉRIVÉ, de trois sources et d'aucune autre :

* le manifeste de build, pour ce qui est réellement observé -- SHA source,
  empreinte du PDF, nombre de pages, reproductibilité ;
* les sorties de construction posées à côté du PDF, pour les empreintes de
  journal et d'inventaires ;
* les artefacts de contrôle déjà produits, pour la QA -- ils ne sont pas
  recalculés ici, seulement cités avec leur verdict.

Ce reçu n'approuve rien : il constate. Les deux revues humaines, le D7 et le
gel du contenu restent en attente, et le reçu le dit.

Métriques bloquantes : `RECEIPT_DESCRIBES_HEAD`, `OBSERVED_VARIANTS`,
`QA_ARTIFACTS_MISSING`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json"
MD_TARGET = ROOT / "audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.md"
GENERATED_BY = "scripts/build_1spe_print_candidate_receipt.py"

MANIFEST = ROOT / "audit/BUILD_MANIFEST.json"
BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
MANUAL = "1SPE"
VARIANTS = ("eleve", "professeur")

# Les contrôles déjà produits, et la métrique qui porte leur verdict. Ce reçu
# les CITE ; il ne refait aucune mesure.
QA_SOURCES = {
    "audit/1SPE_LATEX_LOG_WARNING_GATE.json": (
        "LATEX_WARNINGS",
        "UNCLASSIFIED_WARNING_LINES",
    ),
    "audit/1SPE_CHAPTER_OPENER_SPAN.json": (
        "MULTI_PAGE_OPENERS",
        "OPENER_MISSING_CONTENT",
    ),
    "audit/1SPE_CHAPTER_OPENER_RASTER_QA.json": (
        "OPENER_CLIPPING",
        "OPENER_EMPTY_ZONE",
        "OPENER_TEXT_WITHOUT_TRACE",
    ),
    "audit/1SPE_MARGIN_RASTER_QA.json": (
        "MISSING",
        "DUPLICATE",
        "WRONG_PAGE",
        "WRONG_SIDE",
        "EMPTY_RENDER",
        "UNKNOWN",
    ),
    "audit/1SPE_ALL_PAGES_QA.json": (
        "UNDECLARED_INK_IN_BLEED_BAND",
        "TEXT_INSIDE_SAFETY_MARGIN",
        "TEXT_LAYER_CONTROL_CHARACTERS",
    ),
    "audit/1SPE_PAGINATION_BASELINE_RATIFICATION.json": (
        "MISSING_CONTENT",
        "DUPLICATED_CONTENT",
        "UNINTENTIONAL_BLANK_PAGE",
        "CURRENT_BUILD_FALSE_CHAPTER_FOLIO",
    ),
}


class ReceiptError(RuntimeError):
    """Une preuve manque : le reçu ne peut pas être dérivé."""


def _reject(message: str) -> None:
    raise ReceiptError(message)


def head_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        _reject("git rev-parse HEAD a échoué")
    return result.stdout.strip()


def _digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def observed_builds() -> dict[str, dict[str, Any]]:
    if not MANIFEST.is_file():
        _reject(f"manifeste de build absent : {MANIFEST}")
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    builds = {
        build["variant"]: build
        for build in payload.get("builds", [])
        if build.get("manual") == MANUAL
    }
    if not builds:
        _reject(
            "le manifeste n'observe aucune construction 1SPE : rien à recevoir"
        )
    return builds


def variant_receipt(variant: str, build: dict[str, Any]) -> dict[str, Any]:
    stem = f"MANUEL_{MANUAL}_{variant}"
    return {
        "variant": variant,
        "page_count": build["page_count"],
        "source_sha": build["git_sha"],
        "pdf_path": build["pdf_path"],
        "pdf_sha256": build["pdf_sha256"],
        "log_sha256": _digest(BUILD / f"{stem}.log"),
        "margin_layout_sha256": _digest(BUILD / f"{stem}.margin-layout.json"),
        "margin_links_sha256": _digest(BUILD / f"{stem}.margin-links.json"),
        "preflight_present": (BUILD / f"{stem}.preflight.json").is_file(),
        "observed_receipt_present": (BUILD / f"{stem}.receipt.json").is_file(),
        "reproducibility": build.get("reproducibility"),
    }


def quality_evidence() -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for relative, metrics in QA_SOURCES.items():
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)
            continue
        summary = json.loads(path.read_text(encoding="utf-8"))["summary"]
        rows.append(
            {
                "artifact": relative,
                "artifact_sha256": _digest(path),
                "metrics": {name: summary.get(name) for name in metrics},
            }
        )
    return rows, missing


def build_receipt() -> dict[str, Any]:
    head = head_sha()
    builds = observed_builds()
    variants = {
        variant: variant_receipt(variant, builds[variant])
        for variant in VARIANTS
        if variant in builds
    }
    evidence, missing = quality_evidence()
    # Comparer les SHA de commit dirait toujours faux : chaque enregistrement
    # se lie à son propre commit, et le HEAD avance ensuite d'un commit par
    # manifeste. Ce qui compte est que les SOURCES observées soient les
    # sources courantes -- un commit qui n'ajoute qu'un artefact d'audit ne
    # change pas les sources. C'est donc le condensat de sources qui répond,
    # et le manifeste comme l'inventaire le publient.
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    inventory_path = ROOT / "audit/INVENTAIRE_COLLECTION.json"
    current_digest = (
        json.loads(inventory_path.read_text(encoding="utf-8")).get("source_digest")
        if inventory_path.is_file()
        else None
    )
    observed_digest = manifest.get("source_digest")
    describes_head = (
        len(variants) == len(VARIANTS)
        and observed_digest is not None
        and observed_digest == current_digest
    )
    return {
        "artifact_type": "1spe_print_candidate_build_receipt",
        "schema_version": 2,
        "generated_by": GENERATED_BY,
        "manual": MANUAL,
        "approves_nothing": True,
        "not_final": (
            "Ces PDF ne sont pas finals : aucun 1SPE_FINAL_CONTENT_SHA n'est "
            "figé, les deux revues humaines par chapitre et le dossier D7 "
            "restent en attente."
        ),
        "why_it_is_derived_now": (
            "L'artefact qui portait ce nom était une saisie manuelle : rien ne "
            "le produisait, donc rien ne le rafraîchissait, et il décrivait "
            "encore un manuel de 357 et 629 pages sans signets ni TrimBox. Un "
            "reçu qui ne peut pas se périmer ne prouve rien."
        ),
        "build_command": (
            "python3 Mathematiques/manuel-maths/scripts/assemble_manuel.py "
            "--manual 1SPE --variant <variant> --record-observed"
        ),
        "source_sha": head,
        "observed_source_digest": observed_digest,
        "current_source_digest": current_digest,
        "what_describes_current_is_the_source_digest_not_the_commit": (
            "Chaque enregistrement se lie à son propre commit, et le HEAD "
            "avance ensuite d'un commit par manifeste : comparer les SHA "
            "dirait toujours faux. Un commit qui n'ajoute qu'un artefact "
            "d'audit ne change pas les sources."
        ),
        "variants": variants,
        "quality_evidence_is_cited_not_recomputed": True,
        "quality_evidence": evidence,
        "summary": {
            "OBSERVED_VARIANTS": len(variants),
            "EXPECTED_VARIANTS": len(VARIANTS),
            "RECEIPT_DESCRIBES_HEAD": describes_head,
            "QA_ARTIFACTS_MISSING": len(missing),
            "QA_METRICS_NOT_ZERO": sum(
                1
                for row in evidence
                for value in row["metrics"].values()
                if value
            ),
            "PAGE_COUNTS": {
                variant: row["page_count"] for variant, row in variants.items()
            },
        },
        "missing_quality_artifacts": missing,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reçu des candidats d'impression — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['not_final']}",
        "",
        f"> {payload['why_it_is_derived_now']}",
        "",
        f"SHA source : `{payload['source_sha']}`",
        "",
        f"> {payload['what_describes_current_is_the_source_digest_not_the_commit']}",
        "",
        f"Condensat de sources observé : `{payload['observed_source_digest']}`",
        f"Condensat de sources courant : `{payload['current_source_digest']}`",
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
        "## Constructions observées",
        "",
        "| Variante | Pages | SHA source | Empreinte du PDF | Journal |",
        "|---|---:|---|---|---|",
    ]
    for row in payload["variants"].values():
        lines.append(
            f"| {row['variant']} | {row['page_count']} | "
            f"`{row['source_sha'][:12]}` | `{row['pdf_sha256'][7:19]}` | "
            f"`{(row['log_sha256'] or '—')[7:19]}` |"
        )
    lines += [
        "",
        "## Contrôles cités",
        "",
        "| Artefact | Métriques |",
        "|---|---|",
    ]
    for row in payload["quality_evidence"]:
        metrics = ", ".join(
            f"`{name}`={value}" for name, value in row["metrics"].items()
        )
        lines.append(f"| `{row['artifact']}` | {metrics} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build_receipt()
    except ReceiptError as error:
        print(f"1SPE-PRINT-CANDIDATE-RECEIPT-ERROR: {error}", file=sys.stderr)
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
    return (
        0
        if summary["RECEIPT_DESCRIBES_HEAD"]
        and not summary["QA_ARTIFACTS_MISSING"]
        and not summary["QA_METRICS_NOT_ZERO"]
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
