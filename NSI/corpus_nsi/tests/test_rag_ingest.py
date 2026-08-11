"""Tests for the RAG ingestion pipeline (scripts/rag_ingest.py)."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

import scripts.rag_ingest as rag_ingest

CANONICAL_KEYS = {
    "path", "section_anchor", "capacity_ids", "document_type", "status",
    "level", "theme", "notion", "sequence_id", "sha256", "collection",
    "source_type", "private_data",
}


def test_build_chunks_has_canonical_scalar_metadata() -> None:
    """Every chunk carries all canonical keys as scalars (Chroma-safe)."""
    files = rag_ingest.iter_source_files(ROOT)
    if not files:
        pytest.skip("No source files found")
    chunks = rag_ingest.build_chunks(files[0])
    assert chunks, "Expected at least one chunk"
    for chunk in chunks:
        missing = CANONICAL_KEYS - set(chunk.metadata.keys())
        assert not missing, f"Missing metadata keys: {missing}"
        for key, val in chunk.metadata.items():
            assert not isinstance(val, (list, dict)), (
                f"Non-scalar metadata {key}={val!r} — Chroma will reject this"
            )


def test_capacity_ids_read_from_official_program() -> None:
    """capacity_ids comes from official_program.capacities, not top-level."""
    p07 = ROOT / "03_progressions" / "supports" / "premiere" / "P07"
    candidates = sorted(p07.glob("P07_tp_*.md"))
    if not candidates:
        pytest.skip("P07 TP file not found")
    chunks = rag_ingest.build_chunks(candidates[0])
    assert chunks, "Expected chunks"
    caps_csv = chunks[0].metadata["capacity_ids"]
    assert caps_csv, f"capacity_ids is empty: {caps_csv!r}"
    assert "P-LANG" in caps_csv, f"Expected P-LANG capacities, got: {caps_csv}"


def test_adapt_metadata_roundtrip() -> None:
    """ingest(list) -> store(csv) -> adapt -> list identical."""
    original = ["P-TABLE-01", "P-TABLE-02"]
    csv_str = ",".join(original)
    from scripts.rag_core import adapt_metadata
    adapted = adapt_metadata({"capacity_ids": csv_str})
    assert adapted["capacity_ids"] == original


def test_adapt_metadata_empty() -> None:
    from scripts.rag_core import adapt_metadata
    adapted = adapt_metadata({"capacity_ids": ""})
    assert adapted["capacity_ids"] == []


def test_build_chunks_refuses_private_data_flag() -> None:
    """private_data: true → zero chunks."""
    test_dir = ROOT / "03_progressions" / "supports"
    if not test_dir.exists():
        pytest.skip("supports dir missing")
    sentinel = test_dir / "_test_private_sentinel.md"
    try:
        sentinel.write_text(
            "---\nprivate_data: true\nstatus: needs_review\n---\nContenu privé.\n",
            encoding="utf-8",
        )
        chunks = rag_ingest.build_chunks(sentinel)
        assert chunks == [], "private_data: true should produce zero chunks"
    finally:
        sentinel.unlink(missing_ok=True)


def test_private_data_is_bool_not_string() -> None:
    """private_data metadata must be False (bool), not 'false' (string)."""
    files = rag_ingest.iter_source_files(ROOT)
    if not files:
        pytest.skip("No source files")
    chunks = rag_ingest.build_chunks(files[0])
    assert chunks
    pd = chunks[0].metadata["private_data"]
    assert pd is False, f"private_data should be False (bool), got {pd!r} ({type(pd).__name__})"


def test_source_type_enum_rejects_invalid() -> None:
    """extract_metadata raises ValueError on invalid source_type."""
    from scripts.rag_core import extract_metadata
    test_dir = ROOT / "03_progressions" / "supports"
    files = sorted(test_dir.rglob("*.md"))
    if not files:
        pytest.skip("No source files")
    try:
        extract_metadata(files[0], ROOT, source_type="bogus")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "bogus" in str(e)


def test_source_type_enum_accepts_all_valid() -> None:
    """All valid source_types are accepted without error."""
    from scripts.rag_core import extract_metadata
    test_dir = ROOT / "03_progressions" / "supports"
    files = sorted(test_dir.rglob("*.md"))
    if not files:
        pytest.skip("No source files")
    for st in ("nsi_corpus", "golden_example", "excluded"):
        chunks, _ = extract_metadata(files[0], ROOT, source_type=st)
        # No ValueError raised = accepted


def test_slug_preserves_accents() -> None:
    """The slugger must preserve accented characters."""
    from scripts.rag_core import github_slug
    assert github_slug("À savoir") == "à-savoir"
    assert github_slug("Évaluation") == "évaluation"
    assert github_slug("Barème détaillé") == "barème-détaillé"


def test_both_ingestors_import_rag_core() -> None:
    """Anti-divergence: both scripts import from rag_core."""
    for name in ("scripts/rag_ingest.py", "scripts/rag_ingest_server.py"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "from scripts.rag_core import" in text, (
            f"{name} does not import from rag_core — divergence risk"
        )


def test_rag_ingest_no_local_redefinitions() -> None:
    """rag_ingest.py must NOT redefine PII/slug/chunk logic locally."""
    text = (ROOT / "scripts" / "rag_ingest.py").read_text(encoding="utf-8")
    for func in ("_file_has_pii", "_split_sections", "parse_frontmatter", "github_slug", "sha256_file"):
        assert f"def {func}" not in text, (
            f"rag_ingest.py redefines {func} locally — must import from rag_core"
        )


def test_code_file_gets_level_from_path_fallback() -> None:
    """A .py file under code/ with no frontmatter still gets level/sequence_id."""
    code_dirs = list((ROOT / "03_progressions" / "supports").rglob("code"))
    py_files = []
    for d in code_dirs:
        py_files.extend(d.glob("*.py"))
    if not py_files:
        pytest.skip("No code .py files found")
    chunks = rag_ingest.build_chunks(py_files[0])
    if not chunks:
        pytest.skip("Chunks empty (PII or private)")
    meta = chunks[0].metadata
    assert meta["level"], f"level should not be empty for code file: {meta['path']}"
    assert meta["sequence_id"], f"sequence_id should not be empty: {meta['path']}"


def test_dry_run_produces_report() -> None:
    with tempfile.TemporaryDirectory() as td:
        report = rag_ingest.ingest(Path(td), dry_run=True)
    assert report.files_seen > 0
    assert report.errors == []
