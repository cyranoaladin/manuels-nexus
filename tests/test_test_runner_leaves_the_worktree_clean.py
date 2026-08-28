"""Executer les tests supportes ne doit jamais salir l'arbre canonique.

Defaut mesure le 2026-08-28 : `pytest --cov` ecrivait un `.coverage` non suivi
a la racine du depot, ce qui suffisait a faire echouer les quatre gates du
manifeste sur "depot Git sale pour le manifeste observe". Le diagnostic etait
un faux negatif de methode, pas un etat du depot. Le nettoyage manuel apres
coup n'est pas une correction : le runner ne doit pas salir.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FAST_SUPPORTED_TARGET = "tests/test_official_program_atoms.py"


def _status(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


@pytest.fixture(scope="module")
def repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("runner-cleanliness") / "repository"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(destination)],
        check=True,
        timeout=600,
    )
    return destination


def test_coverage_data_file_is_declared_outside_any_worktree() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    data_file = config["tool"]["coverage"]["run"]["data_file"]

    assert Path(data_file).is_absolute()
    assert not str(ROOT) in data_file


def test_running_a_supported_command_with_coverage_leaves_the_worktree_clean(
    repo: Path, tmp_path: Path
) -> None:
    before = _status(repo)
    environment = dict(os.environ)
    environment.pop("COVERAGE_FILE", None)
    environment["PYTHONHASHSEED"] = "0"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            FAST_SUPPORTED_TARGET,
            "-q",
            "--cov=scripts",
            "--cov-report=",
            "--no-cov-on-fail",
        ],
        cwd=repo,
        env=environment,
        capture_output=True,
        text=True,
        timeout=900,
    )

    assert completed.returncode in (0, 1), completed.stdout[-2000:]
    assert not (repo / ".coverage").exists(), "le runner a ecrit .coverage dans l'arbre"
    assert _status(repo) == before, f"arbre sali par le runner:\n{_status(repo)}"
