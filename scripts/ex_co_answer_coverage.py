#!/usr/bin/env python3
"""Le corrige repond-il a TOUTES les questions de son exercice ?

Le graphe EX/CO prouve qu'une paire est structurellement saine : le corrige
nomme son exercice, il est unique, les capacites concordent. Cela ne dit
toujours pas qu'il y REPOND. Sept corriges de 1SPE-PROBA-COND en etaient la
preuve : structurellement parfaits, ils laissaient sans reponse la question
« Construire l'arbre pondere ».

CE QUE CE MODULE ETABLIT, ET CE QU'IL N'ETABLIT PAS.

Il etablit une COUVERTURE : chaque question de l'exercice recoit une reponse
reperable dans le corrige. C'est une condition necessaire, verifiable
mecaniquement, et elle attrape la lacune franche.

Il n'etablit PAS que la reponse est juste. L'exactitude scientifique reste
prouvee ailleurs -- blocs d'execution, oracle independant, relecture humaine.
Confondre les deux ferait passer un corrige complet mais faux pour un corrige
valide.

COMPTER LES QUESTIONS. Seuls les items du PREMIER niveau de liste comptent.
Un exercice de quatre questions dont chacune porte des sous-questions n'en a
pas dix-sept : compter a plat gonflerait le denominateur et ferait passer un
corrige complet pour un corrige lacunaire.

RECONNAITRE LES REPONSES. Le corpus emploie plusieurs conventions, toutes
legitimes : `\\textbf{1.}`, `\\textbf{Question 1 — ...}`, `\\textbf{2a.}`,
`\\textbf{a)}`, ou une liste de meme cardinal. Une convention non reconnue ne
vaut PAS une lacune : elle sort en `UNRECOGNISED_ANSWER_LAYOUT` et demande un
examen individuel.
"""

from __future__ import annotations

import re
import string
from pathlib import Path

LIST_OPEN = re.compile(r"\\begin\{(enumerate|itemize|description)\}")
LIST_CLOSE = re.compile(r"\\end\{(enumerate|itemize|description)\}")
# Les corrigés numérotent leurs réponses de plusieurs façons : « 1. »,
# « Question 1. » et, dans tout le corpus de terminale spécialité, « Q1. ».
# Ne pas connaître la troisième faisait passer 134 corrigés complets pour des
# dispositions de réponse non reconnues.
# Les corrigés numérotent leurs réponses de plusieurs façons : « 1. »,
# « Question 1. », « Q1. », et « Q1 (C6). » lorsque la réponse rappelle la
# capacité travaillée. Ne connaître que les deux premières faisait passer 134
# corrigés complets pour des dispositions de réponse non reconnues.
NUMBERED_ANSWER = re.compile(
    r"\\textbf\{\s*(?:Question\s+|Q\s*)?(\d+)\s*(?:[a-z]\s*)?"
    r"(?:\([^)]*\)\s*)?[.\u2014\u2013:)-]"
)
ALPHABETIC_ANSWER = re.compile(r"\\textbf\{\s*([a-z])\s*[).]")

#: Un corrigé peut répondre par un seul programme lorsque l'énoncé énumère les
#: étapes d'un même livrable — « crée un dossier ; crée deux fichiers ; liste le
#: contenu » n'appelle pas trois réponses séparées mais un script qui fait les
#: trois. Exiger un marqueur par étape reviendrait à demander un balisage
#: cosmétique.
CODE_ENVIRONMENT = re.compile(r"\\begin\{(python|sql|text|verbatim|lstlisting)\}")

#: Au-delà, un énoncé décrit des questions indépendantes plutôt que les étapes
#: d'un même programme, et la réponse doit être repérable question par question.
SINGLE_PROGRAM_MAX_STEPS = 4

ESTABLISHED = "ANSWER_COVERAGE_ESTABLISHED"
SINGLE_PROGRAM = "SINGLE_PROGRAM_ANSWER"
SINGLE_QUESTION = "SINGLE_QUESTION_NO_ENUMERATION"
MISSING = "ANSWERS_MISSING"
UNRECOGNISED = "UNRECOGNISED_ANSWER_LAYOUT"


def pedagogical_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return text.split("\n", 1)[1] if "\n" in text else ""


def top_level_items(text: str) -> int:
    """Les QUESTIONS : items du premier niveau d'une enumeration.

    Deux pieges, tous deux rencontres dans le corpus.

    Un `itemize` qui DECRIT la situation avant les questions -- « il recoit
    36 euros », « sinon il perd sa mise » -- n'est pas une liste de questions.
    Seule une `enumerate` en porte.

    Une `enumerate` IMBRIQUEE porte des sous-questions. Les compter au meme
    rang que les questions gonflerait le denominateur et ferait passer un
    corrige complet pour un corrige lacunaire.
    """

    stack: list[str] = []
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        opened = LIST_OPEN.match(stripped)
        closed = LIST_CLOSE.match(stripped)
        if opened:
            stack.append(opened.group(1))
        elif closed:
            if stack:
                stack.pop()
        elif stripped.startswith(r"\item"):
            if stack[-1:] == ["enumerate"] and stack.count("enumerate") == 1:
                count += 1
    return count


def answered_numbers(correction_body: str) -> set[int]:
    return {int(value) for value in NUMBERED_ANSWER.findall(correction_body)}


def classify(exercise_body: str, correction_body: str) -> tuple[str, dict]:
    """Couverture d'un couple, avec les nombres qui l'ont decidee."""

    questions = top_level_items(exercise_body)
    numbered = answered_numbers(correction_body)
    alphabetic = {value for value in ALPHABETIC_ANSWER.findall(correction_body)}
    answers_as_list = top_level_items(correction_body)
    evidence = {
        "questions": questions,
        "numbered_answers": sorted(numbered),
        "alphabetic_answers": sorted(alphabetic),
        "answer_list_items": answers_as_list,
    }
    if questions == 0:
        return SINGLE_QUESTION, evidence
    if numbered == set(range(1, questions + 1)):
        return ESTABLISHED, evidence
    if answers_as_list == questions:
        return ESTABLISHED, evidence
    if alphabetic == set(string.ascii_lowercase[:questions]):
        return ESTABLISHED, evidence
    if numbered:
        evidence["missing"] = sorted(
            set(range(1, questions + 1)) - numbered
        )
        return MISSING, evidence
    code_blocks = len(CODE_ENVIRONMENT.findall(correction_body))
    evidence["code_blocks"] = code_blocks
    if code_blocks and questions <= SINGLE_PROGRAM_MAX_STEPS:
        return SINGLE_PROGRAM, evidence
    return UNRECOGNISED, evidence
