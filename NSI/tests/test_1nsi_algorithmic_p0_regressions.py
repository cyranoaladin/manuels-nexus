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
DICHOTOMY_QCM_JSON = (
    CHAPTERS
    / "1NSI-ALGO-DICHO-GLOUTON-KNN"
    / "qcm"
    / "1NSI-ALGO-DICHO-GLOUTON-KNN-QCM.json"
)
ALGORITHMS_QCM_JSON = ALGORITHMS_QCM.with_suffix(".json")
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


def test_dichotomy_qcm_does_not_confuse_variant_with_halving_the_zone() -> None:
    payload = json.loads(DICHOTOMY_QCM_JSON.read_text(encoding="utf-8"))
    question = next(item for item in payload["questions"] if item["id"] == "Q2")
    diagnostic = question["diagnostics"]["D"]["erreur"]

    assert "variant est divisé" not in diagnostic
    assert "taille de la zone de recherche" in diagnostic
    assert "approximativement de moitié" in diagnostic
    assert "rôle logique du variant" in diagnostic


def test_selection_qcm_assesses_both_clauses_of_the_loop_invariant() -> None:
    payload = json.loads(ALGORITHMS_QCM_JSON.read_text(encoding="utf-8"))
    question = next(item for item in payload["questions"] if item["id"] == "Q6")
    correct = question["options"][question["correcte"]]

    assert "deux clauses" in question["enonce"]
    # Le code inline porte la macro \\code du corpus : l'assertion suit le
    # balisage reellement publie, elle ne le contourne pas.
    assert r"\code{tableau[0:i]} est trié" in correct
    assert "inférieur ou égal" in correct
    assert r"\code{tableau[i:n]}" in correct


def test_knn_qcm_does_not_claim_a_small_k_avoids_computing_the_distances() -> None:
    payload = json.loads(DICHOTOMY_QCM_JSON.read_text(encoding="utf-8"))
    question = next(item for item in payload["questions"] if item["id"] == "Q6")
    diagnostic = question["diagnostics"]["D"]["erreur"]

    # Les distances a TOUS les points sont calculees quel que soit $k$ : dire
    # qu'un grand $k$ oblige « a considerer l'ensemble des distances » laisse
    # croire qu'un petit $k$ en dispenserait. Le surcout d'un grand $k$ porte
    # sur le vote, pas sur le calcul des distances.
    assert "trier et considérer l'ensemble des distances" not in diagnostic
    assert "quel que soit $k$" in diagnostic
    assert "vote" in diagnostic


def test_absence_sentinel_of_the_sequential_search_is_unique_in_the_chapter() -> None:
    """Un meme nom de fonction ne peut pas avoir deux contrats dans un chapitre.

    Le chapitre livrait `return -1` dans le cours et ses deux corriges
    d'evaluation, et `return None` partout ailleurs -- fiche methode,
    remediation, exercices, corriges et les deux sujets d'evaluation. Le sujet
    dit pourtant a l'eleve d'utiliser « `recherche_occurrence` du cours », et
    son corrige repondait avec l'autre contrat.

    C'est le critere pose par la fiche methode elle-meme qui tranche : une
    sentinelle d'absence ne doit pas pouvoir se confondre avec un indice
    valide. En Python `-1` en est un -- `tableau[-1]` renvoie le dernier
    element au lieu de signaler l'absence -- donc la sentinelle est `None`.
    """
    chapter = CHAPTERS / "1NSI-ALGO-PARCOURS-TRIS"

    def _sentinel(lines: list[str], start: int) -> str | None:
        """Le `return` du corps de la fonction, pas celui de la boucle."""
        for line in lines[start + 1:]:
            # Les blocs BEGIN-VERIFY portent le prefixe de commentaire "% ".
            bare = line[2:] if line.startswith("% ") else line
            if bare.strip() and not bare.startswith("    "):
                return None
            if bare.startswith("    return ") and not bare.startswith("        "):
                return bare.strip()
        return None

    sentinels: dict[str, set[str]] = {}
    for path in sorted(chapter.rglob("*.tex")):
        lines = path.read_text(encoding="utf-8").split("\n")
        for index, line in enumerate(lines):
            if "def recherche_occurrence(tableau, valeur):" not in line:
                continue
            found = _sentinel(lines, index)
            assert found is not None, f"{path}: definition sans return final"
            sentinels.setdefault(str(path.relative_to(chapter)), set()).add(found)

    assert sentinels, "aucune definition trouvee : le motif ne capture plus rien"
    divergent = {
        path: sorted(found)
        for path, found in sentinels.items()
        if found != {"return None"}
    }
    assert divergent == {}, (
        "contrat d'absence divergent selon les objets du chapitre : "
        f"{divergent}"
    )

    course = " ".join(
        (chapter / "cours" / "1NSI-APT-COURS-C1.tex").read_text(
            encoding="utf-8"
        ).split()
    )
    assert "ou None si elle est absente" in course
    assert "-1 si absente" not in course


def test_selection_invariant_correction_answers_that_clause_a_is_not_enough() -> None:
    """EX-106 est bati pour montrer que la clause (a) SEULE ne conclut pas.

    Le corrige repondait « Oui » a la question 2 puis expliquait, dans la meme
    phrase, pourquoi c'etait faux. A la sortie, l'enonce A ne donne que
    `tableau[0:n-1]` trie : rien n'y borne `tableau[n-1]`. Un etat comme
    [1, 2, 5, 0] satisfait A sans etre trie.
    """
    correction = CHAPTERS / (
        "1NSI-ALGO-PARCOURS-TRIS/corriges/1NSI-APT-CO-106.tex"
    )
    answer = _normalized(correction.read_text(encoding="utf-8")).split(
        "\\textbf{2.}", maxsplit=1
    )[1].split("\\textbf{3.}", maxsplit=1)[0]

    assert "Non" in answer
    assert "Oui, mais seulement parce" not in answer
    # La phrase fautive peut rester CITEE entre guillemets pour etre rejetee ;
    # ce qui est interdit, c'est de la poser comme justification.
    assert "case, laquelle ne peut être qu'à sa place" not in answer
    assert "revient à réutiliser ce que l'on sait de l'algorithme" in answer
