#!/usr/bin/env python3
"""Prepare classified scraped documents for RAG ingestion; never ingests directly."""

from __future__ import annotations

import argparse
import hashlib

import yaml

from scripts._qa_common import ROOT


CATALOG = ROOT / "sources_catalog.yml"


def source_rows() -> list[dict[str, object]]:
    payload = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        return []
    return [row for row in payload["sources"] if isinstance(row, dict)]


def hash_if_local(path_text: str) -> str:
    if not path_text:
        return ""
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        return ""
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run de préparation RAG pour sources classées.")
    parser.add_argument("--dry-run", action="store_true", help="obligatoire pour cette passe")
    args = parser.parse_args()
    if not args.dry_run:
        print("ERREUR: ingestion réelle bloquée ; utilisez --dry-run et faites valider le plan.")
        return 1
    for row in source_rows():
        collection = str(row.get("rag_collection", ""))
        decision = str(row.get("decision", ""))
        local_path = str(row.get("local_path", ""))
        digest = hash_if_local(local_path)
        print(f"{row.get('title')} | collection={collection or 'none'} | decision={decision} | sha256={digest or 'not_local_file'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
