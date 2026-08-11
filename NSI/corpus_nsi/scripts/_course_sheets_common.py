#!/usr/bin/env python3
"""Shared helpers for course sheet QA checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from scripts._qa_common import ROOT, load_program_entries, read_frontmatter, strip_frontmatter

__all__ = ["read_frontmatter"]

SHEETS_ROOT = ROOT / "03_progressions" / "fiches_cours"
PROGRESSION_FILES = {
    "premiere": ROOT / "03_progressions" / "progression_premiere.md",
    "terminale": ROOT / "03_progressions" / "progression_terminale.md",
}
CAPACITY_RE = re.compile(r"\b[PT]-[A-Z]+(?:-[A-Z]+)*-\d{2}[A-Z]?\b")
SEQUENCE_RE = re.compile(r"\b([PT]\d{2})\b")
SHEET_NAME_RE = re.compile(r"^([PT]\d{2})_fiche_cours_[a-z0-9_]+\.md$")

REQUIRED_SECTIONS = [
    "À savoir",
    "Méthodes",
    "Exemples corrigés",
    "Erreurs fréquentes",
    "Cas limites",
    "Mini-exercices",
    "Réponses rapides",
    "À retenir",
    "Lien avec la progression",
    "Auto-évaluation",
]

REQUIRED_FRONTMATTER = [
    "title",
    "level",
    "sequence_id",
    "document_type",
    "status",
    "version",
    "source",
    "source_creation",
    "theme",
    "notion",
    "official_program",
    "private_data",
    "readiness",
]

VALID_READINESS = {"theoretical", "linked", "operational"}
THEORETICAL_LINK_STATUSES = {"théorique", "theorique", "theoretical", "non prévu", "non prevu"}
REGISTERED_LINK_STATUSES = {"à créer", "a creer", "absent", "inscrit au registre", "registre"}
EXISTING_LINK_STATUSES = {"existant", "prêt", "prete", "prête", "operational", "opérationnel"}

DENSE_MIN_SHEETS = {
    "P01": 2,
    "P02": 2,
    "P03": 2,
    "P04": 3,
    "P08": 2,
    "T03": 3,
    "T10": 2,
}


@dataclass
class SequencePlan:
    sequence_id: str
    level: str
    capacities: set[str]


@dataclass(frozen=True)
class CourseSheetLink:
    element: str
    file: str
    status: str
    remark: str

    @property
    def normalized_status(self) -> str:
        return normalize_status_text(self.status)

    @property
    def is_session(self) -> bool:
        return self.element.lower().startswith("séance") or self.element.lower().startswith("seance")

    @property
    def is_resource(self) -> bool:
        return not self.is_session and self.file not in {"", "NA", "na", "-"}


def normalize(text: str) -> str:
    text = re.sub(r"`[^`]+`", "`code`", text.lower())
    text = re.sub(r"\b\d+\b", "n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_status_text(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a")
    text = re.sub(r"\s+", " ", text)
    return text


def useful_lines(text: str) -> list[str]:
    body = strip_frontmatter(text)
    return [line.strip() for line in body.splitlines() if line.strip()]


def extract_capacities(text: str) -> set[str]:
    return set(CAPACITY_RE.findall(text))


def frontmatter_capacities(metadata: dict[str, Any]) -> set[str]:
    official = metadata.get("official_program")
    if not isinstance(official, dict):
        return set()
    raw = official.get("capacities")
    if not isinstance(raw, list):
        return set()
    capacities: set[str] = set()
    for item in raw:
        if isinstance(item, str):
            capacities.add(item)
        elif isinstance(item, dict) and item.get("id"):
            capacities.add(str(item["id"]))
    return capacities


def level_for_sequence(sequence_id: str) -> str:
    return "premiere" if sequence_id.startswith("P") else "terminale"


def parse_progression_table(path: Path, level: str) -> dict[str, SequencePlan]:
    plans: dict[str, SequencePlan] = {}
    if not path.exists():
        return plans
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        seq_match = SEQUENCE_RE.search(cells[0])
        if not seq_match:
            continue
        sequence_id = seq_match.group(1)
        capacities = extract_capacities(cells[4])
        if sequence_id not in plans:
            plans[sequence_id] = SequencePlan(sequence_id, level, set())
        plans[sequence_id].capacities.update(capacities)
    return plans


def planned_sequences(root: Path = ROOT) -> dict[str, SequencePlan]:
    progressions = {
        "premiere": root / "03_progressions" / "progression_premiere.md",
        "terminale": root / "03_progressions" / "progression_terminale.md",
    }
    plans: dict[str, SequencePlan] = {}
    for level, path in progressions.items():
        plans.update(parse_progression_table(path, level))
    return dict(sorted(plans.items()))


def sheet_files(root: Path = ROOT) -> list[Path]:
    base = root / "03_progressions" / "fiches_cours"
    if not base.exists():
        return []
    return sorted(path for path in base.rglob("*.md") if path.is_file())


def sheets_by_sequence(root: Path = ROOT) -> dict[str, list[Path]]:
    by_sequence: dict[str, list[Path]] = {}
    for path in sheet_files(root):
        match = SHEET_NAME_RE.match(path.name)
        if not match:
            continue
        by_sequence.setdefault(match.group(1), []).append(path)
    return {key: sorted(value) for key, value in sorted(by_sequence.items())}


def section_text(text: str, section: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(section)}\s*$\n(.*?)(?=^##\s+|\Z)",
        flags=re.M | re.S,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def parse_markdown_table(block: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in block.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def course_sheet_links(path: Path) -> list[CourseSheetLink]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = parse_markdown_table(section_text(text, "Lien avec la progression"))
    links: list[CourseSheetLink] = []
    for row in rows:
        links.append(
            CourseSheetLink(
                element=row.get("Élément") or row.get("Element") or "",
                file=row.get("Fichier") or "",
                status=row.get("Statut") or "",
                remark=row.get("Remarque") or "",
            )
        )
    return links


def registered_missing_files(root: Path = ROOT) -> set[str]:
    path = root / "missing_documents_register_v2.md"
    if not path.exists():
        return set()
    registered: set[str] = set()
    text = path.read_text(encoding="utf-8", errors="replace")
    for block in text.split("\n\n"):
        rows = parse_markdown_table(block)
        for row in rows:
            filename = row.get("Fichier") or ""
            if filename and filename not in {"NA", "na", "-"}:
                registered.add(filename)
                registered.add(Path(filename).name)
    return registered


def session_ids(root: Path = ROOT) -> set[str]:
    ids: set[str] = set()
    for relative in ["03_progressions/seances_premiere.md", "03_progressions/seances_terminale.md"]:
        path = root / relative
        if not path.exists():
            continue
        ids.update(re.findall(r"\b[PT]\d{2}-S\d+\b", path.read_text(encoding="utf-8", errors="replace")))
    return ids


def resource_exists(root: Path, reference: str) -> bool:
    if not reference or reference in {"NA", "na", "-"}:
        return False
    candidate = root / reference
    if candidate.exists():
        return True
    if "/" in reference:
        return False
    return any(path.name == reference for path in root.rglob(reference))


def link_is_registered(root: Path, reference: str) -> bool:
    registered = registered_missing_files(root)
    return reference in registered or Path(reference).name in registered


def compute_sheet_readiness(root: Path, links: list[CourseSheetLink]) -> str:
    sessions = session_ids(root)
    has_session = any(link.is_session and link.file in sessions for link in links)
    resource_links = [link for link in links if link.is_resource]
    existing = [link for link in resource_links if resource_exists(root, link.file)]
    registered = [link for link in resource_links if link_is_registered(root, link.file)]
    unresolved = [link for link in resource_links if not resource_exists(root, link.file) and not link_is_registered(root, link.file)]
    if not has_session or not resource_links or unresolved:
        return "theoretical"
    if len(existing) == len(resource_links):
        return "operational"
    if existing or registered:
        return "linked"
    return "theoretical"


def program_ids() -> set[str]:
    return set(load_program_entries())
