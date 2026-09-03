"""Les barèmes transcrits ne valent que si le producteur refuse d'inventer.

Le producteur lit le sujet et n'écrit dans le corrigé que ce que le sujet a
déjà décidé. Ce module vérifie la vérité courante, puis mute les preuves : un
sujet qui ne value pas ses questions, une somme qui ne tombe pas juste, un
barème qui contredit son sujet doivent tous être refusés.
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

import build_1spe_assessment_bareme_transcription as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Vérité courante
# ---------------------------------------------------------------------------


def test_every_point_sums_to_the_total_its_subject_declares(
    payload: dict[str, Any],
) -> None:
    """Contrôle secondaire, mais il doit passer partout."""

    assert payload["summary"]["SUM_MISMATCH"] == 0
    for row in payload["assessments"]:
        assert row["declared_total"] == "20", row["object_id"]
        for exercise in row["exercises"]:
            if exercise["marked_question_count"]:
                assert exercise["sum_matches_exercise_total"] is True, (
                    row["object_id"],
                    exercise["number"],
                )


def test_no_committed_bareme_contradicts_its_own_subject(
    payload: dict[str, Any],
) -> None:
    """Le point doit être attaché à SA tâche, pas seulement au bon total."""

    assert payload["summary"]["CARRIER_CONTRADICTS_SUBJECT"] == 0
    assert payload["carrier_contradictions"] == []
    assert payload["summary"]["CARRIER_WITHOUT_SUBJECT_SOURCE"] == 0
    # Le contrôle serait vide de sens s'il ne portait sur rien.
    assert payload["summary"]["CARRIER_MATCHES_SUBJECT"] >= 70


def test_every_transcriptible_assessment_carries_its_bareme(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    assert summary["CARRIER_MISSING_AFTER_APPLY"] == 0
    assert summary["CARRIER_MISPLACED_OR_MISSING"] == 0
    assert summary["CARRIER_OUTSIDE_ANY_EXERCISE"] == 0
    assert summary["TRANSCRIPTIBLE"] + summary[
        "HUMAN_PEDAGOGICAL_JUDGEMENT_REQUIRED"
    ] == summary["ASSESSMENTS"]


def test_what_is_not_derivable_stays_a_human_decision(
    payload: dict[str, Any],
) -> None:
    """Deux sujets ne valuent pas leurs questions : rien n'y est écrit."""

    summary = payload["summary"]
    assert summary["HUMAN_REQUIRED_IDS"] == [
        "1SPE-GEOREP-EV-A",
        "1SPE-GEOREP-EV-B",
    ]
    assert summary["ATTENTION_REQUIRED"] == 2
    for entry in payload["human_decision_packet"]:
        assert entry["verdict"] == "PENDING"
        assert entry["status"] == "ATTENTION_REQUIRED"
        assert entry["verdict_owner"] == "EXPERT_PROGRAMME_PEDAGOGIE"
        assert entry["scientific_confirmation_owner"] == "EXPERT_MATHEMATIQUE"
        assert entry["proposal_is_not_a_decision"]
        assert entry["why_human"], entry["object_id"]
        assert entry["parallel_form_of"] != entry["object_id"]


def test_the_human_packet_gives_the_task_before_asking_for_a_price(
    payload: dict[str, Any],
) -> None:
    """Un nombre de points sans énoncé ne se relit pas."""

    for entry in payload["human_decision_packet"]:
        for exercise in entry["exercises"]:
            assert exercise["questions"], (entry["object_id"], exercise["number"])
            assert len(exercise["questions"]) == exercise["question_count"]
            for question in exercise["questions"]:
                assert question["statement"].strip()
            assert exercise["candidate_allocation"]
            assert len(exercise["candidate_allocation"]) == exercise[
                "question_count"
            ]
            for candidate in exercise["candidate_allocation"]:
                assert candidate["rationale"].strip()
            assert exercise["candidate_sum_matches_declared_total"] is True
    assert payload["summary"]["CANDIDATE_PROPOSAL_SUM_MISMATCH"] == 0


def test_no_candidate_proposal_reaches_a_correction() -> None:
    """La proposition machine ne doit exister QUE dans l'artefact d'audit."""

    for object_id in ("1SPE-GEOREP-EV-A", "1SPE-GEOREP-EV-B"):
        chapter = "1SPE-GEOMETRIE-REPEREE"
        correction = (
            ROOT
            / "Mathematiques/manuel-maths/chapitres"
            / chapter
            / "evaluations"
            / f"{object_id}-corrige.tex"
        )
        assert correction.is_file()
        assert gate.CARRIER not in correction.read_text(encoding="utf-8"), object_id


