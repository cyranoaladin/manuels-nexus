"""Preuve adversariale des trois digests : on mute, on regarde qui bouge.

Un digest unique confondait deux questions : « le contenu enseigné a-t-il
changé ? » et « le rendu a-t-il changé ? ». Une couleur de charte périmait
alors la validation scientifique d'un chapitre, tandis qu'un manifeste de
livre — qui décide de la liste et de l'ordre des chapitres — n'entrait dans
aucun digest, alors qu'il décide de ce que l'élève lit.

Chaque test mute une seule chose et vérifie exactement qui bouge. Un modèle
qu'on n'attaque pas ne prouve rien.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evidence_freshness.py"


def load():
    spec = importlib.util.spec_from_file_location("evidence_freshness_mutation", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def depot(tmp_path: Path):
    """Un dépôt minimal portant une source de chaque famille."""
    def ecrire(relatif: str, contenu: str) -> Path:
        chemin = tmp_path / relatif
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(contenu, encoding="utf-8")
        return chemin

    ecrire("NSI/chapitres/1NSI-TABLES/cours/01_cours.tex",
           "% META: {\"id\": \"C1\"}\nUne table est une liste de dictionnaires.\n")
    ecrire("NSI/manifests/books/TNSI.json",
           json.dumps({"chapitres": ["TNSI-ALGO", "TNSI-BDD"]}, indent=2) + "\n")
    ecrire("NSI/scripts/assemble_manuel.py",
           "VARIANTES = {'eleve': ('cours', 'exercices'), 'professeur': ('cours', 'corriges')}\n")
    ecrire("gabarits/common/nexus-charte.sty", "\\definecolor{nexusbleu}{HTML}{1F4E79}\n")
    ecrire("requirements-ci-audit.txt", "pytest==9.0.2\n")
    ecrire("audit/foo.md", "# Un rapport d'audit\n")

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "socle"], cwd=tmp_path, check=True)

    module = load()
    avant = {
        "CONTENT": module.content_semantic_digest(tmp_path, module.WORKTREE),
        "RENDER": module.render_source_digest(tmp_path, module.WORKTREE),
        "TOOLCHAIN": module.toolchain_digest(tmp_path, module.WORKTREE),
    }
    return tmp_path, module, avant, ecrire


def apres(module, racine: Path) -> dict[str, str]:
    return {
        "CONTENT": module.content_semantic_digest(racine, module.WORKTREE),
        "RENDER": module.render_source_digest(racine, module.WORKTREE),
        "TOOLCHAIN": module.toolchain_digest(racine, module.WORKTREE),
    }


def test_mutation_a_a_report_alone_moves_nothing(depot) -> None:
    """A — un rapport d'audit n'enseigne rien et n'imprime rien."""
    racine, module, avant, ecrire = depot
    ecrire("audit/foo.md", "# Un rapport d'audit\n\nUne phrase de plus.\n")
    assert apres(module, racine) == avant


def test_mutation_b_a_course_sentence_moves_content_only(depot) -> None:
    """B — modifier une phrase de cours change ce que l'élève lit."""
    racine, module, avant, ecrire = depot
    ecrire("NSI/chapitres/1NSI-TABLES/cours/01_cours.tex",
           "% META: {\"id\": \"C1\"}\nUne table est une liste d'enregistrements.\n")
    obtenu = apres(module, racine)
    assert obtenu["CONTENT"] != avant["CONTENT"]
    assert obtenu["RENDER"] == avant["RENDER"]
    assert obtenu["TOOLCHAIN"] == avant["TOOLCHAIN"]


def test_mutation_c_swapping_two_chapters_in_a_manifest_moves_content(depot) -> None:
    """C — l'ordre des chapitres est du contenu, pas de la mise en forme."""
    racine, module, avant, ecrire = depot
    ecrire("NSI/manifests/books/TNSI.json",
           json.dumps({"chapitres": ["TNSI-BDD", "TNSI-ALGO"]}, indent=2) + "\n")
    obtenu = apres(module, racine)
    assert obtenu["CONTENT"] != avant["CONTENT"], (
        "inverser deux chapitres d'un manifeste ne change pas le digest de contenu"
    )
    assert obtenu["RENDER"] == avant["RENDER"]


def test_mutation_d_a_charter_colour_moves_render_only(depot) -> None:
    """D — une couleur ne doit pas périmer une validation scientifique."""
    racine, module, avant, ecrire = depot
    ecrire("gabarits/common/nexus-charte.sty", "\\definecolor{nexusbleu}{HTML}{2E75B6}\n")
    obtenu = apres(module, racine)
    assert obtenu["CONTENT"] == avant["CONTENT"], (
        "une couleur de charte a perime la preuve de contenu"
    )
    assert obtenu["RENDER"] != avant["RENDER"]
    assert obtenu["TOOLCHAIN"] == avant["TOOLCHAIN"]


def test_mutation_e_a_teacher_leak_in_the_student_edition_moves_content(depot) -> None:
    """E — la règle de variante décide de ce que l'élève voit : c'est du contenu."""
    racine, module, avant, ecrire = depot
    ecrire("NSI/scripts/assemble_manuel.py",
           "VARIANTES = {'eleve': ('cours', 'exercices', 'corriges'), "
           "'professeur': ('cours', 'corriges')}\n")
    obtenu = apres(module, racine)
    assert obtenu["CONTENT"] != avant["CONTENT"], (
        "faire entrer les corrigés dans l'édition élève n'a pas bougé le contenu"
    )
    assert obtenu["RENDER"] == avant["RENDER"]


def test_mutation_f_a_dependency_version_moves_toolchain_only(depot) -> None:
    """F — épingler autrement ne change ni le cours ni sa mise en page."""
    racine, module, avant, ecrire = depot
    ecrire("requirements-ci-audit.txt", "pytest==9.0.3\n")
    obtenu = apres(module, racine)
    assert obtenu["CONTENT"] == avant["CONTENT"]
    assert obtenu["RENDER"] == avant["RENDER"]
    assert obtenu["TOOLCHAIN"] != avant["TOOLCHAIN"]


def test_no_path_belongs_to_two_families() -> None:
    """Un chemin classé deux fois rendrait tout verdict ambigu."""
    module = load()
    suivis = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    doubles = {p: sorted(module.classify(p)) for p in suivis if len(module.classify(p)) > 1}
    assert not doubles, f"chemins classés dans deux familles : {list(doubles)[:5]}"


def test_the_book_manifests_are_content_not_render() -> None:
    """Le manque exact que ce modèle corrige."""
    module = load()
    for manifeste in ("NSI/manifests/books/1NSI.json", "NSI/manifests/books/TNSI.json"):
        assert module.classify(manifeste) == {"CONTENT"}, manifeste
