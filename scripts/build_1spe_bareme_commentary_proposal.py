#!/usr/bin/env python3
"""Propositions de barème commenté : dérivées du sujet et du corrigé, jamais inventées.

La politique est décidée : pour chaque question évaluée, le manuel professeur
doit porter les points, l'attendu qui permet de les attribuer, et -- seulement
lorsqu'une décomposition pédagogiquement objective existe -- un crédit partiel.

Deux cent quatre-vingt-douze questions ne sont pas deux cent quatre-vingt-douze
décisions humaines : ce module en fabrique la PROPOSITION, et l'expert
programme/pédagogie juge le chapitre entier.

Ce qui est dérivé, et d'où :

* les POINTS viennent du sujet, verbatim -- jamais recalculés, jamais répartis ;
* l'ATTENDU se compose du GESTE que le sujet demande (son verbe : « calculer »,
  « justifier », « en déduire », « démontrer ») et du RÉSULTAT que le corrigé
  établit. Deux sources réelles, aucune invention ;
* le CRÉDIT PARTIEL n'est proposé que si le corrigé montre des étapes
  explicitement séparables ET que les points se divisent sans inventer de
  granularité. Sinon : plein crédit ou rien, ce que la politique autorise.

Ce que ce module refuse de faire, et le dit : répartir uniformément, inventer
un demi-point partout, recopier le schéma d'une autre question, fabriquer des
sous-critères absents de la solution. Quand la décomposition est ambiguë, la
proposition porte `PEDAGOGICAL_JUDGEMENT_REQUIRED` et reste vide.

Métriques : `QUESTIONS`, `PROPOSED`, `PARTIAL_CREDIT_PROPOSED`,
`PEDAGOGICAL_JUDGEMENT_REQUIRED`.
Métrique bloquante : `QUESTIONS_WITHOUT_PROPOSAL_OR_FLAG`.
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

import build_1spe_bareme_commentary_request as request  # noqa: E402
import tex_units  # noqa: E402
from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_BAREME_COMMENTARY_PROPOSAL.json"
MD_TARGET = ROOT / "audit/1SPE_BAREME_COMMENTARY_PROPOSAL.md"
GENERATED_BY = "scripts/build_1spe_bareme_commentary_proposal.py"

DECISION = "RESOLVED_BY_HUMAN_DECISION_2026_09_04"

# Le geste que le sujet demande, lu sur son propre verbe. C'est le sujet qui
# dit ce qu'il évalue ; ce module ne le devine pas.
GESTURES = (
    (r"\bd[ée]montrer\b|\bprouver\b", "démontrer"),
    (r"\bjustifier\b", "justifier"),
    (r"\ben d[ée]duire\b", "en déduire"),
    (r"\bd[ée]terminer\b", "déterminer"),
    (r"\br[ée]soudre\b", "résoudre"),
    (r"\b[ée]tudier\b", "étudier"),
    (r"\bv[ée]rifier\b", "vérifier"),
    (r"\bcalculer\b", "calculer"),
    (r"\bexprimer\b", "exprimer"),
    (r"\bdresser\b|\bconstruire\b|\btracer\b", "construire"),
    (r"\binterpr[ée]ter\b|\bexpliquer\b", "interpréter"),
    (r"\bmontrer\b", "montrer"),
    (r"\bdonner\b|\bindiquer\b|\b[ée]crire\b", "donner"),
    # Ces verbes-là ont été LUS dans le corpus, un par un, parmi les énoncés
    # que la première liste laissait sans geste : « convertir », « simplifier »,
    # « comparer », « approcher », « établir », « rappeler », « commenter ».
    # Les ajouter, c'est lire le sujet ; les deviner aurait été l'inverse.
    (r"\bconvertir\b", "convertir"),
    (r"\bsimplifier\b", "simplifier"),
    (r"\bcomparer\b", "comparer"),
    (r"\bapprocher\b", "approcher"),
    (r"\b[ée]tablir\b", "établir"),
    (r"\brappeler\b", "rappeler"),
    (r"\bcommenter\b", "commenter"),
)

# Une étape séparable s'annonce dans le corrigé : « donc », « puis », « d'où »,
# « en déduire ». Sans marqueur explicite, il n'y a pas de décomposition à
# constater -- et en inventer une serait précisément l'interdit.
STEP_MARKERS = re.compile(
    r"\bdonc\b|\bpuis\b|\bd'o[uù]\b|\ben d[ée]duit\b|\bensuite\b|\bd'abord\b",
    re.IGNORECASE,
)


class ProposalError(RuntimeError):
    """Une preuve manque : la proposition ne peut pas être dérivée."""


def gesture_of(statement: str) -> str | None:
    """Le geste demandé, lu sur le verbe du sujet."""

    lowered = statement.lower()
    for pattern, name in GESTURES:
        if re.search(pattern, lowered):
            return name
    return None


def _strip_comments(text: str) -> str:
    """Retire les lignes de commentaire LaTeX, garde le reste tel quel.

    Les corrigés séparent leurs exercices par des lignes de `%=====`. Les
    laisser entrer faisait apparaître ces barres dans l'attendu.
    """

    # Un commentaire LaTeX commence à un `%` non échappé, N'IMPORTE OÙ dans la
    # ligne, et court jusqu'au bout. Ne couper que les lignes qui COMMENCENT
    # par `%` laissait passer les séparateurs posés en fin de ligne, juste
    # après une formule.
    kept: list[str] = []
    for line in text.splitlines():
        cut = re.sub(r"(?<!\\)%.*$", "", line)
        if cut.strip():
            kept.append(cut)
    return " ".join(" ".join(kept).split())


def key_result(answer: str) -> str | None:
    """Le résultat que le corrigé établit, VERBATIM.

    Une première version « nettoyait » le LaTeX pour produire une phrase
    lisible. Elle mutilait les mathématiques -- `\\pi` disparaissait, et
    « 5π/6 » devenait « (5 )/(6) ». Un barème qui déforme la formule qu'il
    évalue est pire qu'absent. Le fragment est donc repris tel que le corrigé
    l'écrit ; c'est du LaTeX, et le manuel professeur en est fait.
    """

    cleaned = _strip_comments(answer)
    if not cleaned:
        return None
    # Le découpage en phrases ne tombe jamais dans une unité TeX : un point à
    # l'intérieur de `\[ ... u_{n+1} = 1{,}05\,u_n. \]` ponctue la formule, il
    # ne termine pas la phrase. Découper dessus produisait des attendus qui
    # commençaient par `\end{align*}` ou s'arrêtaient avant `\]`.
    for sentence in reversed(tex_units.sentences(cleaned)):
        if "$" not in sentence and not re.search(r"\d", sentence):
            continue
        if len(sentence) > 180:
            continue
        # Le fragment porte déjà sa ponctuation finale ; le format en ajoute
        # une, et deux points de suite se lisent mal.
        candidate = sentence.rstrip(".;").strip()
        if not candidate or not tex_units.is_balanced(candidate):
            # Retirer la ponctuation finale peut rouvrir la question : un
            # fragment qui ne tient plus debout n'est pas un résultat.
            continue
        return candidate
    return None


def separable_steps(answer: str) -> int:
    """Le nombre d'étapes que le corrigé sépare LUI-MÊME."""

    cleaned = _strip_comments(answer)
    if not cleaned:
        return 0
    return len(STEP_MARKERS.findall(cleaned)) + 1


