"""Le gate anti-charte-legacy doit juger un chargement, pas une mention.

Deux defauts le rendaient inutilisable. Il filtrait `.worktrees` sur les
segments du chemin ABSOLU : execute depuis `.worktrees/t3-publish-readiness`,
ou vivait toute la production, il analysait zero fichier et concluait SUCCESS.
Et il signalait les scripts qui nomment le motif legacy pour l'exclure ou le
detecter, faux positifs qu'une liste blanche de noms de fichiers masquait.

Le gate interdit de CHARGER l'ancien moteur dans les chemins de compilation.
Ce qu'il doit donc reconnaitre est une directive de chargement.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_no_legacy_charter_refs.py"


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_no_legacy_charter_refs", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Racine placee sous un segment exclu, comme le worktree de production."""
    root = tmp_path / ".worktrees" / "une-copie"
    (root / "gabarits").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "gabarits" / "nexus-manuel-v5.cls").write_text(
        "\\LoadClass{book}\n\\RequirePackage{nexus-charte-v6}\n", encoding="utf-8")
    return root


def test_the_gate_scans_a_repo_nested_under_an_excluded_segment(repo):
    module = load(repo)
    violations, scanned = module.check_legacy_refs_detail()
    assert scanned > 0, "un depot sous .worktrees ne doit pas s'auto-exclure"
    assert violations == []


@pytest.mark.parametrize("directive", [
    "\\documentclass{nexus-manuel-v4}",
    "\\LoadClass{nexus-manuel-v4}",
    "\\usepackage{gabarits/v4/charte}",
    "\\RequirePackage{reference-v4/manuel}",
    "\\input{gabarits/v4/preambule}",
])
def test_an_actual_legacy_load_is_a_violation(repo, directive):
    (repo / "gabarits" / "nexus-manuel-v5.cls").write_text(directive + "\n", encoding="utf-8")
    module = load(repo)
    violations, _ = module.check_legacy_refs_detail()
    assert len(violations) == 1, violations


@pytest.mark.parametrize("emitted", [
    'lines.append("\\\\usepackage{reference-v4/manuel}")',
    'master.write("\\\\documentclass{nexus-manuel-v4}")',
])
def test_a_loader_emitted_by_an_assembler_is_a_violation(repo, emitted):
    (repo / "scripts" / "assemble.py").write_text(emitted + "\n", encoding="utf-8")
    module = load(repo)
    violations, _ = module.check_legacy_refs_detail()
    assert len(violations) == 1, violations


@pytest.mark.parametrize("policing", [
    'if "reference-v4" not in path.parts:  # maquette historique, rien ne la compose',
    'LEGACY = re.compile(r"(^|/)gabarits/reference-v4/")',
    'legacy_loaded = [p for p in inputs if "nexus-manuel-v4" in p.as_posix()]',
    '"""`reference-v4` est une maquette historique que rien ne compose."""',
])
def test_naming_the_legacy_pattern_in_order_to_exclude_it_is_not_a_violation(repo, policing):
    (repo / "scripts" / "police.py").write_text(policing + "\n", encoding="utf-8")
    module = load(repo)
    violations, _ = module.check_legacy_refs_detail()
    assert violations == [], violations


def test_the_gate_carries_no_allowlist_of_its_own_policemen():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "build_style_inventory.py" not in source, "liste blanche de noms de fichiers"


def test_directories_excluded_inside_the_repo_are_still_skipped(repo):
    for excluded in (".worktrees", "archive", ".git"):
        target = repo / excluded / "gabarits"
        target.mkdir(parents=True)
        (target / "vieux.cls").write_text("\\LoadClass{nexus-manuel-v4}\n", encoding="utf-8")
    module = load(repo)
    violations, _ = module.check_legacy_refs_detail()
    assert violations == [], violations
