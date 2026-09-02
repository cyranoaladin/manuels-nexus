"""L'independance du solveur doit etre STRUCTURELLE, pas declarative.

Un raisonnement ecrit apres avoir lu la cle n'est pas une preuve independante.
Ces tests imposent donc l'independance par le contrat d'entree et la verifient
par mutation : cle fausse, permutation des options, unicite.
"""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import qcm_independent_solver as S  # noqa: E402

CORPUS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"


def _question(chapter: str, question_id: str) -> dict:
    path = next((CORPUS / chapter / "qcm").glob("*-QCM.json"))
    document = json.loads(path.read_text(encoding="utf-8"))
    return next(item for item in document["questions"] if item["id"] == question_id)


# -- 2. La cle ne peut pas entrer -------------------------------------------


@pytest.mark.parametrize(
    "field",
    ["correcte", "declared_answer", "correct_answer", "key", "independent_solution"],
)
def test_supplying_the_declared_answer_is_rejected(field: str) -> None:
    payload = {
        "id": "FIXTURE-1",
        "enonce": "Combien vaut $1+1$ ?",
        "options": {"A": "$1$", "B": "$2$"},
        field: "B",
    }
    with pytest.raises(S.DeclaredAnswerLeak):
        S.sanitize(payload)


def test_the_sanitized_bundle_carries_no_answer_field() -> None:
    question = _question("1SPE-VARIABLES-ALEATOIRES", "Q1")
    assert "correcte" in question, "la question canonique porte bien une cle"

    sanitized = S.sanitize_canonical(question)
    payload = sanitized.payload()
    serialised = json.dumps(payload, ensure_ascii=False)

    assert set(payload) == {"question_id", "statement", "options", "capacity"}
    assert not (S.FORBIDDEN_INPUT_FIELDS & set(payload))
    assert question["correcte"] not in {
        value for key, value in payload.items() if key != "options"
    }
    assert "correcte" not in serialised
    assert sanitized.digest().startswith("sha256:")


def test_the_solver_input_digest_is_stable_and_content_addressed() -> None:
    question = _question("1SPE-VARIABLES-ALEATOIRES", "Q4")
    first = S.sanitize_canonical(question)
    second = S.sanitize_canonical(dict(question))
    assert first.digest() == second.digest()

    altered = dict(question)
    altered["enonce"] = question["enonce"] + " "
    assert S.sanitize_canonical(altered).digest() != first.digest()


# -- 3. Aucun routage par identifiant de question ---------------------------


def _solver_code_without_prose() -> str:
    """Le code seul : ni commentaires, ni chaines, ni docstrings.

    Le lint doit porter sur ce que le solveur EXECUTE. La prose peut citer la
    regle qu'elle s'interdit sans l'enfreindre.
    """

    import tokenize

    path = ROOT / "scripts" / "qcm_independent_solver.py"
    kept: list[str] = []
    with path.open("rb") as handle:
        for token in tokenize.tokenize(handle.readline):
            if token.type in {tokenize.COMMENT, tokenize.STRING}:
                continue
            kept.append(token.string)
    return " ".join(kept)


