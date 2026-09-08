#!/usr/bin/env python3
"""Separate current QCM key proofs, full scientific review, and human approval.

Current routing must match the exact current question set and complete semantic
content, including remediation references. A stale aggregate cannot certify a
current question or contribute a retired question to current totals.

The declarations in qcm_reviews.py have no recorded source/dependency binding.
They remain inspectable historical evidence, and cannot close a current review.
A new binding must come from an actual independent review; this producer never
manufactures one by hashing current content after the fact. Generic answer-key
proofs remain distinct from complete scientific review and human approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402
import qcm_reviews as declarations  # noqa: E402
import build_qcm_review_proof_reconciliation as reconciliation  # noqa: E402
import build_qcm_independent_evidence_v2 as independent_evidence  # noqa: E402

EVIDENCE = ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json"
OUTPUT_JSON = ROOT / "audit/QCM_REVIEW_CLOSURE.json"
OUTPUT_MD = ROOT / "audit/QCM_REVIEW_CLOSURE.md"

PROVEN = "MECHANICALLY_PROVEN"
REVIEWED = "CONCEPTUALLY_REVIEWED"
OPEN = "REVIEW_OPEN"
DISAGREEMENT = "KEY_DISAGREEMENT"
BROKEN = "DERIVATION_FAILED"


def _current_evidence(root: Path) -> dict[str, Any]:
    """Fail closed before using an old route or count as current evidence."""
    evidence = json.loads((root / EVIDENCE.relative_to(ROOT)).read_text("utf-8"))
    corpus = reconciliation._load_corpus(root)
    rows = evidence.get("questions") or []
    keys = [(row.get("chapter"), row.get("question_id")) for row in rows]
    if len(set(keys)) != len(keys) or set(keys) != set(corpus):
        raise ValueError("stale QCM evidence: current question set differs")
    states = {"CARRIED_FORWARD_IDENTICAL", "MACHINE_RECALCULATED", "HUMAN_REVIEW_REQUIRED"}
    counts = evidence.get("counts") or {}
    if counts.get("question_count") != len(corpus) or counts.get("UNKNOWN") != 0:
        raise ValueError("stale QCM evidence: current counts differ")
    for status in states:
        if counts.get(status) != sum(row.get("evidence_status") == status for row in rows):
            raise ValueError(f"stale QCM evidence: count differs for {status}")
    for row in rows:
        key = (row["chapter"], row["question_id"])
        question, source = corpus[key]
        if (row.get("evidence_status") not in states or row.get("source_path") != source
                or row.get("full_question_digest") != reconciliation.current_question_digest(question)):
            raise ValueError(f"stale QCM evidence: current content differs for {key}")
    independent_evidence.validate_current_evidence(evidence, root)
    return evidence


def _questions(root: Path, evidence: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    # Every current question needs a full scientific review. A proven answer
    # key alone does not review its diagnostics, references or programme fit.
    if evidence is None:
        evidence = _current_evidence(root)
    corpus = reconciliation._load_corpus(root)
    enriched = []
    for row in evidence["questions"]:
        brute, source = corpus[(row["chapter"], row["question_id"])]
        enriched.append({
            "chapter": row["chapter"], "question_id": row["question_id"],
            "capacity": brute.get("capacite"), "source_path": source,
            "enonce": brute["enonce"], "options": dict(brute["options"]),
            "cle": brute["correcte"], "diagnostics": brute.get("diagnostics") or {},
            "full_question_digest": row["full_question_digest"],
            "answer_key_state": row.get("answer_key_state", "PENDING"),
            "historical_route": row["evidence_status"],
        })
    return enriched


def _evaluer_mecanique(question, famille, derivation) -> dict[str, Any]:
    """Legacy ID-only declarations have no binding to their reviewed statement.

    Never manufacture that missing binding from the current source. The old
    calculation remains inspectable below; a current review belongs to the
    source/dependency-bound review index, not this declaration table.
    """
    return {
        "state": OPEN, "family": famille, "computed": None,
        "current_scientific_credit": False,
        "detail": "legacy mechanical declaration has no recorded current source/dependency binding",
    }


def _calculate_legacy_answer(question, famille, derivation) -> dict[str, Any]:
    """Forensic helper only: computes a declaration, never current evidence."""
    # La dérivation ne reçoit QUE les options : une copie, pour qu'elle ne
    # puisse pas non plus muter la question.
    options = dict(question["options"])
    try:
        lettre = derivation(options)
    except Exception as erreur:  # noqa: BLE001 - on publie l'échec
        return {
            "state": BROKEN,
            "family": famille,
            "computed": None,
            "detail": f"{type(erreur).__name__}: {erreur}",
            "traceback": traceback.format_exc(limit=3),
        }
    if lettre not in question["options"]:
        return {
            "state": BROKEN,
            "family": famille,
            "computed": lettre,
            "detail": "la dérivation a renvoyé une lettre hors des options",
        }
    if lettre != question["cle"]:
        return {
            "state": DISAGREEMENT,
            "family": famille,
            "computed": lettre,
            "detail": (
                f"la dérivation conclut {lettre}, la clé dit "
                f"{question['cle']}"
            ),
        }
    return {"state": "LEGACY_DERIVATION_RESULT", "family": famille, "computed": lettre,
            "current_scientific_credit": False}


def _evaluer_conceptuelle(question, revue, root: Path) -> dict[str, Any]:
    """An unbound historical assertion has no authority over a current key."""
    return {
        "state": OPEN,
        "computed": None,
        "current_scientific_credit": False,
        "detail": "legacy conceptual review has no recorded current source/dependency binding",
        "historical_observation": {
            "declared_answer": revue.get("reponse"),
            "source_cours": revue.get("source_cours"),
            "source_programme": revue.get("source_programme"),
            "current_authority": False,
        },
    }


def _inspect_legacy_conceptual_review(question, revue, root: Path) -> dict[str, Any]:
    """Forensic structural comparison only; never a current product verdict."""
    cours = str(revue["source_cours"])
    if not (root / cours).is_file():
        return {
            "state": BROKEN,
            "computed": revue["reponse"],
            "detail": f"objet de cours absent du dépôt : {cours}",
        }
    distracteurs = set(question["options"]) - {question["cle"]}
    refutes = set(revue["refutations"])
    if refutes != distracteurs:
        manquants = sorted(distracteurs - refutes)
        surnumeraires = sorted(refutes - distracteurs)
        return {
            "state": BROKEN,
            "computed": revue["reponse"],
            "detail": (
                f"réfutations incomplètes — manquantes {manquants}, "
                f"hors options {surnumeraires}"
            ),
        }
    courtes = sorted(
        lettre for lettre, texte in revue["refutations"].items()
        if len(str(texte).strip()) < 40
    )
    if courtes:
        return {
            "state": BROKEN,
            "computed": revue["reponse"],
            "detail": f"réfutations trop brèves pour établir quoi que ce soit : {courtes}",
        }
    if revue["reponse"] != question["cle"]:
        return {
            "state": DISAGREEMENT,
            "computed": revue["reponse"],
            "detail": (
                f"la revue conclut {revue['reponse']}, la clé dit "
                f"{question['cle']}"
            ),
        }
    return {
        "state": OPEN,
        "computed": None,
        "current_scientific_credit": False,
        "detail": "legacy conceptual review has no recorded current source/dependency binding",
        "source_cours": cours,
        "source_programme": revue["source_programme"],
    }


def _corpus_totals(root: Path, evidence: dict[str, Any] | None = None) -> dict[str, int]:
    """Read validated current routes; these are not full review verdicts."""

    if evidence is None:
        evidence = _current_evidence(root)
    counts = evidence["counts"]
    return {
        "total": int(counts["question_count"]),
        "carried_forward": int(counts["CARRIED_FORWARD_IDENTICAL"]),
        "machine": int(counts["MACHINE_RECALCULATED"]),
        "routed_to_review": int(counts["HUMAN_REVIEW_REQUIRED"]),
        "unrouted": int(counts["UNKNOWN"]),
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    source_set = {path.relative_to(root).as_posix() for path in reconciliation._qcm_sources(root)}
    input_paths = ["audit/QCM_INDEPENDENT_EVIDENCE_V2.json", "scripts/qcm_reviews.py",
                   "scripts/build_qcm_review_closure.py", "scripts/build_qcm_review_proof_reconciliation.py",
                   *independent_evidence._proof_input_paths(root)]
    observed_inputs = freshness.stamp(input_paths, root=root)
    current = _current_evidence(root)
    question_set = {(row["chapter"], row["question_id"]) for row in current["questions"]}
    resultats = []
    for question in _questions(root, current):
        cle = (question["chapter"], question["question_id"])
        mecanique = declarations.MECHANICAL_DERIVATIONS.get(cle)
        conceptuelle = declarations.CONCEPTUAL_REVIEWS.get(cle)
        if mecanique is not None:
            famille, derivation = mecanique
            verdict = _evaluer_mecanique(question, famille, derivation)
            regime = declarations.MECHANICAL
        elif conceptuelle is not None:
            verdict = _evaluer_conceptuelle(question, conceptuelle, root)
            regime = declarations.CONCEPTUAL
        else:
            verdict = {
                "state": OPEN,
                "computed": None,
                "detail": "aucune dérivation ni revue déclarée",
            }
            regime = None
        resultats.append({
            "chapter": question["chapter"],
            "question_id": question["question_id"],
            "capacity": question["capacity"],
            "source_path": question["source_path"],
            "regime": regime,
            "key": question["cle"],
            "full_question_digest": question["full_question_digest"],
            "answer_key_state": question["answer_key_state"],
            "human_approval": "PENDING",
            **verdict,
        })

    etats = {etat: 0 for etat in (PROVEN, REVIEWED, OPEN, DISAGREEMENT, BROKEN)}
    for ligne in resultats:
        etats[ligne["state"]] += 1
    familles = {famille: 0 for famille in declarations.FAMILIES}
    for ligne in resultats:
        if ligne["state"] == PROVEN:
            familles[ligne["family"]] += 1

    total = len(resultats)
    summary = {
        "QCM_HUMAN_REVIEW_POPULATION": total,
        "QCM_SCIENTIFIC_REVIEW_POPULATION": total,
        "QCM_ANSWER_KEY_PROVEN": sum(r["answer_key_state"] == "ANSWER_KEY_PROVEN" for r in resultats),
        "QCM_ANSWER_KEY_HISTORICAL_IDENTICAL": sum(r["answer_key_state"] == "ANSWER_KEY_PROVEN_BY_IDENTICAL_HISTORICAL_EVIDENCE" for r in resultats),
        "QCM_MECHANICAL_PROVEN": etats[PROVEN],
        "QCM_MECHANICAL_BY_FAMILY": familles,
        "QCM_CONCEPTUAL_REVIEWED": etats[REVIEWED],
        "QCM_REVIEW_OPEN": etats[OPEN],
        "QCM_KEY_DISAGREEMENTS": etats[DISAGREEMENT],
        "QCM_DERIVATION_FAILURES": etats[BROKEN],
        "QCM_REVIEW_CLOSED": etats[PROVEN] + etats[REVIEWED],
    }

    # ABSENCE DE REVUE ET ABSENCE D'APPROBATION SONT DEUX DETTES DISTINCTES.
    # Les confondre autorise deux mensonges symetriques : declarer close une
    # dette scientifique parce que personne n'a encore approuve, ou declarer
    # approuve un contenu parce que la revue a ete faite. On publie donc les
    # deux, et aucun ne se deduit de l'autre.
    totaux = _corpus_totals(root, current)
    scientifique_en_attente = (
        etats[OPEN] + etats[DISAGREEMENT] + etats[BROKEN] + totaux["unrouted"]
    )
    couvertes = totaux["total"] - scientifique_en_attente
    summary.update({
        "QCM_TOTAL_CURRENT": totaux["total"],
        "QCM_PROOF_ROUTES": {
            "CARRIED_FORWARD_IDENTICAL": totaux["carried_forward"],
            "MACHINE_RECALCULATED": totaux["machine"],
            "ROUTED_TO_SCIENTIFIC_REVIEW": totaux["routed_to_review"],
        },
        "QCM_PROOF_COVERAGE": f"{couvertes}/{totaux['total']}",
        "QCM_SCIENTIFIC_REVIEW_PENDING": scientifique_en_attente,
        # Aucun recu d'approbation humaine n'existe pour un QCM, et aucun
        # agent n'en cree : la dette d'approbation reste entiere.
        "QCM_HUMAN_APPROVAL_PENDING": totaux["total"],
        "REVIEW_IS_NOT_APPROVAL": True,
    })
    if sum(etats.values()) != total:
        raise ValueError("items perdus dans la clôture QCM")

    payload = {
        "artifact_type": "qcm_review_closure",
        "schema_version": 1,
        "generated_by": "scripts/build_qcm_review_closure.py",
        "declaration_table": "scripts/qcm_reviews.py",
        "approves_nothing": True,
        "answer_key_proof_is_not_complete_scientific_review": True,
        "legacy_declarations_without_recorded_binding_are_not_current_reviews": True,
        "independence_contract": (
            "Generic key evidence is source-bound by current question identity. "
            "Historical declarations without a recorded source/dependency binding "
            "never close current scientific review; forensic helpers grant no credit."
        ),
        "summary": summary,
        "questions": resultats,
    }
    payload["closure_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(
            [
                [r["chapter"], r["question_id"], r["state"], r.get("computed")]
                for r in resultats
            ],
            ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    final_inputs = freshness.stamp(input_paths, root=root)
    final_source_set = {path.relative_to(root).as_posix() for path in reconciliation._qcm_sources(root)}
    if final_source_set != source_set:
        raise ValueError("QCM source set changed during current review construction")
    final_corpus = reconciliation._load_corpus(root)
    if set(final_corpus) != question_set:
        raise ValueError("QCM question set changed during current review construction")
    for row in current["questions"]:
        question, source = final_corpus[(row["chapter"], row["question_id"])]
        if source != row["source_path"] or reconciliation.current_question_digest(question) != row["full_question_digest"]:
            raise ValueError("QCM content changed during current review construction")
    if final_inputs != observed_inputs:
        raise ValueError("QCM inputs or HEAD changed during current review construction")
    if independent_evidence._proof_method_binding(root) != current["proof_method_binding"]:
        raise ValueError("QCM proof method, dependency or runtime changed during current review construction")
    payload["freshness"] = observed_inputs
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# État courant des preuves et revues QCM",
        "",
        f"- Population : `{s['QCM_HUMAN_REVIEW_POPULATION']}`",
        f"- `QCM_MECHANICAL_PROVEN` : `{s['QCM_MECHANICAL_PROVEN']}` "
        f"({s['QCM_MECHANICAL_BY_FAMILY']})",
        f"- `QCM_CONCEPTUAL_REVIEWED` : `{s['QCM_CONCEPTUAL_REVIEWED']}`",
        f"- `QCM_REVIEW_OPEN` : `{s['QCM_REVIEW_OPEN']}`",
        f"- `QCM_KEY_DISAGREEMENTS` : `{s['QCM_KEY_DISAGREEMENTS']}`",
        f"- `QCM_DERIVATION_FAILURES` : `{s['QCM_DERIVATION_FAILURES']}`",
        "",
        f"- `QCM_TOTAL_CURRENT` : `{s['QCM_TOTAL_CURRENT']}`",
        f"- `QCM_PROOF_COVERAGE` : `{s['QCM_PROOF_COVERAGE']}` "
        f"({s['QCM_PROOF_ROUTES']})",
        f"- `QCM_SCIENTIFIC_REVIEW_PENDING` : `{s['QCM_SCIENTIFIC_REVIEW_PENDING']}`",
        f"- `QCM_HUMAN_APPROVAL_PENDING` : `{s['QCM_HUMAN_APPROVAL_PENDING']}`",
        "",
        "Une revue faite n'est pas une approbation : les deux dettes sont "
        "comptees separement, et aucune ne se deduit de l'autre.",
        "",
    ]
    ennuis = [
        r for r in payload["questions"]
        if r["state"] in (DISAGREEMENT, BROKEN)
    ]
    if ennuis:
        lignes += ["## Divergences et échecs", ""]
        for r in ennuis:
            lignes.append(
                f"- `{r['chapter']}/{r['question_id']}` — `{r['state']}` : "
                f"{r.get('detail', '')}"
            )
        lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT_JSON.is_file():
            print("QCM_REVIEW_CLOSURE check: MISSING")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("QCM_REVIEW_CLOSURE check: STALE")
            return 1
        print("QCM_REVIEW_CLOSURE check: OK")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
