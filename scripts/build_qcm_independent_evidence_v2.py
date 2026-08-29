#!/usr/bin/env python3
"""Preuve de revue independante des QCM, version 2 : une identite par question.

La v1 liait chaque ligne au sha256 du FICHIER entier : modifier une question
perimait tout le lot. La v2 est content-addressed par question, et chaque
question du corpus courant se trouve dans exactement un etat :

    CARRIED_FORWARD_IDENTICAL   condense semantique identique a la preuve v1
    MACHINE_RECALCULATED        resolue independamment par le solveur canonique
    HUMAN_REVIEW_REQUIRED       aucune famille generique ne la modelise

    question_count = carried_forward + machine_recalculated + human_required
    unknown = 0

Le verificateur ne s'execute qu'APRES le solveur. Le solveur recoit une entree
assainie d'ou la cle est absente et interdite ; la cle canonique n'est chargee
qu'ici, pour etre comparee au vecteur de verite deja calcule.

La v1 n'est pas reecrite : elle reste l'enregistrement HISTORIQUE.

Cet artefact n'approuve rien. Une question HUMAN_REVIEW_REQUIRED reste
bloquante pour la release, et le gate humain des QCM demeure distinct : le
routage de la preuve peut etre complet alors que la revue humaine ne l'est pas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_qcm_review_proof_reconciliation as reconciliation  # noqa: E402
import qcm_independent_solver as solver  # noqa: E402

JSON_TARGET = ROOT / "audit" / "QCM_INDEPENDENT_EVIDENCE_V2.json"
MD_TARGET = ROOT / "audit" / "QCM_INDEPENDENT_EVIDENCE_V2.md"

EVIDENCE_SCHEMA_FIELDS = (
    "statement",
    "options",
    "key",
    "diagnostics",
    "remediation_refs",
    "capacity",
)


class EvidenceError(RuntimeError):
    """Levee quand la preuve ne peut pas etre etablie sans invention."""


def _digest(payload: Any) -> str:
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _diagnostic_coverage(question: dict[str, Any]) -> dict[str, Any]:
    """Chaque distracteur doit porter une erreur documentee et un renvoi."""

    options = set(question["options"])
    correct = question["correcte"]
    distractors = sorted(options - {correct})
    diagnostics = question.get("diagnostics") or {}
    missing_error = sorted(
        letter
        for letter in distractors
        if not (diagnostics.get(letter) or {}).get("erreur")
    )
    missing_renvoi = sorted(
        letter
        for letter in distractors
        if not (diagnostics.get(letter) or {}).get("renvoi")
    )
    on_correct = sorted(letter for letter in diagnostics if letter == correct)
    return {
        "distractors": distractors,
        "missing_error_model": missing_error,
        "missing_remediation_reference": missing_renvoi,
        "diagnostic_on_the_correct_option": on_correct,
        "complete": not missing_error and not missing_renvoi and not on_correct,
    }


def _equivalent_option_groups(question: dict[str, Any]) -> list[list[str]]:
    """Deux options de meme valeur rendent l'eleve indiagnosticable."""

    values = solver.option_values(question["options"])
    groups: dict[str, list[str]] = {}
    for letter, value in sorted(values.items()):
        if value is None:
            continue
        groups.setdefault(str(value), []).append(letter)
    return [letters for letters in groups.values() if len(letters) > 1]


