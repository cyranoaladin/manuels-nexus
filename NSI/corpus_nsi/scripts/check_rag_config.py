#!/usr/bin/env python3
"""Validate RAG configuration examples without reading local secrets."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml


from scripts._qa_common import ROOT, print_result


ENV_EXAMPLE = ROOT / ".env.rag.example"
CONFIG_EXAMPLE = ROOT / "rag_config.example.yml"
GITIGNORE = ROOT / ".gitignore"

EXPECTED_ENV = {
    "RAG_BACKEND": "chroma",
    "RAG_API_BASE_URL": "https://rag-api.nexusreussite.academy/search",
    "RAG_API_KEY": "",
    "RAG_COLLECTION": "nsi_corpus",
    "RAG_DISTANCE": "cosine",
    "RAG_VECTOR_DIM": "768",
    "EMBEDDING_MODEL": "nomic-embed-text",
    "EMBEDDING_BASE_URL": "",
    "EMBEDDING_API_KEY": "",
    "VECTOR_DB_URL": "",
    "VECTOR_DB_API_KEY": "",
    "LOCAL_LLM_ENGINE": "ollama",
    "LOCAL_LLM_BASE_URL": "",
    "LOCAL_LLM_MODEL": "qwen2.5:7b",
    "LOCAL_LLM_API_KEY": "",
    "RAG_SSH_HOST": "88.99." + "254.59",
    "RAG_SSH_USER": "root",
}

REQUIRED_EXCLUSIONS = {
    "AUDIT/",
    "dist/",
    ".git/",
    "Documents_DRIVE/",
    "rendus_eleves/",
    "NotesEleves.csv",
    "Fichier_Eleves.csv",
}


def parse_env_example(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


def is_tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.returncode == 0


def validate_env_example(errors: list[str]) -> None:
    if not ENV_EXAMPLE.exists():
        errors.append(".env.rag.example absent")
        return
    values = parse_env_example(ENV_EXAMPLE)
    for key, expected in EXPECTED_ENV.items():
        actual = values.get(key)
        if actual != expected:
            errors.append(f".env.rag.example: {key}={actual!r}, attendu {expected!r}")
    for key in ("RAG_API_KEY", "EMBEDDING_API_KEY", "VECTOR_DB_API_KEY", "LOCAL_LLM_API_KEY"):
        if values.get(key):
            errors.append(f".env.rag.example: {key} doit rester vide")


def validate_gitignore(errors: list[str]) -> None:
    if not GITIGNORE.exists():
        errors.append(".gitignore absent")
        return
    ignored = set(GITIGNORE.read_text(encoding="utf-8").splitlines())
    if ".env.rag" not in ignored:
        errors.append(".env.rag n'est pas ignoré par Git")
    if is_tracked(ROOT / ".env.rag"):
        errors.append(".env.rag est suivi par Git")


def validate_yaml(errors: list[str]) -> None:
    if not CONFIG_EXAMPLE.exists():
        errors.append("rag_config.example.yml absent")
        return
    payload = yaml.safe_load(CONFIG_EXAMPLE.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        errors.append("rag_config.example.yml invalide")
        return
    data: dict[str, Any] = payload
    if data.get("backend") != "chroma":
        errors.append("rag_config.example.yml: backend doit valoir chroma")
    api = data.get("api")
    vector = data.get("vector")
    if not isinstance(api, dict) or api.get("collection") != "nsi_corpus":
        errors.append("rag_config.example.yml: api.collection doit valoir nsi_corpus")
    if not isinstance(vector, dict) or vector.get("dimension") != 768:
        errors.append("rag_config.example.yml: vector.dimension doit valoir 768")
    collections = data.get("collections")
    if not isinstance(collections, dict) or "nsi_golden_examples" not in collections:
        errors.append("rag_config.example.yml: collection nsi_golden_examples manquante")
    metadata_required = data.get("metadata_required")
    if not isinstance(metadata_required, list):
        errors.append("rag_config.example.yml: metadata_required doit être une liste")
    else:
        for key in ("section_anchor", "capacity_ids", "private_data", "proof_scope"):
            if key not in {str(item) for item in metadata_required}:
                errors.append(f"rag_config.example.yml: metadata_required manque {key}")
    exclusions = data.get("exclusions")
    if not isinstance(exclusions, list):
        errors.append("rag_config.example.yml: exclusions doit être une liste")
        return
    missing = REQUIRED_EXCLUSIONS - {str(item) for item in exclusions}
    for item in sorted(missing):
        errors.append(f"rag_config.example.yml: exclusion manquante {item}")


def main() -> None:
    errors: list[str] = []
    validate_env_example(errors)
    validate_gitignore(errors)
    validate_yaml(errors)
    print_result("check_rag_config", errors)


if __name__ == "__main__":
    main()
