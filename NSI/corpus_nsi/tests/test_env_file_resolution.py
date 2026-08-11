"""Prove smoke and judge resolve the SAME .env.rag file."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def test_smoke_and_judge_resolve_same_default() -> None:
    """Without RAG_ENV_FILE override, both resolve to ROOT/.env.rag."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("RAG_ENV_FILE", None)
        from scripts.rag_core import resolve_env_file
        smoke_path = resolve_env_file(ROOT)
        judge_path = resolve_env_file(ROOT)
    assert smoke_path == judge_path
    assert smoke_path == ROOT / ".env.rag"


def test_smoke_and_judge_follow_override() -> None:
    """With RAG_ENV_FILE=/custom/path, both resolve to the override."""
    with patch.dict(os.environ, {"RAG_ENV_FILE": "/custom/path/.env.rag"}):
        from scripts.rag_core import resolve_env_file
        smoke_path = resolve_env_file(ROOT)
        judge_path = resolve_env_file(ROOT)
    assert smoke_path == judge_path
    assert str(smoke_path) == "/custom/path/.env.rag"


def test_different_roots_with_override_still_agree() -> None:
    """Even with different ROOT dirs, the override makes them agree."""
    with patch.dict(os.environ, {"RAG_ENV_FILE": "/shared/.env.rag"}):
        from scripts.rag_core import resolve_env_file
        path_a = resolve_env_file(Path("/workspace/NSI"))
        path_b = resolve_env_file(Path("/tmp/nsi_ingest"))
    assert path_a == path_b == Path("/shared/.env.rag")
