#!/usr/bin/env python3
"""Server-side RAG ingestion via Chroma REST API + ollama embeddings.

Uses HTTP only (no pip chromadb required). Embedding via ollama ensures
dimension parity with prod retrieval (nomic-embed-text, 768d).

NEVER uses the Chroma default embedder (all-MiniLM-L6-v2, 384d).

Environment variables:
    CHROMA_URL      Chroma REST base URL  (default: http://127.0.0.1:8000)
    OLLAMA_URL      Ollama API base URL   (default: http://127.0.0.1:11434)
    EMBED_MODEL     Ollama embed model    (default: nomic-embed-text)
    TARGET_COLLECTION  Collection name    (default: nsi_corpus_v2)
    NSI_ROOT        Path to NSI repo root (default: cwd)

Usage (on server):
    NSI_ROOT=/tmp/nsi_ingest TARGET_COLLECTION=nsi_corpus_v2 python3 scripts/rag_ingest_server.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Ensure repo root is on sys.path for direct invocation (python3 scripts/rag_ingest_server.py)
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Shared logic: frontmatter, chunking, slug, PII guard, metadata
from scripts.rag_core import extract_metadata, iter_source_files

# ---------------------------------------------------------------------------
# Configuration from environment (never hardcoded, token never logged)
# ---------------------------------------------------------------------------

CHROMA_URL = os.environ.get("CHROMA_URL", "http://127.0.0.1:8000")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
TARGET_COLLECTION = os.environ.get("TARGET_COLLECTION", "nsi_corpus_v2")
NSI_ROOT = Path(os.environ.get("NSI_ROOT", "."))
EXPECTED_DIM = 768  # nomic-embed-text dimension; assert at runtime

TENANT = "default_tenant"
DB = "default_database"
BATCH_SIZE = 20


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _http(method: str, url: str, data: dict[str, Any] | None = None) -> Any:
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=body, method=method,
        headers={"Content-Type": "application/json"} if body else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:300]
        if e.code == 409:
            return None
        raise RuntimeError(f"HTTP {method} {url}: {e.code} {err}")


def embed(texts: list[str]) -> list[list[float]]:
    result = _http("POST", f"{OLLAMA_URL}/api/embed", {
        "model": EMBED_MODEL, "input": texts,
    })
    embeddings: list[list[float]] = result["embeddings"]
    if embeddings and len(embeddings[0]) != EXPECTED_DIM:
        raise RuntimeError(
            f"Embedding dim {len(embeddings[0])} != {EXPECTED_DIM}. STOP."
        )
    return embeddings


# ---------------------------------------------------------------------------
# Chroma REST v2
# ---------------------------------------------------------------------------

_BASE = f"{CHROMA_URL}/api/v2/tenants/{TENANT}/databases/{DB}"


def get_or_create_collection(name: str) -> str:
    _http("POST", f"{_BASE}/collections", {
        "name": name, "metadata": {"hnsw:space": "cosine"},
    })
    cols: list[dict[str, Any]] = _http("GET", f"{_BASE}/collections")
    for c in cols:
        if c["name"] == name:
            return str(c["id"])
    raise RuntimeError(f"Collection {name} not found")


def collection_count(col_id: str) -> int:
    url = f"{_BASE}/collections/{col_id}/count"
    with urllib.request.urlopen(url, timeout=30) as r:
        return int(r.read().decode())


def upsert(col_id: str, ids: list[str], docs: list[str],
           embs: list[list[float]], metas: list[dict[str, Any]]) -> None:
    _http("POST", f"{_BASE}/collections/{col_id}/upsert", {
        "ids": ids, "documents": docs, "embeddings": embs, "metadatas": metas,
    })


def delete_collection(name: str) -> None:
    _http("DELETE", f"{_BASE}/collections/{name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print(f"CHROMA_URL={CHROMA_URL}")
    print(f"OLLAMA_URL={OLLAMA_URL}")
    print(f"EMBED_MODEL={EMBED_MODEL} (expected dim={EXPECTED_DIM})")
    print(f"TARGET_COLLECTION={TARGET_COLLECTION}")
    print(f"NSI_ROOT={NSI_ROOT}")

    col_id = get_or_create_collection(TARGET_COLLECTION)
    print(f"Collection ID: {col_id}")

    files = iter_source_files(NSI_ROOT)
    print(f"Files found: {len(files)}")

    all_chunks: list[dict[str, Any]] = []
    pii_skipped = 0
    for p in files:
        chunks, skipped = extract_metadata(p, NSI_ROOT, TARGET_COLLECTION)
        if skipped:
            pii_skipped += 1
        all_chunks.extend(chunks)
    print(f"Chunks built: {len(all_chunks)}, PII skipped: {pii_skipped}")

    ingested = 0
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        embs = embed(texts)
        upsert(
            col_id,
            ids=[c["id"] for c in batch],
            docs=texts,
            embs=embs,
            metas=[c["metadata"] for c in batch],
        )
        ingested += len(batch)
        if ingested % 200 == 0:
            print(f"  ingested {ingested}/{len(all_chunks)}")

    count = collection_count(col_id)
    print(f"DONE: {ingested} chunks, PII_skipped={pii_skipped}")
    print(f"Collection count: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
