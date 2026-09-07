"""Preuves de régression des trois fiches ADGK, exigées par la décision humaine.

Le Release Owner autorise la requalification de ces trois objets **sur leur
contenu courant**, sous réserve stricte que les objets soient exactement ceux
audités par les preuves annoncées. Ces tests SONT ces preuves.

Ils n'exécutent pas une copie du code : ils extraient le programme du fichier
`.tex` déposé et le font tourner. Si la fiche change, la preuve change avec
elle — c'est ce qui rend le lien entre le receipt et le contenu vérifiable.
"""

from __future__ import annotations

import hashlib
import itertools
import random
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPITRE = ROOT / "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/methodes"

PYTHON_BLOCK = re.compile(r"\\begin\{python\}(.*?)\\end\{python\}", re.S)


def _programme(nom: str) -> dict:
    """Le programme Python écrit dans la fiche, exécuté tel quel."""
    texte = (CHAPITRE / nom).read_text(encoding="utf-8")
    blocs = PYTHON_BLOCK.findall(texte)
    assert blocs, nom
    espace: dict = {}
    # Les appels d'exemple en fin de bloc ne doivent pas gêner : ils sont sans
    # effet de bord et leur valeur est ignorée.
    exec(compile("\n".join(blocs), nom, "exec"), espace)  # noqa: S102
    return espace


def digest(nom: str) -> str:
    return "sha256:" + hashlib.sha256(
        (CHAPITRE / nom).read_bytes()
    ).hexdigest()


# ═══════════════════════════════════════════════════════════════════════
# ME-001 — recherche dichotomique
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def dichotomie():
    return _programme("1NSI-ADGK-ME-001.tex")["recherche_dichotomique"]


def test_dichotomie_contract_absent_is_minus_one(dichotomie) -> None:
    """Le contrat que la décision nomme : élément absent -> -1."""
    assert dichotomie([2, 5, 7], 4) == -1
    assert dichotomie([], 1) == -1
    assert dichotomie([1], 2) == -1


def test_dichotomie_empty_array(dichotomie) -> None:
    assert dichotomie([], 0) == -1
    assert dichotomie([], -1) == -1


def test_dichotomie_present_and_bounds(dichotomie) -> None:
    t = [2, 5, 7, 11, 13, 17, 19, 23]
    assert dichotomie(t, 2) == 0, "première case"
    assert dichotomie(t, 23) == 7, "dernière case"
    assert dichotomie(t, 13) == 4, "valeur intérieure, exemple de la fiche"
    for i, v in enumerate(t):
        assert t[dichotomie(t, v)] == v


def test_dichotomie_duplicates_return_an_occurrence(dichotomie) -> None:
    """Avec des doublons, l'indice renvoyé doit porter la bonne valeur."""
    t = [1, 3, 3, 3, 5, 5, 9]
    for v in (1, 3, 5, 9):
        i = dichotomie(t, v)
        assert i != -1 and t[i] == v, (v, i)


def test_dichotomie_four_thousand_cases_against_an_oracle(dichotomie) -> None:
    """4 000 cas contre l'oracle `in` / `index`, doublons inclus."""
    random.seed(20260907)
    cas = 0
    for _ in range(1000):
        n = random.randint(0, 12)
        t = sorted(random.randint(-8, 8) for _ in range(n))
        for v in range(-9, -5):
            attendu_present = v in t
            i = dichotomie(t, v)
            cas += 1
            if attendu_present:
                assert i != -1 and t[i] == v, (t, v, i)
            else:
                assert i == -1, (t, v, i)
    for _ in range(1000):
        n = random.randint(1, 12)
        t = sorted(random.randint(-8, 8) for _ in range(n))
        v = random.choice(t)
        i = dichotomie(t, v)
        cas += 1
        assert i != -1 and t[i] == v, (t, v, i)
    assert cas >= 4000, cas


def test_dichotomie_variant_strictly_decreases(dichotomie) -> None:
    """Le variant d-g décroît strictement et reste positif ou nul."""
    def trace(t, v):
        g, d = 0, len(t) - 1
        variants = []
        while g <= d:
            variants.append(d - g)
            m = (g + d) // 2
            if t[m] == v:
                return variants
            if t[m] < v:
                g = m + 1
            else:
                d = m - 1
        return variants

    random.seed(7)
    for _ in range(500):
        t = sorted(random.sample(range(-50, 50), random.randint(1, 20)))
        v = random.randint(-55, 55)
        variants = trace(t, v)
        assert all(x >= 0 for x in variants)
        for a, b in zip(variants, variants[1:]):
            assert b < a, (t, v, variants)


def test_dichotomie_matches_the_prose_example(dichotomie) -> None:
    """La fiche annonce 7 -> 3 -> 0 pour chercher 13 : on le vérifie."""
    t = [2, 5, 7, 11, 13, 17, 19, 23]
    g, d, variants = 0, len(t) - 1, []
    while g <= d:
        variants.append(d - g)
        m = (g + d) // 2
        if t[m] == 13:
            break
        if t[m] < 13:
            g = m + 1
        else:
            d = m - 1
    assert variants == [7, 3, 0]


# ═══════════════════════════════════════════════════════════════════════
# ME-002 — algorithme glouton
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def glouton():
    return _programme("1NSI-ADGK-ME-002.tex")["rendu_monnaie"]


def _optimal(montant: int, pieces: tuple[int, ...]) -> int | None:
    infini = float("inf")
    table = [0] + [infini] * montant
    for m in range(1, montant + 1):
        for p in pieces:
            if p <= m and table[m - p] + 1 < table[m]:
                table[m] = table[m - p] + 1
    return None if table[montant] == infini else table[montant]


