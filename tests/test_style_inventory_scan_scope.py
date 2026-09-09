"""Le balayage de l'inventaire de style doit etre relatif a la racine du depot.

Le filtre d'exclusion s'appliquait aux segments du chemin ABSOLU. Un depot
place sous un repertoire nommé `.worktrees` -- exactement le cas de
`.worktrees/t3-publish-readiness` -- voyait donc chacun de ses fichiers
rejete, et l'inventaire publie comme preuve d'audit valait `[]`. Une preuve
qui affirme « aucun fichier de style » parce qu'elle s'est exclue elle-meme
est pire qu'une preuve absente.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_style_inventory.py"


def load(root: Path):
    spec = importlib.util.spec_from_file_location("build_style_inventory", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Un depot dont la racine est elle-meme situee sous un segment exclu."""
    root = tmp_path / ".worktrees" / "une-copie"
    (root / "gabarits").mkdir(parents=True)
    (root / "audit").mkdir()
    (root / "gabarits" / "nexus-charte-v6.sty").write_text("% v6.0.0\n", encoding="utf-8")
    (root / "gabarits" / "nexus-manuel-v5.cls").write_text("% v5.0.0\n", encoding="utf-8")
    return root


def test_a_repo_nested_under_an_excluded_segment_still_scans_its_own_files(repo):
    module = load(repo)
    paths = {row["path"] for row in module.scan_style_files()}
    assert paths == {"gabarits/nexus-charte-v6.sty", "gabarits/nexus-manuel-v5.cls"}


@pytest.mark.parametrize("excluded", [".worktrees", ".git", "Fiches_cours_exercices"])
def test_excluded_directories_inside_the_repo_are_still_skipped(repo, excluded):
    nested = repo / excluded / "gabarits"
    nested.mkdir(parents=True)
    (nested / "nexus-intrus.sty").write_text("% hors perimetre\n", encoding="utf-8")
    module = load(repo)
    paths = {row["path"] for row in module.scan_style_files()}
    assert not any(path.startswith(f"{excluded}/") for path in paths)
    assert "gabarits/nexus-charte-v6.sty" in paths


def test_the_report_never_states_a_generation_date_it_did_not_observe(repo):
    module = load(repo)
    module.main()
    report = (repo / "audit/LATEX_STYLE_INVENTORY.md").read_text(encoding="utf-8")
    inventory = json.loads((repo / "audit/LATEX_STYLE_INVENTORY.json").read_text(encoding="utf-8"))
    assert len(inventory) == 2
    assert "2026-08-15" not in report, "date de generation codee en dur"
    assert f"{len(inventory)}" in report
