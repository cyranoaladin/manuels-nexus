#!/usr/bin/env python3
"""Contrôler le référentiel canonique du programme 1SPE 2026."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PDF_SHA256 = (
    "5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08"
)
EXPECTED_COUNTS = {
    ("contenu", "mandatory_content"): 42,
    ("contenu", "contextual_guidance"): 5,
    ("capacite", "prescribed_teaching"): 44,
    ("demonstration", "prescribed_teaching"): 11,
    ("algorithme", "mandatory_content"): 4,
    ("algorithme", "contextual_guidance"): 11,
    ("approfondissement", "optional_extension"): 17,
    ("transversal", "mandatory_content"): 8,
    ("transversal", "prescribed_teaching"): 29,
    ("transversal", "contextual_guidance"): 4,
}
REQUIRED_EXPERIMENTS = {
    "VA-EXP-SIMULER",
    "VA-EXP-FONCTION-MOYENNE",
    "VA-EXP-DISTANCE-MOYENNE-ESPERANCE",
    "VA-EXP-PROPORTION-2SIGMA",
}
REQUIRED_OBJECTIVE_BOUNDARIES = {
    "OBJ-ALG-SUITES-BORNE-001",
    "OBJ-ALG-LIMITE-BORNE-001",
    "OBJ-ALG-SD-BORNE-001",
    "OBJ-ANA-DERIVEE-BORNE-001",
    "OBJ-GEO-VECTEURS-PRESC-001",
    "OBJ-PROB-UNIVERS-BORNE-001",
}
OFFICIAL_THEMATIC_DOMAINS = {
    "Algèbre",
    "Analyse",
    "Géométrie",
    "Probabilités et statistiques",
}
OFFICIAL_TRANSVERSAL_DOMAINS = {
    "Vocabulaire ensembliste et logique",
    "Algorithmique et programmation",
    "Automatismes",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def normalized_pages(text: str) -> list[str]:
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return [normalize_whitespace(page) for page in pages]


def extract_pdf_text(source: Path) -> bytes:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise RuntimeError("pdftotext absent")
    result = subprocess.run(
        [str(Path(executable).absolute()), "-layout", str(source), "-"],
        cwd=source.parent,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        diagnostic = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"pdftotext code {result.returncode}: {diagnostic}")
    decoded = result.stdout.decode("utf-8")
    return decoded.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} doit contenir un objet JSON")
    return value


def compact_schema_error(error: Any) -> str:
    location = "/".join(str(part) for part in error.absolute_path) or "$"
    return f"{location}: {error.message}"


def count_key(item: dict[str, Any]) -> tuple[str, str] | None:
    item_type = item.get("type")
    obligation = item.get("obligation_class")
    if isinstance(item_type, str) and isinstance(obligation, str):
        return item_type, obligation
    return None


def check(
    programme_path: Path,
    schema_path: Path,
    source_path: Path,
    text_path: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    schema_errors: list[str] = []
    duplicate_ids: list[str] = []
    orphan_quotes: list[str] = []
    unjustified_distributions: list[str] = []
    assignment_errors: list[str] = []
    obligation_errors: list[str] = []
    editorial_errors: list[str] = []
    domain_errors: list[str] = []

    try:
        programme = load_json(programme_path)
        schema = load_json(schema_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return {
            "status": "needs_fix",
            "item_count": 0,
            "source_sha256": None,
            "text_sha256": None,
            "schema_errors": [str(exc)],
            "duplicate_ids": [],
            "orphan_quotes": [],
            "unjustified_distributions": [],
            "assignment_errors": [],
            "obligation_errors": [],
            "editorial_errors": [],
            "domain_errors": [],
            "cardinality_errors": [],
            "experiment_errors": [],
            "objective_boundary_errors": [],
            "errors": ["référentiel ou schéma illisible"],
        }

    try:
        Draft202012Validator.check_schema(schema)
        schema_errors = sorted(
            compact_schema_error(error)
            for error in Draft202012Validator(schema).iter_errors(programme)
        )
    except Exception as exc:
        schema_errors = [f"schéma invalide : {exc}"]

    try:
        source_hash = sha256(source_path)
    except OSError as exc:
        source_hash = None
        errors.append(f"source PDF inaccessible : {exc}")
    if source_hash != EXPECTED_PDF_SHA256:
        errors.append(
            f"SHA-256 PDF attendu {EXPECTED_PDF_SHA256}, obtenu {source_hash}"
        )

    try:
        text_bytes = text_path.read_bytes()
        text_hash = hashlib.sha256(text_bytes).hexdigest()
        text_value = text_bytes.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        text_hash = None
        text_value = ""
        errors.append(f"texte officiel inaccessible : {exc}")

    source_metadata = programme.get("source")
    if not isinstance(source_metadata, dict):
        source_metadata = {}
    if source_metadata.get("pdf_sha256") != source_hash:
        errors.append("le SHA-256 PDF du référentiel ne correspond pas au PDF")
    if source_metadata.get("text_sha256") != text_hash:
        errors.append("le SHA-256 texte du référentiel ne correspond pas au TXT")

    if source_hash == EXPECTED_PDF_SHA256 and text_hash is not None:
        try:
            regenerated = extract_pdf_text(source_path)
        except (RuntimeError, UnicodeError, OSError) as exc:
            errors.append(f"recoupement PDF/TXT impossible : {exc}")
        else:
            if regenerated != text_bytes:
                errors.append("le TXT n’est pas l’extraction déterministe du PDF")

    pages = normalized_pages(text_value)
    if len(pages) != 11:
        errors.append(f"nombre de pages texte attendu 11, obtenu {len(pages)}")

    raw_items = programme.get("items")
    items = raw_items if isinstance(raw_items, list) else []
    identifiers = [
        item.get("id")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    duplicate_ids = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )

    counts: Counter[tuple[str, str]] = Counter()
    by_id: dict[str, dict[str, Any]] = {}
    for position, raw_item in enumerate(items):
        if not isinstance(raw_item, dict):
            continue
        item_id = raw_item.get("id")
        display_id = item_id if isinstance(item_id, str) else f"index-{position}"
        if isinstance(item_id, str):
            by_id.setdefault(item_id, raw_item)
        key = count_key(raw_item)
        if key is not None:
            counts[key] += 1

        page = raw_item.get("bo_page")
        quote = raw_item.get("bo_quote")
        if (
            not isinstance(page, int)
            or not isinstance(quote, str)
            or not (1 <= page <= len(pages))
            or normalize_whitespace(quote) not in pages[page - 1]
        ):
            orphan_quotes.append(display_id)

        assigned = raw_item.get("assigned_chapters")
        if not isinstance(assigned, list) or not assigned:
            assignment_errors.append(display_id)
        elif len(assigned) > 1:
            justification = raw_item.get("distribution_justification")
            if not isinstance(justification, str) or not justification.strip():
                unjustified_distributions.append(display_id)

        obligation = raw_item.get("obligation_class")
        item_type = raw_item.get("type")
        if obligation not in {
            "mandatory_content",
            "prescribed_teaching",
            "optional_extension",
            "contextual_guidance",
        }:
            obligation_errors.append(display_id)
        if (
            item_type == "approfondissement"
            and obligation != "optional_extension"
        ):
            obligation_errors.append(display_id)
        if (
            item_id in REQUIRED_EXPERIMENTS
            and (
                item_type != "algorithme"
                or obligation != "mandatory_content"
            )
        ):
            obligation_errors.append(display_id)

        verdict = raw_item.get("editorial_verdict")
        rationale = raw_item.get("editorial_rationale")
        if obligation in {"mandatory_content", "prescribed_teaching"} and verdict != "included":
            editorial_errors.append(display_id)
        if verdict == "excluded_with_rationale" and not isinstance(rationale, str):
            editorial_errors.append(display_id)

        domain_kind = raw_item.get("domain_kind")
        domain = raw_item.get("domain")
        if (
            domain_kind == "thematic"
            and domain not in OFFICIAL_THEMATIC_DOMAINS
        ) or (
            domain_kind == "transversal"
            and domain not in OFFICIAL_TRANSVERSAL_DOMAINS
        ):
            domain_errors.append(display_id)

    cardinality_errors: list[str] = []
    if dict(counts) != EXPECTED_COUNTS:
        cardinality_errors.append(
            f"attendu {EXPECTED_COUNTS!r}, obtenu {dict(counts)!r}"
        )
    declared_counts: dict[tuple[str, str], int] = {}
    for declaration in programme.get("expected_cardinalities", []):
        if isinstance(declaration, dict):
            key = (declaration.get("type"), declaration.get("obligation_class"))
            value = declaration.get("count")
            if isinstance(key[0], str) and isinstance(key[1], str) and isinstance(value, int):
                declared_counts[key] = value
    if declared_counts != EXPECTED_COUNTS:
        cardinality_errors.append("cardinalités déclarées différentes de la fixture")

    experiment_errors = sorted(REQUIRED_EXPERIMENTS - by_id.keys())
    objective_boundary_errors = sorted(
        REQUIRED_OBJECTIVE_BOUNDARIES - by_id.keys()
    )
    if set(programme.get("thematic_domains", [])) != OFFICIAL_THEMATIC_DOMAINS:
        domain_errors.append("thematic_domains")
    if set(programme.get("transversal_domains", [])) != OFFICIAL_TRANSVERSAL_DOMAINS:
        domain_errors.append("transversal_domains")

    all_findings = (
        errors
        + schema_errors
        + duplicate_ids
        + orphan_quotes
        + unjustified_distributions
        + assignment_errors
        + obligation_errors
        + editorial_errors
        + domain_errors
        + cardinality_errors
        + experiment_errors
        + objective_boundary_errors
    )
    return {
        "status": "certified" if not all_findings else "needs_fix",
        "item_count": len(items),
        "source_sha256": source_hash,
        "text_sha256": text_hash,
        "counts_by_type_and_obligation": [
            {
                "type": item_type,
                "obligation_class": obligation,
                "count": count,
            }
            for (item_type, obligation), count in sorted(counts.items())
        ],
        "schema_errors": schema_errors,
        "duplicate_ids": duplicate_ids,
        "orphan_quotes": sorted(set(orphan_quotes)),
        "unjustified_distributions": sorted(
            set(unjustified_distributions)
        ),
        "assignment_errors": sorted(set(assignment_errors)),
        "obligation_errors": sorted(set(obligation_errors)),
        "editorial_errors": sorted(set(editorial_errors)),
        "domain_errors": sorted(set(domain_errors)),
        "cardinality_errors": cardinality_errors,
        "experiment_errors": experiment_errors,
        "objective_boundary_errors": objective_boundary_errors,
        "errors": errors,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--programme",
        type=Path,
        default=ROOT / "referentiel" / "programme_1SPE_2026.json",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=ROOT / "schemas" / "programme_1spe_2026.schema.json",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "sources" / "BO2026_1SPE_specialite.pdf",
    )
    parser.add_argument(
        "--text",
        type=Path,
        default=ROOT / "sources" / "txt" / "BO2026_1SPE_specialite.txt",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = check(
        args.programme.absolute(),
        args.schema.absolute(),
        args.source.absolute(),
        args.text.absolute(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "certified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
