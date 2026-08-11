"""Tests attendus TP T08. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib, os
MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T08_starter_bfs_dfs_cycles_chemins"))
GRAPHE = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A"], "D": ["B"]}
CYCLE = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}


def test_nominal_bfs_chemin() -> None:
    pred = MODULE.bfs_predecesseurs(GRAPHE, "A")
    assert pred["D"] == "B"
    assert MODULE.reconstruire_chemin(pred, "A", "D") == ["A", "B", "D"]


def test_limite_cycle_et_absent() -> None:
    assert MODULE.detecter_cycle_non_oriente(CYCLE) is True
    assert MODULE.reconstruire_chemin({"A": None}, "A", "Z") == []


def test_invalide_depart_absent() -> None:
    try:
        MODULE.bfs_predecesseurs(GRAPHE, "Z")
    except ValueError:
        return
    raise AssertionError("ValueError attendue")

if __name__ == "__main__":
    test_nominal_bfs_chemin(); test_limite_cycle_et_absent(); test_invalide_depart_absent(); print("tests attendus OK")