def test_glouton_exactness_in_the_claimed_domain(glouton) -> None:
    """Domaine revendiqué : le système euro, canonique."""
    euro = (200, 100, 50, 20, 10, 5, 2, 1)
    for montant in range(0, 500):
        rendu = glouton(montant)
        assert sum(rendu) == montant, montant
        assert all(p in euro for p in rendu), montant


def test_glouton_is_optimal_on_the_euro_system(glouton) -> None:
    """Comparaison à la programmation dynamique sur les cas testés."""
    euro = (200, 100, 50, 20, 10, 5, 2, 1)
    for montant in range(0, 500):
        assert len(glouton(montant)) == _optimal(montant, euro), montant


def test_glouton_zero_returns_an_empty_list(glouton) -> None:
    assert glouton(0) == []


def test_glouton_matches_its_worked_example(glouton) -> None:
    assert glouton(263) == [200, 50, 10, 2, 1]
    assert sum(glouton(263)) == 263


def test_glouton_refuses_a_partial_rendering(glouton) -> None:
    """Un rendu partiel serait une réponse fausse : la fonction refuse."""
    with pytest.raises(ValueError):
        glouton(7, pieces=(3, 5))
    with pytest.raises(ValueError):
        glouton(4, pieces=(3, 5))
    assert sum(glouton(8, pieces=(3, 5))) == 8


def test_the_counterexample_refutes_only_general_optimality(glouton) -> None:
    """{1,3,4} et 6 : le glouton rend 3 pièces, l'optimum en vaut 2.

    Le contre-exemple sert à réfuter l'optimalité GÉNÉRALE. Il ne dit rien de
    l'exactitude, ni du système euro — et ne doit jamais être élargi.
    """
    pieces = (1, 3, 4)
    rendu = glouton(6, pieces=pieces)
    assert sum(rendu) == 6, "le glouton reste EXACT"
    assert len(rendu) == 3
    assert sorted(rendu, reverse=True) == [4, 1, 1]
    assert _optimal(6, pieces) == 2
    # Et sur le système euro, aucun contre-exemple n'existe dans le domaine testé.
    euro = (200, 100, 50, 20, 10, 5, 2, 1)
    assert all(
        len(glouton(m)) == _optimal(m, euro) for m in range(0, 500)
    )


# ═══════════════════════════════════════════════════════════════════════
# ME-003 — k plus proches voisins
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def knn():
    return _programme("1NSI-ADGK-ME-003.tex")["knn_classe"]


def _reference(donnees, cible, k):
    """Règle annoncée : classe majoritaire, égalité tranchée par le plus proche."""
    tri = sorted(donnees, key=lambda p: (p[0] - cible[0]) ** 2 + (p[1] - cible[1]) ** 2)
    classes = [c for _, _, c in tri[:k]]
    meilleur = classes[0]
    for classe in classes:
        if classes.count(classe) > classes.count(meilleur):
            meilleur = classe
    return meilleur


def test_knn_matches_its_worked_examples(knn) -> None:
    pts = [(1, 1, "A"), (2, 1, "A"), (1, 2, "A"),
           (6, 6, "B"), (7, 6, "B"), (6, 7, "B")]
    assert knn(pts, (2, 2), 3) == "A"
    assert knn(pts, (6, 5), 3) == "B"


def test_knn_tie_is_broken_by_the_nearest_neighbour(knn) -> None:
    """Règle de départage courante : à égalité, le plus proche l'emporte."""
    pts = [(0, 0, "A"), (10, 0, "B")]
    assert knn(pts, (1, 0), 2) == "A", "A est plus proche"
    assert knn(pts, (9, 0), 2) == "B", "B est plus proche"


def test_knn_k_equals_one(knn) -> None:
    pts = [(0, 0, "A"), (1, 0, "B"), (2, 0, "B")]
    assert knn(pts, (0, 0), 1) == "A"
    assert knn(pts, (2, 0), 1) == "B"


def test_knn_k_equals_n(knn) -> None:
    pts = [(0, 0, "A"), (1, 0, "B"), (2, 0, "B")]
    assert knn(pts, (0, 0), 3) == "B", "majorité globale"


def test_knn_k_greater_than_n(knn) -> None:
    """La fiche exige que k > n soit traité : la tranche prend tout."""
    pts = [(0, 0, "A"), (1, 0, "B"), (2, 0, "B")]
    assert knn(pts, (0, 0), 99) == knn(pts, (0, 0), 3)


def test_knn_twenty_thousand_multisets_against_the_stated_rule(knn) -> None:
    """20 000 multisets : le code doit suivre exactement la règle annoncée."""
    random.seed(20260907)
    for essai in range(20000):
        n = random.randint(1, 6)
        donnees = [
            (random.randint(-5, 5), random.randint(-5, 5),
             random.choice("ABC"))
            for _ in range(n)
        ]
        k = random.randint(1, n + 2)
        cible = (random.randint(-5, 5), random.randint(-5, 5))
        assert knn(donnees, cible, k) == _reference(donnees, cible, k), (
            essai, donnees, cible, k,
        )


def test_knn_prose_and_code_agree_on_the_tie_rule() -> None:
    """La prose promet le voisin le plus proche ; le code ne remplace que sur
    un compte STRICTEMENT supérieur, ce qui préserve le premier trouvé."""
    texte = (CHAPITRE / "1NSI-ADGK-ME-003.tex").read_text(encoding="utf-8")
    assert "voisin le plus proche" in texte
    assert "strictement" in texte.lower()
    assert "classes.count(classe) > classes.count(classe_majoritaire)" in texte