def _verify(question: dict[str, Any], result: solver.SolverResult) -> dict[str, Any]:
    """Confrontation a la cle canonique, APRES le calcul independant."""

    declared = question["correcte"]
    checks: dict[str, Any] = {
        "declared_key": declared,
        "computed_unique_answer": result.unique_answer,
        "true_option_count": result.true_option_count,
        "unique_true_option": result.true_option_count == 1,
        "declared_key_matches_computation": result.unique_answer == declared,
    }
    groups = _equivalent_option_groups(question)
    checks["equivalent_option_groups"] = groups
    checks["no_equivalent_options"] = not groups
    coverage = _diagnostic_coverage(question)
    checks["diagnostic_coverage"] = coverage
    checks["capacity"] = question.get("capacite")
    checks["capacity_declared"] = bool(question.get("capacite"))

    # Deux verdicts distincts. Le premier porte sur la MATHEMATIQUE : la
    # question a-t-elle une reponse unique, et la cle declaree est-elle celle
    # que le calcul independant produit. Un echec ici est un defaut
    # scientifique et arrete la production.
    #
    # Le second porte sur la COUVERTURE editoriale des diagnostics et des
    # renvois. Un echec ici est un manque connu du corpus, deja compte par
    # REQUIRED_DISTRACTOR_WITHOUT_DIAGNOSTIC : il est enregistre et reste
    # bloquant pour la release, mais il ne remet pas en cause la preuve de la
    # cle et ne doit donc pas empecher de l'etablir.
    checks["answer_key_verdict"] = (
        "PASS"
        if (
            checks["unique_true_option"]
            and checks["declared_key_matches_computation"]
            and checks["no_equivalent_options"]
            and checks["capacity_declared"]
        )
        else "FAIL"
    )
    checks["coverage_verdict"] = "PASS" if coverage["complete"] else "FAIL"
    checks["verdict"] = (
        "PASS"
        if checks["answer_key_verdict"] == "PASS" and checks["coverage_verdict"] == "PASS"
        else "FAIL"
    )
    return checks