# ---------------------------------------------------------------------------
#  Mutations : le producteur doit refuser
# ---------------------------------------------------------------------------


UNMARKED_SUBJECT = r"""% META: {"id": "FIXTURE-EV-A", "type_objet": "evaluation", "points": 4, "duree_min": 55, "version": "A"}
\section*{Exercice 1 \hfill (4 points) \hfill Capacités C1}
\begin{enumerate}
  \item Première question.
  \item Deuxième question.
\end{enumerate}
"""

MARKED_SUBJECT = r"""% META: {"id": "FIXTURE-EV-A", "type_objet": "evaluation", "points": 4, "duree_min": 55, "version": "A"}
\section*{Exercice 1 \hfill (4 points) \hfill Capacités C1}
\begin{enumerate}
  \item Première question. \hfill \textit{(1,5 pt)}
  \item Deuxième question. \hfill \textit{(2,5 pts)}
\end{enumerate}
"""

BAD_SUM_SUBJECT = r"""% META: {"id": "FIXTURE-EV-A", "type_objet": "evaluation", "points": 4, "duree_min": 55, "version": "A"}
\section*{Exercice 1 \hfill (4 points) \hfill Capacités C1}
\begin{enumerate}
  \item Première question. \hfill \textit{(1 pt)}
  \item Deuxième question. \hfill \textit{(2 pts)}
\end{enumerate}
"""

NESTED_SUBJECT = r"""% META: {"id": "FIXTURE-EV-A", "type_objet": "evaluation", "points": 4, "duree_min": 55, "version": "A"}
\section*{Exercice 1 \hfill (4 points) \hfill Capacités C1}
\begin{enumerate}
  \item Première question. \hfill \textit{(2 pts)}
  \item Deuxième question, en deux temps.
  \begin{enumerate}
    \item Premier temps. \hfill \textit{(1 pt)}
    \item Second temps. \hfill \textit{(1 pt)}
  \end{enumerate}
\end{enumerate}
"""


def _subject(tmp_path: Path, text: str) -> dict[str, Any]:
    path = tmp_path / "FIXTURE-EV-A.tex"
    path.write_text(text, encoding="utf-8")
    return gate.analyse_subject(path)


def test_a_subject_that_does_not_value_its_questions_is_refused(
    tmp_path: Path,
) -> None:
    verdict = gate.classify(_subject(tmp_path, UNMARKED_SUBJECT))

    assert verdict["classification"] == gate.HUMAN_REQUIRED
    assert "question par question" in " ".join(verdict["reasons"])


def test_a_fully_valued_subject_is_transcriptible(tmp_path: Path) -> None:
    subject = _subject(tmp_path, MARKED_SUBJECT)
    verdict = gate.classify(subject)

    assert verdict["classification"] == gate.TRANSCRIPTIBLE
    assert verdict["reasons"] == []
    assert gate.bareme_line(subject["exercises"][0]) == (
        gate.CARRIER + "{Q1 : 1,5 pt ; Q2 : 2,5 pts}"
    )


def test_a_subject_whose_questions_do_not_sum_to_its_total_is_refused(
    tmp_path: Path,
) -> None:
    subject = _subject(tmp_path, BAD_SUM_SUBJECT)
    verdict = gate.classify(subject)

    assert verdict["classification"] == gate.HUMAN_REQUIRED
    assert "ne fait pas le total" in " ".join(verdict["reasons"])


def test_a_question_valued_through_its_subquestions_is_valued(
    tmp_path: Path,
) -> None:
    """« 4. a) b) » : la valeur est portée par les sous-questions."""

    subject = _subject(tmp_path, NESTED_SUBJECT)
    verdict = gate.classify(subject)

    assert verdict["classification"] == gate.TRANSCRIPTIBLE
    assert gate.bareme_line(subject["exercises"][0]) == (
        gate.CARRIER + "{Q1 : 2 pts ; Q2a : 1 pt ; Q2b : 1 pt}"
    )


def test_the_unit_follows_french_agreement_and_the_number_stays_verbatim() -> None:
    assert gate.render_mark("2", Fraction(2)) == "2 pts"
    assert gate.render_mark("1,5", Fraction(3, 2)) == "1,5 pt"
    assert gate.render_mark("1{,}5", Fraction(3, 2)) == "1,5 pt"
    assert gate.render_mark("0,5", Fraction(1, 2)) == "0,5 pt"
    # Le sujet écrit parfois « (2 pt) » ; le nombre est conservé, l'accord est
    # rétabli — c'est la convention des barèmes déjà écrits du corpus.
    assert gate.render_mark("2", Fraction(2)).endswith("pts")


