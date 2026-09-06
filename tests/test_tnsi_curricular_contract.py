"""Le contrat TNSI se prouve par les capacités, jamais par un compte de chapitres.

Décision Release Owner du 2026-09-06 : `target_chapters: 12` n'est pas un
critère de publication. Ces tests vérifient que la substitution n'a pas
simplement supprimé une exigence — elle l'a remplacée par une exigence plus
forte, qui bloque sur du contenu réellement absent et non sur un découpage
éditorial.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import inventory_collection as ic  # noqa: E402

CONTRACT = "audit/TNSI_CURRICULAR_COVERAGE.json"


def test_chapter_count_is_no_longer_a_tnsi_criterion() -> None:
    spec = ic.DELIVERABLE_SPECS["TNSI"]
    assert spec["target_chapters"] is None
    assert spec["curricular_contract"] == CONTRACT


def test_a_missing_contract_blocks_instead_of_passing_silently(tmp_path: Path) -> None:
    """Fail-closed : sans preuve, la conformité n'est pas supposée."""
    blockers = ic._curricular_coverage_blockers(tmp_path, "TNSI", CONTRACT)
    assert [b["code"] for b in blockers] == ["couverture_curriculaire_non_prouvee"]


def test_an_unreadable_contract_blocks(tmp_path: Path) -> None:
    (tmp_path / "audit").mkdir()
    (tmp_path / CONTRACT).write_text("pas du json", encoding="utf-8")
    blockers = ic._curricular_coverage_blockers(tmp_path, "TNSI", CONTRACT)
    assert [b["code"] for b in blockers] == ["couverture_curriculaire_illisible"]


def _contract(tmp_path: Path, **summary) -> Path:
    (tmp_path / "audit").mkdir(parents=True, exist_ok=True)
    base = {
        "OFFICIAL_RUBRICS_UNCOVERED": [],
        "PROJECT_REQUIREMENT_COVERED": "YES",
        "PEDAGOGICAL_STRUCTURE_COHERENT": "YES",
        "OFFICIAL_CAPACITIES_UNCOVERED": 0,
        "OFFICIAL_CAPACITIES_TOTAL": 61,
    }
    base.update(summary)
    (tmp_path / CONTRACT).write_text(json.dumps({"summary": base}), encoding="utf-8")
    return tmp_path


def test_full_curricular_coverage_produces_no_blocker(tmp_path: Path) -> None:
    assert ic._curricular_coverage_blockers(_contract(tmp_path), "TNSI", CONTRACT) == []


def test_each_curricular_requirement_blocks_on_its_own(tmp_path: Path) -> None:
    """Aucune des quatre exigences n'est décorative."""
    cases = {
        "rubriques_officielles_non_couvertes": {"OFFICIAL_RUBRICS_UNCOVERED": ["ALGORITHMIQUE"]},
        "demarche_de_projet_non_couverte": {"PROJECT_REQUIREMENT_COVERED": "NO"},
        "structure_pedagogique_incoherente": {"PEDAGOGICAL_STRUCTURE_COHERENT": "NO"},
        "capacites_officielles_non_couvertes": {"OFFICIAL_CAPACITIES_UNCOVERED": 10},
    }
    for expected_code, mutation in cases.items():
        root = _contract(tmp_path / expected_code, **mutation)
        codes = [b["code"] for b in ic._curricular_coverage_blockers(root, "TNSI", CONTRACT)]
        assert codes == [expected_code], (expected_code, codes)


def test_the_real_contract_is_evaluated_and_no_longer_counts_chapters() -> None:
    """Le critère appliqué est curriculaire, quel que soit son verdict du jour.

    La couverture TNSI est aujourd'hui complète (61/61) une fois les codes
    locaux résolus, donc aucun blocage curriculaire ne subsiste. Ce test ne
    fige pas ce verdict — il vérifie que le critère évalué est bien celui des
    capacités, et jamais un comptage de chapitres. Les quatre exigences sont
    éprouvées une à une par `test_each_curricular_requirement_blocks_on_its_own`.
    """
    codes = [b["code"] for b in ic._curricular_coverage_blockers(ROOT, "TNSI", CONTRACT)]
    assert "chapitres_manquants" not in codes
    assert "objectif_chapitres_non_fige" not in codes
    assert set(codes) <= {
        "rubriques_officielles_non_couvertes",
        "demarche_de_projet_non_couverte",
        "structure_pedagogique_incoherente",
        "capacites_officielles_non_couvertes",
    }


def test_the_contract_is_reachable_through_the_deliverable_matrix() -> None:
    """Le chemin complet doit fonctionner, pas seulement l'helper isolé.

    Les premiers tests appelaient `_curricular_coverage_blockers` directement
    et passaient alors que `build_deliverable_matrix` levait un NameError :
    `root` n'était pas dans la portée de `_manual_blockers`. On exerce donc
    l'appelant réel.
    """
    inventory = ic._build_inventory_for_stale_manifest_invalidation(ROOT)
    codes = [b["code"] for b in inventory["deliverable_matrix"]["manuals"]["TNSI"]["blockers"]]
    assert "chapitres_manquants" not in codes
    assert "objectif_chapitres_non_fige" not in codes


def test_build_deliverable_matrix_still_accepts_a_lone_inventory() -> None:
    """Les appelants historiques ne passent que l'inventaire : ils doivent tenir."""
    inventory = ic._build_inventory_for_stale_manifest_invalidation(ROOT)
    matrix = ic.build_deliverable_matrix(inventory)
    assert "TNSI" in matrix["manuals"]
