"""Une modalité d'évaluation déclarée doit encore prouver une évaluation réelle.

Décision Release Owner : TNSI-PROJET est évalué par son projet et sa grille
critériée, non par deux devoirs écrits. Le risque de cette souplesse serait
qu'un chapitre échappe à toute évaluation en déclarant simplement un régime.
Le gate lit donc la grille : critères, poids totalisant 100 %, preuve attendue
en regard de chacun. Un fichier au bon nom mais vide échoue.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assessment_modes as modes  # noqa: E402
import build_publish_readiness_chapter_matrix as matrix  # noqa: E402

PROJECT_CHAPTER = ROOT / "NSI/chapitres/TNSI-PROJET"
GRID_SOURCE = PROJECT_CHAPTER / "projet/TNSI-PROJET-ANNUEL.tex"


def _grid(rows: list[tuple[str, int, str]]) -> str:
    body = ["\\subsection*{Grille d'évaluation}", "\\begin{tabular}{|l|l|l|}", "\\hline"]
    for criterion, weight, evidence in rows:
        body.append(f"{criterion} & {weight}\\,\\% & {evidence} \\\\")
        body.append("\\hline")
    body.append("\\end{tabular}")
    return "\n".join(body)


# --- État de référence --------------------------------------------------------

def test_the_project_chapter_declares_the_project_mode() -> None:
    assert matrix._declared_assessment_mode(PROJECT_CHAPTER) == modes.PROJECT_ASSESSMENT


def test_other_chapters_keep_the_written_default() -> None:
    """La souplesse ne doit pas se propager : les autres restent à l'écrit."""
    for chapter in (
        "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE",
        "NSI/chapitres/TNSI-ALGORITHMIQUE",
    ):
        assert matrix._declared_assessment_mode(ROOT / chapter) == modes.WRITTEN_ASSESSMENT


def test_a_valid_grid_without_any_written_paper_is_green() -> None:
    """Mutation 2 : grille valide, aucun devoir écrit -> couverture verte."""
    result = matrix._project_assessment(
        "TNSI-PROJET", PROJECT_CHAPTER, modes.PROJECT_ASSESSMENT
    )
    assert result["status"] == "COMPLETE"
    assert result["criteria_grid_violations"] == []
    assert result["subjects"] == []


def test_the_real_grid_is_exploitable() -> None:
    rows = modes.parse_criteria_grid(GRID_SOURCE.read_text(encoding="utf-8"))
    assert len(rows) >= modes.MIN_CRITERIA
    assert sum(row["weight"] for row in rows) == modes.WEIGHT_TOTAL
    assert all(row["evidence"] for row in rows)


# --- Mutations ----------------------------------------------------------------

def test_removing_the_grid_turns_coverage_red(tmp_path: Path) -> None:
    """Mutation 1 : plus de grille -> rouge."""
    chapter = tmp_path / "TNSI-PROJET"
    (chapter / "projet").mkdir(parents=True)
    result = matrix._project_assessment("TNSI-PROJET", chapter, modes.PROJECT_ASSESSMENT)
    assert result["status"] == "GAP"
    assert result["criteria_grid_violations"]


def test_an_empty_grid_file_turns_coverage_red(tmp_path: Path) -> None:
    """Mutation 3 : faux fichier de grille sans contenu -> rouge."""
    chapter = tmp_path / "TNSI-PROJET"
    (chapter / "projet").mkdir(parents=True)
    (chapter / "projet/TNSI-PROJET-ANNUEL.tex").write_text(
        "\\subsection*{Grille d'évaluation}\n", encoding="utf-8"
    )
    result = matrix._project_assessment("TNSI-PROJET", chapter, modes.PROJECT_ASSESSMENT)
    assert result["status"] == "GAP"


def test_an_inconsistent_total_turns_coverage_red(tmp_path: Path) -> None:
    """Mutation 4 : total incohérent -> rouge."""
    chapter = tmp_path / "TNSI-PROJET"
    (chapter / "projet").mkdir(parents=True)
    (chapter / "projet/p.tex").write_text(
        _grid([("Cadrage", 30, "Cahier des charges"),
               ("Produit", 30, "Version exécutable"),
               ("Tests", 30, "Rapport de tests")]),
        encoding="utf-8",
    )
    result = matrix._project_assessment("TNSI-PROJET", chapter, modes.PROJECT_ASSESSMENT)
    assert result["status"] == "GAP"
    assert any("90%" in v for v in result["criteria_grid_violations"])


def test_a_criterion_without_expected_evidence_turns_coverage_red(tmp_path: Path) -> None:
    chapter = tmp_path / "TNSI-PROJET"
    (chapter / "projet").mkdir(parents=True)
    (chapter / "projet/p.tex").write_text(
        _grid([("Cadrage", 50, "Cahier des charges"),
               ("Produit", 30, ""),
               ("Tests", 20, "Rapport de tests")]),
        encoding="utf-8",
    )
    result = matrix._project_assessment("TNSI-PROJET", chapter, modes.PROJECT_ASSESSMENT)
    assert result["status"] == "GAP"
    assert any("sans preuve attendue" in v for v in result["criteria_grid_violations"])


def test_a_grid_with_too_few_criteria_turns_coverage_red(tmp_path: Path) -> None:
    chapter = tmp_path / "TNSI-PROJET"
    (chapter / "projet").mkdir(parents=True)
    (chapter / "projet/p.tex").write_text(
        _grid([("Produit", 100, "Version exécutable")]), encoding="utf-8"
    )
    result = matrix._project_assessment("TNSI-PROJET", chapter, modes.PROJECT_ASSESSMENT)
    assert result["status"] == "GAP"
    assert any("trop pauvre" in v for v in result["criteria_grid_violations"])


# --- Garde de vocabulaire -----------------------------------------------------

def test_an_unknown_mode_falls_back_to_written(tmp_path: Path) -> None:
    """Un régime inventé ne dispense de rien."""
    assert modes.declared_mode({"assessment_mode": "AUCUNE"}) == modes.WRITTEN_ASSESSMENT
    assert modes.declared_mode({}) == modes.WRITTEN_ASSESSMENT
    assert modes.declared_mode({"assessment_mode": "project_assessment"}) == (
        modes.PROJECT_ASSESSMENT
    )
