"""Exhaustive adverse matrix for check_rag_collection_policy (AST-based).

Each rule is tested with a fixture that should make the checker FAIL (ROUGE)
and one that should PASS (VERT). Fixtures are in-memory strings, never
mutations of the real substance_judge.py.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.check_rag_collection_policy import check_judge_collection_policy

# A minimal VALID judge source (all rules pass)
VALID_JUDGE = '''
from typing import Any

INTERNAL_COVERAGE_COLLECTIONS = {"nsi_corpus", "nsi_corpus_v2"}

def is_internal_collection(name: str) -> bool:
    return name in INTERNAL_COVERAGE_COLLECTIONS

def is_internal_hit(hit: dict) -> bool:
    if not isinstance(hit, dict):
        return False
    metadata = hit.get("metadata")
    if not isinstance(metadata, dict):
        return False
    return str(metadata.get("source_type", "")) == "nsi_corpus"

def search_rag(env, query, k=5, doc_type_filter=None):
    hits = _http_json(env["RAG_API_BASE_URL"],
        body={"q": query, "collection": env.get("RAG_COLLECTION", "nsi_corpus"), "k": k},
    ).get("hits", [])
    hits = [h for h in hits if is_internal_hit(h)]
    if doc_type_filter:
        hits = [h for h in hits if h.get("metadata", {}).get("document_type", "") in doc_type_filter]
    return hits
'''


def test_valid_judge_passes() -> None:
    """The valid fixture must produce 0 errors."""
    errors = check_judge_collection_policy(VALID_JUDGE)
    assert not errors, f"Valid judge should pass but got: {errors}"


# --- Rule 1: hardcoded collection literal ---

def test_rouge_collection_literal_double_quote() -> None:
    src = VALID_JUDGE.replace(
        'env.get("RAG_COLLECTION", "nsi_corpus")',
        '"nsi_corpus_v2"',
    )
    errors = check_judge_collection_policy(src)
    assert any("littéral" in e for e in errors), f"Should detect literal: {errors}"


def test_rouge_collection_literal_single_quote() -> None:
    src = VALID_JUDGE.replace(
        '"collection": env.get("RAG_COLLECTION", "nsi_corpus")',
        "'collection': 'rag_education'",
    )
    errors = check_judge_collection_policy(src)
    assert any("littéral" in e or "rag_education" in e for e in errors), f"Should detect literal: {errors}"


# --- Rule 2: RAG_COLLECTION default ---

def test_rouge_env_get_no_default() -> None:
    src = VALID_JUDGE.replace(
        'env.get("RAG_COLLECTION", "nsi_corpus")',
        'env.get("RAG_COLLECTION")',
    )
    errors = check_judge_collection_policy(src)
    assert any("sans défaut" in e for e in errors), f"Should detect missing default: {errors}"


def test_rouge_env_bracket_no_default() -> None:
    src = VALID_JUDGE.replace(
        'env.get("RAG_COLLECTION", "nsi_corpus")',
        'env["RAG_COLLECTION"]',
    )
    errors = check_judge_collection_policy(src)
    # env["X"] is not a .get call -> RAG_COLLECTION read not found via get
    assert any("n'est pas lu" in e or "sans défaut" in e for e in errors), f"Should detect: {errors}"


def test_rouge_wrong_default() -> None:
    src = VALID_JUDGE.replace(
        'env.get("RAG_COLLECTION", "nsi_corpus")',
        'env.get("RAG_COLLECTION", "rag_education")',
    )
    errors = check_judge_collection_policy(src)
    assert any("défaut" in e and "rag_education" in e for e in errors), f"Should detect wrong default: {errors}"


# --- Rule 3: Barrier A ---

def test_rouge_missing_is_internal_collection() -> None:
    src = VALID_JUDGE.replace("def is_internal_collection", "def _removed_internal_collection")
    errors = check_judge_collection_policy(src)
    assert any("is_internal_collection" in e for e in errors), f"Should detect missing: {errors}"


def test_rouge_missing_allowlist() -> None:
    src = VALID_JUDGE.replace("INTERNAL_COVERAGE_COLLECTIONS", "SOME_OTHER_NAME")
    errors = check_judge_collection_policy(src)
    assert any("INTERNAL_COVERAGE_COLLECTIONS" in e for e in errors), f"Should detect missing: {errors}"


# --- Rule 4: Barrier B ---

def test_rouge_missing_is_internal_hit() -> None:
    src = VALID_JUDGE.replace("def is_internal_hit", "def _removed_internal_hit")
    errors = check_judge_collection_policy(src)
    assert any("is_internal_hit" in e and "non définie" in e for e in errors), f"Should detect: {errors}"


def test_rouge_is_internal_hit_no_isinstance_guard() -> None:
    src = VALID_JUDGE.replace(
        "if not isinstance(metadata, dict):",
        "if metadata is None:  # weak guard",
    )
    errors = check_judge_collection_policy(src)
    assert any("isinstance" in e for e in errors), f"Should detect missing isinstance: {errors}"


def test_rouge_is_internal_hit_not_called_in_search_rag() -> None:
    src = VALID_JUDGE.replace(
        "hits = [h for h in hits if is_internal_hit(h)]",
        "hits = [h for h in hits if h]  # barrier removed",
    )
    errors = check_judge_collection_policy(src)
    assert any("search_rag" in e and "is_internal_hit" in e for e in errors), f"Should detect: {errors}"


# --- Hole 1: multiple defaults, one bad (last-write-wins before fix) ---

def test_rouge_multiple_defaults_one_bad() -> None:
    src = VALID_JUDGE.replace(
        '"collection": env.get("RAG_COLLECTION", "nsi_corpus")',
        '"collection": env.get("RAG_COLLECTION", "rag_education")',
    )
    # Add a second read with correct default — old checker kept only last
    src += '\nx = env.get("RAG_COLLECTION", "nsi_corpus")\n'
    errors = check_judge_collection_policy(src)
    assert any("rag_education" in e for e in errors), f"Should detect bad default: {errors}"


# --- Hole 2: isinstance(metadata, str) instead of dict ---

def test_rouge_isinstance_metadata_str() -> None:
    src = VALID_JUDGE.replace(
        "if not isinstance(metadata, dict):",
        "if not isinstance(metadata, str):",
    )
    errors = check_judge_collection_policy(src)
    assert any("isinstance" in e for e in errors), f"Should detect wrong isinstance type: {errors}"


# --- Hole 3: name incident without real call ---

def test_rouge_name_incident_no_call() -> None:
    src = VALID_JUDGE.replace(
        "hits = [h for h in hits if is_internal_hit(h)]",
        "is_internal_hit_enabled = True\n    hits = [h for h in hits if h]",
    )
    errors = check_judge_collection_policy(src)
    assert any("search_rag" in e and "is_internal_hit" in e for e in errors), f"Should detect no call: {errors}"


# --- Hole 4: annotated allowlist (AnnAssign) ---

def test_vert_annotated_allowlist() -> None:
    src = VALID_JUDGE.replace(
        'INTERNAL_COVERAGE_COLLECTIONS = {"nsi_corpus", "nsi_corpus_v2"}',
        'INTERNAL_COVERAGE_COLLECTIONS: set[str] = {"nsi_corpus", "nsi_corpus_v2"}',
    )
    errors = check_judge_collection_policy(src)
    # Should NOT flag as missing (AnnAssign is accepted now)
    assert not any("INTERNAL_COVERAGE_COLLECTIONS" in e for e in errors), f"AnnAssign should be accepted: {errors}"


# --- Hole 5 (3-ter): bare AnnAssign without value ---

def test_rouge_bare_annassign_no_value() -> None:
    src = VALID_JUDGE.replace(
        'INTERNAL_COVERAGE_COLLECTIONS = {"nsi_corpus", "nsi_corpus_v2"}',
        'INTERNAL_COVERAGE_COLLECTIONS: set[str]',  # no value = not bound
    )
    errors = check_judge_collection_policy(src)
    assert any("INTERNAL_COVERAGE_COLLECTIONS" in e for e in errors), (
        f"Bare AnnAssign should be rejected: {errors}"
    )


# --- Hole 6 (3-ter): call in nested scope only ---

def test_rouge_call_in_nested_def_only() -> None:
    src = VALID_JUDGE.replace(
        "hits = [h for h in hits if is_internal_hit(h)]",
        "def _inner():\n        return [h for h in [] if is_internal_hit(h)]\n    hits = [h for h in hits if h]",
    )
    errors = check_judge_collection_policy(src)
    assert any("search_rag" in e and "is_internal_hit" in e for e in errors), (
        f"Call only in nested def should be rejected: {errors}"
    )


# --- Rule negative: rag_education ---

def test_rouge_rag_education_query() -> None:
    src = VALID_JUDGE + '\nx = {"q": "test", "collection": "rag_education"}\n'
    errors = check_judge_collection_policy(src)
    assert any("rag_education" in e for e in errors), f"Should detect: {errors}"


# --- Real judge must pass ---

def test_real_judge_passes() -> None:
    """The actual substance_judge.py must pass ALL rules."""
    source = (ROOT / "scripts" / "substance_judge.py").read_text(encoding="utf-8")
    errors = check_judge_collection_policy(source)
    assert not errors, f"Real judge should pass but got: {errors}"
