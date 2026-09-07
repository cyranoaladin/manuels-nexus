#!/usr/bin/env python3
"""Construit la file humaine courante sans approbation implicite.

La file est une projection, jamais une source d'approbation. Elle réunit des
unités de travail disjointes et nommées par dimension : dette objet, preuve de
réponse QCM, preuve de renvoi de remédiation, décision éditoriale.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "audit/HUMAN_REVIEW_QUEUE.json"
PARTITION = ROOT / "audit/CURRENT_REVIEW_DEBT_PARTITION.json"
EVIDENCE = ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json"
RECONCILIATION = ROOT / "audit/QCM_REVIEW_PROOF_RECONCILIATION.json"
DECISION = ROOT / "audit/TNSI_PROJET_ASSESSMENT_MODE.json"
CLOSURE = ROOT / "audit/QCM_REVIEW_CLOSURE.json"
RENVOI_AUDIT = ROOT / "audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.json"

#: États de fermeture QCM qui retirent une question de la file HUMAINE.
#: Une dérivation mécanique calcule la réponse sans jamais voir la clé : c'est
#: une preuve, pas un avis, et elle vaut `VALIDATED_BY_EVIDENCE`. Une revue
#: conceptuelle est un raisonnement écrit par un agent : elle informe l'humain,
#: elle ne le remplace pas. Les deux régimes sont donc traités différemment,
#: et aucune unité n'est perdue : ce qui ne ferme pas reste dans la file.
MACHINE_PROVEN_STATES = frozenset({"MECHANICALLY_PROVEN"})
AGENT_REVIEWED_STATES = frozenset({"CONCEPTUALLY_REVIEWED"})


def _read(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"racine JSON non objet: {path}")
    return payload


def _set_digest(values: Iterable[str]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(
            sorted(str(value) for value in values),
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _reviewers_for_chapter(chapter: str) -> list[str]:
    if chapter.startswith(("1NSI-", "TNSI-")):
        return ["EXPERT_NSI", "EXPERT_PROGRAMME_PEDAGOGIE"]
    if chapter.startswith(
        ("1SPE-", "TSPE-", "TCOMPL-", "TEXP-", "TEXPERTES-")
    ):
        return ["EXPERT_MATHEMATIQUE", "EXPERT_PROGRAMME_PEDAGOGIE"]
    raise ValueError(f"chapitre sans gouvernance de reviewer: {chapter}")


def _reviewer_fields(chapters: Iterable[str]) -> dict[str, Any]:
    by_chapter = {
        chapter: _reviewers_for_chapter(chapter) for chapter in sorted(set(chapters))
    }
    result: dict[str, Any] = {"required_reviewers_by_chapter": by_chapter}
    distinct = {tuple(roles) for roles in by_chapter.values()}
    if len(distinct) == 1:
        result["required_reviewers"] = list(next(iter(distinct)))
    return result


def _chapter_buckets(rows: Iterable[tuple[str, str]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[str]] = {}
    for chapter, unit_id in rows:
        buckets.setdefault(chapter, []).append(unit_id)
    return {
        chapter: {
            "count": len(unit_ids),
            "unit_ids": sorted(unit_ids),
            "set_digest": _set_digest(unit_ids),
        }
        for chapter, unit_ids in sorted(buckets.items())
    }


def _closed_by_machine_proof(closure: dict[str, Any]) -> set[str]:
    """Questions QCM dont la réponse est ÉTABLIE par une dérivation exécutée.

    On n'accepte que les états de preuve mécanique, et seulement si la
    fermeture ne rapporte ni désaccord de clé ni échec de dérivation : une
    fermeture qui contient un désaccord ne ferme rien du tout.
    """
    if closure.get("artifact_type") != "qcm_review_closure":
        raise ValueError("fermeture QCM schema invalide")
    resume = closure.get("summary") or {}
    if resume.get("QCM_KEY_DISAGREEMENTS") or resume.get("QCM_DERIVATION_FAILURES"):
        raise ValueError("fermeture QCM avec désaccord ou échec de dérivation")
    return {
        f"{row['chapter']}/{row['question_id']}"
        for row in closure.get("questions") or []
        if row.get("state") in MACHINE_PROVEN_STATES
    }


def _agent_reviewed(closure: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Questions QCM couvertes par une revue conceptuelle écrite.

    Elles ne quittent pas la file : la revue est une pièce versée au dossier
    de l'humain, pas une approbation. Elle est jointe à l'unité pour être lue.
    """
    return {
        f"{row['chapter']}/{row['question_id']}": {
            "source_cours": row.get("source_cours"),
            "source_programme": row.get("source_programme"),
            "reponse_etablie": row.get("computed"),
        }
        for row in closure.get("questions") or []
        if row.get("state") in AGENT_REVIEWED_STATES
    }


