"""Vérification exécutable des trois fiches méthode 1NSI réécrites après qualification.

`QUALIFICATION_STALENESS_FORENSICS` classe trois qualifications A4 en
`PEDAGOGICAL_CONTENT_CHANGE` : leur corps a réellement changé depuis la revue
humaine (critère glouton trié, départage kNN, dichotomie renvoyant `-1`).

Ces tests n'approuvent rien — l'approbation reste humaine (§24). Ils
établissent une preuve *reproductible* que le code imprimé dans ces fiches est
scientifiquement correct : le code est extrait du `.tex` lui-même, exécuté, et
confronté à un oracle indépendant. Si une fiche est réécrite, la preuve est
rejouée.
"""

from __future__ import annotations

import random
import re
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/methodes"


def load_python_block(sheet: str) -> dict:
    """Exécute le bloc `\\begin{python}` imprimé dans la fiche et rend son espace de noms."""
    text = (CHAPTER / f"{sheet}.tex").read_text(encoding="utf-8")
    blocks = re.findall(r"\\begin\{python\}\n(.*?)\\end\{python\}", text, re.S)
    assert blocks, f"aucun bloc python imprimé dans {sheet}"
    namespace: dict = {}
    # Les lignes d'appel commentées en fin de bloc servent d'exemples ; on
    # exécute le bloc entier, elles sont sans effet de bord.
    exec(compile(blocks[0], f"{sheet}.tex", "exec"), namespace)
    return namespace


# --- M1 : recherche dichotomique ---------------------------------------------

@pytest.fixture(scope="module")
def dichotomie():
    return load_python_block("1NSI-ADGK-ME-001")["recherche_dichotomique"]


def test_dichotomie_matches_printed_examples(dichotomie) -> None:
    t = [2, 5, 7, 11, 13, 17, 19, 23]
    assert dichotomie(t, 13) == 4
    assert dichotomie(t, 4) == -1


def test_dichotomie_edge_cases(dichotomie) -> None:
    assert dichotomie([], 9) == -1, "tableau vide"
    assert dichotomie([5], 5) == 0, "singleton présent"
    assert dichotomie([5], 4) == -1, "singleton absent"


def test_dichotomie_bounds(dichotomie) -> None:
    t = [2, 5, 7, 11, 13, 17, 19, 23]
    assert dichotomie(t, 2) == 0, "première case"
    assert dichotomie(t, 23) == 7, "dernière case"
    assert dichotomie(t, 1) == -1, "sous la borne inférieure"
    assert dichotomie(t, 99) == -1, "au-dessus de la borne supérieure"


def test_dichotomie_with_duplicates_returns_a_valid_index(dichotomie) -> None:
    """Le tableau trié peut contenir des doublons : la fiche ne promet pas
    la *première* occurrence, seulement *une* occurrence correcte."""
    t = [1, 3, 3, 3, 5, 5, 9]
    for value in (1, 3, 5, 9):
        index = dichotomie(t, value)
        assert index != -1 and t[index] == value, (value, index)
    assert dichotomie(t, 4) == -1


def test_dichotomie_agrees_with_an_independent_oracle(dichotomie) -> None:
    rng = random.Random(20260906)
    for _ in range(4000):
        array = sorted(rng.sample(range(30), rng.randint(0, 12)))
        value = rng.randint(0, 30)
        expected = array.index(value) if value in array else -1
        assert dichotomie(array, value) == expected, (array, value)


def test_dichotomie_variant_strictly_decreases() -> None:
    """La fiche affirme le variant $7 \\to 3 \\to 0$ : on le rejoue."""
    t = [2, 5, 7, 11, 13, 17, 19, 23]
    g, d, trace = 0, len(t) - 1, [len(t) - 1]
    while g <= d:
        m = (g + d) // 2
        if t[m] == 13:
            break
        if t[m] < 13:
            g = m + 1
        else:
            d = m - 1
        trace.append(d - g)
    assert trace == [7, 3, 0]
    assert all(b < a for a, b in zip(trace, trace[1:])), "variant non strictement décroissant"


# --- M2 : rendu de monnaie glouton -------------------------------------------

@pytest.fixture(scope="module")
def rendu():
    return load_python_block("1NSI-ADGK-ME-002")["rendu_monnaie"]


EURO = (200, 100, 50, 20, 10, 5, 2, 1)


def _minimal_coin_count(amount: int, coins: tuple[int, ...]) -> int:
    """Oracle indépendant du glouton : programmation dynamique exacte."""
    best = [0] + [float("inf")] * amount
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and best[value - coin] + 1 < best[value]:
                best[value] = best[value - coin] + 1
    return best[amount]


def test_rendu_matches_printed_example(rendu) -> None:
    assert rendu(263) == [200, 50, 10, 2, 1]
    assert sum(rendu(263)) == 263 and len(rendu(263)) == 5


