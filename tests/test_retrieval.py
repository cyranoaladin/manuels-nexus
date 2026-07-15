"""20 requêtes de test pour valider la précision de la recherche hybride (critère 2 du CDC).
Nécessite la base indexée ; skip sinon."""
import os

import pytest

pytestmark = pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="base non configurée")

QUERIES = [
    ("montrer qu'une suite est géométrique", "exercice"),
    ("somme des premiers termes suite géométrique démonstration", "cours"),
    ("erreur fréquente suites arithmétiques rapport jury", "erreur_type"),
    ("algorithme seuil boucle while suite", "exercice"),
    ("activité introduction suites intérêts composés", "activite"),
    # ... compléter jusqu'à 20 lors du LOT 1
]


@pytest.mark.parametrize("query,expected_type", QUERIES)
def test_topk_contains_type(query, expected_type):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp" / "mcp_corpus"))
    from server import search_corpus
    results = search_corpus(query, top_k=10)
    assert any(r["type"] == expected_type for r in results), f"type {expected_type} absent du top 10"
