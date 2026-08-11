#!/usr/bin/env python3
"""Check that Documents_DRIVE enrichment is traced, hashed and honest."""

from __future__ import annotations

from dataclasses import dataclass, field
import csv
import hashlib
import re
import sys
from pathlib import Path
from typing import Iterable

import yaml

from scripts._drive_paths import documents_drive_root, resolve_drive_reference
from scripts._qa_common import ROOT, read_frontmatter

INVENTORY = "drive_inventory.csv"
TRACE = "support_source_trace.yml"
REPORT = "reports/drive_enrichment_report.md"
AUTHORIZED_DECISIONS = {
    "integrated_adapted",
    "inspiration_only",
    "quarantined",
    "rejected_sensitive",
    "missing_local_copy",
    "deferred",
}
TRACE_REUSE_TYPES = {
    "adaptation_drive",
    "adaptation",
    "adapted_from_drive",
    "import_partiel",
    "inspiration_drive",
    "inspiration_only",
}
INTEGRATED_DECISIONS = {"integrated_adapted"}
LOCAL_DECISIONS = {"integrated_adapted", "inspiration_only", "quarantined", "deferred", "rejected_sensitive"}
MISSING_MARKERS = {"", "NA", "NA_REMOTE_NOT_DOWNLOADED", "missing_local_copy"}
SENSITIVE_NAME = re.compile(r"(notes?[_ -]?eleves?|fichier[_ -]?eleves?|rendus?[_ -]?eleves?|\.git|\.venv)", re.I)
DRIVE_MENTION = re.compile(r"(?:[A-Za-z0-9_./-]+/)?Documents_DRIVE/[^\s\"`)]+")


@dataclass
class DriveEnrichmentResult:
    errors: list[str] = field(default_factory=list)
    inventory_rows: int = 0
    integrated: int = 0
    inspiration: int = 0
    rejected: int = 0
    missing: int = 0
    deferred: int = 0
    quarantined: int = 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = child.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(child).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def read_inventory(root: Path) -> list[dict[str, str]]:
    path = root / INVENTORY
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def load_trace(root: Path) -> list[dict[str, str]]:
    path = root / TRACE
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = data.get("supports", []) if isinstance(data, dict) else []
    cleaned: list[dict[str, str]] = []
    for row in rows:
        if isinstance(row, dict):
            cleaned.append({str(key): "" if value is None else str(value).strip() for key, value in row.items()})
    return cleaned


def support_markdown_files(root: Path) -> Iterable[Path]:
    preferred_roots = [
        root / "03_progressions",
        root / "premiere",
        root / "terminale",
    ]
    if any(path.exists() for path in preferred_roots):
        for base in preferred_roots:
            if base.exists():
                yield from sorted(path for path in base.rglob("*.md") if path.is_file())
        return
    yield from sorted(path for path in root.rglob("*.md") if path.is_file() and "reports" not in path.parts)


def resolve_local(value: str, root: Path) -> Path | None:
    if value in MISSING_MARKERS:
        return None
    return resolve_drive_reference(value, root)


def support_status(root: Path, support: str) -> str:
    path = root / support
    if not path.exists():
        return ""
    if path.suffix == ".md":
        return str(read_frontmatter(path).get("status") or "")
    return "needs_review"