def test_rendu_is_exact_for_every_amount(rendu) -> None:
    assert rendu(0) == []
    for amount in range(501):
        assert sum(rendu(amount)) == amount


def test_greedy_is_optimal_on_the_canonical_euro_system(rendu) -> None:
    """Portée exacte de la preuve : système euro canonique, montants 0 à 500.

    La fiche n'affirme l'optimalité que pour un système *canonique*, et la
    donne comme fausse en général. Ce test vérifie donc une propriété bornée
    — il ne l'étend pas à d'autres systèmes ni au-delà de 500 centimes.
    """
    for amount in range(501):
        assert len(rendu(amount)) == _minimal_coin_count(amount, EURO), amount


def test_printed_counterexample_is_genuine(rendu) -> None:
    """La fiche donne $\\{1,3,4\\}$ et 6 comme contre-exemple d'optimalité.

    Un contre-exemple réfute « le glouton est toujours optimal ». Il ne prouve
    rien de plus : ni que le glouton échoue souvent, ni qu'il échoue sur
    d'autres systèmes. Ce test se limite strictement à cette réfutation.
    """
    greedy = rendu(6, (1, 3, 4))
    assert greedy == [4, 1, 1]
    assert len(greedy) == 3
    assert _minimal_coin_count(6, (1, 3, 4)) == 2


def test_unreachable_amount_is_refused_not_silently_partial(rendu) -> None:
    with pytest.raises(ValueError):
        rendu(1, (2, 4))


# --- M3 : k plus proches voisins ---------------------------------------------

@pytest.fixture(scope="module")
def knn():
    return load_python_block("1NSI-ADGK-ME-003")["knn_classe"]


POINTS = [(1, 1, "A"), (2, 1, "A"), (1, 2, "A"), (6, 6, "B"), (7, 6, "B"), (6, 7, "B")]


def test_knn_matches_printed_examples(knn) -> None:
    assert knn(POINTS, (2, 2), 3) == "A"
    assert knn(POINTS, (6, 5), 3) == "B"


def _majority_nearest_wins(classes: list[str]) -> str:
    """Oracle de la règle imprimée : majorité, égalité tranchée au plus proche."""
    counts = Counter(classes)
    top = max(counts.values())
    tied = {name for name, n in counts.items() if n == top}
    for name in classes:  # ordre = distance croissante
        if name in tied:
            return name
    raise AssertionError("unreachable")


def test_knn_tie_break_rule_matches_its_stated_semantics(knn) -> None:
    """La fiche affirme : « en cas d'égalité, garde celle du voisin le plus proche »."""
    rng = random.Random(1)
    for _ in range(20000):
        k = rng.randint(1, 7)
        classes = [rng.choice("ABC") for _ in range(k)]
        points = [(i, 0, c) for i, c in enumerate(classes)]
        assert knn(points, (-1, 0), k) == _majority_nearest_wins(classes), classes


def test_knn_limit_values_of_k(knn) -> None:
    """k = 1, k = n, et k supérieur au nombre de données."""
    assert knn(POINTS, (1, 1), 1) == "A", "k=1 : le plus proche décide"
    assert knn(POINTS, (6, 6), 1) == "B"
    # k = n : égalité globale 3 A / 3 B, tranchée par le voisin le plus proche
    assert knn(POINTS, (1, 1), len(POINTS)) == "A"
    assert knn(POINTS, (6, 6), len(POINTS)) == "B"
    # k > n : `tri[:k]` tronque sans erreur
    assert knn(POINTS, (1, 1), len(POINTS) + 5) == "A"


def test_knn_tie_break_is_consistent_with_the_prose_of_the_sheet() -> None:
    """Le texte imprimé et le code doivent énoncer la même règle."""
    source = (CHAPTER / "1NSI-ADGK-ME-003.tex").read_text(encoding="utf-8")
    assert "En cas d'égalité, garde celle du" in source
    assert "voisin le plus proche" in source
    assert "strictement" in source, (
        "la prose doit justifier le `>` strict qui réalise le départage"
    )
    block = re.search(r"\\begin\{python\}\n(.*?)\\end\{python\}", source, re.S).group(1)
    assert ">" in block and ">=" not in block, (
        "un `>=` casserait le départage annoncé au profit du dernier voisin"
    )


def test_knn_uses_squared_distance_without_sqrt() -> None:
    """La fiche affirme que la racine carrée est inutile : elle ne l'écrit pas."""
    source = (CHAPTER / "1NSI-ADGK-ME-003.tex").read_text(encoding="utf-8")
    block = re.search(r"\\begin\{python\}\n(.*?)\\end\{python\}", source, re.S).group(1)
    assert "sqrt" not in block
