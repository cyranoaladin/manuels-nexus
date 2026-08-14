#!/usr/bin/env python3
"""Validate RAG configuration examples without reading local secrets."""

from __future__ import annotations

import re
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
    "OPENROUTER_API_KEY": "",
    "OPENROUTER_MODEL": "",
    "RAG_SSH_HOST": "88.99." + "254.59",
    "RAG_SSH_USER": "root",
}

FORBIDDEN_LOCAL_LLM_KEYS = {
    "LOCAL_LLM_ENGINE",
    "LOCAL_LLM_BASE_URL",
    "LOCAL_LLM_MODEL",
    "LOCAL_LLM_API_KEY",
}

FORBIDDEN_YAML_KEY_TOKENS = {
    "endpoint",
    "endpoints",
    "llm",
    "provider",
    "providers",
}

FORBIDDEN_PROVIDER_IDENTIFIERS = {
    "anthropic",
    "chutes",
    "claude",
    "cohere",
    "gemini",
    "generativeai",
    "groq",
    "mistral",
    "mistralai",
    "ollama",
    "openai",
    "openrouter",
}

LLM_ENDPOINT_MARKERS = (
    "/chat",
    "/messages",
    "/completions",
    "/responses",
)

EXPECTED_YAML_MAPPING_KEYS = {
    (): frozenset(
        {
            "backend",
            "api",
            "vector",
            "embedding",
            "collections",
            "exclusions",
            "metadata_required",
        }
    ),
    ("api",): frozenset({"base_url", "auth", "collection"}),
    ("vector",): frozenset({"distance", "dimension"}),
    ("embedding",): frozenset({"model", "base_url_env"}),
    ("collections",): frozenset(
        {
            "nsi_corpus",
            "rag_education",
            "nsi_golden_examples",
            "nsi_official",
            "nsi_annales",
        }
    ),
    ("collections", "nsi_corpus"): frozenset(
        {"role", "proof_scope", "source_roots", "canonical_metadata"}
    ),
    ("collections", "nsi_corpus", "canonical_metadata"): frozenset(
        {"section_anchor", "capacity_ids", "private_data"}
    ),
    ("collections", "rag_education"): frozenset({"role", "proof_scope"}),
    ("collections", "nsi_golden_examples"): frozenset(
        {"role", "proof_scope", "usable_for_coverage"}
    ),
    ("collections", "nsi_official"): frozenset({"role", "proof_scope"}),
    ("collections", "nsi_annales"): frozenset({"role", "proof_scope"}),
}

EXPECTED_YAML_VALUES = {
    ("backend",): "chroma",
    ("api", "base_url"): "https://rag-api.nexusreussite.academy/search",
    ("api", "auth"): "bearer",
    ("api", "collection"): "nsi_corpus",
    ("vector", "distance"): "cosine",
    ("vector", "dimension"): 768,
    ("embedding", "model"): "nomic-embed-text",
    ("embedding", "base_url_env"): "EMBEDDING_BASE_URL",
    ("collections", "nsi_corpus", "role"): "ressources internes produites",
    ("collections", "nsi_corpus", "proof_scope"): "internal_only",
    ("collections", "nsi_corpus", "source_roots"): [
        "03_progressions/supports/",
        "03_progressions/fiches_cours/",
    ],
    (
        "collections",
        "nsi_corpus",
        "canonical_metadata",
        "section_anchor",
    ): "required",
    (
        "collections",
        "nsi_corpus",
        "canonical_metadata",
        "capacity_ids",
    ): "required",
    (
        "collections",
        "nsi_corpus",
        "canonical_metadata",
        "private_data",
    ): False,
    (
        "collections",
        "rag_education",
        "role",
    ): "sources Drive, ressources externes et inspiration uniquement",
    ("collections", "rag_education", "proof_scope"): "not_internal_coverage",
    (
        "collections",
        "nsi_golden_examples",
        "role",
    ): "pilotes historiques premiere/sequences et terminale/sequences",
    (
        "collections",
        "nsi_golden_examples",
        "proof_scope",
    ): "style_reference_only",
    (
        "collections",
        "nsi_golden_examples",
        "usable_for_coverage",
    ): False,
    ("collections", "nsi_official", "role"): "textes officiels",
    ("collections", "nsi_official", "proof_scope"): "reference_only",
    (
        "collections",
        "nsi_annales",
        "role",
    ): "sujets publics et annales si licence compatible",
    ("collections", "nsi_annales", "proof_scope"): "external_reference",
}

