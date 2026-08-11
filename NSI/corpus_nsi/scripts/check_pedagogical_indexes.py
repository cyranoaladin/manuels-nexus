#!/usr/bin/env python3
"""Validate generated pedagogical indexes."""

from __future__ import annotations

from collections import Counter

from scripts._qa_common import ROOT, print_result
import scripts.generate_pedagogical_indexes as generate_pedagogical_indexes


INDEX_FILES = [
    "INDEX_BY_LEVEL.md",
    "INDEX_BY_THEME.md",
    "INDEX_BY_DOMAIN.md",
    "INDEX_BY_CHAPTER.md",
    "INDEX_BY_SEQUENCE.md",
    "INDEX_BY_SESSION.md",
    "INDEX_BY_DOCUMENT_TYPE.md",
    "INDEX_BY_CAPACITY.md",
    "INDEX_BY_AUDIENCE.md",
    "INDEX_BY_RAG_COLLECTION.md",
]
FORBIDDEN_MARKERS = (
    "AUDIT/",
    "dist/",
    ".git/",
    "Documents_DRIVE/",
    "rendus_eleves/",
    "NotesEleves.csv",
    "Fichier_Eleves.csv",
)


def main() -> None:
    errors: list[str] = []
    resources = generate_pedagogical_indexes.indexed_resources()
    if not resources:
        errors.append("aucune ressource pédagogique indexable")
    audience_weak = [
        item for item in resources
        if str(item["audience"]) in {"", "mixte", "non renseigné", "non renseignée"}
    ]
    if resources and len(audience_weak) / len(resources) > 0.05:
        errors.append(f"audience mixte/non renseignée > 5% ({len(audience_weak)}/{len(resources)})")
    session_weak = [
        item for item in resources
        if str(item["path"]).startswith("03_progressions/supports/")
        and str(item["session"]) in {"", "non renseigné", "non renseignée"}
    ]
    if resources and len(session_weak) / len(resources) > 0.05:
        errors.append(f"session non renseignée > 5% ({len(session_weak)}/{len(resources)})")
    for item in resources:
        path = str(item["path"])
        if path.startswith("03_progressions/supports/"):
            for key in ("level", "sequence", "document_type", "status"):
                if not str(item.get(key) or "").strip() or str(item.get(key)) in {"non renseigné", "non renseignée"}:
                    errors.append(f"{path}: champ canonique manquant {key}")
    for name in INDEX_FILES:
        index_path = ROOT / name
        if not index_path.exists():
            errors.append(f"{name} absent")
            continue
        text = index_path.read_text(encoding="utf-8")
        if "Généré par `scripts/generate_pedagogical_indexes.py`" not in text:
            errors.append(f"{name}: marqueur de génération absent")
        if "## Synthèse" not in text:
            errors.append(f"{name}: synthèse absente")
        if "Ressources avec capacity_ids" not in text:
            errors.append(f"{name}: compteur capacity_ids absent")
        if "03_progressions/supports/" not in text and "Aucune ressource" not in text:
            errors.append(f"{name}: aucune ressource canonique visible")
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                errors.append(f"{name}: marqueur interdit {marker}")
    PROMOTED_STATUSES = {"validated_pedagogy", "validated_science", "validated_technical", "published"}
    by_status = Counter(str(item["status"]) for item in resources)
    promoted = {s: c for s, c in by_status.items() if s in PROMOTED_STATUSES}
    if promoted:
        errors.append(f"statuts promus dans les index: {promoted}")
    print_result("check_pedagogical_indexes", errors)


if __name__ == "__main__":
    main()
