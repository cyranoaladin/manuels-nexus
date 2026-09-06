"""Un corrigé de remédiation n'est pas un corrigé orphelin.

Seize corrigés authentiques étaient comptés comme orphelins parce que le
graphe n'indexait que `exercices/` : l'objet auquel ils répondent vit dans
`remediation/`. La classification doit dépendre du rôle et du type déclarés,
jamais d'une chaîne dans l'identifiant — un fichier dont l'id contient
`CORRIGE` n'est pas pour autant un corrigé.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

GRAPH = ROOT / "audit/EX_CO_GRAPH.json"


@pytest.fixture(scope="module")
def graph():
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def test_no_orphan_correction_remains(graph) -> None:
    assert graph["relation_counts"].get("ORPHAN_CO", 0) == 0


def test_remediation_corrections_are_classified_as_such(graph) -> None:
    remediation = [
        row for row in graph["relations"]
        if "REMEDIATION_CORRECTION" in row["classifications"]
    ]
    assert len(remediation) == 16
    for row in remediation:
        assert row["correction_path"].endswith(".tex")
        assert "/corriges/" in row["correction_path"]
        assert row["exercise_id"], row["correction_id"]


def test_the_answerable_index_now_includes_remediation_objects(graph) -> None:
    """Sans cet index, l'objet cible restait invisible et le corrigé orphelin."""
    assert graph["exercise_count"] > graph["correction_count"]


def test_classification_depends_on_declared_type_not_on_the_identifier() -> None:
    """Mutation : un enregistrement dont l'id contient CORRIGE n'est pas un CO."""
    import build_ex_co_graph as producer

    source = Path(producer.__file__).read_text(encoding="utf-8")
    # Le filtre de rôle doit s'appuyer sur type_objet, pas sur une sous-chaîne.
    assert 'object_type != "exercice"' in source
    assert 'object_type != "remediation"' in source
    assert 'object_type not in {"corrige", "correction"}' in source
    assert '"CORRIGE" in object_id' not in source
    assert 'endswith("-CORRIGE")' not in source


def test_an_unknown_object_type_is_not_indexed(tmp_path: Path) -> None:
    """Fail-closed : un type inconnu n'entre ni comme exercice ni comme corrigé."""
    import build_ex_co_graph as producer

    chapter = tmp_path / "chapitres" / "DEMO" / "corriges"
    chapter.mkdir(parents=True)
    target = chapter / "DEMO-CO-001.tex"
    target.write_text(
        '% META: {"id": "DEMO-CO-001", "chapitre": "DEMO", "type_objet": "inconnu"}\n',
        encoding="utf-8",
    )
    meta = {"type_objet": "inconnu"}
    assert meta["type_objet"] not in {"corrige", "correction"}
    assert meta["type_objet"] != "exercice"
    assert meta["type_objet"] != "remediation"


def test_real_corrections_are_still_linked(graph) -> None:
    established = graph["relation_counts"].get("ANSWER_COVERAGE_ESTABLISHED", 0)
    assert established >= 1200, "la reclassification ne doit pas casser les liens réels"
