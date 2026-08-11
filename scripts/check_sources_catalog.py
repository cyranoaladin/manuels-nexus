#!/usr/bin/env python3
"""Validate the controlled source catalog before any RAG ingestion."""

from __future__ import annotations

from typing import Any

import yaml

from scripts._qa_common import ROOT, print_result


CATALOG = ROOT / "sources_catalog.yml"
REQUIRED_FIELDS = {
    "id",
    "title",
    "url",
    "local_path",
    "source_type",
    "license",
    "copyright_status",
    "rgpd_status",
    "level",
    "theme",
    "capacity_ids",
    "reuse_policy",
    "rag_collection",
    "decision",
    "reviewer",
    "date_review",
    "risk_level",
    "allowed_actions",
}
SOURCE_TYPES = {
    "officiel",
    "annale_publique",
    "ressource_pedagogique_ouverte",
    "drive_interne",
    "inspiration",
    "rejet",
}
COLLECTIONS = {"", "nsi_corpus", "rag_education", "nsi_official", "nsi_annales"}
FORBIDDEN_PATH_PARTS = {
    "/AUDIT",
    "AUDIT/",
    "dist/",
    ".git/",
    "rendus_eleves/",
    "Fichier_Eleves.csv",
}


def load_catalog() -> list[dict[str, Any]]:
    payload = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        return []
    return [row for row in payload["sources"] if isinstance(row, dict)]


def main() -> None:
    errors: list[str] = []
    if not CATALOG.exists():
        print_result("check_sources_catalog", ["sources_catalog.yml absent"])
    rows = load_catalog()
    if not rows:
        errors.append("sources_catalog.yml: aucune source")
    for index, row in enumerate(rows, 1):
        missing = REQUIRED_FIELDS - set(row)
        for field in sorted(missing):
            errors.append(f"source #{index}: champ manquant {field}")
        source_type = str(row.get("source_type", ""))
        if source_type not in SOURCE_TYPES:
            errors.append(f"source #{index}: source_type invalide {source_type}")
        collection = str(row.get("rag_collection", ""))
        if collection not in COLLECTIONS:
            errors.append(f"source #{index}: collection invalide {collection}")
        capacity_ids = row.get("capacity_ids")
        if not isinstance(capacity_ids, list):
            errors.append(f"source #{index}: capacity_ids doit être une liste")
        local_path = str(row.get("local_path", ""))
        for marker in FORBIDDEN_PATH_PARTS:
            if marker in local_path:
                errors.append(f"source #{index}: chemin interdit {local_path}")
        if "donnees_personnelles" in str(row.get("rgpd_status", "")) and row.get("decision") != "rejet":
            errors.append(f"source #{index}: données personnelles non rejetées")
        if not isinstance(row.get("allowed_actions"), list):
            errors.append(f"source #{index}: allowed_actions doit être une liste")
        if collection == "nsi_corpus":
            errors.append(f"source #{index}: nsi_corpus réservé aux ressources internes produites, pas au catalogue externe")
    print_result("check_sources_catalog", errors)


if __name__ == "__main__":
    main()
