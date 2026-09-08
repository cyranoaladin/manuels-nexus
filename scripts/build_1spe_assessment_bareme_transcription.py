#!/usr/bin/env python3
"""Barèmes des évaluations 1SPE : transcrire ce qui existe, refuser d'inventer.

Le gate de complétude professeur (`TEACHER_BAREME_PER_GRADED_OBJECT`) compte
la présence de la macro de charte `\\baremeIndicatif` dans le corrigé d'un
objet noté. Il ne dit rien des VALEURS. Ce producteur s'occupe des valeurs, et
il le fait dans un seul sens : il LIT le sujet, et il n'écrit dans le corrigé
que ce que le sujet a déjà décidé.

Pour chaque évaluation :

* le sujet est analysé exercice par exercice — l'intitulé donne le total de
  l'exercice, chaque question de l'`enumerate` porte ou ne porte pas sa valeur ;
* trois contrôles doivent passer ensemble : chaque question a une valeur, la
  somme des questions vaut le total de l'exercice, et la somme des exercices
  vaut le total déclaré dans la META. La somme n'est qu'un contrôle secondaire :
  ce qui compte est que chaque point soit rattaché à SA question, et c'est
  pourquoi la valeur est lue question par question et jamais répartie ;
* si un seul de ces contrôles échoue, l'évaluation est classée
  `HUMAN_PEDAGOGICAL_JUDGEMENT_REQUIRED` et rien n'est écrit. Répartir
  uniformément, deviner 1/2/3 points ou recopier le barème d'une autre
  évaluation est interdit — le producteur ne sait pas le faire.

Le mode `--apply` insère `\\baremeIndicatif{...}` dans le corrigé, sous
l'intitulé de chaque exercice, avec les valeurs transcrites telles quelles,
virgule décimale française comprise.

Métriques : `TRANSCRIPTIBLE`, `HUMAN_PEDAGOGICAL_JUDGEMENT_REQUIRED`,
`SUM_MISMATCH`, `CARRIER_MISSING_AFTER_APPLY`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json"
MD_TARGET = ROOT / "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.md"
GENERATED_BY = "scripts/build_1spe_assessment_bareme_transcription.py"
CHAPTERS = ROOT / "Mathematiques/manuel-maths/chapitres"
CARRIER = r"\baremeIndicatif"

META = re.compile(r"^% META:\s*(\{.*\})\s*$", re.MULTILINE)
GRADED_FIELD = re.compile(r"bar[eè]me|point", re.IGNORECASE)

# Les intitulés d'exercice s'écrivent de plusieurs façons dans le corpus, et
# toutes sont autoritaires : ce sont les sujets composés. On les lit, on ne les
# uniformise pas ici. Un intitulé est une commande de titre — \section*,
# \subsection*, \textbf — qui nomme « Exercice n », ou la macro de charte
# \exerciceEval. Le total et les capacités sont ensuite extraits du corps de
# l'intitulé, ce qui absorbe les variantes : « \hfill \textit{6 points — C1} »,
# « — 5 points — C1, C2 », « \hfill (5 points) \hfill Capacites C1 » et
# « \ifnxVersionProfesseur\hfill (6 points)\fi \hfill Capacités C1 ».
# L'intitulé est lu sur SA LIGNE entière : le total se trouve tantôt dans les
# accolades du titre, tantôt après elles
# (« \textbf{Exercice 1} \hfill \textit{6 points — C1, C2} »).
HEADING = re.compile(
    r"\\(?:sub)?(?:section\*|textbf)\{\s*Exercice\s+(?P<number>\d+)\b"
)
EXERCICE_EVAL = re.compile(
    r"\\exerciceEval\{(?P<number>\d+)\}\{(?P<total>[\d,.]+)\}"
    r"\{(?P<capacities>[^}]*)\}\{[^}]*\}"
)
HEADING_TOTAL = re.compile(r"\(?\s*(?P<total>\d+(?:(?:\{,\}|[,.])\d+)?)\s*points?\s*\)?")
HEADING_CAPACITIES = re.compile(r"(?P<codes>C\d+(?:\s*,\s*C\d+)*)")

# \item ... \hfill \textit{(1,5 pt)} | \hfill(2 pts) | \hfill\textit{(1,5 pt --- calculer)}
# La virgule décimale s'écrit « 1,5 » ou « 1{,}5 » selon les sujets : les deux
# formes sont dans le corpus et les deux composent le même nombre.
DECIMAL = r"\d+(?:(?:\{,\}|[,.])\d+)?"
QUESTION_POINTS = re.compile(
    r"\\hfill\s*(?:\\textit\{)?\(\s*"
    r"(?P<verbatim>(?P<points>" + DECIMAL + r")\s*pts?)\b"
    r"(?:\s*(?:—|---)\s*(?P<competence>[^)}]*))?\s*\)"
)
# Un exercice se lit comme un arbre de questions : `enumerate` imbriqués, et
# la valeur en points est portée par la question qui la mérite -- parfois une
# sous-question. L'étiquette suit donc la structure : Q1, Q2, Q3, Q4a, Q4b.
# C'est la convention déjà écrite dans les barèmes du corpus.
SCAN = re.compile(
    r"\\begin\{enumerate\}|\\end\{enumerate\}|\\item\b"
    r"|\\hfill\s*(?:\\textit\{)?\(\s*"
    r"(?P<verbatim>(?P<points>\d+(?:(?:\{,\}|[,.])\d+)?)\s*pts?)\b"
    r"(?:\s*(?:—|---)\s*(?P<competence>[^)}]*))?\s*\)"
)
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def question_statements(body: str) -> list[str]:
    """Les énoncés des questions de premier rang, pour le dossier humain.

    Le reviewer doit lire la tâche avant d'en fixer le prix : sans l'énoncé,
    un nombre de points ne veut rien dire. Le texte est rendu brut, tel qu'il
    est écrit dans le sujet — la mise en forme LaTeX comprise, qu'on ne cherche
    pas à interpréter ici.
    """

    boundaries = []
    depth = 0
    for match in re.finditer(
        r"\\begin\{enumerate\}|\\end\{enumerate\}|\\item\b", body
    ):
        token = match.group(0)
        if token.endswith("{enumerate}") and token.startswith("\\begin"):
            depth += 1
        elif token.endswith("{enumerate}"):
            depth -= 1
        elif depth == 1:
            boundaries.append((match.end(), depth))
    statements: list[str] = []
    for index, (position, _depth) in enumerate(boundaries):
        stop = (
            boundaries[index + 1][0] - len("\\item")
            if index + 1 < len(boundaries)
            else len(body)
        )
        chunk = body[position:stop]
        # On coupe au premier \end{enumerate} rencontre : la question s'arrete
        # la, meme si elle contenait un enumerate imbrique.
        chunk = chunk.split("\\end{enumerate}")[0]
        statements.append(" ".join(chunk.split())[:400])
    return statements


def scan_questions(body: str) -> tuple[list[dict[str, Any]], int]:
    """Les marques de points étiquetées par leur place dans l'arbre.

    Rend aussi le nombre de questions de PREMIER rang : c'est contre lui que
    la complétude se mesure, une question valuée par ses sous-questions étant
    bien valuée.
    """

    depth = 0
    counters = [0, 0, 0]
    marks: list[dict[str, Any]] = []
    top_level = 0
    covered: set[int] = set()
    for match in SCAN.finditer(body):
        token = match.group(0)
        if token.startswith(r"\begin"):
            depth += 1
            if depth < len(counters):
                counters[depth] = 0
            continue
        if token.startswith(r"\end"):
            depth = max(0, depth - 1)
            continue
        if token.startswith(r"\item"):
            if depth == 1:
                counters[1] += 1
                top_level += 1
                if len(counters) > 2:
                    counters[2] = 0
            elif depth >= 2 and len(counters) > 2:
                counters[2] += 1
            continue
        if match.group("points") is None or depth == 0 or counters[1] == 0:
            continue
        label = f"Q{counters[1]}"
        if depth >= 2 and counters[2] > 0:
            label += LETTERS[(counters[2] - 1) % len(LETTERS)]
        covered.add(counters[1])
        marks.append(
            {
                "label": label,
                "points": parse_points(match.group("points")),
                # Le libellé du point est repris VERBATIM du sujet : « 1,5 pt »,
                # « 1{,}5 pt » et « 2 pts » y coexistent, et transcrire
                # exactement veut dire ne pas renormaliser ce que le sujet
                # imprime.
                "verbatim": render_mark(
                    match.group("points"), parse_points(match.group("points"))
                ),
                "competence": (match.group("competence") or "").strip() or None,
            }
        )
    return marks, top_level, len(covered)


# ---------------------------------------------------------------------------
#  Proposition de barème pour ce qui n'est PAS transcriptible
# ---------------------------------------------------------------------------
# Ces deux sujets ne valuent pas leurs questions : seul le total de chaque
# exercice est imprimé. Répartir ce total est un jugement pédagogique, et il
# n'est PAS pris ici. Ce qui suit est une PROPOSITION machine, motivée question
# par question par l'exigence de raisonnement, et elle n'est écrite dans aucun
# corrigé. Le verdict appartient à EXPERT_PROGRAMME_PEDAGOGIE ;
# EXPERT_MATHEMATIQUE doit au minimum confirmer la pertinence scientifique et
# la complexité relative.
#
# Chaque proposition somme au total imprimé de son exercice. C'est un contrôle
# secondaire : ce qui est proposé, c'est le rattachement d'un point à SA tâche.
CANDIDATE_PROPOSALS: dict[str, dict[int, list[tuple[str, str]]]] = {
    "1SPE-GEOREP": {
        1: [
            ("1 pt", "coordonnées d'un vecteur : application directe"),
            ("1 pt", "coefficient directeur : application directe"),
            ("1,5 pt", "équation cartésienne : c'est la capacité C1 elle-même,"
                       " elle demande d'assembler les deux résultats précédents"),
            ("0,5 pt", "vérification d'appartenance : contrôle, pas de méthode"
                       " nouvelle"),
        ],
        2: [
            ("1 pt", "lecture d'un vecteur normal et d'un vecteur directeur"),
            ("2 pts", "équation de la perpendiculaire par un point donné :"
                      " tâche centrale de C2"),
            ("1 pt", "vérification de l'orthogonalité par le produit scalaire"),
        ],
        3: [
            ("1 pt", "équation du cercle à partir du centre et du rayon"),
            ("0,5 pt", "appartenance d'un point : substitution"),
            ("0,5 pt", "appartenance d'un second point : même substitution"),
            ("2 pts", "développer puis retrouver centre et rayon en complétant"
                      " les carrés : seule question à changer de registre"),
        ],
        4: [
            ("1,5 pt", "distance d'un point à une droite : formule à appliquer"
                       " correctement"),
            ("0,5 pt", "position relative : interprétation immédiate de la"
                       " distance obtenue"),
            ("2 pts", "coordonnées exactes des points d'intersection :"
                      " résolution d'un système, valeurs exactes exigées"),
        ],
        5: [
            ("1,5 pt", "aire du triangle : le choix de la méthode est laissé"
                       " à l'élève, ce que la compétence « chercher » vise"),
            ("1,5 pt", "projeté orthogonal : construction la plus exigeante"
                       " de l'exercice"),
            ("1 pt", "hauteur déduite de l'aire et de la base"),
        ],
    }
}


# Le geste que le sujet demande, lu sur son propre verbe -- même liste que le
# producteur de propositions de barème commenté, et pour la même raison : c'est
# le sujet qui dit ce qu'il évalue.
_PROOF = re.compile(r"\bd[ée]montrer\b|\bprouver\b|\bjustifier\b|\bmontrer\b", re.I)
_DEDUCTION = re.compile(r"\ben d[ée]duire\b|\bd'o[uù]\b", re.I)
_GESTURES = (
    (r"\bd[ée]montrer\b|\bprouver\b", "démontrer"),
    (r"\bjustifier\b", "justifier"),
    (r"\ben d[ée]duire\b", "en déduire"),
    (r"\bd[ée]terminer\b", "déterminer"),
    (r"\br[ée]soudre\b", "résoudre"),
    (r"\bv[ée]rifier\b", "vérifier"),
    (r"\bcalculer\b", "calculer"),
    (r"\bexprimer\b", "exprimer"),
    (r"\bmontrer\b", "montrer"),
    (r"\bdonner\b|\bindiquer\b|\b[ée]crire\b", "donner"),
)


def _gesture_of(statement: str) -> str | None:
    lowered = statement.lower()
    for pattern, name in _GESTURES:
        if re.search(pattern, lowered):
            return name
    return None


def proposal_for(object_id: str) -> dict[int, list[tuple[str, str]]] | None:
    for prefix, proposal in CANDIDATE_PROPOSALS.items():
        if object_id.startswith(prefix):
            return proposal
    return None


TRANSCRIPTIBLE = "TRANSCRIPTIBLE"
HUMAN_REQUIRED = "HUMAN_PEDAGOGICAL_JUDGEMENT_REQUIRED"


def _relative(path: Path) -> str:
    """Chemin relatif au dépôt, ou chemin tel quel hors du dépôt.

    Les fixtures des tests vivent hors de l'arbre : le producteur doit pouvoir
    les analyser sans exiger qu'elles y soient.
    """

    try:
        return relative(path)
    except ValueError:
        return path.as_posix()


class TranscriptionError(RuntimeError):
    """Une preuve manque : rien ne sera écrit."""


def parse_points(raw: str) -> Fraction:
    """« 1,5 » et « 1.5 » valent la même chose ; on garde l'exactitude."""

    return Fraction(raw.replace("{,}", ".").replace(",", "."))


