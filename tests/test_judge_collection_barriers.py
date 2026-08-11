"""Test substance judge collection + source_type barriers.

Tests call the REAL predicates and search_rag (via monkeypatch), never
reimplementing the filter logic locally.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

import scripts.substance_judge as judge


# ---------------------------------------------------------------------------
# Barrier A — is_internal_collection (predicate + refusal path)
# ---------------------------------------------------------------------------

def test_barrier_a_predicate_accepts_internal() -> None:
    assert judge.is_internal_collection("nsi_corpus")
    assert judge.is_internal_collection("nsi_corpus_v2")


def test_barrier_a_predicate_rejects_external() -> None:
    assert not judge.is_internal_collection("rag_education")
    assert not judge.is_internal_collection("nsi_golden_examples")
    assert not judge.is_internal_collection("")


# ---------------------------------------------------------------------------
# Barrier B — is_internal_hit (predicate) — fail-closed on all malformed forms
# ---------------------------------------------------------------------------

def test_barrier_b_predicate_accepts_nsi_corpus() -> None:
    assert judge.is_internal_hit({"metadata": {"source_type": "nsi_corpus"}})


def test_barrier_b_predicate_rejects_golden_example() -> None:
    assert not judge.is_internal_hit({"metadata": {"source_type": "golden_example"}})


def test_barrier_b_predicate_rejects_excluded() -> None:
    assert not judge.is_internal_hit({"metadata": {"source_type": "excluded"}})


def test_barrier_b_predicate_rejects_non_dict_hit() -> None:
    assert not judge.is_internal_hit("not a dict")  # type: ignore[arg-type]


def test_barrier_b_predicate_rejects_metadata_none() -> None:
    assert not judge.is_internal_hit({"metadata": None})


def test_barrier_b_predicate_rejects_metadata_string() -> None:
    assert not judge.is_internal_hit({"metadata": "a string"})


def test_barrier_b_predicate_rejects_metadata_list() -> None:
    assert not judge.is_internal_hit({"metadata": ["a", "list"]})


def test_barrier_b_predicate_rejects_no_metadata_key() -> None:
    assert not judge.is_internal_hit({"other_key": "value"})


def test_barrier_b_predicate_rejects_missing_source_type() -> None:
    assert not judge.is_internal_hit({"metadata": {"document_type": "tp"}})


# ---------------------------------------------------------------------------
# Barrier B via search_rag (end-to-end with monkeypatched network)
# ---------------------------------------------------------------------------

def _fake_http_json_with_malformed(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Return a mix of valid, non-internal, AND malformed hits."""
    return {
        "hits": [
            {"metadata": {"source_type": "nsi_corpus", "document_type": "tp"}},
            {"metadata": {"source_type": "golden_example", "document_type": "tp"}},
            {"metadata": {"source_type": "excluded", "document_type": "cours"}},
            {"metadata": None},                     # malformed: metadata=None
            {"metadata": "not-a-dict"},              # malformed: metadata=str
            {"other": "no metadata key"},            # malformed: no metadata
            "not-a-dict",                            # malformed: hit not dict
        ]
    }


def test_search_rag_without_filter_handles_malformed() -> None:
    """search_rag WITHOUT doc_type_filter: no crash on malformed, only internal kept."""
    env = {"RAG_API_BASE_URL": "http://fake", "RAG_API_KEY": "fake", "RAG_COLLECTION": "nsi_corpus_v2"}
    with patch.object(judge, "_http_json", _fake_http_json_with_malformed):
        result = judge.search_rag(env, "test query")
    assert len(result) == 1
    assert result[0]["metadata"]["source_type"] == "nsi_corpus"


def test_search_rag_with_doc_type_filter_handles_malformed() -> None:
    """search_rag WITH doc_type_filter (the real judge path): no crash, filter applied."""
    env = {"RAG_API_BASE_URL": "http://fake", "RAG_API_KEY": "fake", "RAG_COLLECTION": "nsi_corpus_v2"}
    with patch.object(judge, "_http_json", _fake_http_json_with_malformed):
        # Filter for "tp" — the valid internal hit has document_type="tp"
        result = judge.search_rag(env, "test query", doc_type_filter=["tp"])
    assert len(result) == 1
    assert result[0]["metadata"]["source_type"] == "nsi_corpus"
    assert result[0]["metadata"]["document_type"] == "tp"


def test_search_rag_with_doc_type_filter_excludes_non_matching() -> None:
    """doc_type_filter excludes even valid internal hits with wrong document_type."""
    env = {"RAG_API_BASE_URL": "http://fake", "RAG_API_KEY": "fake", "RAG_COLLECTION": "nsi_corpus_v2"}
    with patch.object(judge, "_http_json", _fake_http_json_with_malformed):
        # Filter for "evaluation" — no hit has this type
        result = judge.search_rag(env, "test query", doc_type_filter=["evaluation"])
    assert len(result) == 0