def test_the_solver_contains_no_question_identifier_and_no_answer_table() -> None:
    source = _solver_code_without_prose()
    identifiers = set()
    for path in CORPUS.glob("*/qcm/*-QCM.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        identifiers.add(document["chapitre"])
        identifiers.update(item["id"] for item in document["questions"])

    # Un identifiant de chapitre ne doit jamais apparaitre dans le solveur.
    leaked = sorted(name for name in identifiers if name.startswith(("1SPE", "TSPE", "TCOMPL", "TEXP")) and name in source)
    assert leaked == [], leaked

    # Ni un aiguillage par identifiant, ni une table de reponses.
    assert not re.search(r"question_id\s*==", source)
    assert not re.search(r"answer_map|ANSWERS\s*=", source)

    # La prose du module s'interdit explicitement ces motifs ; le lint verifie
    # que l'interdiction porte sur le code, pas seulement sur l'intention.
    prose = (ROOT / "scripts" / "qcm_independent_solver.py").read_text(encoding="utf-8")
    assert "question_id ==" in prose, "la regle doit rester documentee"


# -- 7. Une cle fausse ne change rien a la sortie du solveur ----------------


@pytest.mark.parametrize(
    ("chapter", "question_id"),
    [
        ("1SPE-VARIABLES-ALEATOIRES", "Q1"),
        ("1SPE-VARIABLES-ALEATOIRES", "Q7"),
        ("1SPE-VARIABLES-ALEATOIRES", "Q11"),
        ("1SPE-VARIABLES-ALEATOIRES", "Q19"),
        ("1SPE-VARIABLES-ALEATOIRES", "Q20"),
        ("TSPE-DERIVATION-CONVEXITE", "Q6"),
    ],
)
def test_a_false_declared_key_leaves_the_solver_output_identical(
    chapter: str, question_id: str
) -> None:
    question = _question(chapter, question_id)
    truthful = S.solve(S.sanitize_canonical(question))

    forged = dict(question)
    letters = sorted(question["options"])
    forged["correcte"] = next(
        letter for letter in letters if letter != question["correcte"]
    )
    assert forged["correcte"] != question["correcte"], "la mutation doit muter"
    lied = S.solve(S.sanitize_canonical(forged))

    assert truthful.digest() == lied.digest()
    assert truthful.to_dict() == lied.to_dict()
    # Seul le verificateur voit la difference.
    assert truthful.unique_answer == question["correcte"]
    assert truthful.unique_answer != forged["correcte"]


# -- 8. La verite suit le CONTENU des options, pas la lettre ---------------


@pytest.mark.parametrize(
    ("chapter", "question_id"),
    [
        ("1SPE-VARIABLES-ALEATOIRES", "Q4"),
        ("1SPE-VARIABLES-ALEATOIRES", "Q11"),
        ("1SPE-VARIABLES-ALEATOIRES", "Q19"),
    ],
)
def test_permuting_the_options_moves_the_true_letter(
    chapter: str, question_id: str
) -> None:
    question = _question(chapter, question_id)
    before = S.solve(S.sanitize_canonical(question))
    assert before.unique_answer is not None

    letters = sorted(question["options"])
    rotated = dict(question)
    rotated["options"] = {
        letters[index]: question["options"][letters[index - 1]]
        for index in range(len(letters))
    }
    assert rotated["options"] != question["options"], "la permutation doit permuter"

    after = S.solve(S.sanitize_canonical(rotated))
    expected = letters[(letters.index(before.unique_answer) + 1) % len(letters)]
    assert after.unique_answer == expected
    assert after.computed_value == before.computed_value


# -- 9. Unicite : 0, 1 ou plusieurs options vraies -------------------------


def test_the_solver_reports_a_single_true_option_on_the_current_corpus() -> None:
    question = _question("1SPE-VARIABLES-ALEATOIRES", "Q1")
    result = S.solve(S.sanitize_canonical(question))
    assert result.true_option_count == 1
    assert result.unique_answer is not None


def test_two_equivalent_options_are_both_true() -> None:
    """La classe historique : $3/6$ et $1/2$ valent la meme chose."""

    question = {
        "id": "FIXTURE-EQUIV",
        "capacite": "C1",
        "enonce": "On lance un de equilibre. Soit $X$ le resultat. Quelle est $P(X = 3)$ ?",
        "options": {"A": r"$\frac{1}{6}$", "B": r"$\frac{2}{12}$", "C": "$1$", "D": "$0$"},
    }
    result = S.solve(S.sanitize(question))
    assert result.true_option_count == 2
    assert result.unique_answer is None


def test_no_true_option_is_reported_as_zero() -> None:
    question = {
        "id": "FIXTURE-NONE",
        "capacite": "C1",
        "enonce": "On lance un de equilibre. Soit $X$ le resultat. Quelle est $P(X = 3)$ ?",
        "options": {"A": "$1$", "B": "$0$", "C": r"$\frac{1}{2}$", "D": r"$\frac{1}{3}$"},
    }
    result = S.solve(S.sanitize(question))
    assert result.true_option_count == 0
    assert result.unique_answer is None


# -- 10. Le refus est un comportement correct -------------------------------


def test_an_unmodellable_statement_is_refused_not_invented() -> None:
    question = {
        "id": "FIXTURE-OPINION",
        "capacite": "C6",
        "enonce": "Quel nom de variable est le plus lisible dans ce script ?",
        "options": {"A": r"\code{n}", "B": r"\code{taille}"},
    }
    result = S.solve(S.sanitize(question))
    assert result.status == "NOT_MACHINE_RESOLVABLE"
    assert result.family is None
    assert result.option_truths == {}
    assert result.reason


# -- Les regles generiques tiennent sur des fixtures synthetiques ----------


@pytest.mark.parametrize(
    ("statement", "options", "expected"),
    [
        (
            "On sait que $E(X)=7$ et on pose $Y=2X+1$. Quelle est $E(Y)$ ?",
            {"A": "$15$", "B": "$14$", "C": "$8$", "D": "$7$"},
            "A",
        ),
        (
            "Si $V(X) = 25$, alors $\\sigma(X)$ vaut :",
            {"A": "$25$", "B": "$5$", "C": "$625$", "D": "$12{,}5$"},
            "B",
        ),
        (
            "Si $E(X) = 2$ et $V(X) = 3$, quelle est $E(X^2)$ ?",
            {"A": "$5$", "B": "$7$", "C": "$4$", "D": "$6$"},
            "B",
        ),
    ],
)
def test_generic_families_hold_on_synthetic_fixtures(
    statement: str, options: dict, expected: str
) -> None:
    result = S.solve(
        S.sanitize({"id": "FIXTURE", "capacite": "C2", "enonce": statement, "options": options})
    )
    assert result.status == "MACHINE_RESOLVED"
    assert result.unique_answer == expected


def test_the_linear_expectation_rule_has_a_counter_example() -> None:
    """La regle doit se tromper si on lui donne une identite fausse."""

    result = S.solve(
        S.sanitize(
            {
                "id": "FIXTURE-COUNTER",
                "capacite": "C4",
                "enonce": "On sait que $E(X)=7$ et on pose $Y=2X+1$. Quelle est $E(Y)$ ?",
                "options": {"A": "$14$", "B": "$8$", "C": "$7$", "D": "$1$"},
            }
        )
    )
    assert result.status == "MACHINE_RESOLVED"
    assert result.true_option_count == 0, "aucune option ne vaut 2*7+1 = 15"


def test_option_values_compare_by_value_not_by_writing() -> None:
    assert S.option_value(r"$\frac{3}{6}$") == Fraction(1, 2)
    assert S.option_value(r"$0{,}5$") == Fraction(1, 2)
    assert S.option_value("$12$ euros") == Fraction(12)
    assert S.option_value("Le nombre de valeurs prises par $X$") is None


# -- 11. Forme de Gram euclidienne -----------------------------------------
#
# Une famille qui decide une CLASSE : les familles finies de vecteurs d'un
# espace prehilbertien reel specifiees par leurs donnees de Gram. Les tests
# qui suivent l'attaquent par mutation : permutation des valeurs entre les
# etiquettes, alteration d'une donnee de l'enonce, donnees geometriquement
# irrealisables, enonces hors classe.


def _gram_fixture(statement: str, options: dict) -> S.SolverResult:
    return S.solve(
        S.sanitize(
            {
                "id": "FIXTURE-GRAM",
                "capacite": "C1",
                "enonce": statement,
                "options": options,
            }
        )
    )


@pytest.mark.parametrize(
    ("statement", "options", "expected", "value"),
    [
        # Norme d'une somme, noms de vecteurs arbitraires.
        (
            r"Sachant que $\|\vec{a}\|=3$, $\|\vec{b}\|=4$ et "
            r"$\vec{a}\cdot\vec{b}=5$, que vaut $\|\vec{a}+\vec{b}\|$ ?",
            {"A": "$35$", "B": "$7$", "C": r"$\sqrt{35}$", "D": r"$\sqrt{25}$"},
            "C",
            "sqrt(35)",
        ),
        # Meme classe, autres noms, autre combinaison lineaire.
        (
            r"On sait que $\|\vec{p}\|=3$, $\|\vec{q}\|=4$ et "
            r"$\vec{p}\cdot\vec{q}=5$. Que vaut $\|\vec{p}-\vec{q}\|$ ?",
            {"A": r"$\sqrt{15}$", "B": r"$\sqrt{35}$", "C": "$5$", "D": "$1$"},
            "A",
            "sqrt(15)",
        ),
        # Coordonnees en base orthonormee, produit scalaire demande.
        (
            r"Soient $\vec{u}(3,-2)$ et $\vec{v}(1,4)$. Que vaut "
            r"$\vec{u} \cdot \vec{v}$ ?",
            {"A": "$-5$", "B": "$5$", "C": "$-11$", "D": "$11$"},
            "A",
            "-5",
        ),
        # Norme et angle : G_ij = |u||v| cos(theta).
        (
            r"Si $\|\vec{w}\|=5$, $\|\vec{z}\|=4$ et $(\vec{w},\vec{z}) = "
            r"\dfrac{\pi}{3}$, quelle est la valeur de $\vec{w} \cdot \vec{z}$ ?",
            {"A": "$20$", "B": "$10$", "C": r"$10\sqrt{3}$", "D": r"$10\sqrt{2}$"},
            "B",
            "10",
        ),
        # Angle geometrique entre deux vecteurs donnes par leurs coordonnees.
        (
            r"Quel est l'angle geometrique entre les vecteurs $(1,0)$ et "
            r"$(1,1)$ ?",
            {
                "A": r"$\dfrac{\pi}{6}$",
                "B": r"$\dfrac{\pi}{4}$",
                "C": r"$\dfrac{\pi}{3}$",
                "D": r"$\dfrac{\pi}{2}$",
            },
            "B",
            "pi/4",
        ),
        # Cosinus de l'angle de deux vecteurs nommes.
        (
            r"On donne $\|\vec{s}\|=2$, $\|\vec{t}\|=3$ et $\vec{s}\cdot\vec{t}=3$. "
            r"Que vaut le cosinus $\cos(\vec{s},\vec{t})$ de l'angle des vecteurs ?",
            {"A": r"$\dfrac{1}{2}$", "B": "$1$", "C": "$0$", "D": r"$\dfrac{1}{3}$"},
            "A",
            "1/2",
        ),
        # Combinaison lineaire a coefficients.
        (
            r"On donne $\|\vec{e}\|=1$, $\|\vec{f}\|=1$ et $\vec{e}\cdot\vec{f}=0$. "
            r"Que vaut $\|2\vec{e}+3\vec{f}\|^2$ ?",
            {"A": "$13$", "B": "$5$", "C": "$25$", "D": "$6$"},
            "A",
            "13",
        ),
    ],
)
def test_the_gram_family_decides_a_generic_euclidean_class(
    statement: str, options: dict, expected: str, value: str
) -> None:
    result = _gram_fixture(statement, options)
    assert result.status == "MACHINE_RESOLVED"
    assert result.family == "EUCLIDEAN_GRAM_FORM"
    assert result.unique_answer == expected
    assert result.computed_value == value


def test_the_gram_family_recomputes_the_corpus_question_independently() -> None:
    question = _question("1SPE-PRODUIT-SCALAIRE", "Q6")
    result = S.solve(S.sanitize_canonical(question))
    assert result.status == "MACHINE_RESOLVED"
    assert result.family == "EUCLIDEAN_GRAM_FORM"
    assert result.true_option_count == 1
    # La cle declaree n'est lue qu'ICI, apres le calcul.
    assert result.unique_answer == question["correcte"]


def test_a_forged_key_leaves_the_gram_family_output_identical() -> None:
    """La famille ne lit jamais la cle : la mutation ne doit rien changer."""

    question = _question("1SPE-PRODUIT-SCALAIRE", "Q6")
    truthful = S.solve(S.sanitize_canonical(question))
    forged = dict(question)
    forged["correcte"] = next(
        letter for letter in sorted(question["options"]) if letter != question["correcte"]
    )
    lied = S.solve(S.sanitize_canonical(forged))
    assert truthful.to_dict() == lied.to_dict()
    assert truthful.digest() == lied.digest()


def test_permuting_the_option_values_moves_the_gram_answer() -> None:
    """Mutation label-sensitive : un oracle qui reste d'accord ne prouve rien."""

    question = _question("1SPE-PRODUIT-SCALAIRE", "Q6")
    before = S.solve(S.sanitize_canonical(question))
    declared = question["correcte"]
    assert before.unique_answer == declared

    letters = sorted(question["options"])
    rotated = dict(question)
    rotated["options"] = {
        letters[index]: question["options"][letters[index - 1]]
        for index in range(len(letters))
    }
    assert rotated["options"] != question["options"]

    after = S.solve(S.sanitize_canonical(rotated))
    assert after.status == "MACHINE_RESOLVED"
    assert after.computed_value == before.computed_value
    assert after.unique_answer != declared
    assert after.unique_answer == letters[(letters.index(declared) + 1) % len(letters)]


def test_mutating_a_datum_of_the_statement_changes_the_gram_answer() -> None:
    """u.v = 5 -> 6 : la norme cherchee vaut sqrt(37), plus aucune option."""

    base = (
        r"Sachant que $\|\vec{u}\|=3$, $\|\vec{v}\|=4$ et $\vec{u}\cdot\vec{v}=5$, "
        r"quelle est la valeur de $\|\vec{u}+\vec{v}\|$ ?"
    )
    options = {"A": "$35$", "B": "$7$", "C": r"$\sqrt{35}$", "D": r"$\sqrt{25}$"}
    before = _gram_fixture(base, options)
    assert before.unique_answer == "C"

    mutated = base.replace(r"\vec{u}\cdot\vec{v}=5", r"\vec{u}\cdot\vec{v}=6")
    assert mutated != base
    after = _gram_fixture(mutated, options)
    assert after.unique_answer != "C"

    # Et avec l'option qui correspond, la famille suit la donnee mutee.
    moved = dict(options, C=r"$\sqrt{37}$")
    assert _gram_fixture(mutated, moved).unique_answer == "C"
    assert _gram_fixture(mutated, moved).computed_value == "sqrt(37)"


def test_gram_data_that_no_configuration_realises_is_refused() -> None:
    """|u|=1, |v|=1, u.v=5 : matrice de Gram non semi-definie positive."""

    result = _gram_fixture(
        r"Sachant que $\|\vec{u}\|=1$, $\|\vec{v}\|=1$ et $\vec{u}\cdot\vec{v}=5$, "
        r"quelle est la valeur de $\|\vec{u}+\vec{v}\|$ ?",
        {"A": r"$\sqrt{12}$", "B": "$2$", "C": r"$\sqrt{2}$", "D": "$12$"},
    )
    assert result.status == "NOT_MACHINE_RESOLVABLE"
    assert result.family is None


def test_incomplete_gram_data_is_refused() -> None:
    """Sans u.v, la norme de u+v n'est pas determinee."""

    result = _gram_fixture(
        r"Sachant que $\|\vec{u}\|=3$ et $\|\vec{v}\|=4$, quelle est la valeur "
        r"de $\|\vec{u}+\vec{v}\|$ ?",
        {"A": "$7$", "B": "$5$", "C": "$1$", "D": r"$\sqrt{25}$"},
    )
    assert result.status == "NOT_MACHINE_RESOLVABLE"
    assert result.family is None


@pytest.mark.parametrize(
    ("statement", "options"),
    [
        (
            "On lance un de equilibre. Soit $X$ le resultat. Quelle est $P(X = 3)$ ?",
            {"A": r"$\frac{1}{6}$", "B": "$1$", "C": "$0$", "D": r"$\frac{1}{2}$"},
        ),
        (
            "Quel nom de variable est le plus lisible dans ce script ?",
            {"A": r"\code{n}", "B": r"\code{taille}"},
        ),
        (
            r"Deux vecteurs non nuls $\vec{u}$ et $\vec{v}$ sont orthogonaux si "
            r"et seulement si :",
            {
                "A": r"$\vec{u}\cdot\vec{v} > 0$",
                "B": r"$\vec{u}\cdot\vec{v} = 0$",
                "C": r"$\Vert\vec{u}\Vert = \Vert\vec{v}\Vert$",
                "D": r"$\vec{u}\cdot\vec{v} < 0$",
            },
        ),
    ],
)
def test_the_gram_family_stays_inert_outside_its_class(
    statement: str, options: dict
) -> None:
    inp = S.sanitize(
        {"id": "FIXTURE-OUT", "capacite": "C1", "enonce": statement, "options": options}
    )
    assert S._euclidean_gram_form(inp) is None


def test_coordinates_are_refused_when_the_basis_is_not_orthonormal() -> None:
    """Sans base orthonormee, les coordonnees ne donnent pas le produit scalaire."""

    inp = S.sanitize(
        {
            "id": "FIXTURE-NONORTHO",
            "capacite": "C1",
            "enonce": (
                r"Dans une base \emph{non} orthonormee, soient $\vec{u}(3,-2)$ et "
                r"$\vec{v}(1,4)$. Que vaut $\vec{u} \cdot \vec{v}$ ?"
            ),
            "options": {"A": "$-5$", "B": "$5$", "C": "$-11$", "D": "$11$"},
        }
    )
    assert S._euclidean_gram_form(inp) is None


def test_the_gram_family_abstains_when_no_option_matches_exactly_one_value() -> None:
    """Aucune option lisible egale a la valeur calculee : abstention."""

    inp = S.sanitize(
        {
            "id": "FIXTURE-NOMATCH",
            "capacite": "C1",
            "enonce": (
                r"Sachant que $\|\vec{u}\|=3$, $\|\vec{v}\|=4$ et "
                r"$\vec{u}\cdot\vec{v}=5$, quelle est la valeur de "
                r"$\|\vec{u}+\vec{v}\|$ ?"
            ),
            "options": {"A": "$1$", "B": "$2$", "C": "$3$", "D": "$4$"},
        }
    )
    assert S._euclidean_gram_form(inp) is None


def test_the_gram_family_abstains_when_an_option_cannot_be_read() -> None:
    inp = S.sanitize(
        {
            "id": "FIXTURE-UNREADABLE",
            "capacite": "C1",
            "enonce": (
                r"Sachant que $\|\vec{u}\|=3$, $\|\vec{v}\|=4$ et "
                r"$\vec{u}\cdot\vec{v}=5$, quelle est la valeur de "
                r"$\|\vec{u}+\vec{v}\|$ ?"
            ),
            "options": {
                "A": "$35$",
                "B": "$7$",
                "C": r"$\sqrt{35}$",
                "D": "On ne peut pas conclure",
            },
        }
    )
    assert S._euclidean_gram_form(inp) is None


def test_the_gram_family_stays_inert_on_point_coordinates() -> None:
    """Un point n'est pas un vecteur : aucune donnee de Gram a en tirer."""

    inp = S.sanitize(
        {
            "id": "FIXTURE-POINT",
            "capacite": "C1",
            "enonce": (
                r"Une equation cartesienne du plan passant par $A(2;-1;3)$ et de "
                r"vecteur normal $\vec{n}(1;4;-2)$ est :"
            ),
            "options": {
                "A": "$x+4y-2z+4=0$",
                "B": "$x+4y-2z=0$",
                "C": "$2x-y+3z=0$",
                "D": "$x+4y-2z-4=0$",
            },
        }
    )
    assert S._euclidean_gram_form(inp) is None


def test_the_gram_family_stays_inert_without_an_interrogated_quantity() -> None:
    """Des donnees de Gram sans quantite demandee ne suffisent pas."""

    inp = S.sanitize(
        {
            "id": "FIXTURE-NOASK",
            "capacite": "C1",
            "enonce": r"Les vecteurs $\vec{u}(2,3)$ et $\vec{v}(3,-2)$ sont :",
            "options": {
                "A": "orthogonaux",
                "B": "colineaires",
                "C": "de normes differentes",
                "D": "de sens contraire",
            },
        }
    )
    assert S._euclidean_gram_form(inp) is None


def test_the_gram_family_ignores_the_identity_of_the_question() -> None:
    """Interdiction d'un solveur par object-ID : l'identite ne doit rien changer."""

    question = _question("1SPE-PRODUIT-SCALAIRE", "Q6")
    reference = S.solve(S.sanitize_canonical(question))

    for field, value in (("id", "ZZZ-9999"), ("capacite", "CAPACITE-INEXISTANTE")):
        altered = dict(question)
        altered[field] = value
        assert altered[field] != question.get(field)
        assert S.solve(S.sanitize_canonical(altered)).digest() == reference.digest()


# -- 12. La nouvelle famille ne change aucun verdict deja acquis ------------


def _corpus_questions() -> list[tuple[str, str, dict]]:
    rows: list[tuple[str, str, dict]] = []
    for path in sorted(CORPUS.glob("*/qcm/*-QCM.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        for question in document["questions"]:
            rows.append((document["chapitre"], question["id"], question))
    return rows


def test_the_gram_family_changes_no_verdict_already_reached(monkeypatch) -> None:
    """Preuve de non-regression : verdicts identiques sans la nouvelle famille."""

    without = tuple(
        family for family in S.FAMILIES if family is not S._euclidean_gram_form
    )
    assert len(without) == len(S.FAMILIES) - 1, "la famille doit etre enregistree"

    rows = _corpus_questions()
    assert rows, "le corpus doit etre non vide"

    after = {}
    for chapter, question_id, question in rows:
        after[(chapter, question_id)] = S.solve(S.sanitize_canonical(question)).to_dict()

    monkeypatch.setattr(S, "FAMILIES", without)
    before = {}
    for chapter, question_id, question in rows:
        before[(chapter, question_id)] = S.solve(S.sanitize_canonical(question)).to_dict()

    changed = {
        key
        for key in before
        if before[key] != after[key]
    }
    regressions = {
        key for key in changed if before[key]["status"] == "MACHINE_RESOLVED"
    }
    assert regressions == set(), sorted(regressions)
    assert changed, "la nouvelle famille doit resoudre au moins une question"
    for key in changed:
        assert after[key]["solver_family"] == "EUCLIDEAN_GRAM_FORM"
