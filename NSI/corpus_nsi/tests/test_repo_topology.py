from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_repo_topology_policy_document_names_canonical_boundaries() -> None:
    policy = ROOT / "docs" / "repo_topology.md"

    text = policy.read_text(encoding="utf-8")

    for expected in (
        "dépôt canonique",
        "nsi-enseignement/",
        "scrapping_NSI/ressources_nsi_centralisees",
        "scrapping_NSI/ressources_nsi_extraites",
        "scrapping_NSI/ressources_nsi_extraites_v2",
        "scrapping_NSI/sqlite_data",
        "archives livrables",
        "index RAG",
    ):
        assert expected in text


def test_check_repo_topology_passes_current_workspace() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.check_repo_topology"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stdout


def test_check_repo_topology_accepts_github_actions_checkout_name(tmp_path: Path) -> None:
    from scripts.check_repo_topology import analyze_topology

    repo = tmp_path / "NSI"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "remote", "add", "origin", "https://github.com/cyranoaladin/NSI.git")

    result = analyze_topology(repo_root=repo, parent_root=tmp_path)

    assert "dépôt canonique inattendu" not in "\n".join(result.errors)


def test_check_repo_topology_detects_tracked_nested_repo_and_mirrors(tmp_path: Path) -> None:
    from scripts.check_repo_topology import analyze_topology

    parent = tmp_path / "parent"
    parent.mkdir()
    _git(parent, "init")
    _git(parent, "config", "user.email", "tests.invalid")
    _git(parent, "config", "user.name", "Tests")
    child = parent / "nsi-enseignement"
    (child / "docs").mkdir(parents=True)
    (child / "docs" / "repo_topology.md").write_text(
        "dépôt canonique nsi-enseignement/\n",
        encoding="utf-8",
    )
    (child / ".git").mkdir()
    tracked_nested_file = child / "README.md"
    tracked_nested_file.write_text("tracked nested repo\n", encoding="utf-8")
    mirror = parent / "scrapping_NSI" / "ressources_nsi_centralisees" / "data.txt"
    mirror.parent.mkdir(parents=True)
    mirror.write_text("mirror\n", encoding="utf-8")
    _git(parent, "add", "nsi-enseignement/README.md", "scrapping_NSI/ressources_nsi_centralisees/data.txt")
    _git(parent, "commit", "-m", "bad topology")

    result = analyze_topology(repo_root=child, parent_root=parent)

    joined = "\n".join(result.errors)
    assert "nsi-enseignement/ est suivi par Git dans le dépôt parent" in joined
    assert "scrapping_NSI/ressources_nsi_centralisees est suivi par Git" in joined
    assert "politique versionnée" in joined
