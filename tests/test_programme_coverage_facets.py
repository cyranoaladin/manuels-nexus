"""Une facette sans alias officiel ne cree pas d'exigence, et ne disparait pas.

Trois capacites de 1SPE-SECOND-DEGRE (C2, C5, C6) ne portent pas de
`ref_capacite` : elles declarent `sans_alias_officiel`, c'est-a-dire qu'elles
sont des FACETTES pedagogiques d'une capacite officielle unique, portee par un
autre code local. Leur donner chacune la reference officielle la crediterait
plusieurs fois ; les ignorer perdrait la preuve que les objets qui les portent
travaillent bien cette capacite officielle.

Le generateur de la matrice, ecrit avant l'introduction de cette categorie,
levait KeyError('ref_capacite') et ne produisait plus aucune matrice.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_programme_coverage_matrix.py"

CONTRACT = {
    "chapitre": "1SPE-SECOND-DEGRE",
    "capacites": [
        {"code": "C1", "ref_capacite": "1SPE-SECOND-DEGRE-2026-C4", "libelle_eleve": "Portee."},
        {"code": "C2", "libelle_eleve": "Facette sommet.",
         "sans_alias_officiel": {"facette_de": "1SPE-SECOND-DEGRE-2026-C4", "porte_par": "C1"}},
    ],
}


def load(root: Path):
    spec = importlib.util.spec_from_file_location("build_programme_coverage_matrix", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    chapter = tmp_path / "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE"
    (chapter / "exercices").mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(yaml.safe_dump(CONTRACT, allow_unicode=True), encoding="utf-8")
    (chapter / "exercices" / "EX-001.tex").write_text(
        '% META: {"id": "EX-001", "capacites_codes": ["C2"]}\nEnonce.\n', encoding="utf-8")
    return tmp_path


CONFIG = {"root": "Mathematiques/manuel-maths", "chapter_prefix": "1SPE-"}


def test_loading_contracts_no_longer_fails_on_a_facet(repo):
    module = load(repo)
    by_ref, _ = module.load_contracts(CONFIG)
    assert "1SPE-SECOND-DEGRE-2026-C4" in by_ref
    assert by_ref["1SPE-SECOND-DEGRE-2026-C4"]["contract_capacity"] == "C1"


def test_a_facet_never_becomes_a_separate_official_requirement(repo):
    module = load(repo)
    by_ref, _ = module.load_contracts(CONFIG)
    assert len(by_ref) == 1, "la facette ne doit pas creer une seconde exigence"
    assert "C2" not in by_ref


def test_the_facet_is_reported_with_the_capacity_it_is_a_facet_of(repo):
    module = load(repo)
    _, extras = module.load_contracts(CONFIG)
    facets = [row for row in extras if row.get("facet_of")]
    assert len(facets) == 1
    assert facets[0]["contract_capacity"] == "C2"
    assert facets[0]["facet_of"] == "1SPE-SECOND-DEGRE-2026-C4"
    assert facets[0]["carried_by"] == "C1"


def test_evidence_tagged_with_a_facet_credits_the_official_capacity(repo):
    module = load(repo)
    evidence = module.build_evidence(CONFIG)
    assert "1SPE-SECOND-DEGRE-2026-C4" in evidence, "la preuve de la facette est perdue"
    assert "C2" not in evidence, "un code local ne doit pas devenir une reference officielle"