def divide(points: Fraction, steps: int) -> tuple[Fraction, Fraction] | None:
    """Une coupure en deux qui n'invente aucune granularité.

    Les barèmes du corpus s'expriment au demi-point. Une coupure n'est
    proposable que si les deux parts tombent sur cette grille et qu'aucune
    n'est nulle -- sinon la décomposition serait fabriquée pour les besoins de
    la cause.
    """

    if steps < 2 or points < 2:
        return None
    half = Fraction(1, 2)
    first = (points * Fraction(2, 3)).limit_denominator(2)
    second = points - first
    for part in (first, second):
        if part <= 0 or part % half != 0:
            return None
    return first, second


def render_points(value: Fraction) -> str:
    number = f"{float(value):g}".replace(".", ",")
    return f"{number} {'pt' if value < 2 else 'pts'}"


def propose(question: dict[str, Any]) -> dict[str, Any]:
    """La proposition pour UNE question, ou le drapeau qui la refuse."""

    statement = question["statement"]
    answer = question["correction_answer"]
    verbatim = question["points"]
    gesture = gesture_of(statement)
    result = key_result(answer)

    row: dict[str, Any] = {
        "question": question["question"],
        "points": verbatim,
        "competence": question.get("competence"),
        "gesture": gesture,
        "answer_scope": question.get("correction_answer_scope"),
    }

    scope = question.get("correction_answer_scope")
    # Un corrigé écrit à l'échelle de l'exercice répond à toutes ses questions
    # à la fois. En tirer un attendu, c'est donner le même à des questions dont
    # les gestes diffèrent -- « rappeler » et « simplifier » recevaient le même
    # texte. Ce qui manque ici n'est pas une phrase : c'est une réponse
    # question par question, et personne d'autre que l'enseignant ne peut la
    # découper sans l'inventer.
    if verbatim is None or gesture is None or result is None or scope != "question":
        row["verdict"] = "PEDAGOGICAL_JUDGEMENT_REQUIRED"
        row["why"] = (
            "le sujet ne value pas cette question"
            if verbatim is None
            else "le geste évalué ne se lit pas dans l'énoncé"
            if gesture is None
            else "le corrigé répond à l'échelle de l'exercice, pas de cette "
            "question : aucun attendu question par question ne s'en déduit"
            if scope == "exercise"
            else "le corrigé répond à la question mère sans distinguer cette "
            "sous-question"
            if scope == "parent_question"
            else "le corrigé n'établit aucun résultat repérable"
        )
        row["expected"] = ""
        row["partial_credit"] = ""
        return row

    row["verdict"] = "PROPOSED"
    row["expected"] = f"{gesture} — {result}"
    row["partial_credit"] = ""

    # Le crédit partiel n'existe que si le corrigé sépare lui-même ses étapes
    # ET si les points se coupent sur la grille du corpus.
    points = request.transcription.parse_points(
        verbatim.split()[0].replace(",", ".")
    )
    steps = separable_steps(answer)
    split = divide(points, steps)
    if split is not None:
        row["partial_credit"] = (
            f"{render_points(split[0])} si la première étape est correcte "
            f"mais la suite erronée"
        )
        row["separable_steps"] = steps
    return row


