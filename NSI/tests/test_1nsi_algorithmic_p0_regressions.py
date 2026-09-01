import ast
import json
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
    / "1NSI-APT-COURS-C2.tex"
)
SELECTION_COURSE = (
    CHAPTERS
    / "1NSI-ALGO-PARCOURS-TRIS"
    / "cours"
    / "1NSI-APT-COURS-C3.tex"
)
ALGORITHMS_QCM = (
    CHAPTERS
    / "1NSI-ALGO-PARCOURS-TRIS"
    / "qcm"
    / "1NSI-ALGO-PARCOURS-TRIS-QCM.tex"
)
COUPLED_CHAPTERS = (
    CHAPTERS / "1NSI-ALGO-DICHO-GLOUTON-KNN",
    CHAPTERS / "1NSI-ALGO-PARCOURS-TRIS",
)


def _meta(path: Path) -> dict:
    first = path.read_text(encoding="utf-8").splitlines()[0]
    assert "META:" in first, path
    return json.loads(first.split("META:", 1)[1].strip())


def _normalized(text: str) -> str:
    return " ".join(text.split())


def test_coupled_object_ids_match_their_current_source_stems() -> None:
    for chapter in COUPLED_CHAPTERS:
        for path in sorted(chapter.rglob("*.tex")):
            assert _meta(path)["id"] == path.stem, path


def test_coupled_evaluations_declare_exact_a_b_variants_and_targets() -> None:
    evaluations = COUPLED_CHAPTERS[1] / "evaluations"
    for version in ("A", "B"):
        subject = evaluations / f"1NSI-APT-EVAL-{version}.tex"
        correction = evaluations / f"1NSI-APT-EVAL-{version}-corrige.tex"
        assert _meta(subject)["version"] == version
        assert _meta(correction)["evaluation_ref"] == subject.stem


def test_coupled_current_tex_sources_contain_no_legacy_agt_identity() -> None:
    for chapter in COUPLED_CHAPTERS:
        for path in sorted(chapter.rglob("*.tex")):
            assert "1NSI-AGT" not in path.read_text(encoding="utf-8"), path


def test_greedy_change_does_not_promise_an_optimal_solution() -> None:
    source = GREEDY_COURSE.read_text(encoding="utf-8")
    normalized = _normalized(source)

    assert (
        "pour tenter d'obtenir un rendu avec peu de pièces, on choisit à chaque "
        "étape la plus grande pièce (ou billet) ne dépassant pas le montant restant."
        in normalized
    )
    assert (
        "Construit un rendu en choisissant d'abord les plus grandes pieces disponibles."
        in normalized
    )
    listing = re.search(
        r"% PYTHON-SOURCE: code/rendu_glouton\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        source,
        re.DOTALL,
    )
    assert listing is not None
    module = ast.parse(listing.group("python"))
    function = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "rendu_glouton"
    )
    assert ast.get_docstring(function).splitlines()[0] == (
        "Construit un rendu en choisissant d'abord les plus grandes pieces disponibles."
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


def test_selection_sort_termination_covers_empty_and_singleton_arrays() -> None:
    source = SELECTION_COURSE.read_text(encoding="utf-8")
    property_block = source.split(
        r"\propriete[Terminaison et coût]{", maxsplit=1
    )[1].split(r"\demonstration{", maxsplit=1)[0]
    demonstration_block = source.split(r"\demonstration{", maxsplit=1)[1].split(
        "% BEGIN-VERIFY", maxsplit=1
    )[0]
    normalized_property = _normalized(property_block)
    normalized_demonstration = _normalized(demonstration_block)

    assert "$\\max(n-1,0)$ itérations" in normalized_property
    assert (
        "Si $n\\leqslant1$, la boucle externe ne s'exécute pas"
        in normalized_property
    )
    assert "le tableau est déjà trié" in normalized_property
    assert (
        "Si $n\\leqslant1$, la boucle externe ne s'exécute pas"
        in normalized_demonstration
    )
    assert "le tableau est déjà trié" in normalized_demonstration
    assert (
        "Si $n\\geqslant2$, la dernière itération a $i=n-2$"
        in normalized_demonstration
    )
    assert "le tableau entier est donc trié" in normalized_demonstration
    assert "Après la dernière itération ($i=n-2$)" not in normalized_demonstration


def test_maximum_qcm_uses_four_unambiguous_options_in_order() -> None:
    source = ALGORITHMS_QCM.read_text(encoding="utf-8")
    # Le rendu derive desormais du .json et n'emet plus de \bigskip : la borne
    # du bloc est la fin de la liste d'options.
    q2 = re.search(
        r"\\item \\textbf\{\[Q2\]\}(.*?)\\end\{enumerate\}", source, re.DOTALL
    )

    assert q2 is not None
    options = re.findall(r"^\s*\\item\s+(.+)$", q2.group(1), flags=re.MULTILINE)
    assert options == [
        "la valeur $0$.",
        "le premier élément du tableau.",
        "la plus grande valeur représentable.",
        "le nombre d'éléments du tableau.",
    ]