def build_evidence() -> dict[str, Any]:
    routing = reconciliation.build_reconciliation()
    corpus = reconciliation._load_corpus()

    carried_keys = {
        (entry["chapter"], entry["question_id"]) for entry in routing["carried_forward"]
    }
    reproof_keys = {
        (entry["chapter"], entry["question_id"])
        for entry in routing["reproof_required"]
    }
    reproof_by_key = {
        (entry["chapter"], entry["question_id"]): entry
        for entry in routing["reproof_required"]
    }

    questions: list[dict[str, Any]] = []
    failures: list[str] = []
    coverage_findings: list[dict[str, Any]] = []

    for key in sorted(corpus):
        chapter, question_id = key
        question, source_path = corpus[key]
        semantic = reconciliation.semantic_question_digest(
            reconciliation._semantic_fields_from_source(question)
        )
        common = {
            "chapter": chapter,
            "question_id": question_id,
            "source_path": source_path,
            "semantic_question_digest": semantic,
            "capacity": question.get("capacite"),
        }

        if key in carried_keys:
            entry = {
                **common,
                "evidence_status": "CARRIED_FORWARD_IDENTICAL",
                "solver_family": None,
                "solver_version": None,
                "solver_input_digest": None,
                "computed_option_truths": {},
                "computed_unique_answer": None,
                "independent_evidence": (
                    "condense semantique identique a la preuve independante v1 ; "
                    "report d'identite, aucun recalcul necessaire"
                ),
                "human_review_required": False,
                "verification": None,
            }
            entry["evidence_digest"] = _digest(entry)
            questions.append(entry)
            continue

        if key not in reproof_keys:  # pragma: no cover - garde de partition
            raise EvidenceError(f"question hors partition: {chapter}/{question_id}")

        sanitized = solver.sanitize_canonical(question)
        result = solver.solve(sanitized)

        if result.status != "MACHINE_RESOLVED":
            entry = {
                **common,
                "evidence_status": "HUMAN_REVIEW_REQUIRED",
                "solver_family": None,
                "solver_version": solver.SOLVER_VERSION,
                "solver_input_digest": sanitized.digest(),
                "computed_option_truths": {},
                "computed_unique_answer": None,
                "independent_evidence": "",
                "reason": result.reason,
                "delta_classes": reproof_by_key[key].get("delta_classes", []),
                "human_review_required": True,
                "release_blocking": True,
                "verification": None,
            }
            entry["evidence_digest"] = _digest(entry)
            questions.append(entry)
            continue

        verification = _verify(question, result)
        if verification["answer_key_verdict"] != "PASS":
            failures.append(
                f"{chapter}/{question_id}: "
                f"{json.dumps(verification, ensure_ascii=False)[:200]}"
            )
        if verification["coverage_verdict"] != "PASS":
            coverage_findings.append(
                {
                    "chapter": chapter,
                    "question_id": question_id,
                    "missing_error_model": verification["diagnostic_coverage"][
                        "missing_error_model"
                    ],
                    "missing_remediation_reference": verification[
                        "diagnostic_coverage"
                    ]["missing_remediation_reference"],
                }
            )
        entry = {
            **common,
            "evidence_status": "MACHINE_RECALCULATED",
            "solver_family": result.family,
            "solver_version": solver.SOLVER_VERSION,
            "solver_input_digest": sanitized.digest(),
            "solver_output_digest": result.digest(),
            "computed_option_truths": dict(sorted(result.option_truths.items())),
            "computed_unique_answer": result.unique_answer,
            "computed_value": result.computed_value,
            "independent_evidence": result.independent_evidence,
            "delta_classes": reproof_by_key[key].get("delta_classes", []),
            "human_review_required": False,
            "verification": verification,
        }
        entry["evidence_digest"] = _digest(entry)
        questions.append(entry)

    counts = {
        "question_count": len(questions),
        "CARRIED_FORWARD_IDENTICAL": sum(
            1 for e in questions if e["evidence_status"] == "CARRIED_FORWARD_IDENTICAL"
        ),
        "MACHINE_RECALCULATED": sum(
            1 for e in questions if e["evidence_status"] == "MACHINE_RECALCULATED"
        ),
        "HUMAN_REVIEW_REQUIRED": sum(
            1 for e in questions if e["evidence_status"] == "HUMAN_REVIEW_REQUIRED"
        ),
        "UNKNOWN": sum(
            1
            for e in questions
            if e["evidence_status"]
            not in {
                "CARRIED_FORWARD_IDENTICAL",
                "MACHINE_RECALCULATED",
                "HUMAN_REVIEW_REQUIRED",
            }
        ),
    }
    total = (
        counts["CARRIED_FORWARD_IDENTICAL"]
        + counts["MACHINE_RECALCULATED"]
        + counts["HUMAN_REVIEW_REQUIRED"]
    )
    if total != counts["question_count"] or counts["UNKNOWN"]:
        raise EvidenceError("la partition des etats ne couvre pas le corpus")
    if failures:
        raise EvidenceError(
            "cle declaree contredite par le calcul independant: " + " | ".join(failures)
        )

    human_required = sorted(
        f"{e['chapter']}/{e['question_id']}"
        for e in questions
        if e["human_review_required"]
    )

    return {
        "artifact_type": "qcm_independent_evidence_v2",
        "schema_version": 2,
        "generated_by": "scripts/build_qcm_independent_evidence_v2.py",
        "solver_version": solver.SOLVER_VERSION,
        "supersedes_without_rewriting": "audit/qcm_review_evidence/*.json (v1, HISTORICAL)",
        "approves_nothing": True,
        "evidence_schema_fields": list(EVIDENCE_SCHEMA_FIELDS),
        "independence_contract": {
            "solver_never_receives": sorted(solver.FORBIDDEN_INPUT_FIELDS),
            "enforced_by": "qcm_independent_solver.sanitize (leve DeclaredAnswerLeak)",
            "verifier_runs_after_solver": True,
            "routing_is_by_generic_family_never_by_question_id": True,
        },
        "counts": counts,
        "equation": (
            f"{counts['question_count']} = {counts['CARRIED_FORWARD_IDENTICAL']}"
            f" + {counts['MACHINE_RECALCULATED']}"
            f" + {counts['HUMAN_REVIEW_REQUIRED']}"
        ),
        "EVIDENCE_ROUTING_COMPLETE": counts["UNKNOWN"] == 0,
        "ALL_QCM_HUMAN_REVIEW_COMPLETE": not human_required,
        "human_review_required_questions": human_required,
        "human_review_is_release_blocking": True,
        "answer_key_verified_by_independent_computation": sum(
            1
            for e in questions
            if e["evidence_status"] == "MACHINE_RECALCULATED"
            and e["verification"]["answer_key_verdict"] == "PASS"
        ),
        "diagnostic_coverage_findings": coverage_findings,
        "diagnostic_coverage_is_release_blocking": True,
        "solver_families_used": sorted(
            {e["solver_family"] for e in questions if e["solver_family"]}
        ),
        "set_digest": _digest(
            [
                [e["chapter"], e["question_id"], e["evidence_digest"]]
                for e in questions
            ]
        ),
        "questions": questions,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    counts = payload["counts"]
    lines = [
        "<!-- generated by build_qcm_independent_evidence_v2.py -->",
        "",
        "# Preuve de revue independante des QCM — v2",
        "",
        "Une identite par question. La v1 reste l'enregistrement historique.",
        "Cet artefact n'approuve rien.",
        "",
        f"- Questions du corpus : {counts['question_count']}",
        f"- Report d'identite : {counts['CARRIED_FORWARD_IDENTICAL']}",
        f"- Recalcul independant : {counts['MACHINE_RECALCULATED']}",
        f"- Revue humaine requise : {counts['HUMAN_REVIEW_REQUIRED']}",
        f"- UNKNOWN : {counts['UNKNOWN']}",
        f"- Equation : {payload['equation']}",
        f"- EVIDENCE_ROUTING_COMPLETE : {payload['EVIDENCE_ROUTING_COMPLETE']}",
        f"- ALL_QCM_HUMAN_REVIEW_COMPLETE : {payload['ALL_QCM_HUMAN_REVIEW_COMPLETE']}",
        "",
        "## Familles generiques employees",
        "",
    ]
    lines += [f"- `{family}`" for family in payload["solver_families_used"]]
    lines += [
        "",
        "## Questions recalculees independamment",
        "",
        "| chapitre | question | famille | verite calculee | cle declaree | verdict |",
        "|---|---|---|---|---|---|",
    ]
    for entry in payload["questions"]:
        if entry["evidence_status"] != "MACHINE_RECALCULATED":
            continue
        verification = entry["verification"]
        lines.append(
            f"| {entry['chapter']} | {entry['question_id']} | {entry['solver_family']} "
            f"| {entry['computed_unique_answer']} | {verification['declared_key']} "
            f"| {verification['verdict']} |"
        )
    lines += [
        "",
        "## Questions renvoyees a la revue humaine",
        "",
        "Comportement correct du solveur, pas un echec : aucune regle "
        "mathematique generique ne les modelise sans ecrire une derivation "
        "propre a la question. Elles restent bloquantes pour la release.",
        "",
        "| chapitre | question | motif |",
        "|---|---|---|",
    ]
    for entry in payload["questions"]:
        if entry["evidence_status"] != "HUMAN_REVIEW_REQUIRED":
            continue
        lines.append(
            f"| {entry['chapter']} | {entry['question_id']} | {entry.get('reason', '')} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="echoue si perime")
    args = parser.parse_args(argv)

    payload = build_evidence()
    rendered_json = render_json(payload)
    rendered_md = render_md(payload)

    if args.check:
        stale = [
            str(target.relative_to(ROOT))
            for target, rendered in (
                (JSON_TARGET, rendered_json),
                (MD_TARGET, rendered_md),
            )
            if not target.is_file() or target.read_text(encoding="utf-8") != rendered
        ]
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print(f"PASS preuve QCM v2: {payload['equation']} | UNKNOWN=0")
        return 0

    JSON_TARGET.write_text(rendered_json, encoding="utf-8")
    MD_TARGET.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {JSON_TARGET.name} / {MD_TARGET.name}: {payload['equation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