def result_of(expected: str) -> str:
    """La part de l'attendu qui vient du corrigé, sans le geste du sujet.

    Deux questions peuvent légitimement demander le même geste ; ce qui ne
    peut pas être partagé, c'est le résultat. Comparer l'attendu entier
    laisserait passer « rappeler — X » et « simplifier — X ».
    """

    return expected.split("—", 1)[1].strip() if "—" in expected else expected.strip()


def build() -> dict[str, Any]:
    payload = request.build()
    chapters: list[dict[str, Any]] = []
    for packet in payload["packets"]:
        exercises = []
        for exercise in packet["exercises"]:
            exercises.append(
                {
                    "exercise": exercise["exercise"],
                    "capacities": exercise["capacities"],
                    "declared_total": exercise["declared_total"],
                    "questions": [
                        propose(question) for question in exercise["questions"]
                    ],
                }
            )
        chapters.append(
            {
                "object_id": packet["object_id"],
                "chapter": packet["chapter"],
                "version": packet["version"],
                "subject_path": packet["subject_path"],
                "correction_path": packet["correction_path"],
                "exercises": exercises,
            }
        )

    rows = [
        question
        for chapter in chapters
        for exercise in chapter["exercises"]
        for question in exercise["questions"]
    ]
    proposed = [row for row in rows if row["verdict"] == "PROPOSED"]
    flagged = [row for row in rows if row["verdict"] != "PROPOSED"]

    # Un attendu que personne ne peut composer n'est pas un attendu, et deux
    # questions qui reçoivent le même n'ont pas été évaluées séparément. Les
    # deux se comptent ici, sur ce qui vient d'être produit.
    unbalanced: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for chapter in chapters:
        for exercise in chapter["exercises"]:
            shared: dict[str, list[str]] = {}
            for question in exercise["questions"]:
                expected = question["expected"]
                if not expected:
                    continue
                faults = tex_units.imbalances(expected)
                if faults:
                    unbalanced.append(
                        {
                            "object_id": chapter["object_id"],
                            "question": question["question"],
                            "faults": faults,
                            "expected": expected,
                        }
                    )
                shared.setdefault(result_of(expected), []).append(
                    question["question"]
                )
            for result, questions in shared.items():
                if len(questions) > 1:
                    ambiguous.append(
                        {
                            "object_id": chapter["object_id"],
                            "exercise": exercise["exercise"],
                            "questions": questions,
                            "shared_result": result,
                        }
                    )

    return {
        "artifact_type": "1spe_bareme_commentary_proposal",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "approves_nothing": True,
        "policy": DECISION,
        "the_format_is_the_one_the_policy_fixed": (
            "X pt(s) — Attendu : <ce qui permet d'attribuer les points>. "
            "Crédit partiel : <seulement si pertinent>."
        ),
        "what_is_derived_and_from_where": {
            "points": "le sujet, verbatim",
            "expected": (
                "le geste que le sujet demande (son verbe) et le résultat que "
                "le corrigé établit"
            ),
            "partial_credit": (
                "seulement si le corrigé sépare lui-même ses étapes et si les "
                "points se coupent sur la grille du demi-point"
            ),
        },
        "what_is_refused": (
            "répartir uniformément, inventer un demi-point partout, recopier le "
            "schéma d'une autre question, fabriquer des sous-critères absents "
            "de la solution"
        ),
        "an_expected_must_be_typesettable": (
            "Un attendu est du LaTeX que le manuel professeur composera. Une "
            "formule coupée en deux -- `\\[` sans `\\]`, un `\\end{align*}` "
            "orphelin -- n'est pas un attendu : c'est un accident d'extraction. "
            "Le découpage s'arrête désormais aux frontières où le fragment "
            "tient debout."
        ),
        "an_expected_must_belong_to_its_question": (
            "Un corrigé écrit à l'échelle de l'exercice répond à toutes ses "
            "questions à la fois : en tirer un attendu donnait le même texte à "
            "des questions dont les gestes diffèrent. Ces questions-là "
            "attendent désormais un jugement, elles ne reçoivent plus une "
            "copie."
        ),
        "unbalanced_expected": unbalanced,
        "ambiguous_scope": ambiguous,
        "these_are_proposals_not_content": (
            "Rien n'est écrit dans les corrigés : ces propositions entrent dans "
            "la revue de chapitre, et c'est l'expert programme/pédagogie qui "
            "tranche."
        ),
        "assessments": chapters,
        "summary": {
            "ASSESSMENTS": len(chapters),
            "QUESTIONS": len(rows),
            "PROPOSED": len(proposed),
            "PARTIAL_CREDIT_PROPOSED": sum(
                1 for row in proposed if row["partial_credit"]
            ),
            "PEDAGOGICAL_JUDGEMENT_REQUIRED": len(flagged),
            "QUESTIONS_WITHOUT_PROPOSAL_OR_FLAG": sum(
                1 for row in rows if row["verdict"] not in
                {"PROPOSED", "PEDAGOGICAL_JUDGEMENT_REQUIRED"}
            ),
            "BAREME_EXPECTED_TEX_UNBALANCED": len(unbalanced),
            "BAREME_QUESTION_SCOPE_AMBIGUOUS": sum(
                len(row["questions"]) for row in ambiguous
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Barème commenté — propositions",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Politique : `{payload['policy']}`.",
        "",
        f"> {payload['these_are_proposals_not_content']}",
        "",
        f"> Refusé : {payload['what_is_refused']}.",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    for chapter in payload["assessments"]:
        lines += ["", f"## {chapter['object_id']}", ""]
        for exercise in chapter["exercises"]:
            lines += [
                f"### Exercice {exercise['exercise']} — "
                f"{exercise['declared_total']} points ({exercise['capacities']})",
                "",
            ]
            for question in exercise["questions"]:
                if question["verdict"] != "PROPOSED":
                    lines += [
                        f"- **{question['question']}** — "
                        f"`PEDAGOGICAL_JUDGEMENT_REQUIRED` : {question['why']}",
                    ]
                    continue
                line = (
                    f"- **{question['question']}** — {question['points']} — "
                    f"Attendu : {question['expected']}."
                )
                if question["partial_credit"]:
                    line += f" *Crédit partiel : {question['partial_credit']}.*"
                lines.append(line)
            lines.append("")
    return "\n".join(lines) + "\n"


BLOCKING = (
    "QUESTIONS_WITHOUT_PROPOSAL_OR_FLAG",
    "BAREME_EXPECTED_TEX_UNBALANCED",
    "BAREME_QUESTION_SCOPE_AMBIGUOUS",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except (ProposalError, request.CommentaryError) as error:
        print(f"1SPE-BAREME-COMMENTARY-PROPOSAL-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"][name] for name in BLOCKING) else 0


if __name__ == "__main__":
    raise SystemExit(main())
