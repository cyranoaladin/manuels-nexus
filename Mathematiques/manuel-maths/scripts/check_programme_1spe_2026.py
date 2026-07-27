#!/usr/bin/env python3
"""Contrôler le référentiel canonique du programme 1SPE 2026."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if os.fspath(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, os.fspath(SCRIPT_DIRECTORY))

from extract_official_source import (
    ExtractionError,
    load_source_entry,
    open_registered_source,
    resolve_pdftotext,
    run_pdftotext,
    snapshot_source,
)


ROOT = Path(__file__).resolve().parents[1]
APPROVED_PROGRAMME_SHA256 = (
    "79357aebc60c2c53d82c62760175c97bfb8069c82b3300c52e3fe438b8faf91a"
)
APPROVED_SCHEMA_SHA256 = (
    "61e3c2c4a7093c5c38af1d6c3fd2a791804d9d2980e616c860dc7a36242e1140"
)
APPROVED_COMPLIANCE_SHA256 = (
    "66ba2770e23cd8fe1f1c5bd44a6cfff5190af54e5a5e6b7a93995fc963e00c8a"
)
APPROVED_ATTESTATION_SHA256 = (
    "4d8b6bbc670c3387dd9684f26e294f4079317c645ec9277a259cedd28ba5a071"
)
EXPECTED_PDF_SHA256 = (
    "5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08"
)
EXPECTED_COUNTS = {
    ("contenu", "mandatory_content"): 42,
    ("contenu", "contextual_guidance"): 5,
    ("capacite", "mandatory_content"): 44,
    ("demonstration", "prescribed_teaching"): 11,
    ("algorithme", "mandatory_content"): 4,
    ("algorithme", "prescribed_teaching"): 11,
    ("approfondissement", "optional_extension"): 17,
    ("transversal", "mandatory_content"): 8,
    ("transversal", "prescribed_teaching"): 29,
    ("transversal", "contextual_guidance"): 4,
}
EXPECTED_OBJECTIVE_COVERAGE = {
    "OBJ-COV-SUITES-TAUX-FIXE": {
        "covered_by_item_ids": {"ALG-SUI-CONT-004", "ALG-SUI-CAP-005"},
        "assigned_chapters": {"1SPE-SUITES"},
        "coverage_kind": "required_learning_outcome",
    },
    "OBJ-COV-SD-COMPLETION-CARRE": {
        "covered_by_item_ids": {"ALG-SD-CONT-002"},
        "assigned_chapters": {"1SPE-SECOND-DEGRE"},
        "coverage_kind": "required_learning_outcome",
    },
    "OBJ-COV-SD-FACTORISATION-DIRECTE": {
        "covered_by_item_ids": {"ALG-SD-CAP-003"},
        "assigned_chapters": {"1SPE-SECOND-DEGRE"},
        "coverage_kind": "required_learning_outcome",
    },
    "OBJ-COV-DERIVEE-GRAPHIQUE": {
        "covered_by_item_ids": {
            "ANA-DERLOC-CONT-001",
            "ANA-DERLOC-CONT-003",
        },
        "assigned_chapters": {"1SPE-DERIVATION-LOCAL"},
        "coverage_kind": "required_introduction_modality",
    },
    "OBJ-COV-DERIVEE-ALGEBRIQUE": {
        "covered_by_item_ids": {"ANA-DERLOC-CAP-001"},
        "assigned_chapters": {"1SPE-DERIVATION-LOCAL"},
        "coverage_kind": "required_introduction_modality",
    },
    "OBJ-COV-DERIVEE-NUMERIQUE": {
        "covered_by_item_ids": {
            "ANA-DERLOC-CONT-004",
            "ANA-DERLOC-CAP-005",
        },
        "assigned_chapters": {"1SPE-DERIVATION-LOCAL"},
        "coverage_kind": "required_introduction_modality",
    },
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
SECTION_HEADINGS = {
    "Vocabulaire ensembliste et logique",
    "Algorithmique et programmation",
    "Objectifs",
    "Histoire des mathématiques",
    "Notion de liste",
    "Automatismes",
    "Algèbre",
    "Analyse",
    "Géométrie",
    "Probabilités et statistiques",
    "Contenus",
    "Capacités attendues",
    "Démonstration",
    "Démonstrations",
    "Exemples d’algorithme",
    "Exemples d’algorithmes",
    "Exemple d’algorithme",
    "Approfondissements possibles",
    "Expérimentations",
    "Variables aléatoires réelles",
}
CANONICAL_PATHS = {
    "programme": ROOT / "referentiel" / "programme_1SPE_2026.json",
    "schema": ROOT / "schemas" / "programme_1spe_2026.schema.json",
    "source": ROOT / "sources" / "BO2026_1SPE_specialite.pdf",
    "text": ROOT / "sources" / "txt" / "BO2026_1SPE_specialite.txt",
    "attestation": (
        ROOT
        / "validations"
        / "release-1spe"
        / "programme-1spe-2026.attestation.json"
    ),
    "attestation_schema": (
        ROOT / "schemas" / "programme_1spe_2026.attestation.schema.json"
    ),
    "review": ROOT / "validations" / "release-1spe" / "revue-programme.md",
    "registry": ROOT / "sources" / "registry.yaml",
    "compliance": ROOT / "referentiel" / "CONFORMITE_BO2026.md",
}
APPROVED_ASSETS = {
    "programme": (CANONICAL_PATHS["programme"], APPROVED_PROGRAMME_SHA256),
    "schema": (CANONICAL_PATHS["schema"], APPROVED_SCHEMA_SHA256),
    "compliance": (CANONICAL_PATHS["compliance"], APPROVED_COMPLIANCE_SHA256),
    "attestation": (
        CANONICAL_PATHS["attestation"],
        APPROVED_ATTESTATION_SHA256,
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def same_canonical_path(candidate: Path, canonical: Path) -> bool:
    return lexical_absolute(candidate) == lexical_absolute(canonical)


def approved_asset_errors() -> list[str]:
    findings: list[str] = []
    for name, (path, expected_hash) in APPROVED_ASSETS.items():
        try:
            actual_hash = sha256(path)
        except OSError as exc:
            findings.append(f"{name}: actif approuvé inaccessible : {exc}")
            continue
        if actual_hash != expected_hash:
            findings.append(
                f"{name}: SHA-256 approuvé {expected_hash}, obtenu {actual_hash}"
            )
    return findings


def unique_review_value(
    review_text: str,
    label_pattern: str,
) -> str | None:
    matches = re.findall(
        rf"{label_pattern}\s*:\s*`([0-9a-f]{{64}})`",
        review_text,
    )
    return matches[0] if len(matches) == 1 else None


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def citation_index(
    text: str,
) -> tuple[list[str], list[int], list[tuple[int, str]]]:
    raw_pages = text.split("\f")
    if raw_pages and not raw_pages[-1].strip():
        raw_pages.pop()
    pages = [normalize_whitespace(page) for page in raw_pages]
    page_bases: list[int] = []
    section_positions: list[tuple[int, str]] = []
    base = 0
    for raw_page, page in zip(raw_pages, pages):
        page_bases.append(base)
        for match in re.finditer(r"(?m)^([^\r\n]+?)\s*$", raw_page):
            heading = match.group(1).strip()
            if heading not in SECTION_HEADINGS:
                continue
            prefix = normalize_whitespace(raw_page[: match.start()])
            local_offset = len(prefix) + (1 if prefix else 0)
            section_positions.append((base + local_offset, heading))
        base += len(page) + 1
    return pages, page_bases, section_positions


def quote_offsets(page: str, quote: str) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        position = page.find(quote, start)
        if position < 0:
            return offsets
        offsets.append(position)
        start = position + 1


def has_valid_citation_anchor(
    record: dict[str, Any],
    pages: list[str],
    page_bases: list[int],
    section_positions: list[tuple[int, str]],
) -> bool:
    page_number = record.get("bo_page")
    quote = record.get("bo_quote")
    occurrence = record.get("bo_occurrence")
    expected_offset = record.get("bo_offset")
    expected_section = record.get("bo_section")
    if (
        not isinstance(page_number, int)
        or not isinstance(quote, str)
        or not normalize_whitespace(quote)
        or not isinstance(occurrence, int)
        or occurrence < 1
        or not isinstance(expected_offset, int)
        or expected_offset < 0
        or not isinstance(expected_section, str)
        or not normalize_whitespace(expected_section)
        or not (1 <= page_number <= len(pages))
    ):
        return False
    offsets = quote_offsets(
        pages[page_number - 1],
        normalize_whitespace(quote),
    )
    if occurrence > len(offsets):
        return False
    actual_offset = offsets[occurrence - 1]
    if expected_offset != actual_offset:
        return False
    absolute_offset = page_bases[page_number - 1] + actual_offset
    preceding_sections = [
        section
        for position, section in section_positions
        if position <= absolute_offset
    ]
    return bool(preceding_sections) and preceding_sections[-1] == expected_section


def extract_pdf_text(source: Path, registry: Path) -> bytes:
    entry = load_source_entry(registry)
    opened_source = open_registered_source(source, entry)
    try:
        executable = resolve_pdftotext()
        with tempfile.TemporaryDirectory(
            prefix="nexus-bo2026-check-"
        ) as raw_directory:
            snapshot = snapshot_source(opened_source, Path(raw_directory))
            return run_pdftotext(executable, snapshot)
    finally:
        os.close(opened_source.descriptor)


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
    attestation_path: Path,
    attestation_schema_path: Path,
    review_path: Path,
    registry_path: Path,
    compliance_path: Path,
) -> dict[str, Any]:
    supplied_paths = {
        "programme": programme_path,
        "schema": schema_path,
        "source": source_path,
        "text": text_path,
        "attestation": attestation_path,
        "attestation_schema": attestation_schema_path,
        "review": review_path,
        "registry": registry_path,
        "compliance": compliance_path,
    }
    noncanonical_inputs = sorted(
        name
        for name, path in supplied_paths.items()
        if not same_canonical_path(path, CANONICAL_PATHS[name])
    )
    approval_errors = approved_asset_errors()
    errors: list[str] = []
    schema_errors: list[str] = []
    duplicate_ids: list[str] = []
    orphan_quotes: list[str] = []
    unjustified_distributions: list[str] = []
    assignment_errors: list[str] = []
    obligation_errors: list[str] = []
    editorial_errors: list[str] = []
    domain_errors: list[str] = []
    objective_coverage_errors: list[str] = []
    attestation_errors: list[str] = []
    review_errors: list[str] = []

    try:
        programme = load_json(programme_path)
        schema = load_json(schema_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return {
            "status": (
                "review_required"
                if noncanonical_inputs or approval_errors
                else "needs_fix"
            ),
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
            "objective_coverage_errors": [],
            "attestation_errors": [],
            "review_errors": [],
            "noncanonical_inputs": noncanonical_inputs,
            "approved_asset_errors": approval_errors,
            "errors": ["référentiel ou schéma illisible"],
        }

    try:
        Draft202012Validator.check_schema(schema)
        schema_errors = sorted(
            compact_schema_error(error)
            for error in Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            ).iter_errors(programme)
        )
    except Exception as exc:
        schema_errors = [f"schéma invalide : {exc}"]

    try:
        programme_hash = sha256(programme_path)
        schema_hash = sha256(schema_path)
    except OSError as exc:
        programme_hash = None
        schema_hash = None
        attestation_errors.append(f"empreinte programme/schéma inaccessible : {exc}")

    try:
        attestation = load_json(attestation_path)
        attestation_hash = sha256(attestation_path)
        attestation_schema = load_json(attestation_schema_path)
        Draft202012Validator.check_schema(attestation_schema)
        attestation_schema_errors = sorted(
            compact_schema_error(error)
            for error in Draft202012Validator(attestation_schema).iter_errors(
                attestation
            )
        )
        attestation_errors.extend(
            f"schéma attestation : {error}" for error in attestation_schema_errors
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        attestation = {}
        attestation_hash = None
        attestation_errors.append(f"attestation illisible : {exc}")
    except Exception as exc:
        attestation = {}
        attestation_hash = None
        attestation_errors.append(f"schéma attestation invalide : {exc}")

    try:
        registry_hash = sha256(registry_path)
    except OSError as exc:
        registry_hash = None
        attestation_errors.append(f"registre inaccessible : {exc}")
    try:
        compliance_hash = sha256(compliance_path)
    except OSError as exc:
        compliance_hash = None
        attestation_errors.append(f"document de conformité inaccessible : {exc}")

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
            regenerated = extract_pdf_text(source_path, registry_path)
        except (ExtractionError, UnicodeError, OSError) as exc:
            errors.append(f"recoupement PDF/TXT impossible : {exc}")
        else:
            if regenerated != text_bytes:
                errors.append("le TXT n’est pas l’extraction déterministe du PDF")

    pages, page_bases, section_positions = citation_index(text_value)
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

        if not has_valid_citation_anchor(
            raw_item,
            pages,
            page_bases,
            section_positions,
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
        if item_type == "capacite" and obligation != "mandatory_content":
            obligation_errors.append(display_id)
        if (
            item_type == "algorithme"
            and item_id not in REQUIRED_EXPERIMENTS
            and obligation != "prescribed_teaching"
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
    raw_coverage = programme.get("objective_coverage")
    coverage = raw_coverage if isinstance(raw_coverage, list) else []
    seen_coverage_ids: set[str] = set()
    for position, raw_entry in enumerate(coverage):
        if not isinstance(raw_entry, dict):
            objective_coverage_errors.append(f"index-{position}")
            continue
        coverage_id = raw_entry.get("id")
        display_id = (
            coverage_id if isinstance(coverage_id, str) else f"index-{position}"
        )
        if not isinstance(coverage_id, str) or coverage_id in seen_coverage_ids:
            objective_coverage_errors.append(display_id)
            continue
        seen_coverage_ids.add(coverage_id)
        expected = EXPECTED_OBJECTIVE_COVERAGE.get(coverage_id)
        covered_ids = raw_entry.get("covered_by_item_ids")
        assigned_chapters = raw_entry.get("assigned_chapters")
        expected_ids = (
            expected.get("covered_by_item_ids")
            if isinstance(expected, dict)
            else None
        )
        expected_chapters = (
            expected.get("assigned_chapters")
            if isinstance(expected, dict)
            else None
        )
        if (
            not isinstance(expected_ids, set)
            or not isinstance(expected_chapters, set)
            or not isinstance(covered_ids, list)
            or set(covered_ids) != expected_ids
            or not expected_ids <= by_id.keys()
            or not isinstance(assigned_chapters, list)
            or set(assigned_chapters) != expected_chapters
            or raw_entry.get("coverage_kind") != expected.get("coverage_kind")
            or raw_entry.get("release_gate") is not True
            or any(
                not (
                    set(by_id[item_id].get("assigned_chapters", []))
                    & expected_chapters
                )
                for item_id in expected_ids
            )
            or raw_entry.get("bo_section") != "Objectifs"
            or not has_valid_citation_anchor(
                raw_entry,
                pages,
                page_bases,
                section_positions,
            )
        ):
            objective_coverage_errors.append(display_id)
    if seen_coverage_ids != EXPECTED_OBJECTIVE_COVERAGE.keys():
        objective_coverage_errors.append("objective_coverage")
    if set(programme.get("thematic_domains", [])) != OFFICIAL_THEMATIC_DOMAINS:
        domain_errors.append("thematic_domains")
    if set(programme.get("transversal_domains", [])) != OFFICIAL_TRANSVERSAL_DOMAINS:
        domain_errors.append("transversal_domains")

    expected_attestation = {
        "attestation_version": 1,
        "programme_path": "referentiel/programme_1SPE_2026.json",
        "programme_sha256": programme_hash,
        "schema_path": "schemas/programme_1spe_2026.schema.json",
        "schema_sha256": schema_hash,
        "source_pdf_path": "sources/BO2026_1SPE_specialite.pdf",
        "source_pdf_sha256": source_hash,
        "source_text_path": "sources/txt/BO2026_1SPE_specialite.txt",
        "source_text_sha256": text_hash,
        "registry_path": "sources/registry.yaml",
        "registry_sha256": registry_hash,
        "compliance_path": "referentiel/CONFORMITE_BO2026.md",
        "compliance_sha256": compliance_hash,
        "review_report_path": "validations/release-1spe/revue-programme.md",
        "required_review_status": "approved",
        "item_count": len(items),
        "item_ids_sha256": canonical_sha256(identifiers),
        "matrix_sha256": canonical_sha256(
            programme.get("expected_cardinalities")
        ),
    }
    for field, expected_value in expected_attestation.items():
        if attestation.get(field) != expected_value:
            attestation_errors.append(field)

    try:
        review_text = review_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        review_errors.append(f"rapport de revue illisible : {exc}")
    else:
        status_matches = re.findall(
            r"(?m)^Statut\s*:\s*`([^`]+)`\s*$",
            review_text,
        )
        if status_matches != ["approved"]:
            review_errors.append("statut de revue non approuvé")
        reviewed_assets = {
            "référentiel": (
                unique_review_value(
                    review_text,
                    r"SHA-256 du référentiel revu",
                ),
                programme_hash,
                APPROVED_PROGRAMME_SHA256,
            ),
            "schéma": (
                unique_review_value(
                    review_text,
                    r"SHA-256 du schéma revu",
                ),
                schema_hash,
                APPROVED_SCHEMA_SHA256,
            ),
            "documentation": (
                unique_review_value(
                    review_text,
                    r"SHA-256 de la documentation revue",
                ),
                compliance_hash,
                APPROVED_COMPLIANCE_SHA256,
            ),
            "attestation": (
                unique_review_value(
                    review_text,
                    r"SHA-256 de l[’']attestation revue",
                ),
                attestation_hash,
                APPROVED_ATTESTATION_SHA256,
            ),
        }
        for name, (reviewed_hash, active_hash, approved_hash) in reviewed_assets.items():
            if reviewed_hash is None:
                review_errors.append(
                    f"empreinte de revue absente ou ambiguë pour {name}"
                )
            elif reviewed_hash != active_hash or reviewed_hash != approved_hash:
                review_errors.append(
                    f"rapport de revue périmé pour {name}"
                )

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
        + objective_coverage_errors
        + attestation_errors
        + review_errors
        + approval_errors
    )
    if noncanonical_inputs or approval_errors:
        status = "review_required"
    elif attestation_errors == ["compliance_sha256"]:
        status = "review_required"
    elif attestation_errors:
        status = "stale"
    elif review_errors:
        status = "review_required"
    elif all_findings:
        status = "needs_fix"
    else:
        status = "certified"
    return {
        "status": status,
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
        "objective_coverage_errors": sorted(set(objective_coverage_errors)),
        "attestation_errors": sorted(set(attestation_errors)),
        "review_errors": sorted(set(review_errors)),
        "noncanonical_inputs": noncanonical_inputs,
        "approved_asset_errors": approval_errors,
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
    parser.add_argument(
        "--attestation",
        type=Path,
        default=(
            ROOT
            / "validations"
            / "release-1spe"
            / "programme-1spe-2026.attestation.json"
        ),
    )
    parser.add_argument(
        "--attestation-schema",
        type=Path,
        default=ROOT / "schemas" / "programme_1spe_2026.attestation.schema.json",
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=ROOT / "validations" / "release-1spe" / "revue-programme.md",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=ROOT / "sources" / "registry.yaml",
    )
    parser.add_argument(
        "--compliance",
        type=Path,
        default=ROOT / "referentiel" / "CONFORMITE_BO2026.md",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = check(
        args.programme.absolute(),
        args.schema.absolute(),
        args.source.absolute(),
        args.text.absolute(),
        args.attestation.absolute(),
        args.attestation_schema.absolute(),
        args.review.absolute(),
        args.registry.absolute(),
        args.compliance.absolute(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "certified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