MISSING = object()

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
    for key in (
        "RAG_API_KEY",
        "EMBEDDING_API_KEY",
        "VECTOR_DB_API_KEY",
        "OPENROUTER_API_KEY",
    ):
        if values.get(key):
            errors.append(f".env.rag.example: {key} doit rester vide")
    unexpected_keys = set(values) - set(EXPECTED_ENV)
    for key in sorted(unexpected_keys):
        if key in FORBIDDEN_LOCAL_LLM_KEYS:
            errors.append(f".env.rag.example: clé LLM locale interdite {key}")
        else:
            errors.append(f".env.rag.example: clé inattendue {key}")


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
    _validate_yaml_schema(data, errors)
    _validate_yaml_values(data, errors)
    _validate_yaml_semantics(data, errors)
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


def _semantic_tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _value_at_path(value: Any, path: tuple[str, ...]) -> Any:
    current = value
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return MISSING
        current = current[part]
    return current


def _validate_yaml_values(value: Any, errors: list[str]) -> None:
    for path, expected in EXPECTED_YAML_VALUES.items():
        actual = _value_at_path(value, path)
        if actual is MISSING:
            continue
        if type(actual) is not type(expected) or actual != expected:
            errors.append(
                "rag_config.example.yml: valeur canonique attendue pour "
                f"{'.'.join(path)}: {expected!r}"
            )


def _validate_yaml_schema(
    value: Any,
    errors: list[str],
    path: tuple[str, ...] = (),
) -> None:
    expected_keys = EXPECTED_YAML_MAPPING_KEYS.get(path)
    location = ".".join(path) or "<racine>"
    if isinstance(value, dict):
        if expected_keys is None:
            errors.append(f"rag_config.example.yml: mapping inattendu dans {location}")
        else:
            actual_keys = {str(key) for key in value}
            for key in sorted(actual_keys - expected_keys):
                errors.append(
                    f"rag_config.example.yml: clé inattendue {location}.{key}"
                )
            for key in sorted(expected_keys - actual_keys):
                errors.append(
                    f"rag_config.example.yml: clé manquante {location}.{key}"
                )
        for raw_key, nested in value.items():
            _validate_yaml_schema(nested, errors, (*path, str(raw_key)))
        return
    if expected_keys is not None:
        errors.append(f"rag_config.example.yml: mapping attendu dans {location}")
        return
    if isinstance(value, list):
        for index, nested in enumerate(value):
            _validate_yaml_schema(nested, errors, (*path, f"[{index}]"))


def _contains_provider_identifier(value: str) -> bool:
    tokens = _semantic_tokens(value)
    return bool(tokens & FORBIDDEN_PROVIDER_IDENTIFIERS) or any(
        token.startswith("qwen") for token in tokens
    )


def _validate_yaml_semantics(
    value: Any,
    errors: list[str],
    path: tuple[str, ...] = (),
) -> None:
    if isinstance(value, dict):
        for raw_key, nested in value.items():
            key = str(raw_key)
            current_path = (*path, key)
            key_tokens = _semantic_tokens(key)
            if key_tokens & FORBIDDEN_YAML_KEY_TOKENS or _contains_provider_identifier(key):
                errors.append(
                    "rag_config.example.yml: clé LLM interdite "
                    + ".".join(current_path)
                )
            _validate_yaml_semantics(nested, errors, current_path)
        return
    if isinstance(value, list):
        for index, nested in enumerate(value):
            _validate_yaml_semantics(nested, errors, (*path, f"[{index}]"))
        return
    if not isinstance(value, str):
        return
    location = ".".join(path) or "<racine>"
    if _contains_provider_identifier(value):
        errors.append(
            f"rag_config.example.yml: fournisseur LLM interdit dans {location}"
        )
    if any(marker in value.casefold() for marker in LLM_ENDPOINT_MARKERS):
        errors.append(
            f"rag_config.example.yml: endpoint LLM arbitraire interdit dans {location}"
        )


def main() -> None:
    errors: list[str] = []
    validate_env_example(errors)
    validate_gitignore(errors)
    validate_yaml(errors)
    print_result("check_rag_config", errors)


if __name__ == "__main__":
    main()
