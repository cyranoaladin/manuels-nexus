#!/usr/bin/env python3
"""Validate sources_catalog.yml against the actionable ingestion policy."""

from __future__ import annotations

from pathlib import Path
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
ALLOWED_ACTIONS = {"index", "summarize", "inspire", "adapt", "reject"}
EXTERNAL_TYPES = SOURCE_TYPES - {"rejet"}


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        return []
    return [row for row in payload["sources"] if isinstance(row, dict)]


def source_id(row: dict[str, Any], index: int) -> str:
    return str(row.get("id") or row.get("title") or f"source #{index}")


def check_catalog(path: Path = CATALOG) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return ["sources_catalog.yml absent"]
    rows = load_rows(path)
    if not rows:
        return ["sources_catalog.yml: aucune source"]
    for index, row in enumerate(rows, 1):
        ident = source_id(row, index)
        for field in sorted(REQUIRED_FIELDS - set(row)):
            errors.append(f"{ident}: champ manquant {field}")
        source_type = str(row.get("source_type", ""))
        collection = str(row.get("rag_collection", ""))
        decision = str(row.get("decision", ""))
        license_value = str(row.get("license", "")).lower()
        actions = row.get("allowed_actions")
        if source_type not in SOURCE_TYPES:
            errors.append(f"{ident}: source_type invalide {source_type}")
        if not isinstance(row.get("capacity_ids"), list):
            errors.append(f"{ident}: capacity_ids doit être une liste")
        if not isinstance(actions, list) or not actions:
            errors.append(f"{ident}: allowed_actions doit être une liste non vide")
        elif any(str(action) not in ALLOWED_ACTIONS for action in actions):
            errors.append(f"{ident}: allowed_actions contient une action invalide")
        if source_type in EXTERNAL_TYPES and collection == "nsi_corpus":
            errors.append(f"{ident}: une source externe ne peut pas aller dans nsi_corpus")
        if source_type == "drive_interne" and collection not in {"rag_education", ""}:
            errors.append(f"{ident}: Documents_DRIVE doit rester rag_education ou rejet")
        if source_type == "officiel" and collection != "nsi_official":
            errors.append(f"{ident}: une source officielle doit aller dans nsi_official")
        if source_type == "annale_publique" and collection != "nsi_annales":
            errors.append(f"{ident}: une annale doit aller dans nsi_annales")
        if source_type == "rejet" and collection:
            errors.append(f"{ident}: une source rejetée ne doit pas avoir de rag_collection")
        if "donnees_personnelles" in str(row.get("rgpd_status", "")) and decision != "rejet":
            errors.append(f"{ident}: données élèves ou personnelles => rejet obligatoire")
        if "vérifier" in license_value or "verifier" in license_value:
            if decision != "a_classifier_avant_ingestion":
                errors.append(f"{ident}: licence à vérifier incompatible avec decision={decision}")
    return errors


def main() -> None:
    print_result("check_sources_catalog_schema", check_catalog())


if __name__ == "__main__":
    main()
