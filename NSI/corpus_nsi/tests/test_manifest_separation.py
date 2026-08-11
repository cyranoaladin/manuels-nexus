"""Prove that tooling/config changes do not affect the pedagogical manifest."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PEDAGOGICAL_DIRS = (
    "00_programmes_officiels/",
    "02_modeles_documents/",
    "03_progressions/",
    "premiere/",
    "terminale/",
)


def test_pedagogical_manifest_contains_only_pedagogical_content() -> None:
    manifest = ROOT / "manifest.csv"
    assert manifest.exists(), "manifest.csv missing"
    with manifest.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            path = row["chemin"]
            assert path.startswith(PEDAGOGICAL_DIRS), (
                f"Non-pedagogical file {path} leaked into manifest.csv"
            )


def test_manifests_cover_all_inventoried_resources() -> None:
    manifest = ROOT / "manifest.csv"
    tooling = ROOT / "manifest_tooling.csv"
    all_paths: set[str] = set()
    for csv_path in (manifest, tooling):
        with csv_path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                all_paths.add(row["chemin"])
    assert len(all_paths) > 100, f"Too few resources: {len(all_paths)}"


def test_manifest_idempotent_after_rebuild() -> None:
    """Two consecutive rebuilds produce byte-identical output."""
    for _ in range(2):
        subprocess.run(
            [sys.executable, "-m", "scripts.rebuild_inventory"],
            cwd=ROOT, check=True, capture_output=True,
        )
    first_manifest = (ROOT / "manifest.csv").read_bytes()
    first_tooling = (ROOT / "manifest_tooling.csv").read_bytes()
    subprocess.run(
        [sys.executable, "-m", "scripts.rebuild_inventory"],
        cwd=ROOT, check=True, capture_output=True,
    )
    assert (ROOT / "manifest.csv").read_bytes() == first_manifest, (
        "manifest.csv is not idempotent across rebuilds"
    )
    assert (ROOT / "manifest_tooling.csv").read_bytes() == first_tooling, (
        "manifest_tooling.csv is not idempotent across rebuilds"
    )
