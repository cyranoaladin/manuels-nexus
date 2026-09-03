"""La demande de corrigé-barème commenté : préparée, jamais pré-remplie.

Le contrat pédagogique exige une couche que rien ne permet de dériver : pour
chaque question, ce qui rapporte les points, les erreurs pénalisées, les points
de rédaction. L'écrire à la place d'un enseignant serait le « barème inventé »
que la campagne s'interdit ; ne rien faire laisserait le blocage sans issue.

Ce module vérifie donc les deux moitiés : que la demande est complète -- énoncé,
valeur, réponse du corrigé, pour chacune des questions -- et que les trois
cases de jugement restent vides.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_bareme_commentary_request as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  La couche est demandée par le contrat, pas par ce module
# ---------------------------------------------------------------------------


def test_the_requirement_is_read_from_the_contract(payload: dict[str, Any]) -> None:
    """« Ne pas inventer une couche si elle n'est pas demandée. »"""

    source = payload["the_layer_is_contractual_not_invented"]
    contract = ROOT / source["contract"]
    assert contract.is_file()
    text = contract.read_text(encoding="utf-8")
    assert source["sentence"] in text, "la phrase citée n'est pas celle du contrat"
    for expected in ("rapporte les points", "pénalisées", "rédaction"):
        assert expected in source["sentence"], expected


def test_a_contract_that_stopped_asking_stops_the_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Si le contrat retire l'exigence, ce module doit se taire, pas insister."""

    silent = tmp_path / "contrat.md"
    silent.write_text("Temps 9 — Évaluation\n\nUn sujet type.\n", encoding="utf-8")
    monkeypatch.setattr(gate, "CONTRACT", silent.name)
    monkeypatch.setattr(gate, "ROOT", tmp_path)

    with pytest.raises(gate.CommentaryError, match="ne demande plus"):
        gate.contract_requirement()


# ---------------------------------------------------------------------------
#  La demande est complète
# ---------------------------------------------------------------------------


