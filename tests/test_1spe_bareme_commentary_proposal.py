"""Une proposition de barème se dérive ou se refuse — elle ne s'invente pas.

La politique fixe le format et interdit la granularité fictive : pas de
répartition uniforme, pas de demi-point partout, pas de sous-critère absent de
la solution. Ce module vérifie que chaque proposition vient bien du sujet et du
corrigé, que le crédit partiel n'apparaît que sur une décomposition réelle, et
que l'ambiguïté devient un drapeau plutôt qu'une invention.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_bareme_commentary_proposal as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Chaque question reçoit une proposition ou un drapeau
# ---------------------------------------------------------------------------


def test_every_question_is_either_proposed_or_flagged(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    assert summary["QUESTIONS_WITHOUT_PROPOSAL_OR_FLAG"] == 0
    assert summary["QUESTIONS"] == (
        summary["PROPOSED"] + summary["PEDAGOGICAL_JUDGEMENT_REQUIRED"]
    )
    assert summary["ASSESSMENTS"] == 20
    assert summary["PROPOSED"] > 200


def test_a_proposal_carries_points_a_gesture_and_a_result(
    payload: dict[str, Any],
) -> None:
    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                if question["verdict"] != "PROPOSED":
                    assert question["expected"] == "", question
                    assert question["partial_credit"] == "", question
                    assert question["why"].strip(), question
                    continue
                assert question["points"], question
                assert question["gesture"], question
                assert " — " in question["expected"], question


def test_the_mathematics_is_carried_verbatim(payload: dict[str, Any]) -> None:
    """Un barème qui déforme la formule qu'il évalue est pire qu'absent.

    Une première version « nettoyait » le LaTeX : `\\pi` disparaissait, et
    « 5π/6 » devenait « (5 )/(6) ». Les attendus doivent donc porter du LaTeX
    réel, et jamais une formule mutilée.
    """

    with_math = 0
    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                expected = question["expected"]
                if "$" in expected:
                    with_math += 1
                    # Les délimiteurs vont par paires : une formule coupée en
                    # deux ne serait pas compilable.
                    assert expected.count("$") % 2 == 0, question
                # La trace de l'ancien mutilage : une fraction vidée.
                assert "( )/(" not in expected, question
    assert with_math > 100, "presque aucun attendu ne porte de mathématiques"


def test_no_expected_swallows_a_latex_comment(payload: dict[str, Any]) -> None:
    """Les corrigés séparent leurs exercices par des lignes de `%=====`."""

    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                expected = question["expected"]
                assert "%===" not in expected, question
                # Un `\%` échappé n'est pas un commentaire : c'est un signe
                # pour cent, et « 0,06 % » a parfaitement sa place dans un
                # attendu. Seul le `%` NON échappé ouvre un commentaire.
                assert not __import__("re").search(r"(?<!\\)%", expected), question


# ---------------------------------------------------------------------------
#  Le `%` : marqueur de commentaire ou signe pour cent
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "answer,expected_absent,expected_present",
    [
        # Le défaut trouvé : un séparateur posé en FIN de ligne, après la
        # formule. Le filtre « ligne commençant par % » le laissait passer.
        (
            "$x = 3$. %===========================",
            "%=====",
            "$x = 3$",
        ),
        # Le même, sur sa propre ligne.
        ("%-----------------\n$x = 3$.", "-----", "$x = 3$"),
        # Et l'inverse : un `\%` échappé est un SIGNE POUR CENT, pas un
        # commentaire. Le refuser mutilerait « 0,06 % ».
        ("L'erreur vaut $0{,}06\\,\\%$.", None, "\\%"),
        # Un `%` en fin de ligne coupe bien la suite, pas ce qui précède.
        ("$a = 1$ % un commentaire\n$b = 2$.", "commentaire", "$a = 1$"),
    ],
)
def test_the_percent_sign_is_read_as_latex_reads_it(
    answer: str, expected_absent: str | None, expected_present: str
) -> None:
    """Un commentaire s'ouvre à un `%` NON échappé, n'importe où dans la ligne."""

    cleaned = gate._strip_comments(answer)

    if expected_absent is not None:
        assert expected_absent not in cleaned, cleaned
    assert expected_present in cleaned, cleaned


def test_the_mathematics_is_never_altered_to_please_the_parser() -> None:
    """Le contenu mathématique traverse le nettoyage sans une égratignure."""

    formula = "$\\dfrac{5\\pi}{6} = \\pi - \\dfrac{\\pi}{6}$"
    cleaned = gate._strip_comments(f"{formula} %séparateur")

    assert cleaned == formula
    assert "\\pi" in cleaned
    assert "( )/(" not in cleaned


# ---------------------------------------------------------------------------
#  Le crédit partiel n'apparaît que sur une décomposition réelle
# ---------------------------------------------------------------------------


def test_partial_credit_only_where_the_correction_separates_its_steps(
    payload: dict[str, Any],
) -> None:
    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                if not question["partial_credit"]:
                    continue
                assert question.get("separable_steps", 0) >= 2, question
                assert question["answer_scope"] == "question", question
    # Il en existe, sinon la règle ne serait jamais exercée -- et il n'y en a
    # pas partout, sinon elle serait devenue une répartition uniforme.
    proposed = payload["summary"]["PROPOSED"]
    partial = payload["summary"]["PARTIAL_CREDIT_PROPOSED"]
    assert 0 < partial < proposed // 4, (partial, proposed)


def test_a_single_step_answer_gets_no_partial_credit() -> None:
    """Plein crédit ou rien : la politique l'autorise explicitement."""

    question = {
        "question": "Q1",
        "points": "1 pt",
        "statement": "Calculer $u_1$.",
        "correction_answer": "$u_1 = 7$.",
        "correction_answer_scope": "question",
        "competence": None,
    }

    row = gate.propose(question)

    assert row["verdict"] == "PROPOSED"
    assert row["partial_credit"] == ""


