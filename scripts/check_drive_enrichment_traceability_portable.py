#!/usr/bin/env python3
"""Portable Drive enrichment traceability check.

This check is designed for source archives that do not contain the raw
Documents_DRIVE mirror. It validates declarations and trace consistency, but it
does not dereference local Drive paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import csv
import re
import sys
from pathlib import Path

import yaml

from scripts._qa_common import ROOT, read_frontmatter
from scripts.check_drive_enrichment_traceability import (
    AUTHORIZED_DECISIONS,
    DRIVE_MENTION,
    INVENTORY,
    REPORT,
    SENSITIVE_NAME,
    TRACE,
    TRACE_REUSE_TYPES,
    support_markdown_files,
)

HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
MISSING_HASH = {"", "-", "NA", "NA_REMOTE_NOT_DOWNLOADED", "missing_local_copy"}
INTEGRATED_DECISIONS = {"integrated_adapted"}


@dataclass
class PortableDriveTraceabilityResult:
    errors: list[str] = field(default_factory=list)
    integrated: int = 0
    inspiration: int = 0
    rejected: int = 0
    missing: int = 0
    deferred: int = 0
    quarantined: int = 0


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
    return [
        {str(key): "" if value is None else str(value).strip() for key, value in row.items()}
        for row in rows
        if isinstance(row, dict)
    ]


def report_lines(root: Path) -> list[list[str]]:
    path = root / REPORT
    if not path.exists():
        return []
    lines: list[list[str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|") or re.match(r"^\|[-: ]+\|", line):
            continue
        cells = [cell.strip(" `") for cell in line.strip().strip("|").split("|")]
        lines.append(cells)
    return lines


def support_status(root: Path, support: str) -> str:
    path = root / support
    if not path.exists() or path.suffix != ".md":
        return "needs_review" if path.exists() else ""
    return str(read_frontmatter(path).get("status") or read_frontmatter(path).get("statut") or "needs_review")


def analyze_drive_enrichment_traceability_portable(root: Path = ROOT) -> PortableDriveTraceabilityResult:
    result = PortableDriveTraceabilityResult()
    for required in [INVENTORY, TRACE, REPORT]:
        if not (root / required).exists():
            result.errors.append(f"{required} absent")
    if result.errors:
        return result

    inventory = read_inventory(root)
    trace_rows = load_trace(root)
    trace_by_support = {row.get("support", ""): row for row in trace_rows if row.get("support")}
    traced_sources = {row.get("source_locale_drive", "") for row in trace_rows if row.get("source_locale_drive")}

    for row in inventory:
        name = row.get("file_name", "")
        decision = row.get("decision", "")
        digest = row.get("sha256", "")
        local_copy = row.get("local_copy", "")
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
            result.errors.append(f"{name}: ressource sensible marquée intégrée")
        if decision in {"integrated_adapted", "inspiration_only", "deferred", "rejected_sensitive"}:
            if digest in MISSING_HASH:
                if decision in {"integrated_adapted", "inspiration_only", "deferred"}:
                    result.errors.append(f"{name}: hash SHA-256 requis pour décision {decision}")
            elif not HEX_SHA256.match(digest):
                result.errors.append(f"{name}: hash SHA-256 mal formé")
        if decision == "integrated_adapted" and local_copy not in traced_sources:
            result.errors.append(f"{name}: ressource intégrée sans source_locale_drive tracée")

    for row in trace_rows:
        support = row.get("support", "")
        source = row.get("source_locale_drive", "")
        reuse = row.get("type_reprise", "")
        if not source:
            continue
        if reuse not in TRACE_REUSE_TYPES:
            result.errors.append(f"{support}: type_reprise Drive non explicite -> {reuse}")
        digest = row.get("hash_source", "")
        if digest in MISSING_HASH or not HEX_SHA256.match(digest):
            result.errors.append(f"{support}: hash_source SHA-256 requis")
        if not row.get("statut_rgpd"):
            result.errors.append(f"{support}: statut_rgpd requis")
        if row.get("statut_relecture") != "needs_review":
            result.errors.append(f"{support}: statut_relecture doit rester needs_review")
        status = support_status(root, support)
        if status and status != "needs_review":
            result.errors.append(f"{support}: support enrichi doit rester needs_review")
        elif not status:
            result.errors.append(f"{support}: support enrichi introuvable")

    rows = report_lines(root)
    if not rows:
        result.errors.append(f"{REPORT}: tableau absent")
    else:
        header = rows[0]
        for expected in ["Ressource Drive", "Hash", "Décision", "Support enrichi", "RGPD", "Statut final"]:
            if expected not in header:
                result.errors.append(f"{REPORT}: colonne absente -> {expected}")
        for cells in rows[1:]:
            if len(cells) < 9:
                continue
            decision = cells[3]
            digest = cells[2]
            status = cells[7]
            if decision not in AUTHORIZED_DECISIONS:
                result.errors.append(f"{REPORT}: décision non autorisée -> {decision}")
            if decision in {"integrated_adapted", "inspiration_only", "deferred", "rejected_sensitive"}:
                if digest not in MISSING_HASH and not HEX_SHA256.match(digest):
                    result.errors.append(f"{REPORT}: hash mal formé pour {cells[0]}")
            if status != "needs_review":
                result.errors.append(f"{REPORT}: statut final doit rester needs_review pour {cells[0]}")

    for path in support_markdown_files(root):
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if DRIVE_MENTION.findall(text):
            trace = trace_by_support.get(rel) or trace_by_support.get(path.name)
            if trace is None or not trace.get("source_locale_drive"):
                result.errors.append(f"{rel}: source Drive mentionnée sans trace")
    return result


def main() -> int:
    result = analyze_drive_enrichment_traceability_portable()
    if result.errors:
        print("check_drive_enrichment_traceability_portable: KO")
        for error in result.errors[:200]:
            print(f"- {error}")
        return 1
    print(
        "check_drive_enrichment_traceability_portable: PASS "
        f"({result.integrated} intégrées, {result.inspiration} inspiration, "
        f"{result.rejected} rejetées sensibles, {result.missing} absentes, "
        f"{result.deferred} différées, {result.quarantined} quarantaines)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
