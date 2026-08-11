#!/usr/bin/env python3
"""Check that locally prepared NSI chunks expose required RAG metadata."""

from __future__ import annotations

from typing import Any

from scripts._qa_common import print_result
import scripts.ingest_nsi_corpus as ingest_nsi_corpus


REQUIRED_METADATA = {
    "path",
    "level",
    "sequence_id",
    "document_type",
    "theme",
    "notion",
    "capacity_ids",
    "status",
    "section_anchor",
    "sha256",
    "chunk_index",
    "source_type",
    "proof_scope",
    "usable_for_coverage",
    "private_data",
    "collection",
}


def check_chunk(chunk: dict[str, Any]) -> list[str]:
    metadata = chunk.get("metadata")
    if not isinstance(metadata, dict):
        return ["chunk sans metadata objet"]
    errors: list[str] = []
    missing = REQUIRED_METADATA - set(metadata)
    for key in sorted(missing):
        errors.append(f"{metadata.get('path', '?')}: metadata manquante {key}")
    if metadata.get("collection") != "nsi_corpus":
        errors.append(f"{metadata.get('path', '?')}: collection != nsi_corpus")
    if metadata.get("source_type") != "nsi_corpus":
        errors.append(f"{metadata.get('path', '?')}: source_type != nsi_corpus")
    if metadata.get("proof_scope") != "internal_coverage_candidate":
        errors.append(f"{metadata.get('path', '?')}: proof_scope non interne")
    if metadata.get("usable_for_coverage") is not True:
        errors.append(f"{metadata.get('path', '?')}: usable_for_coverage doit être true")
    if metadata.get("private_data") is not False:
        errors.append(f"{metadata.get('path', '?')}: private_data doit être false")
    if metadata.get("status") not in {"needs_review", "needs_content", "draft"}:
        errors.append(f"{metadata.get('path', '?')}: statut RAG non conservateur")
    if not isinstance(metadata.get("capacity_ids"), list):
        errors.append(f"{metadata.get('path', '?')}: capacity_ids doit être une liste")
    return errors


def main() -> None:
    errors: list[str] = []
    checked = 0
    for path in ingest_nsi_corpus.iter_source_files():
        for chunk in ingest_nsi_corpus.build_chunks(path):
            checked += 1
            errors.extend(check_chunk(chunk))
    if checked == 0:
        errors.append("aucun chunk local préparé")
    print_result("check_rag_index_metadata", errors)


if __name__ == "__main__":
    main()