def render_mark(number: str, value: Fraction) -> str:
    """Le NOMBRE vient du sujet, verbatim ; l'unité suit l'accord français.

    Le corpus écrit tantôt « (2 pt) » dans le sujet et « 2 pts » dans le
    barème. Le nombre est ce qui doit être transcrit exactement — c'est lui qui
    porte le point. « pt » au singulier après « 2 » est une faute d'accord, et
    la règle appliquée ici (« pt » sous 2, « pts » à partir de 2) reproduit
    exactement les vingt-sept barèmes déjà écrits et vérifiés du corpus.
    """

    # « 1{,}5 » et « 1,5 » composent le même nombre ; les vingt-sept barèmes
    # déjà écrits emploient la seconde forme, plus lisible en source.
    return f"{number.replace('{,}', ',')} {'pt' if value < 2 else 'pts'}"


def read_meta(path: Path) -> dict[str, Any]:
    match = META.search(path.read_text(encoding="utf-8"))
    if match is None:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def declared_total(meta: dict[str, Any]) -> Fraction | None:
    for key, value in meta.items():
        if GRADED_FIELD.search(key) and isinstance(value, (int, float)):
            return Fraction(str(value))
    return None


def split_exercises(text: str) -> list[dict[str, Any]]:
    """Découpe le sujet en exercices, avec leur total et leurs bornes.

    Un exercice dont l'intitulé ne porte pas de total est signalé par un total
    nul : le classement le refusera, plutôt que de lui en inventer un.
    """

    found: list[dict[str, Any]] = []
    for match in HEADING.finditer(text):
        end_of_line = text.find("\n", match.end())
        if end_of_line < 0:
            end_of_line = len(text)
        heading = text[match.start() : end_of_line]
        total = HEADING_TOTAL.search(heading)
        capacities = HEADING_CAPACITIES.search(heading)
        found.append(
            {
                "number": int(match.group("number")),
                "declared_total": parse_points(total.group("total")) if total else None,
                "capacities": capacities.group("codes") if capacities else "",
                "start": end_of_line,
                "heading_start": match.start(),
            }
        )
    for match in EXERCICE_EVAL.finditer(text):
        found.append(
            {
                "number": int(match.group("number")),
                "declared_total": parse_points(match.group("total")),
                "capacities": " ".join(match.group("capacities").split()),
                "start": match.end(),
                "heading_start": match.start(),
            }
        )
    found.sort(key=lambda row: row["heading_start"])
    # Un même exercice ne doit être compté qu'une fois : \exerciceEval suit
    # parfois un commentaire de titre, jamais deux intitulés composés.
    unique: list[dict[str, Any]] = []
    for row in found:
        if unique and unique[-1]["number"] == row["number"]:
            continue
        unique.append(row)
    for index, row in enumerate(unique):
        row["end"] = (
            unique[index + 1]["heading_start"]
            if index + 1 < len(unique)
            else len(text)
        )
    return unique