def test_a_carrier_that_swaps_two_questions_is_caught_and_recollated(
    tmp_path: Path,
) -> None:
    """La somme reste juste, l'attribution est fausse : il faut le voir.

    Les valeurs sont les bonnes, seul leur rattachement est inversé : le sujet
    dit à quelle tâche va chaque point, donc le porteur est recollé.
    """

    subject = _subject(tmp_path, MARKED_SUBJECT)
    correction = tmp_path / "FIXTURE-EV-A-corrige.tex"
    correction.write_text(
        "\\section*{Exercice 1}\n"
        + gate.CARRIER
        + "{Q1 : 2,5 pts ; Q2 : 1,5 pt}\n\nRéponse.\n",
        encoding="utf-8",
    )

    findings = gate.audit_existing_carriers(subject, correction)
    result = gate.apply_to_correction(subject, correction, True)

    assert [row["verdict"] for row in findings] == [
        "CARRIER_CONTRADICTS_SUBJECT_ORDER"
    ]
    assert result["refused_overwrites"] == []
    assert gate.CARRIER + "{Q1 : 1,5 pt ; Q2 : 2,5 pts}" in correction.read_text(
        encoding="utf-8"
    )


def test_a_carrier_with_wrong_values_is_caught_and_never_realigned(
    tmp_path: Path,
) -> None:
    """Des valeurs franchement différentes ne sont pas un recollage."""

    subject = _subject(tmp_path, MARKED_SUBJECT)
    correction = tmp_path / "FIXTURE-EV-A-corrige.tex"
    body = (
        "\\section*{Exercice 1}\n"
        + gate.CARRIER
        + "{Q1 : 3 pts ; Q2 : 1 pt}\n\nRéponse.\n"
    )
    correction.write_text(body, encoding="utf-8")

    findings = gate.audit_existing_carriers(subject, correction)
    result = gate.apply_to_correction(subject, correction, True)

    assert [row["verdict"] for row in findings] == [
        "CARRIER_CONTRADICTS_SUBJECT_VALUES"
    ]
    assert [row["exercise"] for row in result["refused_overwrites"]] == [1]
    assert result["placed_exercises"] == []
    # Le désaccord est signalé, jamais écrasé.
    assert correction.read_text(encoding="utf-8") == body


def test_placement_is_idempotent_and_canonical(tmp_path: Path) -> None:
    subject = _subject(tmp_path, MARKED_SUBJECT)
    correction = tmp_path / "FIXTURE-EV-A-corrige.tex"
    correction.write_text(
        "%=====\n\\section*{Exercice 1 — corrigé}\n%=====\n\nRéponse.\n",
        encoding="utf-8",
    )

    first = gate.apply_to_correction(subject, correction, True)
    written = correction.read_text(encoding="utf-8")
    second = gate.apply_to_correction(subject, correction, True)

    assert first["placed_exercises"] == [1]
    assert first["would_change"] is True
    assert second["would_change"] is False
    assert correction.read_text(encoding="utf-8") == written
    # Le porteur vient sous le titre et sous son filet, jamais entre les deux.
    lines = written.splitlines()
    assert lines[2].startswith("%")
    assert lines[3].strip() == ""
    assert lines[4].startswith(gate.CARRIER)


def test_an_inline_heading_is_split_rather_than_broken(tmp_path: Path) -> None:
    subject = _subject(tmp_path, MARKED_SUBJECT)
    correction = tmp_path / "FIXTURE-EV-A-corrige.tex"
    correction.write_text(
        "\\textbf{Exercice 1.} La réponse tient sur la même ligne.\n",
        encoding="utf-8",
    )

    result = gate.apply_to_correction(subject, correction, True)
    lines = correction.read_text(encoding="utf-8").splitlines()

    assert result["placements"] == [
        {"exercise": 1, "placement": "SPLIT_INLINE_HEADING"}
    ]
    assert lines[0] == "\\textbf{Exercice 1.}"
    assert lines[1].startswith(gate.CARRIER)
    assert lines[2] == ""
    assert lines[3] == "La réponse tient sur la même ligne."


def test_a_carrier_belonging_to_no_exercise_is_removed(tmp_path: Path) -> None:
    subject = _subject(tmp_path, MARKED_SUBJECT)
    correction = tmp_path / "FIXTURE-EV-A-corrige.tex"
    correction.write_text(
        "\\section*{Corrigé — titre général}\n"
        + gate.CARRIER
        + "{Q1 : 9 pts}\n\n\\section*{Exercice 1}\n\nRéponse.\n",
        encoding="utf-8",
    )

    result = gate.apply_to_correction(subject, correction, True)
    written = correction.read_text(encoding="utf-8")

    assert result["stray_carriers_removed"] == 1
    assert "9 pts" not in written
    assert written.count(gate.CARRIER) == 1
