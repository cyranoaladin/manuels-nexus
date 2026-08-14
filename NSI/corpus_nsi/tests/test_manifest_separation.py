"""Prove that tooling/config changes do not affect the pedagogical manifest."""
from __future__ import annotations

import csv
import runpy
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

PEDAGOGICAL_DIRS = (
    "00_programmes_officiels/",
    "02_modeles_documents/",
    "03_progressions/",
    "premiere/",
    "terminale/",
)


def manifest_paths(path: Path) -> set[str]:
    with path.open(encoding="utf-8", newline="") as stream:
        return {row["chemin"] for row in csv.DictReader(stream)}


def tracked_inventory_paths() -> set[str]:
    from scripts._inventory_utils import IGNORED_DIRS, IGNORED_SUFFIXES

    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    excluded_names = {
        "manifest.csv",
        "manifest_tooling.csv",
        "inventory_report.md",
        "duplicates_report.md",
        "coverage.md",
        "coverage_sources.md",
        "privacy_report.md",
        "quality_checklist.md",
    }
    result: set[str] = set()
    for raw in completed.stdout.decode("utf-8").split("\0"):
        if not raw:
            continue
        path = Path(raw)
        if path.name in excluded_names:
            continue
        if path in {Path("AGENTS.md"), Path("SKILLS.md")}:
            continue
        if path.name.startswith(".env") and path.name != ".env.rag.example":
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix in IGNORED_SUFFIXES:
            continue
        if not path.suffix and path.name not in {"SKILLS.md", "AGENTS.md", "README.md"}:
            continue
        result.add(path.as_posix())
    return result


def test_pedagogical_manifest_contains_only_pedagogical_content() -> None:
    manifest = ROOT / "manifest.csv"
    tooling = ROOT / "manifest_tooling.csv"
    assert manifest.exists(), "manifest.csv missing"
    assert tooling.exists(), "manifest_tooling.csv missing"
    with manifest.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            path = row["chemin"]
            assert path.startswith(PEDAGOGICAL_DIRS), (
                f"Non-pedagogical file {path} leaked into manifest.csv"
            )
    new_test = "tests/test_openrouter_judges.py"
    assert new_test not in manifest_paths(manifest)
    assert new_test in manifest_paths(tooling)


def test_manifests_cover_all_inventoried_resources() -> None:
    manifest = ROOT / "manifest.csv"
    tooling = ROOT / "manifest_tooling.csv"
    all_paths = manifest_paths(manifest) | manifest_paths(tooling)
    tracked = tracked_inventory_paths()
    assert len(all_paths) > 100, f"Too few resources: {len(all_paths)}"
    assert all_paths == tracked, (
        f"missing={sorted(tracked - all_paths)} extra={sorted(all_paths - tracked)}"
    )


def test_manifest_idempotent_after_rebuild(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A rebuild is isolated, matches tracked outputs, then stays idempotent."""
    copied_root = tmp_path / "corpus_nsi"
    shutil.copytree(
        ROOT,
        copied_root,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", ".pytest_cache", ".ruff_cache", "__pycache__", "01_build_reports"
        ),
    )
    tracked_before = {
        name: (ROOT / name).read_bytes()
        for name in ("manifest.csv", "manifest_tooling.csv")
    }
    network_attempts: list[str] = []

    def blocked(*args: object, **kwargs: object) -> None:
        network_attempts.append("attempted")
        raise AssertionError("network forbidden during inventory rebuild")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(urllib.request, "urlopen", blocked)
    saved_scripts = {
        name: module
        for name, module in sys.modules.items()
        if name == "scripts" or name.startswith("scripts.")
    }
    for name in list(saved_scripts):
        sys.modules.pop(name, None)
    monkeypatch.syspath_prepend(str(copied_root))
    monkeypatch.chdir(copied_root)
    try:
        runpy.run_module("scripts.rebuild_inventory", run_name="__main__")
        first = {
            name: (copied_root / name).read_bytes()
            for name in ("manifest.csv", "manifest_tooling.csv")
        }
        runpy.run_module("scripts.rebuild_inventory", run_name="__main__")
        second = {
            name: (copied_root / name).read_bytes()
            for name in ("manifest.csv", "manifest_tooling.csv")
        }
    finally:
        for name in list(sys.modules):
            if name == "scripts" or name.startswith("scripts."):
                sys.modules.pop(name, None)
        sys.modules.update(saved_scripts)

    assert network_attempts == []
    assert second == first
    assert first == tracked_before