def analyse_subject(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    meta = read_meta(path)
    exercises = []
    for row in split_exercises(text):
        body = text[row["start"] : row["end"]]
        marks, item_count, covered = scan_questions(body)
        observed = sum((mark["points"] for mark in marks), Fraction(0))
        exercises.append(
            {
                "number": row["number"],
                "declared_total": row["declared_total"],
                "capacities": row["capacities"],
                "question_count": item_count,
                "marked_question_count": len(marks),
                "marks": marks,
                "observed_total": observed,
                "statements": question_statements(body),
                "covered_question_count": covered,
                # Une question est valuée si elle porte une valeur, ou si ses
                # sous-questions en portent : c'est le cas de « 4. a) b) ».
                "every_question_is_marked": covered == item_count and item_count > 0,
                "sum_matches_exercise_total": (
                    row["declared_total"] is not None
                    and observed == row["declared_total"]
                ),
            }
        )
    return {
        "path": _relative(path),
        "object_id": meta.get("id"),
        "chapter": meta.get("chapitre"),
        "version": meta.get("version"),
        "duration_min": meta.get("duree_min"),
        "declared_total": declared_total(meta),
        "capacities": meta.get("capacites_codes", []),
        "exercises": exercises,
    }


def classify(subject: dict[str, Any]) -> dict[str, Any]:
    exercises = subject["exercises"]
    reasons: list[str] = []
    if not exercises:
        reasons.append("aucun exercice reconnu dans le sujet")
    unmarked = [row["number"] for row in exercises if not row["every_question_is_marked"]]
    if unmarked:
        reasons.append(
            "exercice(s) "
            + ", ".join(str(number) for number in unmarked)
            + " : le sujet ne donne pas de valeur question par question ; "
            "repartir le total serait un jugement pedagogique"
        )
    untotalled = [row["number"] for row in exercises if row["declared_total"] is None]
    if untotalled:
        reasons.append(
            "exercice(s) "
            + ", ".join(str(number) for number in untotalled)
            + " : l'intitule ne porte pas de total"
        )
    mismatch = [
        row["number"] for row in exercises if not row["sum_matches_exercise_total"]
    ]
    if mismatch and not unmarked:
        reasons.append(
            "exercice(s) "
            + ", ".join(str(number) for number in mismatch)
            + " : la somme des questions ne fait pas le total de l'exercice"
        )
    total = sum(
        (
            row["declared_total"]
            for row in exercises
            if row["declared_total"] is not None
        ),
        Fraction(0),
    )
    declared = subject["declared_total"]
    if declared is not None and total != declared:
        reasons.append(
            f"la somme des exercices vaut {total} et la META declare {declared}"
        )
    return {
        "classification": HUMAN_REQUIRED if reasons else TRANSCRIPTIBLE,
        "reasons": reasons,
        "exercise_total_sum": str(total),
        "declared_total": str(declared) if declared is not None else None,
        "sum_matches_declared_total": declared is not None and total == declared,
    }


def bareme_line(exercise: dict[str, Any]) -> str:
    parts = []
    for mark in exercise["marks"]:
        rendered = f"{mark['label']} : {mark['verbatim']}"
        if mark["competence"]:
            rendered += f" ({mark['competence']})"
        parts.append(rendered)
    return CARRIER + "{" + " ; ".join(parts) + "}"


CARRIER_IN_TEXT = re.compile(r"\\baremeIndicatif\{(?P<content>[^}]*)\}")
CARRIER_QUESTION = re.compile(
    r"Q(?P<label>\w+)\s*:\s*(?P<verbatim>\d+(?:(?:\{,\}|[,.])\d+)?\s*pts?)"
)


def carrier_questions(content: str) -> list[dict[str, str]]:
    return [
        {
            "label": match.group("label"),
            "verbatim": " ".join(match.group("verbatim").split()),
            "points": str(parse_points(match.group("verbatim").split()[0])),
        }
        for match in CARRIER_QUESTION.finditer(content)
    ]


def audit_existing_carriers(
    subject: dict[str, Any], path: Path
) -> list[dict[str, Any]]:
    """Confronte un porteur DÉJÀ écrit au sujet, exercice par exercice.

    Un barème qui contredit son propre sujet est un défaut : c'est le sujet que
    l'élève lit et sur lequel il est noté. Le rattacher à la bonne question
    n'est pas une préférence de style.
    """

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    by_number = {row["number"]: row for row in subject["exercises"]}
    findings: list[dict[str, Any]] = []
    seen: set[int] = set()
    for block in line_blocks(text):
        if block["number"] in seen:
            continue
        seen.add(block["number"])
        region = "".join(lines[block["region_start"] : block["line_end"]])
        carrier = CARRIER_IN_TEXT.search(region)
        exercise = by_number.get(block["number"])
        if carrier is None or exercise is None:
            continue
        committed = carrier_questions(carrier.group("content"))
        expected = [
            {
                "label": mark["label"],
                "verbatim": mark["verbatim"],
                "points": str(mark["points"]),
            }
            for mark in exercise["marks"]
        ]
        if not expected:
            findings.append(
                {
                    "exercise": block["number"],
                    "verdict": "CARRIER_WITHOUT_SUBJECT_SOURCE",
                    "committed": [row["verbatim"] for row in committed],
                    "expected": None,
                }
            )
            continue
        committed_points = [row["points"] for row in committed]
        expected_points = [row["points"] for row in expected]
        if committed_points == expected_points:
            verdict = "CARRIER_MATCHES_SUBJECT"
        elif sorted(committed_points) == sorted(expected_points):
            verdict = "CARRIER_CONTRADICTS_SUBJECT_ORDER"
        else:
            verdict = "CARRIER_CONTRADICTS_SUBJECT_VALUES"
        findings.append(
            {
                "exercise": block["number"],
                "verdict": verdict,
                "committed": [row["verbatim"] for row in committed],
                "expected": [row["verbatim"] for row in expected],
            }
        )
    return findings


CARRIER_LINE_ONLY = re.compile(r"^\s*\\baremeIndicatif\{[^}]*\}\s*$")


def correction_path(subject: Path) -> Path:
    return subject.with_name(subject.stem + "-corrige.tex")


def _is_furniture(line: str) -> bool:
    """Une ligne de clôture de titre : commentaire de filet, ou ligne vide."""

    stripped = line.strip()
    return not stripped or stripped.startswith("%")


def place_carrier(lines: list[str], block: dict[str, Any], wanted: str) -> tuple[
    list[str], str
]:
    """Pose le porteur à SA place, une seule fois, quelle que soit la mise en page.

    Les corrigés du corpus écrivent leur intitulé de trois façons : un titre
    seul entouré de filets de commentaire, un titre seul, ou un titre suivi
    directement de la réponse sur la même ligne. Dans les deux premiers cas le
    barème vient sous le titre et sous son filet ; dans le troisième il vient
    au-dessus, car couper la ligne casserait le paragraphe.

    La fonction est idempotente : un porteur déjà présent dans le bloc est
    retiré avant que le bon soit posé, donc relancer le producteur ne duplique
    ni ne déplace rien deux fois.
    """

    heading_index = block["line_index"]
    heading = lines[heading_index]
    inline = heading.rstrip("\n").rstrip().endswith("}") is False

    body = list(range(block["region_start"], block["line_end"]))
    removed = [index for index in body if CARRIER_LINE_ONLY.match(lines[index])]
    for index in reversed(removed):
        del lines[index]
        if index < len(lines) and not lines[index].strip():
            del lines[index]

    if inline:
        # Le retrait du porteur precedent a pu decaler la ligne d'intitule.
        heading_index = next(
            (
                index
                for index, line in enumerate(lines)
                if HEADING.search(line)
                and int(HEADING.search(line).group("number")) == block["number"]
            ),
            heading_index,
        )
        # L'intitulé partage sa ligne avec la réponse. On détache l'étiquette,
        # on pose le barème sous elle, et la réponse redevient un paragraphe :
        # c'est exactement la forme des corrigés canoniques du corpus.
        heading = lines[heading_index]
        match = HEADING.search(heading)
        label_end = heading.index("}", match.end()) + 1
        label, remainder = heading[:label_end], heading[label_end:].lstrip()
        lines[heading_index : heading_index + 1] = [
            label + "\n",
            wanted + "\n",
            "\n",
            remainder if remainder.endswith("\n") else remainder + "\n",
        ]
        return lines, "SPLIT_INLINE_HEADING"
    else:
        insert_at = heading_index + 1
        while insert_at < len(lines) and _is_furniture(lines[insert_at]):
            insert_at += 1
        payload = [wanted + "\n", "\n"]
        action = "UNDER_HEADING"
    lines[insert_at:insert_at] = payload
    return lines, action


def line_blocks(text: str) -> list[dict[str, Any]]:
    """Les intitulés d'exercice du corrigé, repérés par leur ligne."""

    lines = text.splitlines(keepends=True)
    found: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        match = HEADING.search(line)
        if match is None:
            continue
        found.append({"number": int(match.group("number")), "line_index": index})
    for position, row in enumerate(found):
        row["line_end"] = (
            found[position + 1]["line_index"] if position + 1 < len(found) else len(lines)
        )
        # Le porteur vit TOUJOURS sous son intitulé, y compris lorsque
        # l'intitulé partageait sa ligne avec la réponse : dans ce cas la ligne
        # est détachée. Le bloc d'un exercice commence donc à son intitulé, et
        # tout porteur qui s'y trouve lui appartient.
        row["region_start"] = row["line_index"]
    return found


def apply_to_correction(
    subject: dict[str, Any], path: Path, write: bool
) -> dict[str, Any]:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    by_number = {row["number"]: row for row in subject["exercises"]}
    placed: list[dict[str, Any]] = []
    unmatched: list[int] = []

    # De la fin vers le début : les indices de ligne des blocs précédents
    # restent valides quand on insère plus bas.
    blocks = line_blocks(original)
    original_lines = original.splitlines(keepends=True)
    seen: set[int] = set()
    refused: list[dict[str, Any]] = []
    for block in reversed(blocks):
        exercise = by_number.get(block["number"])
        if exercise is None or not exercise["every_question_is_marked"]:
            continue
        if block["number"] in seen:
            continue
        seen.add(block["number"])
        # Un porteur déjà écrit dont les VALEURS diffèrent de celles du sujet
        # n'est pas un décalage à recoller : c'est un désaccord. Le producteur
        # ne l'écrase pas, il le signale. Un simple échange de deux questions,
        # lui, se recolle : le sujet dit à quelle tâche va le point.
        region = "".join(
            original_lines[block["region_start"] : block["line_end"]]
        )
        existing = CARRIER_IN_TEXT.search(region)
        if existing is not None:
            committed = sorted(
                row["points"] for row in carrier_questions(existing.group("content"))
            )
            expected = sorted(str(mark["points"]) for mark in exercise["marks"])
            if committed and committed != expected:
                refused.append(
                    {
                        "exercise": block["number"],
                        "committed": existing.group(0),
                        "subject": bareme_line(exercise),
                    }
                )
                continue
        lines, action = place_carrier(lines, block, bareme_line(exercise))
        placed.append({"exercise": block["number"], "placement": action})

    unmatched = sorted(set(by_number) - seen)

    # Un porteur qui ne tombe dans aucun bloc d'exercice n'appartient a rien :
    # il est retire. C'est le seul moyen qu'une passe malformee ne laisse pas
    # de bareme orphelin, non rattache a une tache.
    protected: set[int] = set()
    for block in line_blocks("".join(lines)):
        protected.update(range(block["region_start"], block["line_end"]))
    stray = [
        index
        for index, line in enumerate(lines)
        if CARRIER_LINE_ONLY.match(line) and index not in protected
    ]
    for index in reversed(stray):
        del lines[index]
        if index < len(lines) and not lines[index].strip():
            del lines[index]

    rewritten = "".join(lines)
    if write and rewritten != original:
        path.write_text(rewritten, encoding="utf-8")
    final = rewritten if write else original
    return {
        "correction_path": _relative(path),
        "placed_exercises": sorted(row["exercise"] for row in placed),
        "placements": list(reversed(placed)),
        "unmatched_exercises": unmatched,
        "carrier_present": CARRIER in final,
        "carrier_count": final.count(CARRIER),
        "stray_carriers_removed": len(stray),
        "refused_overwrites": refused,
        "would_change": rewritten != original,
    }


def assessments() -> list[Path]:
    found: list[Path] = []
    for directory in sorted(CHAPTERS.glob("1SPE-*/evaluations")):
        for path in sorted(directory.glob("*.tex")):
            if path.name.endswith("-corrige.tex"):
                continue
            meta = read_meta(path)
            if meta.get("type_objet") != "evaluation":
                continue
            if declared_total(meta) is None:
                continue
            found.append(path)
    return found


def build(apply_changes: bool) -> dict[str, Any]:
    rows = []
    for path in assessments():
        subject = analyse_subject(path)
        verdict = classify(subject)
        correction = correction_path(path)
        row: dict[str, Any] = {
            "object_id": subject["object_id"],
            "chapter": subject["chapter"],
            "version": subject["version"],
            "duration_min": subject["duration_min"],
            "subject_path": subject["path"],
            "capacities": subject["capacities"],
            **verdict,
            "exercises": [
                {
                    "number": row_["number"],
                    "declared_total": (
                        str(row_["declared_total"])
                        if row_["declared_total"] is not None
                        else None
                    ),
                    "capacities": row_["capacities"],
                    "question_count": row_["question_count"],
                    "marked_question_count": row_["marked_question_count"],
                    # L'énoncé accompagne le point : un barème se relit contre
                    # la tâche, jamais contre un numéro seul.
                    "statements": row_["statements"],
                    "observed_total": str(row_["observed_total"]),
                    "sum_matches_exercise_total": row_["sum_matches_exercise_total"],
                    "per_question": [
                        {
                            "question": mark["label"],
                            "points": str(mark["points"]),
                            "verbatim": mark["verbatim"],
                            "competence": mark["competence"],
                        }
                        for mark in row_["marks"]
                    ],
                    "bareme_line": (
                        bareme_line(row_) if row_["every_question_is_marked"] else None
                    ),
                }
                for row_ in subject["exercises"]
            ],
        }
        if not correction.is_file():
            row["correction_path"] = None
            row["correction_missing"] = True
            row["carrier_audit"] = []
        else:
            row["carrier_audit"] = audit_existing_carriers(subject, correction)
            if verdict["classification"] == TRANSCRIPTIBLE:
                row.update(apply_to_correction(subject, correction, apply_changes))
            else:
                row["correction_path"] = _relative(correction)
                row["carrier_present"] = (
                    CARRIER in correction.read_text(encoding="utf-8")
                )
                row["placed_exercises"] = []
        rows.append(row)

    transcriptible = [r for r in rows if r["classification"] == TRANSCRIPTIBLE]
    human = [r for r in rows if r["classification"] == HUMAN_REQUIRED]

    packet = []
    for row in human:
        # La présence d'un barème indicatif ne vaut ni dérivation depuis le
        # sujet ni décision humaine. La revue doit encore voir la répartition.
        constraints = {
            "required_total": row["declared_total"],
            "duration_min": row["duration_min"],
            "capacities": row["capacities"],
            "exercise_totals": {
                exercise["number"]: exercise["declared_total"]
                for exercise in row["exercises"]
            },
            "the_subject_values_no_question_individually": True,
        }
        proposal = proposal_for(row["object_id"])
        exercises = []
        for exercise in row["exercises"]:
            entries = (proposal or {}).get(exercise["number"], [])
            proposed_sum = sum(
                (parse_points(value.split()[0]) for value, _ in entries),
                Fraction(0),
            )
            declared = (
                Fraction(exercise["declared_total"])
                if exercise["declared_total"]
                else None
            )
            exercises.append(
                {
                    "number": exercise["number"],
                    "declared_total": exercise["declared_total"],
                    "capacities": exercise["capacities"],
                    "question_count": exercise["question_count"],
                    "questions": [
                        {
                            "question": index,
                            "statement": statement,
                            # Le geste que le sujet demande, lu sur son verbe.
                            "reasoning_gesture": _gesture_of(statement),
                            # Ce qu'on peut OBSERVER, et qui aide à juger sans
                            # rien décider : la difficulté, l'autonomie exigée
                            # de l'élève et la complexité scientifique sont des
                            # jugements humains, et restent vides.
                            "observable_indicators": {
                                "statement_characters": len(statement),
                                "asks_for_a_proof": bool(
                                    _PROOF.search(statement)
                                ),
                                "chains_a_deduction": bool(
                                    _DEDUCTION.search(statement)
                                ),
                            },
                            "to_be_judged_by_a_human": {
                                "difficulty": "",
                                "student_autonomy": "",
                                "scientific_complexity": "",
                            },
                        }
                        for index, statement in enumerate(
                            exercise.get("statements", []), start=1
                        )
                    ],
                    "candidate_allocation": [
                        {"question": index, "points": value, "rationale": reason}
                        for index, (value, reason) in enumerate(entries, start=1)
                    ],
                    "candidate_sum": str(proposed_sum),
                    "candidate_sum_matches_declared_total": declared == proposed_sum,
                }
            )
        packet.append(
            {
                "object_id": row["object_id"],
                "chapter": row["chapter"],
                "version": row["version"],
                "existing_subject_constraints": constraints,
                "what_each_reviewer_owns": {
                    "EXPERT_PROGRAMME_PEDAGOGIE": (
                        "le verdict final de répartition des points"
                    ),
                    "EXPERT_MATHEMATIQUE": (
                        "la difficulté scientifique, la charge de travail "
                        "mathématique et la cohérence des poids relatifs"
                    ),
                },
                "duration_min": row["duration_min"],
                "declared_total": row["declared_total"],
                "capacities": row["capacities"],
                "subject_path": row["subject_path"],
                "correction_path": row["correction_path"],
                "why_human": row["reasons"],
                "parallel_form_of": (
                    row["object_id"][:-1] + ("B" if row["version"] == "A" else "A")
                ),
                "exercises": exercises,
                "verdict_owner": "EXPERT_PROGRAMME_PEDAGOGIE",
                "scientific_confirmation_owner": "EXPERT_MATHEMATIQUE",
                "verdict": "PENDING",
                "status": "ATTENTION_REQUIRED",
                "proposal_is_not_a_decision": (
                    "cette repartition est deja materialisee comme bareme "
                    "indicatif ; sa presence ne vaut pas approbation humaine"
                    if row.get("carrier_present") else
                    "cette repartition est une proposition machine ; elle n'est "
                    "ecrite dans aucun corrige et ne vaut pas barème"
                ),
            }
        )

    def audit_count(*verdicts: str) -> int:
        return sum(
            1
            for row in rows
            for finding in row.get("carrier_audit", [])
            if finding["verdict"] in verdicts
        )

    contradicting = [
        {"object_id": row["object_id"], **finding}
        for row in rows
        for finding in row.get("carrier_audit", [])
        if finding["verdict"].startswith("CARRIER_CONTRADICTS")
    ]
    sourceless = [
        {"object_id": row["object_id"], **finding}
        for row in rows
        for finding in row.get("carrier_audit", [])
        if finding["verdict"] == "CARRIER_WITHOUT_SUBJECT_SOURCE"
    ]
    return {
        "artifact_type": "1spe_assessment_bareme_transcription",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "carrier_macro": CARRIER,
        "no_bareme_is_invented": (
            "aucune valeur n'est repartie, devinee ni recopiee d'une autre "
            "evaluation ; une valeur absente du sujet rend l'evaluation "
            "HUMAN_PEDAGOGICAL_JUDGEMENT_REQUIRED"
        ),
        "authoritative_source": (
            "le sujet compose lui-meme, question par question ; la somme n'est "
            "qu'un controle secondaire"
        ),
        "assessments": rows,
        "summary": {
            "ASSESSMENTS": len(rows),
            "TRANSCRIPTIBLE": len(transcriptible),
            "HUMAN_PEDAGOGICAL_JUDGEMENT_REQUIRED": len(human),
            "SUM_MISMATCH": sum(
                1 for r in rows if r["sum_matches_declared_total"] is False
            ),
            "CARRIER_PRESENT": sum(1 for r in rows if r.get("carrier_present")),
            "CARRIER_MISSING_AFTER_APPLY": sum(
                1 for r in transcriptible if not r.get("carrier_present")
            ),
            "CARRIER_MISPLACED_OR_MISSING": sum(
                1 for r in transcriptible if r.get("would_change")
            ),
            "CARRIER_OUTSIDE_ANY_EXERCISE": sum(
                r.get("stray_carriers_removed", 0) for r in rows
            ),
            "CARRIER_VALUES_DISPUTE_SUBJECT": sum(
                len(r.get("refused_overwrites", [])) for r in rows
            ),
            "HUMAN_REQUIRED_IDS": [r["object_id"] for r in human],
            "ATTENTION_REQUIRED": len(packet),
            "CANDIDATE_PROPOSAL_SUM_MISMATCH": sum(
                1
                for entry in packet
                for exercise in entry["exercises"]
                if not exercise["candidate_sum_matches_declared_total"]
            ),
            "CARRIER_MATCHES_SUBJECT": audit_count("CARRIER_MATCHES_SUBJECT"),
            "CARRIER_CONTRADICTS_SUBJECT": len(contradicting),
            "CARRIER_WITHOUT_SUBJECT_SOURCE": len(sourceless),
        },
        "refused_overwrites": [
            {"object_id": row["object_id"], **entry}
            for row in rows
            for entry in row.get("refused_overwrites", [])
        ],
        "human_decision_packet": packet,
        "carrier_contradictions": contradicting,
        "carriers_without_subject_source": sourceless,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Barèmes des évaluations 1SPE — transcription et décisions restantes",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        "> " + payload["no_bareme_is_invented"],
        "",
        f"Source autoritaire : {payload['authoritative_source']}.",
        f"Porteur de charte : `{payload['carrier_macro']}`.",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---|",
    ]
    for name, value in payload["summary"].items():
        rendered = ", ".join(value) if isinstance(value, list) else value
        lines.append(f"| `{name}` | {rendered or '—'} |")
    lines += [
        "",
        "## Évaluations",
        "",
        "| Objet | Chap. | Ver. | Durée | Total | Somme | Classement | Porteur |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in payload["assessments"]:
        lines.append(
            f"| `{row['object_id']}` | {row['chapter']} | {row['version']} | "
            f"{row['duration_min']} min | {row['declared_total']} | "
            f"{row['exercise_total_sum']} | {row['classification']} | "
            f"{'oui' if row.get('carrier_present') else 'non'} |"
        )
    for row in payload["assessments"]:
        lines += [
            "",
            f"### `{row['object_id']}`",
            "",
            f"- sujet : `{row['subject_path']}`",
            f"- corrigé : `{row['correction_path']}`",
            f"- capacités : {', '.join(row['capacities']) or '—'}",
            f"- classement : **{row['classification']}**",
        ]
        for reason in row["reasons"]:
            lines.append(f"- motif : {reason}")
        lines += [
            "",
            "| Ex. | Total | Questions | Questions valuées | Somme | Barème transcrit |",
            "|---:|---:|---:|---:|---:|---|",
        ]
        for exercise in row["exercises"]:
            carried = exercise["bareme_line"] or "— décision humaine requise"
            lines.append(
                f"| {exercise['number']} | {exercise['declared_total']} | "
                f"{exercise['question_count']} | "
                f"{exercise['marked_question_count']} | "
                f"{exercise['observed_total']} | `{carried}` |"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="écrire \\baremeIndicatif dans les corrigés transcriptibles",
    )
    parser.add_argument("--check", action="store_true", help="ne rien écrire du tout")
    arguments = parser.parse_args(argv)

    try:
        payload = build(arguments.apply)
    except TranscriptionError as error:
        print(f"1SPE-BAREME-TRANSCRIPTION-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {relative(JSON_TARGET)} et {relative(MD_TARGET)}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    blocking = (
        "SUM_MISMATCH",
        "CARRIER_MISSING_AFTER_APPLY",
        "CARRIER_CONTRADICTS_SUBJECT",
        "CARRIER_VALUES_DISPUTE_SUBJECT",
        "CARRIER_OUTSIDE_ANY_EXERCISE",
        "CANDIDATE_PROPOSAL_SUM_MISMATCH",
    )
    return 1 if any(payload["summary"][name] for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