def test_points_that_do_not_divide_on_the_half_point_grid_are_refused() -> None:
    """Pas de granularité fictive : une coupure impossible n'est pas proposée."""

    assert gate.divide(Fraction(1), 3) is None, "un point ne se coupe pas en deux"
    assert gate.divide(Fraction(3), 1) is None, "sans étape séparable, pas de crédit"
    split = gate.divide(Fraction(3), 2)
    assert split is not None
    assert sum(split) == Fraction(3)
    for part in split:
        assert part % Fraction(1, 2) == 0


def test_an_ambiguous_question_is_flagged_not_invented() -> None:
    """Sans geste lisible ni résultat repérable, on demande un humain."""

    row = gate.propose(
        {
            "question": "Q1",
            "points": "2 pts",
            "statement": "Lina observe la courbe.",
            "correction_answer": "",
            "correction_answer_scope": "absent",
            "competence": None,
        }
    )

    assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED"
    assert row["expected"] == ""
    assert row["partial_credit"] == ""


def test_an_unvalued_question_is_flagged() -> None:
    """Les deux GEOREP ne valuent aucune question : rien à proposer."""

    row = gate.propose(
        {
            "question": "Q1",
            "points": None,
            "statement": "Calculer les coordonnées.",
            "correction_answer": "$(2\\,;\\,-1)$.",
            "correction_answer_scope": "question",
            "competence": None,
        }
    )

    assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED"
    assert "ne value pas" in row["why"]


# ---------------------------------------------------------------------------
#  Rien n'est écrit dans les corrigés
# ---------------------------------------------------------------------------


def test_the_proposals_stay_proposals(payload: dict[str, Any]) -> None:
    assert payload["approves_nothing"] is True
    assert payload["policy"] == "RESOLVED_BY_HUMAN_DECISION_2026_09_04"
    assert "revue de chapitre" in payload["these_are_proposals_not_content"]
    # Aucun corrigé ne porte encore la couche : elle entre par la revue.
    corrections = sorted(
        (ROOT / "Mathematiques/manuel-maths/chapitres").glob(
            "1SPE-*/evaluations/*-corrige.tex"
        )
    )
    assert corrections
    for path in corrections:
        text = path.read_text(encoding="utf-8")
        assert "Attendu :" not in text, path


def test_the_gesture_list_is_read_from_the_corpus_not_guessed() -> None:
    """Chaque verbe déclaré doit exister dans un énoncé du corpus."""

    subjects = sorted(
        (ROOT / "Mathematiques/manuel-maths/chapitres").glob(
            "1SPE-*/evaluations/*[AB].tex"
        )
    )
    corpus = " ".join(
        path.read_text(encoding="utf-8").lower() for path in subjects
    )
    for pattern, name in gate.GESTURES:
        assert __import__("re").search(pattern, corpus), name


# ---------------------------------------------------------------------------
#  Un attendu appartient à SA question — les cas observés dans le manuel
# ---------------------------------------------------------------------------

# Ces quatre configurations sont celles où le même paragraphe se retrouvait
# proposé comme attendu de plusieurs questions aux gestes différents.
SCOPE_FIXTURES = {
    "rappeler_vs_simplifier": (
        [("Q1", "Rappeler la définition de la fonction exponentielle."),
         ("Q2", "Simplifier $\\mathrm{e}^{2x-1}\\mathrm{e}^{1-x}$.")],
        "La fonction exponentielle vérifie $y'=y$ et $y(0)=1$. "
        "Les simplifications donnent $\\mathrm{e}^{x}$ et $\\mathrm{e}^{2x}$.",
    ),
    "justifier_vs_calculer": (
        [("Q1", "Justifier que $f$ est décroissante."),
         ("Q2", "Calculer $f(0)$ et $f(5)$.")],
        "$f'(x)=-0{,}4\\mathrm{e}^{-0{,}4x}<0$, donc $f$ est décroissante. "
        "$f(0)=1$ et $f(5)=\\mathrm{e}^{-2}\\approx0{,}14$.",
    ),
    "calculer_interpreter_justifier": (
        [("Q1", "Calculer $P(0)$ et $P(12)$."),
         ("Q2", "Interpréter le coefficient de $t$."),
         ("Q3", "Justifier que le modèle est croissant.")],
        "$P(0)=2500$ et $P(12)\\approx5136$. "
        "Le coefficient de $t$ est positif : le modèle est croissant.",
    ),
    "sous_questions_interpreter_verifier": (
        [("Q4a", "Interpréter la ligne $n = n + 1$."),
         ("Q4b", "Vérifier que l'algorithme renvoie $9$.")],
        "La boucle incrémente le rang. On obtient $n = 9$.",
    ),
}


