"""Ce dépôt porte six manuels ; une collection étrangère n'y est pas suivie.

Le 10 septembre 2026, un `git add -A` a fait entrer 58 Mo de PDF, d'archives et
de documentation HGGSP dans l'arbre actif, par un répertoire `HLP/` apparu à la
racine. Aucun script, test ou manifeste des six manuels n'en dépendait.

Le gate juge l'INDEX, jamais le disque : un dossier non suivi ne gêne personne,
et l'instance HGGSP travaille dans son propre chantier, qu'il ne faut pas
toucher.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_repository_scope.py"


def load():
    spec = importlib.util.spec_from_file_location("check_repository_scope", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un dépôt minimal portant un manuel canonique."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "NSI" / "chapitres").mkdir(parents=True)
    (tmp_path / "NSI" / "chapitres" / "cours.tex").write_text("Un cours.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "socle"], cwd=tmp_path, check=True)
    return tmp_path


def test_the_six_canonical_manuals_are_declared() -> None:
    module = load()
    assert set(module.CANONICAL_MANUALS) == {
        "1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES", "1NSI", "TNSI",
    }


def test_a_repository_holding_only_its_manuals_passes(depot: Path) -> None:
    module = load()
    assert module.foreign_tracked(depot) == {}
    assert module.main(["--root", str(depot)]) == 0


@pytest.mark.parametrize("racine", ["HLP", "HGGSP", "_SAUVEGARDES_HGGSP", "AUDIT_HGGSP_20260909T1"])
def test_mutation_g_a_tracked_foreign_collection_fails_the_gate(depot: Path, racine: str) -> None:
    """Mutation G : une collection étrangère suivie doit faire échouer le gate."""
    intrus = depot / racine / "90_HGGSP"
    intrus.mkdir(parents=True)
    (intrus / "manuel.pdf").write_text("%PDF-1.5\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=depot, check=True)

    module = load()
    trouve = module.foreign_tracked(depot)
    assert racine in trouve, f"{racine}/ suivi mais non détecté"
    assert module.main(["--root", str(depot)]) == 1


@pytest.mark.parametrize("racine", ["HLP", "HGGSP"])
def test_an_untracked_foreign_directory_is_not_a_violation(depot: Path, racine: str) -> None:
    """Le chantier indépendant d'une autre instance ne regarde pas ce dépôt."""
    intrus = depot / racine
    intrus.mkdir()
    (intrus / "manuel.pdf").write_text("%PDF-1.5\n", encoding="utf-8")
    # Volontairement PAS de `git add` : le dossier existe, il n'est pas suivi.
    module = load()
    assert module.foreign_tracked(depot) == {}
    assert module.main(["--root", str(depot)]) == 0


def test_the_real_repository_holds_no_foreign_collection() -> None:
    module = load()
    trouve = module.foreign_tracked(ROOT)
    assert trouve == {}, f"collections étrangères suivies : {sorted(trouve)}"
