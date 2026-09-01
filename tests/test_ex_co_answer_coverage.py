"""Couverture des reponses : ce qu'elle prouve, et ce qu'elle ne prouve pas."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def coverage():
    spec = importlib.util.spec_from_file_location(
        "ex_co_answer_coverage", ROOT / "scripts/ex_co_answer_coverage.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXERCISE_TWO = "\n".join([
    r"\begin{exercice}{EX}{1}{5}",
    r"\begin{enumerate}",
    r"  \item Construire l'arbre.",
    r"  \item Calculer $P(A)$.",
    r"\end{enumerate}",
    r"\end{exercice}",
])


def test_a_missing_answer_is_detected(coverage) -> None:
    """Le defaut reel : deux questions, une seule reponse."""
    correction = r"\begin{corrige}{EX}" "\n" r"\textbf{2.} $P(A)=1/2$." "\n" r"\end{corrige}"
    verdict, evidence = coverage.classify(EXERCISE_TWO, correction)
    assert verdict == coverage.MISSING
    assert evidence["missing"] == [1]


def test_full_coverage_is_established(coverage) -> None:
    correction = (
        r"\begin{corrige}{EX}" "\n"
        r"\textbf{1.} L'arbre a deux niveaux." "\n"
        r"\textbf{2.} $P(A)=1/2$." "\n"
        r"\end{corrige}"
    )
    assert coverage.classify(EXERCISE_TWO, correction)[0] == coverage.ESTABLISHED


def test_nested_subquestions_do_not_inflate_the_denominator(coverage) -> None:
    """Quatre questions a sous-questions ne font pas dix-sept questions."""
    exercise = "\n".join([
        r"\begin{enumerate}",
        r"  \item Formes du trinome.",
        r"  \begin{enumerate}",
        r"    \item Identifier $a$, $b$, $c$.",
        r"    \item Forme canonique.",
        r"  \end{enumerate}",
        r"  \item Representation graphique.",
        r"\end{enumerate}",
    ])
    assert coverage.top_level_items(exercise) == 2
    correction = r"\textbf{1.} ... " "\n" r"\textbf{2.} ..."
    assert coverage.classify(exercise, correction)[0] == coverage.ESTABLISHED


def test_a_nested_itemize_is_not_a_question(coverage) -> None:
    exercise = "\n".join([
        r"\begin{enumerate}",
        r"  \item Comparer les aires.",
        r"  \begin{itemize}",
        r"    \item un carre de cote $x$ ;",
        r"    \item un rectangle.",
        r"  \end{itemize}",
        r"\end{enumerate}",
    ])
    assert coverage.top_level_items(exercise) == 1


@pytest.mark.parametrize(
    "correction",
    [
        r"\textbf{1.} a" "\n" r"\textbf{2.} b",
        r"\textbf{Question 1 — Titre.} a" "\n" r"\textbf{Question 2 — Titre.} b",
        r"\textbf{1a.} a" "\n" r"\textbf{2b.} b",
        r"\textbf{a)} a" "\n" r"\textbf{b)} b",
        "\\begin{enumerate}\n  \\item a\n  \\item b\n\\end{enumerate}",
    ],
)
def test_every_layout_convention_of_the_corpus_is_recognised(coverage, correction) -> None:
    """Une convention typographique differente n'est pas une lacune."""
    assert coverage.classify(EXERCISE_TWO, correction)[0] == coverage.ESTABLISHED


def test_an_unknown_layout_is_not_reported_as_a_missing_answer(coverage) -> None:
    """Fail-closed sans accuser : la prose continue sort pour examen."""
    correction = "Le tableau donne les valeurs, puis la loi s'en deduit."
    assert coverage.classify(EXERCISE_TWO, correction)[0] == coverage.UNRECOGNISED


def test_coverage_never_claims_the_answer_is_correct(coverage) -> None:
    """Un corrige complet mais FAUX reste 'couvert'.

    C'est la limite du controle, et elle doit rester explicite : l'exactitude
    est prouvee ailleurs. Ici, la reponse est absurde et pourtant couverte.
    """
    correction = r"\textbf{1.} 42" "\n" r"\textbf{2.} 42"
    assert coverage.classify(EXERCISE_TWO, correction)[0] == coverage.ESTABLISHED


