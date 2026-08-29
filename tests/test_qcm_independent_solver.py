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
