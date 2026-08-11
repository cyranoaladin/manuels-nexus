#!/usr/bin/env python3
"""Shared helpers for NSI corpus QA scripts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List
import json
import re
import sys
import unicodedata

import yaml

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
PROGRAM_FILE = ROOT / "00_programmes_officiels" / "programme_nsi_2019.yaml"
PILOT_SCOPE_FILE = ROOT / "pilot_scope.yml"
FULL_SEQUENCE_SCOPE = {
    "premiere": [f"P{index:02d}" for index in range(15)],
    "terminale": [f"T{index:02d}" for index in range(20)],
}
FULL_SEQUENCE_CURRENT_LOT = {
    "premiere": [f"P{index:02d}" for index in range(6, 10)],
    "terminale": [f"T{index:02d}" for index in range(6, 10)],
}

# Scope pilote documenté : ces deux séquences servent aux contrôles historiques
# de complétude de séquence. Les contrôles opérationnels doivent découvrir leur
# périmètre depuis les fiches/readiness, pas depuis une liste locale de préfixes.
TARGET_SEQUENCES = {
    "premiere": ROOT / "premiere" / "sequences" / "s01_representation_donnees",
    "terminale": ROOT / "terminale" / "sequences" / "s01_structures_donnees_interfaces_implementations",
}

REQUIRED_SEQUENCE_FILES = {
    "sequence.yaml",
    "cours_eleve.md",
    "trace_ecrite.md",
    "td.md",
    "tp.md",
    "fiche_methode.md",
    "aides_progressives.md",
    "corrige.md",
    "guide_professeur.md",
    "evaluation.md",
    "projet_associe.md",
    "qcm.json",
    "sources.md",
}

REQUIRED_EVIDENCE = {"cours", "trace", "td", "tp", "evaluation", "corrige"}
VALID_STATUSES = {
    "draft",
    "needs_content",
    "needs_review",
    "validated_pedagogy",
    "validated_science",
    "validated_technical",
    "published",
    "archived",
    "deprecated",
}
VALIDATED_STATUSES = {
    "validated_pedagogy",
    "validated_science",
    "validated_technical",
    "published",
}

DOC_TYPES = {
    "cours_eleve.md": "cours",
    "trace_ecrite.md": "trace",
    "td.md": "td",
    "tp.md": "tp",
    "fiche_methode.md": "fiche_methode",
    "aides_progressives.md": "aides",
    "corrige.md": "corrige",
    "guide_professeur.md": "guide_prof",
    "evaluation.md": "evaluation",
    "projet_associe.md": "projet",
    "qcm.json": "qcm",
}


@dataclass
class Evidence:
    capacity_id: str
    label: str
    file: str
    anchor: str
    evidence_type: str
    document_path: Path
    status: str


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def sequence_id_from_path(path: Path) -> str:
    match = re.match(r"([PT]\d{2})[_-]", path.name)
    return match.group(1) if match else ""


def load_pilot_scope(root: Path = ROOT) -> Dict[str, List[str]]:
    path = root / "pilot_scope.yml"
    if not path.exists():
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    result: Dict[str, List[str]] = {}
    for key, value in payload.items():
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            result[key] = list(value)
    return result


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    match = re.search(r"^---\s*\n.*?\n---\s*\n?", text, re.S)
    if not match:
        return text
    return text[match.end():]


def read_frontmatter(path: Path) -> Dict[str, Any]:
    if path.suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        metadata = payload.get("metadata", {})
        return metadata if isinstance(metadata, dict) else {}

    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    match = re.search(r"^---\s*\n(.*?)\n---\s*", text, re.S)
    if not match:
        return {}
    try:
        loaded = yaml.safe_load(match.group(1)) or {}
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def get_status(metadata: Dict[str, Any]) -> str:
    status = str(metadata.get("status") or metadata.get("statut") or "").strip()
    return status if status in VALID_STATUSES else "needs_review"


def sequence_files() -> Iterable[Path]:
    for seq in TARGET_SEQUENCES.values():
        if not seq.exists():
            continue
        for path in sorted(seq.rglob("*")):
            if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".yml", ".py"}:
                yield path


def pedagogical_documents() -> Iterable[Path]:
    for path in sequence_files():
        if path.name == "quality_audit_s01.md":
            continue
        if path.suffix in {".md", ".json"} and path.name in DOC_TYPES:
            yield path


def load_program_entries() -> Dict[str, Dict[str, Any]]:
    data = yaml.safe_load(PROGRAM_FILE.read_text(encoding="utf-8")) or {}
    entries: Dict[str, Dict[str, Any]] = {}
    for level, rows in (data.get("programmes") or {}).items():
        for row in rows or []:
            if isinstance(row, dict) and row.get("id"):
                entry = dict(row)
                entry["level"] = level
                entries[str(row["id"])] = entry
    return entries


def iter_declared_evidence() -> Iterable[Evidence]:
    for path in pedagogical_documents():
        metadata = read_frontmatter(path)
        status = get_status(metadata)
        official = metadata.get("official_program") or {}
        capacities = official.get("capacities") if isinstance(official, dict) else []
        if not isinstance(capacities, list):
            continue
        for capacity in capacities:
            if not isinstance(capacity, dict):
                continue
            capacity_id = str(capacity.get("id") or "").strip()
            if not capacity_id:
                continue
            label = str(capacity.get("label") or "")
            evidence_list = capacity.get("evidence") or []
            if not isinstance(evidence_list, list):
                continue
            for item in evidence_list:
                if not isinstance(item, dict):
                    continue
                file_value = str(item.get("file") or path.relative_to(ROOT).as_posix())
                evidence_type = str(item.get("type") or DOC_TYPES.get(path.name, "")).strip()
                yield Evidence(
                    capacity_id=capacity_id,
                    label=label,
                    file=file_value,
                    anchor=str(item.get("anchor") or ""),
                    evidence_type=evidence_type,
                    document_path=path,
                    status=status,
                )


def useful_lines(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_frontmatter(text)
    return [line.rstrip() for line in body.splitlines() if line.strip()]


def print_result(name: str, errors: List[str]) -> None:
    if errors:
        print(f"{name}: KO")
        for item in errors:
            print(f"- {item}")
        raise SystemExit(1)
    print(f"{name}: PASS")


SUPPORTS_DIR = ROOT / "03_progressions" / "supports"


def iter_sequence_md_files(prefix: str, root: Path = ROOT) -> List[Path]:
    """Enumerate ALL .md files belonging to a sequence prefix.

    Uses rglob (recursive) — the same primitive as the coverage engine
    (_supports_evidence.iter_support_evidence) so that both tools see
    exactly the same files by construction, including sub-directories.
    """
    level = "premiere" if prefix.startswith("P") else "terminale"
    seq_dir = root / "03_progressions" / "supports" / level / prefix
    # Fallback for test fixtures that use a flat root/{prefix}/ layout
    if not seq_dir.is_dir():
        seq_dir = root / prefix
    if not seq_dir.is_dir():
        return []
    return sorted(
        p for p in seq_dir.rglob("*.md")
        if "contracts" not in p.parts
    )
