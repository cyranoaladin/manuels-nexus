#!/usr/bin/env python3
"""Require canonical metadata fields for internal NSI RAG chunks."""

from __future__ import annotations

from typing import Any


from scripts import ingest_nsi_corpus
from scripts._qa_common import print_result


ALLOWED_STATUSES = {"needs_review", "needs_content", "draft"}


def check_metadata(metadata: dict[str, Any]) -> list[str]:
    path = str(metadata.get("path") or "?")
    errors: list[str] = []
    for key in ("section_anchor", "capacity_ids", "status", "private_data", "collection"):
        if key not in metadata:
            errors.append(f"{path}: champ canonique manquant {key}")
    if metadata.get("collection") == "nsi_corpus":
        if metadata.get("source_type") != "nsi_corpus":
            errors.append(f"{path}: source_type doit valoir nsi_corpus")
        if metadata.get("proof_scope") != "internal_coverage_candidate":
            errors.append(f"{path}: proof_scope interne manquant")
        if metadata.get("usable_for_coverage") is not True:
            errors.append(f"{path}: usable_for_coverage doit être true")
    if not isinstance(metadata.get("capacity_ids"), list):
        errors.append(f"{path}: capacity_ids doit être une liste")
    if metadata.get("status") not in ALLOWED_STATUSES:
        errors.append(f"{path}: statut RAG non conservateur")
    if metadata.get("private_data") is not False:
        errors.append(f"{path}: private_data=false obligatoire")
    return errors


def main() -> None:
    errors: list[str] = []
    checked = 0
    for path in ingest_nsi_corpus.iter_source_files():
        for chunk in ingest_nsi_corpus.build_chunks(path):
            metadata = chunk.get("metadata")
            if not isinstance(metadata, dict):
                errors.append(f"{path}: chunk sans metadata objet")
                continue
            checked += 1
            errors.extend(check_metadata(metadata))
    if checked == 0:
        errors.append("aucun chunk local préparé")
    print_result("check_rag_metadata_canonical_fields", errors)


if __name__ == "__main__":
    main()