def _renvois_resolus(audit: dict[str, Any]) -> set[str]:
    """Questions dont TOUS les renvois de diagnostic sont résolus.

    La résolution est mécanique : chaque renvoi est confronté aux objets du
    chapitre. Un seul renvoi non résolu, et la question reste ouverte.
    """
    if audit.get("artifact_type") != "qcm_diagnostic_renvoi_audit":
        raise ValueError("audit de renvois QCM schema invalide")
    resume = audit.get("summary") or {}
    if resume.get("BROKEN_REMEDIATION_REFERENCES") or resume.get("QCM_DIAGNOSTIC_MISMATCH"):
        raise ValueError("audit de renvois QCM avec renvoi casse ou incoherent")
    par_question: dict[str, bool] = {}
    for ligne in audit.get("renvois") or []:
        identite = f"{ligne['chapter']}/{ligne['question_id']}"
        resolu = ligne.get("state") == "RESOLVED"
        par_question[identite] = par_question.get(identite, True) and resolu
    return {identite for identite, resolu in par_question.items() if resolu}


def build_queue(
    *,
    partition: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    reconciliation: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
    closure: dict[str, Any] | None = None,
    renvoi_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    partition = partition or _read(PARTITION)
    evidence = evidence or _read(EVIDENCE)
    reconciliation = reconciliation or _read(RECONCILIATION)
    decision = decision or _read(DECISION)
    closure = closure or _read(CLOSURE)
    renvoi_audit = renvoi_audit or _read(RENVOI_AUDIT)

    if (
        partition.get("artifact_type") != "current_review_debt_partition"
        or partition.get("schema_version") != 1
    ):
        raise ValueError("partition review debt schema invalide")
    if partition.get("unknown_count") != 0:
        raise ValueError("partition review debt unknown non nul")
    if (
        evidence.get("artifact_type") != "qcm_independent_evidence_v2"
        or evidence.get("schema_version") != 2
        or not isinstance(evidence.get("questions"), list)
    ):
        raise ValueError("preuve QCM schema invalide")
    known_evidence_statuses = {
        "CARRIED_FORWARD_IDENTICAL",
        "HUMAN_REVIEW_REQUIRED",
        "MACHINE_RECALCULATED",
    }
    unknown_statuses = sorted(
        {
            str(row.get("evidence_status"))
            for row in evidence["questions"]
            if row.get("evidence_status") not in known_evidence_statuses
        }
    )
    if unknown_statuses:
        raise ValueError(f"statut QCM inconnu: {unknown_statuses}")
    for row in evidence["questions"]:
        if not isinstance(row.get("chapter"), str) or not row["chapter"].strip():
            raise ValueError("identité QCM vide: chapter")
        if not isinstance(row.get("question_id"), str) or not row["question_id"].strip():
            raise ValueError("identité QCM vide: question_id")
    all_qcm_identities = [
        f"{row['chapter']}/{row['question_id']}" for row in evidence["questions"]
    ]
    if len(set(all_qcm_identities)) != len(all_qcm_identities):
        raise ValueError("identité QCM dupliquée dans la preuve indépendante")
    observed_counts = Counter(row["evidence_status"] for row in evidence["questions"])
    declared_counts = evidence.get("counts") or {}
    if int(declared_counts.get("question_count", -1)) != len(evidence["questions"]):
        raise ValueError("preuve QCM question_count divergent")
    for status in known_evidence_statuses:
        if int(declared_counts.get(status, -1)) != observed_counts[status]:
            raise ValueError(f"preuve QCM count divergent: {status}")
    if int(declared_counts.get("UNKNOWN", -1)) != 0:
        raise ValueError("preuve QCM unknown non nul")
    if (
        reconciliation.get("artifact_type")
        != "qcm_review_proof_reconciliation"
        or reconciliation.get("schema_version") != 1
        or not isinstance(reconciliation.get("proof_field_coverage_gaps"), list)
    ):
        raise ValueError("réconciliation QCM schema invalide")
    if decision.get("artifact_type") != "assessment_mode_decision_request":
        raise ValueError("décision éditoriale schema invalide")

    components = partition.get("components")
    if not isinstance(components, dict) or not components:
        raise ValueError("partition de dette sans components")
    items: list[dict[str, Any]] = []
    object_fingerprints: set[str] = set()
    for name, component in sorted(components.items()):
        fingerprints = [str(value) for value in component.get("fingerprints") or []]
        objects = component.get("objects") or []
        if (
            component.get("count") != len(fingerprints)
            or len(objects) != len(fingerprints)
            or len(set(fingerprints)) != len(fingerprints)
        ):
            raise ValueError(f"partition component count incohérent: {name}")
        if component.get("fingerprints_digest") != _set_digest(fingerprints):
            raise ValueError(f"partition component digest incohérent: {name}")
        overlap = object_fingerprints & set(fingerprints)
        if overlap:
            raise ValueError(f"partition objet double-comptée: {sorted(overlap)[:3]}")
        object_fingerprints.update(fingerprints)
        chapters = Counter(str(row.get("chapter") or "") for row in objects)
        if "" in chapters:
            raise ValueError(f"partition objet sans chapitre: {name}")
        unit_ids = sorted(f"OBJECT_REVIEW::{value}" for value in fingerprints)
        units_by_chapter = _chapter_buckets(
            (
                str(row["chapter"]),
                f"OBJECT_REVIEW::{fingerprint}",
            )
            for fingerprint, row in zip(fingerprints, objects, strict=True)
        )
        items.append(
            {
                "item_id": name,
                "category": "OBJECT_REVIEW",
                "count": len(unit_ids),
                "unit_ids": unit_ids,
                "set_digest": _set_digest(unit_ids),
                "chapters": dict(sorted(chapters.items())),
                "units_by_chapter": units_by_chapter,
                "provenance": component.get("provenance"),
                **_reviewer_fields(chapters),
                "distinct_humans_required": True,
                "release_blocking": True,
            }
        )
    expected_object_count = int(partition.get("current_review_debt_count") or -1)
    if len(object_fingerprints) != expected_object_count:
        raise ValueError(
            "partition review debt count divergent: "
            f"{len(object_fingerprints)} != {expected_object_count}"
        )
    if partition.get("current_review_debt_digest") != _set_digest(object_fingerprints):
        raise ValueError("partition review debt digest divergent")
    if partition.get("pairwise_intersections") != []:
        raise ValueError("partition review debt intersections non nulles")
    if partition.get("union_equals_current_review_debt") is not True:
        raise ValueError("partition review debt non exhaustive")

    human_questions = [
        row
        for row in evidence.get("questions") or []
        if row.get("evidence_status") == "HUMAN_REVIEW_REQUIRED"
    ]
    qcm_identities = [
        f"{row.get('chapter')}/{row.get('question_id')}" for row in human_questions
    ]
    if len(set(qcm_identities)) != len(qcm_identities):
        raise ValueError("identité QCM dupliquée dans la preuve indépendante")
    if any(
        row.get("human_review_required") is not True
        or row.get("release_blocking") is not True
        for row in human_questions
    ):
        raise ValueError("QCM HUMAN_REVIEW_REQUIRED non bloquant ou contradictoire")
    # La fermeture QCM est confrontee a la population : une question prouvee
    # mecaniquement quitte la file humaine ; une question seulement relue par
    # un agent y reste, sa revue jointe. Rien n'est retire sans preuve, rien
    # n'est perdu sans trace.
    prouvees = _closed_by_machine_proof(closure)
    relues = _agent_reviewed(closure)
    non_couvertes = sorted(set(qcm_identities) - prouvees - set(relues))
    if non_couvertes:
        raise ValueError(
            f"questions QCM sans fermeture declaree : {non_couvertes[:3]}"
        )
    ouvertes = [row for row in human_questions
                if f"{row['chapter']}/{row['question_id']}" not in prouvees]
    fermees = sorted(f"QCM_ANSWER_SEMANTICS::{value}"
                     for value in set(qcm_identities) & prouvees)
    qcm_units = sorted(
        f"QCM_ANSWER_SEMANTICS::{row['chapter']}/{row['question_id']}"
        for row in ouvertes
    )
    qcm_chapters = Counter(row["chapter"] for row in ouvertes)
    qcm_by_chapter = _chapter_buckets(
        (
            str(row["chapter"]),
            f"QCM_ANSWER_SEMANTICS::{row['chapter']}/{row['question_id']}",
        )
        for row in ouvertes
    )
    items.append(
        {
            "item_id": "QCM_ANSWER_SEMANTICS",
            "category": "QCM_ANSWER_SEMANTICS",
            "count": len(qcm_units),
            "unit_ids": qcm_units,
            "set_digest": _set_digest(qcm_units),
            "chapters": dict(sorted(qcm_chapters.items())),
            "units_by_chapter": qcm_by_chapter,
            "population": len(qcm_identities),
            "closed_by_machine_proof": len(fermees),
            "closed_unit_ids": fermees,
            "closed_set_digest": _set_digest(fermees),
            "closure_evidence": "audit/QCM_REVIEW_CLOSURE.json",
            "agent_review_attached": sum(
                1 for row in ouvertes
                if f"{row['chapter']}/{row['question_id']}" in relues
            ),
            "agent_review_is_not_an_approval": True,
            **_reviewer_fields(qcm_chapters),
            "distinct_humans_required": True,
            "release_blocking": True,
        }
    )

    gaps = reconciliation.get("proof_field_coverage_gaps") or []
    if any(
        not isinstance(row.get("chapter"), str)
        or not row["chapter"].strip()
        or not isinstance(row.get("question_id"), str)
        or not row["question_id"].strip()
        for row in gaps
    ):
        raise ValueError("identité de renvoi QCM vide")
    renvoi_identities = [
        f"{row.get('chapter')}/{row.get('question_id')}" for row in gaps
    ]
    if any(row.get("field") != "diagnostics.renvoi" for row in gaps):
        raise ValueError("champ de preuve QCM inconnu")
    if len(set(renvoi_identities)) != len(renvoi_identities):
        raise ValueError("identité de renvoi QCM dupliquée")
    # La resolution d'un renvoi est mecanique : chaque renvoi est confronte
    # aux objets du chapitre, et un seul renvoi non resolu laisse la question
    # ouverte. Ce qui est resolu quitte donc la file ; le reste y demeure.
    resolus = _renvois_resolus(renvoi_audit)
    gaps_ouverts = [row for row in gaps
                    if f"{row['chapter']}/{row['question_id']}" not in resolus]
    renvois_fermes = sorted(
        f"QCM_DIAGNOSTIC_RENVOI_SEMANTICS::{value}"
        for value in set(renvoi_identities) & resolus
    )
    renvoi_units = sorted(
        f"QCM_DIAGNOSTIC_RENVOI_SEMANTICS::{row['chapter']}/{row['question_id']}"
        for row in gaps_ouverts
    )
    renvoi_chapters = Counter(str(row.get("chapter")) for row in gaps_ouverts)
    renvoi_by_chapter = _chapter_buckets(
        (
            str(row["chapter"]),
            f"QCM_DIAGNOSTIC_RENVOI_SEMANTICS::{row['chapter']}/{row['question_id']}",
        )
        for row in gaps_ouverts
    )
    items.append(
        {
            "item_id": "QCM_DIAGNOSTIC_RENVOI_SEMANTICS",
            "category": "QCM_DIAGNOSTIC_RENVOI_SEMANTICS",
            "count": len(renvoi_units),
            "unit_ids": renvoi_units,
            "set_digest": _set_digest(renvoi_units),
            "chapters": dict(sorted(renvoi_chapters.items())),
            "units_by_chapter": renvoi_by_chapter,
            "population": len(renvoi_identities),
            "closed_by_machine_resolution": len(renvois_fermes),
            "closed_unit_ids": renvois_fermes,
            "closed_set_digest": _set_digest(renvois_fermes),
            "closure_evidence": "audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.json",
            **_reviewer_fields(renvoi_chapters),
            "distinct_humans_required": True,
            "release_blocking": True,
        }
    )

    resolved = decision.get("status") == "RESOLVED_BY_HUMAN_DECISION"
    if resolved:
        # Le Release Owner a tranché : TNSI-PROJET est évalué par son projet et
        # sa grille critériée. La demande de décision est close, la preuve vit
        # dans le contrat de chapitre et le gate la vérifie. La laisser dans la
        # file la ferait réclamer indéfiniment une décision déjà rendue.
        if not decision.get("decision_received", {}).get("decision"):
            raise ValueError("décision éditoriale TNSI-PROJET résolue sans décision consignée")
        if decision.get("release_blocking") is not False:
            raise ValueError("décision éditoriale TNSI-PROJET résolue mais encore bloquante")
    elif (
        decision.get("release_blocking") is not True
        or decision.get("machine_cannot_decide") is not True
        or not decision.get("decision_required_from_human")
    ):
        raise ValueError("décision éditoriale TNSI-PROJET non bloquante ou incomplète")
    decision_units = (
        [] if resolved
        else [f"EDITORIAL_DECISION::{decision.get('chapter')}:ASSESSMENT_MODE"]
    )
    items.append(
        {
            "item_id": "TNSI_PROJET_ASSESSMENT_MODE",
            "category": "EDITORIAL_DECISION",
            "count": 0 if resolved else 1,
            "unit_ids": decision_units,
            "set_digest": _set_digest(decision_units),
            "chapters": {} if resolved else {str(decision.get("chapter")): 1},
            "units_by_chapter": _chapter_buckets(
                [(str(decision.get("chapter")), unit) for unit in decision_units]
            ),
            "question": decision.get("decision_required_from_human"),
            "resolution": decision.get("decision_received") if resolved else None,
            "required_reviewers": [
                "EXPERT_NSI",
                "EXPERT_PROGRAMME_PEDAGOGIE",
            ],
            "required_reviewers_by_chapter": {
                str(decision.get("chapter")): [
                    "EXPERT_NSI",
                    "EXPERT_PROGRAMME_PEDAGOGIE",
                ]
            },
            "distinct_humans_required": True,
            "release_blocking": True,
        }
    )

    unit_sets = {item["item_id"]: set(item["unit_ids"]) for item in items}
    intersections = [
        {
            "left": left,
            "right": right,
            "count": len(unit_sets[left] & unit_sets[right]),
        }
        for left, right in combinations(sorted(unit_sets), 2)
        if unit_sets[left] & unit_sets[right]
    ]
    if intersections:
        raise ValueError("unités de revue humaine double-comptées")
    counts = Counter()
    all_units: set[str] = set()
    for item in items:
        counts[item["category"]] += item["count"]
        all_units.update(item["unit_ids"])
    ordered_counts = {
        "OBJECT_REVIEW": counts["OBJECT_REVIEW"],
        "QCM_ANSWER_SEMANTICS": counts["QCM_ANSWER_SEMANTICS"],
        "QCM_DIAGNOSTIC_RENVOI_SEMANTICS": counts[
            "QCM_DIAGNOSTIC_RENVOI_SEMANTICS"
        ],
        "EDITORIAL_DECISION": counts["EDITORIAL_DECISION"],
        "TOTAL": len(all_units),
    }
    return {
        "artifact_type": "human_review_queue",
        "schema_version": 2,
        "generated_by": "scripts/build_human_review_queue.py",
        "approves_nothing": True,
        "status": "HUMAN_REVIEW_ACTION_REQUIRED" if all_units else "CLOSED",
        "source_inputs": {
            str(PARTITION.relative_to(ROOT)): _file_digest(PARTITION),
            str(EVIDENCE.relative_to(ROOT)): _file_digest(EVIDENCE),
            str(RECONCILIATION.relative_to(ROOT)): _file_digest(RECONCILIATION),
            str(DECISION.relative_to(ROOT)): _file_digest(DECISION),
            str(CLOSURE.relative_to(ROOT)): _file_digest(CLOSURE),
            str(RENVOI_AUDIT.relative_to(ROOT)): _file_digest(RENVOI_AUDIT),
        },
        "counts": ordered_counts,
        "queue_digest": _set_digest(all_units),
        "pairwise_intersections": intersections,
        "unknown_count": 0,
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_queue(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != rendered:
            print(f"stale: {TARGET.relative_to(ROOT)}")
            return 1
        print(f"current: {TARGET.relative_to(ROOT)}")
        return 0
    TARGET.write_text(rendered, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