def test_the_seven_proba_cond_trees_are_now_answered(coverage) -> None:
    """Les sept lacunes reelles trouvees dans 1SPE-PROBA-COND sont fermees."""
    chapter = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND"
    for number in ("015", "019", "021", "041", "044", "045", "047"):
        exercise = chapter / f"exercices/1SPE-PROBCOND-EX-{number}.tex"
        correction = chapter / f"corriges/1SPE-PROBCOND-CO-{number}.tex"
        verdict, evidence = coverage.classify(
            coverage.pedagogical_body(exercise),
            coverage.pedagogical_body(correction),
        )
        assert verdict == coverage.ESTABLISHED, (number, evidence)


def test_a_descriptive_itemize_before_the_questions_is_not_counted(coverage) -> None:
    """Le corpus decrit parfois la situation avant de poser les questions.

    « il recoit 36 euros » / « sinon il perd sa mise » n'est pas une question :
    les compter faisait passer un corrige complet pour lacunaire.
    """
    exercise = "\n".join([
        r"\begin{itemize}",
        r"  \item Si le numero sort, il recoit $36$ euros.",
        r"  \item Sinon, il perd sa mise.",
        r"\end{itemize}",
        r"\begin{enumerate}",
        r"  \item Quelles sont les valeurs de $X$ ?",
        r"  \item Dresser le tableau de loi.",
        r"\end{enumerate}",
    ])
    assert coverage.top_level_items(exercise) == 2


def test_a_nested_enumerate_holds_subquestions_not_questions(coverage) -> None:
    exercise = "\n".join([
        r"\begin{enumerate}",
        r"  \item \textbf{Offre A.}",
        r"  \begin{enumerate}",
        r"    \item Montrer que la suite est geometrique.",
        r"    \item Calculer $A_5$.",
        r"  \end{enumerate}",
        r"  \item \textbf{Offre B.}",
        r"\end{enumerate}",
    ])
    assert coverage.top_level_items(exercise) == 2


# ---------------------------------------------------------------------------
# Le registre semantique branche sur le graphe EX/CO
# ---------------------------------------------------------------------------


def test_coverage_established_is_never_read_as_scientific_correctness(coverage) -> None:
    """Un corrige COMPLET mais FAUX reste « couvert ».

    C'est la frontiere du registre, et elle doit rester visible : la couverture
    dit que chaque question recoit une reponse, jamais que la reponse est
    juste. L'exactitude est prouvee par l'oracle, ailleurs. Si ce test devenait
    faux, c'est que quelqu'un aurait fait dire au registre plus qu'il ne prouve.
    """
    exercise = r"""\begin{enumerate}
  \item Calculer $2+2$.
  \item Calculer $3\times 3$.
\end{enumerate}"""
    faux = r"""\textbf{1.} $2+2=5$.
\textbf{2.} $3\times 3=10$."""
    verdict, _evidence = coverage.classify(exercise, faux)
    assert verdict == coverage.ESTABLISHED


def test_a_correction_that_skips_a_question_is_not_established(coverage) -> None:
    exercise = r"""\begin{enumerate}
  \item Premiere question.
  \item Deuxieme question.
  \item Troisieme question.
\end{enumerate}"""
    lacunaire = r"""\textbf{1.} Reponse.
\textbf{2.} Reponse."""
    verdict, evidence = coverage.classify(exercise, lacunaire)
    assert verdict == coverage.MISSING
    assert evidence["missing"] == [3]


def test_the_committed_ledger_matches_the_producer() -> None:
    import importlib.util
    import json
    import sys

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "build_ex_co_answer_coverage_ledger_under_test",
        root / "scripts" / "build_ex_co_answer_coverage_ledger.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    committed = json.loads(
        (root / "audit" / "EX_CO_ANSWER_COVERAGE_LEDGER.json").read_text(
            encoding="utf-8"
        )
    )
    assert module.build_ledger() == committed


def test_every_missing_answer_stays_release_blocking(coverage) -> None:
    """Les lacunes reelles ne sont pas absorbees par le nouveau statut."""
    import json

    root = Path(__file__).resolve().parents[1]
    ledger = json.loads(
        (root / "audit" / "EX_CO_ANSWER_COVERAGE_LEDGER.json").read_text(
            encoding="utf-8"
        )
    )
    manquantes = [
        row for row in ledger["relations"] if row["verdict"] == coverage.MISSING
    ]
    assert ledger["totals"].get(coverage.MISSING, 0) == len(manquantes)
    # Aucune n'est en Premiere : le perimetre de la vague 1 est net.
    assert [r for r in manquantes if r["chapter"].startswith(("1SPE-", "1NSI-"))] == []