@pytest.mark.parametrize("name", sorted(SCOPE_FIXTURES))
def test_an_exercise_wide_correction_proposes_nothing_question_by_question(
    name: str,
) -> None:
    """Le corrigé répond à l'exercice : aucun attendu ne s'en déduit par question."""

    questions, correction = SCOPE_FIXTURES[name]
    rows = [
        gate.propose(
            {
                "question": label,
                "statement": statement,
                "points": "1 pt",
                "correction_answer": correction,
                "correction_answer_scope": "exercise",
            }
        )
        for label, statement in questions
    ]

    for row in rows:
        assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED", row
        assert row["expected"] == "", row
        assert "échelle de l'exercice" in row["why"], row


@pytest.mark.parametrize("name", sorted(SCOPE_FIXTURES))
def test_the_same_correction_never_becomes_two_identical_expectations(
    name: str,
) -> None:
    """Ce qui était le défaut : un texte partagé, servi à des gestes différents."""

    questions, correction = SCOPE_FIXTURES[name]
    expectations = [
        gate.propose(
            {
                "question": label,
                "statement": statement,
                "points": "1 pt",
                "correction_answer": correction,
                "correction_answer_scope": "exercise",
            }
        )["expected"]
        for label, statement in questions
    ]

    produced = [gate.result_of(row) for row in expectations if row]
    assert len(produced) == len(set(produced))


def test_a_correction_answering_the_parent_question_is_not_credited_to_a_sub_question() -> None:
    row = gate.propose(
        {
            "question": "Q4a",
            "statement": "Interpréter la ligne $n = n + 1$.",
            "points": "1 pt",
            "correction_answer": "La boucle incrémente le rang jusqu'à $n = 9$.",
            "correction_answer_scope": "parent_question",
        }
    )

    assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED"
    assert "question mère" in row["why"]


def test_a_question_scoped_correction_still_produces_its_proposal() -> None:
    """Le remède ne doit pas tout refuser : ce qui est question-specific passe."""

    row = gate.propose(
        {
            "question": "Q2",
            "statement": "Calculer $f(0)$ et $f(5)$.",
            "points": "1 pt",
            "correction_answer": "$f(0)=1$ et $f(5)=\\mathrm{e}^{-2}\\approx0{,}14$.",
            "correction_answer_scope": "question",
        }
    )

    assert row["verdict"] == "PROPOSED"
    assert row["expected"].startswith("calculer — ")
    assert "$f(0)=1$" in row["expected"]


# ---------------------------------------------------------------------------
#  Un attendu doit pouvoir être composé
# ---------------------------------------------------------------------------


def test_a_correction_cut_inside_a_display_yields_no_expectation() -> None:
    """Observé en DERGLOBAL : `\\[ ... = 10x - 11` sans `\\]`."""

    row = gate.propose(
        {
            "question": "Q3",
            "statement": "Donner l'équation de la tangente.",
            "points": "1 pt",
            "correction_answer": (
                "Équation de la tangente : \\[ T : y = f'(2)(x - 2) + 9 = 10x - 11"
            ),
            "correction_answer_scope": "question",
        }
    )

    assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED"
    assert row["expected"] == ""


def test_an_orphan_environment_close_yields_no_expectation() -> None:
    """Observé en DERLOCAL : un fragment ouvert par `\\end{align*}`."""

    row = gate.propose(
        {
            "question": "Q2",
            "statement": "Calculer le taux d'accroissement.",
            "points": "1 pt",
            "correction_answer": "\\end{align*} \\[ \\frac{f(3+h)-f(3)}{h} = h+2",
            "correction_answer_scope": "question",
        }
    )

    assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED"


def test_every_delivered_expectation_can_be_typeset(payload: dict[str, Any]) -> None:
    import tex_units

    assert payload["summary"]["BAREME_EXPECTED_TEX_UNBALANCED"] == 0
    assert payload["unbalanced_expected"] == []
    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                if question["expected"]:
                    assert tex_units.is_balanced(question["expected"]), question


def test_no_two_questions_of_an_exercise_share_a_result(
    payload: dict[str, Any],
) -> None:
    assert payload["summary"]["BAREME_QUESTION_SCOPE_AMBIGUOUS"] == 0
    assert payload["ambiguous_scope"] == []
