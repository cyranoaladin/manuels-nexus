#!/usr/bin/env python3
"""Le corrigé-barème commenté : ce que le contrat demande, et ce qui manque.

`Mathematiques/manuel-maths/docs/01_conception_manuel.md`, Temps 9, l'écrit
noir sur blanc :

> **Corrigé-barème commenté** : pour chaque question, ce qui rapporte les
> points, les erreurs pénalisées, les points de rédaction.

La couche est donc CONTRACTUELLE. Elle n'est pas inventée ici, et la question
« faut-il la produire ? » a une réponse écrite : oui.

Elle ne se dérive de rien. Le sujet dit combien vaut une question ; il ne dit
pas ce qui rapporte ses points, quelle erreur coûte quoi, ni ce qu'on attend
de la rédaction. Ce sont trois jugements pédagogiques, et les écrire à la place
d'un enseignant serait exactement le « barème inventé » que la campagne
s'interdit.

Ce module ne les écrit donc pas. Il prépare la DEMANDE : pour chacune des vingt
évaluations, question par question, avec son énoncé, sa valeur, la réponse du
corrigé, et les trois cases à remplir. Un enseignant ouvre le dossier et
répond ; rien ne lui demande de retrouver le contexte.

Métriques : `ASSESSMENTS`, `QUESTIONS_AWAITING_COMMENTARY`,
`ASSESSMENTS_CARRYING_COMMENTARY`, `REQUEST_PACKETS_WRITTEN`.
Métrique bloquante : `QUESTIONS_WITHOUT_A_PREPARED_REQUEST`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_1spe_assessment_bareme_transcription as transcription  # noqa: E402
from build_1spe_assessment_bareme_transcription import LETTERS  # noqa: E402
from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_BAREME_COMMENTARY_REQUEST.json"
MD_TARGET = ROOT / "audit/1SPE_BAREME_COMMENTARY_REQUEST.md"
PACKET_DIR = ROOT / "audit/1SPE_BAREME_COMMENTARY_REQUEST"
GENERATED_BY = "scripts/build_1spe_bareme_commentary_request.py"

CONTRACT = "Mathematiques/manuel-maths/docs/01_conception_manuel.md"
# La phrase du contrat, cherchée dans le contrat lui-même : si elle disparaît,
# ce module doit cesser de réclamer une couche que plus personne ne demande.
CONTRACT_SENTENCE = re.compile(
    r"Corrig[ée]-bar[èe]me comment[ée]\s*\*\*\s*:\s*(.+)", re.IGNORECASE
)
# Ce que le contrat nomme, et donc ce que la demande met en face du relecteur.
REQUESTED_FIELDS = (
    "ce_qui_rapporte_les_points",
    "erreurs_penalisees",
    "points_de_redaction",
)
# La marque d'une couche déjà écrite, la même que celle du registre de blocage.
COMMENTARY_MARK = re.compile(
    r"erreurs? p[ée]nalis|points? de r[ée]daction", re.IGNORECASE
)


class CommentaryError(RuntimeError):
    """Une preuve manque : la demande ne peut pas être préparée."""


def contract_requirement() -> str:
    """La phrase du contrat, lue dans le contrat -- jamais recopiée ici."""

    path = ROOT / CONTRACT
    if not path.is_file():
        raise CommentaryError(f"contrat pédagogique absent : {CONTRACT}")
    match = CONTRACT_SENTENCE.search(path.read_text(encoding="utf-8"))
    if match is None:
        raise CommentaryError(
            f"{CONTRACT} ne demande plus de corrigé-barème commenté : "
            "cette demande n'a plus lieu d'être"
        )
    return match.group(1).strip().rstrip(".")


def _strip_macro(text: str, macro: str) -> str:
    """Retire `\\macro{...}`, en comptant les accolades.

    Une expression régulière en `[^}]*` s'arrête à la première accolade
    fermante, et une note de marge contient volontiers `$u_{n+1}$` : elle
    laissait alors la moitié de son contenu derrière elle.
    """

    marker = "\\" + macro + "{"
    while (start := text.find(marker)) != -1:
        depth = 0
        index = start + len(marker) - 1
        while index < len(text):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    break
            index += 1
        text = text[:start] + " " + text[index + 1 :]
    return text


# Les corrigés du corpus ouvrent leurs exercices de trois façons -- section,
# sous-section, ou simple gras -- et rédigent leurs réponses de deux façons :
# « Question 3 — titre » ou le seul « 3. ». Quatre chapitres répondent même par
# exercice entier. Chercher une seule convention laissait deux cents questions
# sur trois cents sans la moindre réponse en face d'elles.
EXERCISE_HEADING = re.compile(
    r"\\(?:sub){0,2}section\*\{\s*Exercice\s+(\d+)"
    r"|\\textbf\{\s*Exercice\s+(\d+)",
    re.IGNORECASE,
)
ANSWER_HEADING = re.compile(
    r"\\textbf\{\s*(?:Question\s+)?(\d+)\s*[.\u2014-][^}]*\}"
)


def correction_answers(path: Path) -> dict[int, dict[str, str]]:
    """Ce que le corrigé répond, par exercice et par question.

    Les numéros de question repartent à un dans chaque exercice : les lire à
    plat mélangerait les réponses de l'exercice 1 avec les questions de
    l'exercice 3.
    """

    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    sections = list(EXERCISE_HEADING.finditer(text))
    answers: dict[int, dict[str, str]] = {}
    for index, section in enumerate(sections):
        number = int(section.group(1) or section.group(2))
        stop = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        body = text[section.end() : stop]
        found: dict[str, str] = {}
        # Quatre chapitres repondent par EXERCICE et non par question : un seul
        # paragraphe couvre toutes les questions. Ce texte-la est garde comme
        # contexte, sous la clef vide, plutot que de laisser le dossier muet.
        found[""] = " ".join(
            _strip_macro(
                re.sub(r"\\baremeIndicatif\{[^}]*\}", " ", body),
                "commentaireMarge",
            ).split()
        )[:400]
        questions = list(ANSWER_HEADING.finditer(body))
        for position, question in enumerate(questions):
            end = (
                questions[position + 1].start()
                if position + 1 < len(questions)
                else len(body)
            )
            # La note de marge est une aide de lecture destinee au professeur,
            # pas la reponse : elle est retiree de l'extrait.
            chunk = _strip_macro(body[question.end() : end], "commentaireMarge")
            found[question.group(1)] = " ".join(chunk.split())[:400]
        # Un exercice repete (section puis gras) ne doit pas ecraser ce qui a
        # deja ete lu pour lui.
        answers.setdefault(number, {}).update(
            {key: value for key, value in found.items() if value}
        )
    return answers


def statements_by_label(body: str) -> dict[str, str]:
    """L'énoncé de CHAQUE question, étiqueté comme le sont ses points.

    `question_statements` ne rend que les questions de premier rang, et les
    apparier par leur RANG à des marques qui, elles, descendent dans les
    sous-questions décale tout dès qu'un exercice en porte : « Q4b » se
    retrouvait sans énoncé, et « Q4a » héritait du chapeau de la question 4.
    Le même parcours d'arbre que `scan_questions` est donc refait ici, à ceci
    près qu'il retient le texte plutôt que les points.
    """

    tokens = list(
        re.finditer(r"\\begin\{enumerate\}|\\end\{enumerate\}|\\item\b", body)
    )
    depth = 0
    counters = [0, 0, 0]
    opened: list[tuple[str, int]] = []
    for match in tokens:
        token = match.group(0)
        if token.startswith("\\begin"):
            depth += 1
            if depth < len(counters):
                counters[depth] = 0
            continue
        if token.startswith("\\end"):
            depth = max(0, depth - 1)
            continue
        if depth == 1:
            counters[1] += 1
            if len(counters) > 2:
                counters[2] = 0
            opened.append((f"Q{counters[1]}", match.end()))
        elif depth >= 2 and len(counters) > 2:
            counters[2] += 1
            letter = LETTERS[(counters[2] - 1) % len(LETTERS)]
            opened.append((f"Q{counters[1]}{letter}", match.end()))

    statements: dict[str, str] = {}
    for index, (label, start) in enumerate(opened):
        stop = (
            opened[index + 1][1] - len("\\item")
            if index + 1 < len(opened)
            else len(body)
        )
        chunk = body[start:stop]
        # Le chapeau d'une question qui ouvre des sous-questions s'arrête là où
        # elles commencent : ce qui suit appartient à « a », pas à « 4 ».
        chunk = chunk.split("\\begin{enumerate}")[0]
        chunk = chunk.split("\\end{enumerate}")[0]
        # La valeur en points est donnée à part, dans son propre champ : la
        # laisser traîner en queue d'énoncé ne ferait que brouiller la lecture.
        chunk = re.split(r"\\ifnxVersionProfesseur", chunk)[0]
        statements[label] = " ".join(chunk.split())[:400]
    return statements


def _answer_for(answers: dict[str, str], number: str) -> tuple[str, str]:
    """La reponse du corrige pour une question, et a quelle echelle elle est ecrite.

    Quatre chapitres redigent leur corrige par exercice : un seul paragraphe
    couvre toutes les questions. Le presenter comme la reponse DE la question
    serait faux ; ne rien presenter obligerait l'enseignant a rouvrir le
    corrige. L'echelle est donc dite.
    """

    precise = answers.get(number, "")
    if precise:
        return precise, "question"
    whole = answers.get("", "")
    if whole:
        return whole, "exercise"
    return "", "absent"


def prepare(subject_path: Path, requirement: str) -> dict[str, Any]:
    subject = transcription.analyse_subject(subject_path)
    text = subject_path.read_text(encoding="utf-8")
    correction = transcription.correction_path(subject_path)
    answers = correction_answers(correction)
    already = bool(correction.is_file()) and bool(
        COMMENTARY_MARK.search(correction.read_text(encoding="utf-8"))
    )

    bodies = {
        row["number"]: text[row["start"] : row["end"]]
        for row in transcription.split_exercises(text)
    }
    exercises: list[dict[str, Any]] = []
    for exercise in subject["exercises"]:
        # Les questions viennent des ÉNONCÉS, pas des marques de points. Deux
        # sujets -- les deux GEOREP -- ne valuent leurs questions nulle part :
        # partir des marques aurait rendu leur dossier vide, alors que ce sont
        # justement ceux dont tout reste à écrire. La valeur en points est
        # jointe quand le sujet la porte, et dite absente sinon.
        labelled = statements_by_label(bodies.get(exercise["number"], ""))
        marks = {mark["label"]: mark for mark in exercise["marks"]}
        questions = []
        for label, statement in labelled.items():
            # Un chapeau qui n'ouvre que des sous-questions n'est pas une
            # question : elle est posée dans ses « a », « b ».
            if any(other.startswith(label) and other != label for other in labelled):
                continue
            mark = marks.get(label)
            questions.append(
                {
                    # Le libellé de la question et sa valeur viennent du sujet
                    # tels qu'il les imprime : « Q3a », « 1,5 pt ».
                    "question": label,
                    "points": mark["verbatim"] if mark else None,
                    "competence": mark["competence"] if mark else None,
                    "statement": statement,
                    "correction_answer": _answer_for(
                        answers.get(exercise["number"], {}),
                        label.lstrip("Q").rstrip(LETTERS),
                    )[0],
                    "correction_answer_scope": _answer_for(
                        answers.get(exercise["number"], {}),
                        label.lstrip("Q").rstrip(LETTERS),
                    )[1],
                    # Les trois cases restent VIDES : les remplir serait
                    # inventer le jugement qu'on vient demander.
                    "to_be_written_by_a_teacher": {
                        field: "" for field in REQUESTED_FIELDS
                    },
                }
            )
        exercises.append(
            {
                "exercise": exercise["number"],
                "capacities": exercise["capacities"],
                "declared_total": str(exercise["declared_total"])
                if exercise["declared_total"] is not None
                else None,
                "questions": questions,
            }
        )

    return {
        "object_id": subject["object_id"],
        "chapter": subject["chapter"],
        "version": subject["version"],
        "duration_min": subject["duration_min"],
        "subject_path": subject["path"],
        "correction_path": transcription._relative(correction),
        "declared_total": str(subject["declared_total"])
        if subject["declared_total"] is not None
        else None,
        "carries_commentary_already": already,
        "what_the_contract_asks": requirement,
        "contract": CONTRACT,
        "nothing_here_is_written_for_the_teacher": True,
        "exercises": exercises,
        "question_count": sum(len(row["questions"]) for row in exercises),
    }


def build() -> dict[str, Any]:
    requirement = contract_requirement()
    subjects = transcription.assessments()
    if not subjects:
        raise CommentaryError("aucune évaluation 1SPE trouvée")
    packets = [prepare(path, requirement) for path in subjects]
    awaiting = [row for row in packets if not row["carries_commentary_already"]]
    return {
        "artifact_type": "1spe_bareme_commentary_request",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "approves_nothing": True,
        "the_layer_is_contractual_not_invented": {
            "contract": CONTRACT,
            "sentence": requirement,
        },
        "why_it_cannot_be_derived": (
            "Le sujet dit combien vaut une question ; il ne dit pas ce qui "
            "rapporte ses points, quelle erreur coûte quoi, ni ce qu'on attend "
            "de la rédaction. Ce sont trois jugements pédagogiques, et les "
            "écrire à la place d'un enseignant serait un barème inventé."
        ),
        "requested_fields": list(REQUESTED_FIELDS),
        "packets": packets,
        "summary": {
            "ASSESSMENTS": len(packets),
            "ASSESSMENTS_CARRYING_COMMENTARY": len(packets) - len(awaiting),
            "ASSESSMENTS_AWAITING_COMMENTARY": len(awaiting),
            "QUESTIONS_AWAITING_COMMENTARY": sum(
                row["question_count"] for row in awaiting
            ),
            "QUESTIONS_ANSWERED_AT_EXERCISE_SCALE": sum(
                1
                for row in awaiting
                for exercise in row["exercises"]
                for question in exercise["questions"]
                if question["correction_answer_scope"] == "exercise"
            ),
            "QUESTIONS_WITHOUT_ANY_CORRECTION_TEXT": sum(
                1
                for row in awaiting
                for exercise in row["exercises"]
                for question in exercise["questions"]
                if question["correction_answer_scope"] == "absent"
            ),
            "QUESTIONS_WITHOUT_A_PREPARED_REQUEST": sum(
                1
                for row in awaiting
                for exercise in row["exercises"]
                for question in exercise["questions"]
                if not question["statement"]
            ),
        },
    }


def write_packets(payload: dict[str, Any]) -> int:
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for packet in payload["packets"]:
        if packet["carries_commentary_already"]:
            continue
        target = PACKET_DIR / f"{packet['object_id']}.json"
        target.write_text(
            json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (PACKET_DIR / f"{packet['object_id']}.md").write_text(
            render_packet(packet), encoding="utf-8"
        )
        written += 1
    return written


def render_packet(packet: dict[str, Any]) -> str:
    lines = [
        f"# Corrigé-barème commenté — {packet['object_id']}",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Chapitre `{packet['chapter']}`, version {packet['version']}, "
        f"{packet['duration_min']} min, {packet['declared_total']} points.",
        "",
        f"Le contrat (`{packet['contract']}`) demande : "
        f"{packet['what_the_contract_asks']}.",
        "",
        "Rien n'est pré-rempli : les trois colonnes attendent votre jugement.",
        "",
        f"- Sujet : `{packet['subject_path']}`",
        f"- Corrigé : `{packet['correction_path']}`",
    ]
    for exercise in packet["exercises"]:
        lines += [
            "",
            f"## Exercice {exercise['exercise']} — "
            f"{exercise['declared_total']} points "
            f"({exercise['capacities'] or '—'})",
            "",
        ]
        for question in exercise["questions"]:
            lines += [
                f"### Question {question['question']}"
                + (
                    f" — {question['points']}"
                    if question["points"]
                    else " — valeur non déclarée par le sujet"
                ),
                "",
                f"> {question['statement'] or '_énoncé non retrouvé_'}",
                "",
                (
                    "Réponse du corrigé"
                    + (
                        " (rédigée pour l'exercice entier)"
                        if question["correction_answer_scope"] == "exercise"
                        else ""
                    )
                    + f" : {question['correction_answer'] or '—'}"
                ),
                "",
                "| Ce qui rapporte les points | Erreurs pénalisées | "
                "Points de rédaction |",
                "|---|---|---|",
                "|  |  |  |",
                "",
            ]
    return "\n".join(lines) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Corrigé-barème commenté — demande préparée",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['why_it_cannot_be_derived']}",
        "",
        f"Le contrat `{payload['the_layer_is_contractual_not_invented']['contract']}` "
        f"demande : {payload['the_layer_is_contractual_not_invented']['sentence']}.",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Évaluations",
        "",
        "| Évaluation | Chapitre | Questions | Couche déjà écrite | Dossier |",
        "|---|---|---:|---|---|",
    ]
    for packet in payload["packets"]:
        name = packet["object_id"]
        lines.append(
            f"| `{name}` | {packet['chapter']} | {packet['question_count']} | "
            f"{'oui' if packet['carries_commentary_already'] else '**non**'} | "
            f"`audit/1SPE_BAREME_COMMENTARY_REQUEST/{name}.md` |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except (CommentaryError, transcription.TranscriptionError) as error:
        print(f"1SPE-BAREME-COMMENTARY-REQUEST-ERROR: {error}", file=sys.stderr)
        return 2

    written = 0
    if not arguments.check:
        written = write_packets(payload)
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.name}, {MD_TARGET.name} et {written} dossiers")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    print(f"REQUEST_PACKETS_WRITTEN={written}")
    return 1 if payload["summary"]["QUESTIONS_WITHOUT_A_PREPARED_REQUEST"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