def test_every_assessment_has_a_prepared_request(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert summary["ASSESSMENTS"] == 20
    assert summary["ASSESSMENTS_AWAITING_COMMENTARY"] == 20
    assert summary["QUESTIONS_WITHOUT_A_PREPARED_REQUEST"] == 0
    assert summary["QUESTIONS_AWAITING_COMMENTARY"] > 250
    # Chaque évaluation apporte des questions : aucun dossier vide.
    for packet in payload["packets"]:
        assert packet["question_count"] > 0, packet["object_id"]


def test_every_question_carries_what_a_teacher_needs_to_answer(
    payload: dict[str, Any],
) -> None:
    """Sans l'énoncé et la réponse, la demande obligerait à tout retrouver."""

    for packet in payload["packets"]:
        for exercise in packet["exercises"]:
            for question in exercise["questions"]:
                assert question["question"].startswith("Q"), question
                assert question["statement"].strip(), question
                # Deux sujets ne valuent pas leurs questions : c'est
                # précisément pourquoi ils attendent aussi un barème. La
                # demande de commentaire ne s'y arrête pas.
                if question["points"] is not None:
                    assert question["points"].strip(), question
                assert question["correction_answer"].strip(), question
                assert question["correction_answer_scope"] in (
                    "question",
                    "exercise",
                ), question
    # Aucune question ne doit rester sans texte de corrigé en face d'elle :
    # trois conventions de rédaction coexistent dans le corpus, et n'en lire
    # qu'une laissait deux cents questions muettes.
    assert payload["summary"]["QUESTIONS_WITHOUT_ANY_CORRECTION_TEXT"] == 0


def test_the_three_judgement_boxes_are_left_empty(payload: dict[str, Any]) -> None:
    """C'est le cœur : ce module prépare la question, il n'y répond pas."""

    assert payload["approves_nothing"] is True
    for packet in payload["packets"]:
        assert packet["nothing_here_is_written_for_the_teacher"] is True
        for exercise in packet["exercises"]:
            for question in exercise["questions"]:
                boxes = question["to_be_written_by_a_teacher"]
                assert set(boxes) == set(gate.REQUESTED_FIELDS)
                assert all(value == "" for value in boxes.values()), question


def test_each_awaiting_assessment_has_a_readable_packet_on_disk(
    payload: dict[str, Any],
) -> None:
    for packet in payload["packets"]:
        if packet["carries_commentary_already"]:
            continue
        name = packet["object_id"]
        for suffix in (".json", ".md"):
            path = gate.PACKET_DIR / f"{name}{suffix}"
            assert path.is_file(), path
        readable = (gate.PACKET_DIR / f"{name}.md").read_text(encoding="utf-8")
        assert "Erreurs pénalisées" in readable
        assert packet["subject_path"] in readable


# ---------------------------------------------------------------------------
#  Les questions imbriquées, qui décalaient tout
# ---------------------------------------------------------------------------


NESTED = r"""
\begin{enumerate}
  \item Première question.
  \ifnxVersionProfesseur\hfill\textit{(1 pt — modéliser)}\fi
  \item Chapeau de la quatrième.
  \begin{enumerate}
    \item Sous-question a.
    \ifnxVersionProfesseur\hfill\textit{(1 pt — communiquer)}\fi
    \item Sous-question b.
    \ifnxVersionProfesseur\hfill\textit{(1 pt — chercher)}\fi
  \end{enumerate}
\end{enumerate}
"""


def test_a_nested_question_keeps_its_own_statement() -> None:
    """Apparier par le RANG décalait tout dès qu'un exercice imbriquait.

    « Q2b » se retrouvait sans énoncé et « Q2a » héritait du chapeau : c'est
    exactement ce que la mesure a signalé sur les deux évaluations SUITES.
    """

    labelled = gate.statements_by_label(NESTED)

    assert labelled["Q1"] == "Première question."
    assert labelled["Q2"] == "Chapeau de la quatrième."
    assert labelled["Q2a"] == "Sous-question a."
    assert labelled["Q2b"] == "Sous-question b."


def test_an_answer_written_for_the_whole_exercise_is_said_to_be_so(
    tmp_path: Path,
) -> None:
    """Quatre chapitres répondent par exercice : le présenter autrement mentirait."""

    correction = tmp_path / "corrige.tex"
    correction.write_text(
        "\\textbf{Exercice 1.}\n"
        "\\baremeIndicatif{Q1 : 2 pts ; Q2 : 3 pts}\n\n"
        "Un seul paragraphe couvre les deux questions.\n",
        encoding="utf-8",
    )

    answers = gate.correction_answers(correction)

    # Aucune réponse par question, mais le texte de l'exercice est là.
    assert "1" not in answers[1]
    text, scope = gate._answer_for(answers[1], "1")
    assert scope == "exercise"
    assert "un seul paragraphe" in text.lower()
    # Le barème indicatif n'est pas la réponse : il est retiré.
    assert "baremeIndicatif" not in text


def test_the_three_heading_conventions_are_all_read(tmp_path: Path) -> None:
    """Section, sous-section ou simple gras : le corpus emploie les trois."""

    for index, heading in enumerate(
        ("\\section*{Exercice 1}", "\\subsection*{Exercice 1 — 5 points}",
         "\\textbf{Exercice 1.}"),
    ):
        correction = tmp_path / f"corrige-{index}.tex"
        correction.write_text(
            f"{heading}\n\\textbf{{Question 1.}}\nLa réponse.\n", encoding="utf-8"
        )
        answers = gate.correction_answers(correction)
        assert answers[1]["1"] == "La réponse.", heading


def test_a_margin_note_with_braces_is_removed_whole(tmp_path: Path) -> None:
    """`[^}]*` s'arrêtait à la première accolade et laissait la moitié du texte."""

    correction = tmp_path / "corrige.tex"
    correction.write_text(
        "\\section*{Exercice 1}\n"
        "\\textbf{Question 1 — Titre.}\n"
        "\\commentaireMarge{Appliquer $u_{n+1} = u_n + 4$ ici.}\n"
        "La vraie réponse.\n",
        encoding="utf-8",
    )

    answers = gate.correction_answers(correction)

    assert answers[1]["1"] == "La vraie réponse."


def test_answers_do_not_leak_from_one_exercise_to_another(tmp_path: Path) -> None:
    """Les numéros de question repartent à un dans chaque exercice."""

    correction = tmp_path / "corrige.tex"
    correction.write_text(
        "\\section*{Exercice 1}\n\\textbf{Question 1 — A.}\nRéponse un-un.\n"
        "\\section*{Exercice 2}\n\\textbf{Question 1 — B.}\nRéponse deux-un.\n",
        encoding="utf-8",
    )

    answers = gate.correction_answers(correction)

    assert answers[1]["1"] == "Réponse un-un."
    assert answers[2]["1"] == "Réponse deux-un."
