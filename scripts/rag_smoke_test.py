#!/usr/bin/env python3
"""Smoke-test the RAG search endpoint when a local secret file is configured."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.rag_core import resolve_env_file  # noqa: E402

ROOT = _REPO_ROOT
ENV_FILE = resolve_env_file(ROOT)
REQUIRED_VARS = {
    "RAG_BACKEND",
    "RAG_API_BASE_URL",
    "RAG_API_KEY",
    "RAG_COLLECTION",
    "RAG_VECTOR_DIM",
}


def parse_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        env[key.strip()] = value.strip()
    return env


def validate_examples() -> list[str]:
    errors: list[str] = []
    for rel in (".env.rag.example", "rag_config.example.yml", "rag_connection.md"):
        if not (ROOT / rel).exists():
            errors.append(f"{rel} absent")
    return errors


def metadata_has_required_keys(metadata: dict[str, Any]) -> bool:
    return bool(
        metadata.get("path")
        and (metadata.get("anchor") or metadata.get("section_anchor"))
        and (metadata.get("capacities") or metadata.get("capacity_ids"))
        and metadata.get("document_type")
        and metadata.get("status")
        and metadata.get("source_type")
    )


def check_required(env: dict[str, str]) -> list[str]:
    errors = [key for key in sorted(REQUIRED_VARS) if not env.get(key)]
    ALLOWED_COLLECTIONS = {"nsi_corpus", "nsi_corpus_v2"}
    col = env.get("RAG_COLLECTION", "")
    if not col:
        errors.append("RAG_COLLECTION is required")
    elif col not in ALLOWED_COLLECTIONS:
        errors.append(f"RAG_COLLECTION={col} not in allowed: {sorted(ALLOWED_COLLECTIONS)}")
    if env.get("RAG_VECTOR_DIM") != "768":
        errors.append("RAG_VECTOR_DIM must be 768")
    if env.get("RAG_BACKEND") != "chroma":
        errors.append("RAG_BACKEND must be chroma")
    return errors


def smoke_search(env: dict[str, str]) -> list[str]:
    body = json.dumps(
        {
            "q": "Importer une table depuis un fichier CSV",
            "collection": env.get("RAG_COLLECTION", "nsi_corpus"),
            "k": 5,
            "include_documents": True,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        env["RAG_API_BASE_URL"],
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env['RAG_API_KEY']}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return [f"HTTP {exc.code} sur /search"]
    except (OSError, TimeoutError, urllib.error.URLError) as exc:
        return [f"connexion RAG impossible: {exc}"]

    if not isinstance(payload, dict):
        return ["réponse RAG non JSON objet"]
    hits = payload.get("hits")
    if not isinstance(hits, list) or not hits:
        return ["RAG /search ne retourne aucun hit"]
    for index, hit in enumerate(hits, 1):
        if not isinstance(hit, dict):
            return [f"hit {index}: objet invalide"]
        metadata = hit.get("metadata")
        if not isinstance(metadata, dict) or not metadata_has_required_keys(metadata):
            return [f"hit {index}: métadonnées minimales absentes"]
    col = env.get("RAG_COLLECTION", "nsi_corpus")
    print(f"RAG_SMOKE_TEST_OK collection={col} hits={len(hits)}")
    return []


def main() -> int:
    strict = os.environ.get("RAG_SMOKE_STRICT", "") == "1"
    if not ENV_FILE.exists():
        if strict:
            print("RAG_SMOKE_TEST_FAILED: .env.rag absent in strict mode", file=sys.stderr)
            return 1
        errors = validate_examples()
        if errors:
            print("RAG_SMOKE_TEST_CONFIG_EXAMPLES_INVALID", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print("RAG_SMOKE_TEST_SKIPPED_NO_CONFIG")
        return 0

    env = parse_env(ENV_FILE)
    # os.environ overrides .env.rag (allows RAG_COLLECTION=nsi_corpus_v2 etc.)
    for key in REQUIRED_VARS | {"RAG_COLLECTION"}:
        val = os.getenv(key)
        if val:
            env[key] = val
    errors = check_required(env)
    if errors:
        print("RAG_SMOKE_TEST_CONFIG_INVALID", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    errors = smoke_search(env)
    if errors:
        print("RAG_SMOKE_TEST_FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
