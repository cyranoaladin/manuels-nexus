import re
from pathlib import Path


NSI_ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = NSI_ROOT / "chapitres"
GREEDY_COURSE = (
    CHAPTERS
    / "1NSI-ALGO-DICHO-GLOUTON-KNN"
    / "cours"
    / "1NSI-ADGK-COURS-C2.tex"
)
INSERTION_COURSE = (
    CHAPTERS
    / "1NSI-ALGO-PARCOURS-TRIS"
    / "cours"
    / "1NSI-AGT-COURS-C2.tex"
)
ALGORITHMS_QCM = (
    CHAPTERS
    / "1NSI-ALGO-PARCOURS-TRIS"
    / "qcm"
    / "1NSI-ALGO-PARCOURS-TRIS-QCM.tex"
)


def _normalized(text: str) -> str:
    return " ".join(text.split())


def test_greedy_change_does_not_promise_an_optimal_solution() -> None:
    source = GREEDY_COURSE.read_text(encoding="utf-8")
    normalized = _normalized(source)

    assert (
        "pour tenter d'obtenir un rendu avec peu de pièces, on choisit à chaque "
        "étape la plus grande pièce (ou billet) ne dépassant pas le montant restant."
        in normalized
    )
    assert (
        '"""Construit un rendu en choisissant d\'abord les plus grandes pieces '
        'disponibles."""'
        in source
    )
    assert "moins de pièces possible" not in source
    assert "moins de pieces possible" not in source


def test_insertion_sort_termination_covers_all_array_sizes() -> None:
    source = INSERTION_COURSE.read_text(encoding="utf-8")
    normalized = _normalized(source)

    assert "$\\max(n-1,0)$ fois" in normalized
    assert "$n\\leqslant1$" in normalized
    assert "aucune itération" in normalized
    assert "déjà triés" in normalized
    assert "avant chaque tour exécuté, $j\\geqslant0$" in normalized
    assert "variant entier $j+1$" in normalized
    assert "strictement positif" in normalized
    assert "décroît de $1$" in normalized
    assert "$j=-1$" in normalized
    assert "la condition de la boucle devient fausse" in normalized
    assert "Si $n\\leqslant1$, la boucle ne s'exécute pas" in normalized
    assert "Si $n\\geqslant2$, la dernière itération a $i=n-1$" in normalized


def test_maximum_qcm_uses_four_unambiguous_options_in_order() -> None:
    source = ALGORITHMS_QCM.read_text(encoding="utf-8")
    q2 = re.search(r"\\item \\textbf\{\[Q2\]\}(.*?)\\bigskip", source, re.DOTALL)

    assert q2 is not None
    options = re.findall(r"^\s*\\item\s+(.+)$", q2.group(1), flags=re.MULTILINE)
    assert options == [
        "la valeur $0$.",
        "le premier élément du tableau.",
        "la plus grande valeur possible.",
        "le nombre d'éléments du tableau.",
    ]
