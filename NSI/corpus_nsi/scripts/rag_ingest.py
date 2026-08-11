#!/usr/bin/env python3
"""Deterministic, idempotent RAG ingestion pipeline (local Chroma client).

Walks the content tree, chunks Markdown by section, attaches canonical
metadata, and upserts into a ChromaDB collection. Uses rag_core for all
shared logic (frontmatter, chunking, slug, PII guard, metadata).

NOTE: This script uses Chroma's DEFAULT embedder (all-MiniLM-L6-v2, 384d).
For PROD ingestion, use rag_ingest_server.py (ollama nomic-embed-text, 768d).

Usage:
    python -m scripts.rag_ingest --db /tmp/chroma_ephemeral
    python -m scripts.rag_ingest --db /tmp/chroma_ephemeral --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure repo root is on sys.path for direct invocation (python3 scripts/rag_ingest.py)
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.rag_core import (  # noqa: E402
    extract_metadata,
    iter_source_files,
)

ROOT = _REPO_ROOT


# ---------------------------------------------------------------------------
# Chunk model
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict[str, Any]


# ---------------------------------------------------------------------------
# Ingestion report
# ---------------------------------------------------------------------------

@dataclass
class IngestReport:
    files_seen: int = 0
    files_ingested: int = 0
    files_skipped_pii: int = 0
    files_skipped_unchanged: int = 0
    chunks_upserted: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def build_chunks(path: Path, collection: str = "nsi_corpus") -> list[Chunk]:
    """Build chunks from a source file using shared rag_core logic."""
    raw_chunks, skipped = extract_metadata(path, ROOT, collection=collection)
    if skipped:
        return []
    return [Chunk(id=c["id"], text=c["text"], metadata=c["metadata"]) for c in raw_chunks]


def ingest(
    db_path: Path,
    *,
    collection_name: str = "nsi_corpus",
    dry_run: bool = False,
    embedding_fn: Any = None,
) -> IngestReport:
    report = IngestReport()

    if not dry_run:
        try:
            import chromadb
        except ImportError:
            print("ERREUR: pip install chromadb", file=sys.stderr)
            sys.exit(1)
        client = chromadb.PersistentClient(path=str(db_path))
        col_kwargs: dict[str, Any] = {"name": collection_name}
        if embedding_fn is not None:
            col_kwargs["embedding_function"] = embedding_fn
        collection = client.get_or_create_collection(**col_kwargs)
        existing_ids = set(collection.get()["ids"])
    else:
        existing_ids = set()

    all_chunks: list[Chunk] = []
    for path in iter_source_files(ROOT):
        report.files_seen += 1
        chunks = build_chunks(path, collection=collection_name)
        if not chunks:
            report.files_skipped_pii += 1
            continue
        report.files_ingested += 1
        all_chunks.extend(chunks)

    new_ids = {c.id for c in all_chunks}
    to_upsert = all_chunks  # always upsert for idempotence

    if not dry_run and to_upsert:
        batch_size = 100
        for i in range(0, len(to_upsert), batch_size):
            batch = to_upsert[i:i + batch_size]
            collection.upsert(
                ids=[c.id for c in batch],
                documents=[c.text for c in batch],
                metadatas=[c.metadata for c in batch],
            )

        stale = existing_ids - new_ids
        if stale:
            collection.delete(ids=list(stale))

    report.chunks_upserted = len(to_upsert)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest NSI corpus into ChromaDB.")
    parser.add_argument("--db", type=Path, default=Path("/tmp/chroma_nsi_ephemeral"))
    parser.add_argument("--collection", default="nsi_corpus")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    report = ingest(args.db, collection_name=args.collection, dry_run=args.dry_run)
    print(json.dumps({
        "files_seen": report.files_seen,
        "files_ingested": report.files_ingested,
        "files_skipped_pii": report.files_skipped_pii,
        "chunks_upserted": report.chunks_upserted,
        "errors": report.errors,
        "dry_run": args.dry_run,
    }, indent=2))
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