def report_errors(root: Path) -> list[str]:
    path = root / REPORT
    if not path.exists():
        return [f"{REPORT} absent"]
    text = path.read_text(encoding="utf-8", errors="replace")
    required_headers = [
        "Ressource Drive",
        "Existe localement",
        "Hash",
        "Décision",
        "Support enrichi",
        "Type de reprise",
        "RGPD",
        "Statut final",
    ]
    errors = [f"{REPORT}: colonne absente -> {header}" for header in required_headers if header not in text]
    lines = text.splitlines()
    table_start = next((index for index, line in enumerate(lines) if line.startswith("| Ressource Drive |")), -1)
    table_end = len(lines)
    if table_start >= 0:
        for index in range(table_start + 1, len(lines)):
            if lines[index].startswith("## "):
                table_end = index
                break
    data_lines = [
        line
        for line in lines[table_start:table_end]
        if line.startswith("|") and not re.match(r"^\|[-: ]+\|", line)
    ] if table_start >= 0 else []
    if len(data_lines) <= 1:
        errors.append(f"{REPORT}: aucun classement Drive détaillé")
    for line in data_lines[1:]:
        cells = [cell.strip(" `") for cell in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            continue
        decision = cells[3]
        if decision and decision not in AUTHORIZED_DECISIONS:
            errors.append(f"{REPORT}: décision non autorisée -> {decision}")
    return errors


def trace_by_source(rows: list[dict[str, str]], root: Path) -> dict[Path, list[dict[str, str]]]:
    result: dict[Path, list[dict[str, str]]] = {}
    for row in rows:
        source = row.get("source_locale_drive", "")
        path = resolve_local(source, root)
        if path is not None:
            result.setdefault(path.resolve(), []).append(row)
    return result


def drive_root_errors(root: Path) -> list[str]:
    drive_root = documents_drive_root(root)
    if not drive_root.exists():
        return [f"Documents_DRIVE absent -> {drive_root}"]
    if not any(path.is_file() for path in drive_root.rglob("*")):
        return [f"Documents_DRIVE vide -> {drive_root}"]
    return []


def analyze_drive_enrichment_traceability(root: Path = ROOT) -> DriveEnrichmentResult:
    result = DriveEnrichmentResult()
    result.errors.extend(drive_root_errors(root))
    inventory_path = root / INVENTORY
    trace_path = root / TRACE
    blocking_missing_inputs = False
    if not inventory_path.exists():
        result.errors.append(f"{INVENTORY} absent")
        blocking_missing_inputs = True
    if not trace_path.exists():
        result.errors.append(f"{TRACE} absent")
        blocking_missing_inputs = True
    if blocking_missing_inputs:
        return result

    inventory = read_inventory(root)
    trace_rows = load_trace(root)
    result.inventory_rows = len(inventory)
    source_trace = trace_by_source(trace_rows, root)

    for row in inventory:
        name = row.get("file_name", "")
        decision = row.get("decision", "")
        local_copy = row.get("local_copy", "")
        expected_hash = row.get("sha256", "")
        if decision not in AUTHORIZED_DECISIONS:
            result.errors.append(f"{name}: décision non autorisée -> {decision}")
            continue
        if decision == "integrated_adapted":
            result.integrated += 1
        elif decision == "inspiration_only":
            result.inspiration += 1
        elif decision == "rejected_sensitive":
            result.rejected += 1
        elif decision == "missing_local_copy":
            result.missing += 1
        elif decision == "deferred":
            result.deferred += 1
        elif decision == "quarantined":
            result.quarantined += 1

        if decision in INTEGRATED_DECISIONS and SENSITIVE_NAME.search(name):
            result.errors.append(f"{name}: ressource sensible marquée intégrable")

        local_path = resolve_local(local_copy, root)
        if decision in INTEGRATED_DECISIONS and local_path is None:
            result.errors.append(f"{name}: copie locale absente pour ressource intégrée")
            continue
        if local_path is not None:
            if not local_path.exists():
                result.errors.append(f"{name}: copie locale absente -> {local_copy}")
                continue
            if decision in LOCAL_DECISIONS and expected_hash in MISSING_MARKERS:
                result.errors.append(f"{name}: sha256 requis pour copie locale")
            elif expected_hash not in MISSING_MARKERS:
                actual_hash = sha256_path(local_path)
                if actual_hash != expected_hash:
                    result.errors.append(f"{name}: sha256 incohérent")
            if decision in INTEGRATED_DECISIONS and local_path.resolve() not in source_trace:
                result.errors.append(f"{name}: ressource intégrée sans trace support_source_trace.yml")
        elif decision in {"inspiration_only", "quarantined", "deferred", "rejected_sensitive"} and local_copy not in MISSING_MARKERS:
            result.errors.append(f"{name}: local_copy non résoluble -> {local_copy}")

    trace_by_support = {row.get("support", ""): row for row in trace_rows if row.get("support")}
    for row in trace_rows:
        support = row.get("support", "")
        source = row.get("source_locale_drive", "")
        reuse = row.get("type_reprise", "")
        if not source:
            continue
        source_path = resolve_local(source, root)
        if source_path is None or not source_path.exists():
            result.errors.append(f"{support}: source locale Drive absente -> {source}")
            continue
        if reuse not in TRACE_REUSE_TYPES:
            result.errors.append(f"{support}: type_reprise Drive non explicite -> {reuse}")
        if not row.get("statut_rgpd"):
            result.errors.append(f"{support}: statut_rgpd requis")
        if row.get("statut_relecture") != "needs_review":
            result.errors.append(f"{support}: statut_relecture doit rester needs_review")
        expected_hash = row.get("hash_source", "")
        if expected_hash in MISSING_MARKERS:
            result.errors.append(f"{support}: hash_source requis pour reprise depuis Drive")
        elif sha256_path(source_path) != expected_hash:
            result.errors.append(f"{support}: hash_source incohérent")
        if support:
            status = support_status(root, support)
            if status and status != "needs_review":
                result.errors.append(f"{support}: support enrichi doit rester needs_review")
            elif not status and not (root / support).exists():
                result.errors.append(f"{support}: support enrichi introuvable")

    for path in support_markdown_files(root):
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        mentions = DRIVE_MENTION.findall(text)
        if not mentions:
            continue
        trace = trace_by_support.get(rel) or trace_by_support.get(path.name)
        if trace is None:
            result.errors.append(f"{rel}: source Drive utilisée sans trace dans {TRACE}")
        elif not trace.get("source_locale_drive"):
            result.errors.append(f"{rel}: source Drive mentionnée sans source_locale_drive tracée")

    result.errors.extend(report_errors(root))
    return result


def main() -> int:
    result = analyze_drive_enrichment_traceability()
    if result.errors:
        print("check_drive_enrichment_traceability: KO")
        for error in result.errors[:200]:
            print(f"- {error}")
        return 1
    print(
        "check_drive_enrichment_traceability: PASS "
        f"({result.integrated} intégrées, {result.inspiration} inspiration, "
        f"{result.rejected} rejetées sensibles, {result.missing} absentes, "
        f"{result.deferred} différées, {result.quarantined} quarantaines)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
