#!/usr/bin/env python3
"""Generate multidimensional pedagogical indexes from manifest and metadata."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import re
from pathlib import Path
from typing import Iterable

from scripts._qa_common import ROOT, read_frontmatter


MANIFEST = ROOT / "manifest.csv"
CAPACITY_RE = re.compile(r"\b[PT]-[A-Z0-9-]+\b")
ALLOWED_PREFIXES = (
    "03_progressions/supports/",
    "03_progressions/fiches_cours/",
)
FORBIDDEN_MARKERS = (
    "AUDIT/",
    "dist/",
    ".git/",
    "Documents_DRIVE/",
    "rendus_eleves/",
    "NotesEleves.csv",
    "Fichier_Eleves.csv",
)
INDEX_SPECS = {
    "INDEX_BY_LEVEL.md": "level",
    "INDEX_BY_THEME.md": "theme",
    "INDEX_BY_DOMAIN.md": "domain",
    "INDEX_BY_CHAPTER.md": "chapter",
    "INDEX_BY_SEQUENCE.md": "sequence",
    "INDEX_BY_SESSION.md": "session",
    "INDEX_BY_DOCUMENT_TYPE.md": "document_type",
    "INDEX_BY_CAPACITY.md": "capacity",
    "INDEX_BY_AUDIENCE.md": "audience",
    "INDEX_BY_RAG_COLLECTION.md": "rag_collection",
}


def is_pedagogical_path(path_text: str) -> bool:
    return path_text.startswith(ALLOWED_PREFIXES) and not any(
        marker in path_text for marker in FORBIDDEN_MARKERS
    )


def read_manifest_rows() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def infer_sequence(path_text: str, fallback: str) -> str:
    for part in Path(path_text).parts:
        if re.fullmatch(r"[PT]\d{2}", part):
            return part
    return fallback or "non renseignée"


def infer_document_type(path_text: str, row_type: str, metadata: dict[str, object]) -> str:
    doc_type = str(metadata.get("document_type") or "").strip()
    if doc_type:
        return doc_type
    name = Path(path_text).name.lower()
    for marker in ("cours", "trace", "td", "tp", "corrige", "evaluation", "bareme", "qcm", "remediation"):
        if marker in name:
            return marker
    return row_type or "document"


def infer_audience(document_type: str, row_audience: str, metadata: dict[str, object]) -> str:
    explicit = str(metadata.get("audience") or "").strip()
    if explicit and explicit not in {"mixte", "non renseigné", "non renseignée"}:
        return explicit
    if document_type in {"corrige", "bareme", "guide_prof", "corrige_code", "tests_code"}:
        return "professeur"
    if document_type in {
        "cours",
        "trace",
        "td",
        "tp",
        "tp_papier",
        "evaluation",
        "qcm",
        "fiche_cours",
        "fiche",
        "remediation",
        "version_amenagee",
        "starter_code",
    }:
        return "eleve"
    return row_audience if row_audience not in {"", "mixte"} else "eleve"


def infer_session(metadata: dict[str, object], sequence: str) -> str:
    explicit = str(metadata.get("session") or metadata.get("session_id") or "").strip()
    if explicit:
        return explicit
    if re.fullmatch(r"[PT]\d{2}", sequence):
        return f"{sequence}-S1..{sequence}-S7"
    return "hors séance"


def metadata_capacities(path: Path, metadata: dict[str, object]) -> list[str]:
    raw = metadata.get("capacities")
    capacities: list[str] = []
    if isinstance(raw, str):
        capacities.extend(CAPACITY_RE.findall(raw))
    elif isinstance(raw, list):
        capacities.extend(str(item) for item in raw if CAPACITY_RE.fullmatch(str(item)))
    official = metadata.get("official_program")
    if isinstance(official, dict):
        official_caps = official.get("capacities")
        if isinstance(official_caps, list):
            for item in official_caps:
                if isinstance(item, dict) and CAPACITY_RE.fullmatch(str(item.get("id", ""))):
                    capacities.append(str(item["id"]))
    if not capacities and path.exists() and path.suffix in {".md", ".json", ".yml", ".yaml"}:
        capacities.extend(CAPACITY_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
    return sorted(set(capacities)) or ["non rattachée"]


def indexed_resources() -> list[dict[str, object]]:
    resources: list[dict[str, object]] = []
    for row in read_manifest_rows():
        path_text = row.get("chemin", "")
        if not is_pedagogical_path(path_text):
            continue
        path = ROOT / path_text
        metadata = read_frontmatter(path) if path.exists() else {}
        sequence = infer_sequence(path_text, row.get("sequence_possible", ""))
        level = str(metadata.get("level") or row.get("niveau") or "non renseigné")
        theme = str(metadata.get("theme") or row.get("theme") or "non renseigné")
        document_type = infer_document_type(path_text, row.get("type", ""), metadata)
        capacities = metadata_capacities(path, metadata)
        resources.append(
            {
                "path": path_text,
                "title": row.get("nom") or Path(path_text).name,
                "level": level,
                "theme": theme,
                "domain": str(metadata.get("domain") or theme or "NSI"),
                "chapter": str(metadata.get("chapter") or sequence),
                "sequence": sequence,
                "session": infer_session(metadata, sequence),
                "document_type": document_type,
                "capacity": capacities,
                "has_capacity_ids": capacities != ["non rattachée"],
                "audience": infer_audience(document_type, row.get("audience", ""), metadata),
                "rag_collection": "nsi_corpus",
                "status": row.get("statut", "needs_review"),
                "source": row.get("source", ""),
            }
        )
    return resources


def values_for(resource: dict[str, object], key: str) -> Iterable[str]:
    value = resource[key]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def write_index(filename: str, key: str, resources: list[dict[str, object]]) -> None:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for resource in resources:
        for value in values_for(resource, key):
            groups[value or "non renseigné"].append(resource)
    lines = [
        f"# {filename.removesuffix('.md').replace('_', ' ').title()}",
        "",
        "Généré par `scripts/generate_pedagogical_indexes.py` depuis `manifest.csv` et les métadonnées.",
        "Ce fichier ne valide aucune ressource : les statuts restent ceux du manifeste.",
        "",
        "## Synthèse",
        "",
    ]
    status_counts = Counter(str(item["status"]) for item in resources)
    type_counts = Counter(str(item["document_type"]) for item in resources)
    with_capacity = sum(1 for item in resources if item["has_capacity_ids"])
    with_audience = sum(1 for item in resources if str(item["audience"]) not in {"", "mixte", "non renseigné", "non renseignée"})
    with_session = sum(1 for item in resources if str(item["session"]) not in {"", "non renseignée", "non renseigné"})
    lines.extend(
        [
            f"- Nombre total de ressources : {len(resources)}",
            f"- Nombre par statut : {dict(sorted(status_counts.items()))}",
            f"- Nombre par type de document : {dict(sorted(type_counts.items()))}",
            f"- Ressources avec capacity_ids : {with_capacity}",
            f"- Ressources sans capacity_ids : {len(resources) - with_capacity}",
            f"- Ressources avec audience renseignée : {with_audience}",
            f"- Ressources avec session renseignée : {with_session}",
            "",
        ]
    )
    if not groups:
        lines.append("- Aucune ressource pédagogique indexable.")
    for group, items in sorted(groups.items()):
        lines.append(f"## {group}")
        lines.append("")
        for item in sorted(items, key=lambda row: str(row["path"])):
            lines.append(
                f"- `{item['path']}` — {item['document_type']} — {item['status']} — {item['audience']}"
            )
        lines.append("")
    (ROOT / filename).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    resources = indexed_resources()
    for filename, key in INDEX_SPECS.items():
        write_index(filename, key, resources)
    print(f"generate_pedagogical_indexes: generated {len(INDEX_SPECS)} indexes")


if __name__ == "__main__":
    main()
