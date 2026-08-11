from __future__ import annotations

import subprocess
import tarfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]

import build_source_archive


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_source_archive_policy_document_mentions_git_scope_and_exclusions() -> None:
    policy = ROOT / "docs" / "source_archive_policy.md"

    text = policy.read_text(encoding="utf-8")

    for expected in (
        "git ls-files",
        "fichier non suivi",
        "dist/",
        ".git/",
        "nsi-enseignement/.git",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
    ):
        assert expected in text


def test_source_archive_uses_git_tracked_scope_and_excludes_local_artifacts(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "tests.invalid")
    _git(repo, "config", "user.name", "Tests")

    tracked = repo / "tracked.txt"
    tracked.write_text("tracked\n", encoding="utf-8")
    untracked = repo / "untracked.txt"
    untracked.write_text("untracked\n", encoding="utf-8")
    for artifact in (
        repo / "dist" / "leak.txt",
        repo / "__pycache__" / "leak.pyc",
        repo / ".pytest_cache" / "leak",
        repo / ".ruff_cache" / "leak",
        repo / ".mypy_cache" / "leak",
        repo / "nsi-enseignement" / ".git" / "config",
    ):
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("leak\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt", "dist/leak.txt", "__pycache__/leak.pyc")
    _git(repo, "add", ".pytest_cache/leak", ".ruff_cache/leak", ".mypy_cache/leak")
    _git(repo, "commit", "-m", "fixture")

    target = tmp_path / "dist" / "source_clean.tar.gz"
    build_source_archive.build_source_tar(root=repo, target=target)

    with tarfile.open(target, "r:gz") as archive:
        names = set(archive.getnames())

    assert "nsi-enseignement/tracked.txt" in names
    assert "nsi-enseignement/untracked.txt" not in names
    assert all("dist/" not in name for name in names)
    assert all(".git/" not in name for name in names)
    assert all("__pycache__" not in name for name in names)
    assert all(".pytest_cache" not in name for name in names)
    assert all(".ruff_cache" not in name for name in names)
    assert all(".mypy_cache" not in name for name in names)


def test_source_archive_fallback_without_git_warns(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "source"
    root.mkdir()
    (root / "README.md").write_text("fallback\n", encoding="utf-8")

    paths = build_source_archive.iter_source_paths(root)

    captured = capsys.readouterr()
    assert root / "README.md" in paths
    assert "fallback sans git" in captured.err
