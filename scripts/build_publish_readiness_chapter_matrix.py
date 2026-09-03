#!/usr/bin/env python3
"""Registre de campagne : une ligne par chapitre des six manuels.

Aucun chapitre ne doit manquer. La campagne de publication se juge sur ce
registre : ALL_MACHINE_CONTENT_COMPLETE exige que toutes les lignes soient
machine-completes, et un chapitre absent du registre serait un chapitre oublie.

Le registre MESURE, il n'approuve rien. Les colonnes humaines rapportent l'etat
declare par la gouvernance, jamais un verdict deduit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_editorial_diacritics as diacritics  # noqa: E402
import build_p0_content_clone_ledger as clone_producer  # noqa: E402
import build_course_assembly_truth as course_truth_producer  # noqa: E402
import build_manual_review_disposition_ledger as disposition_producer  # noqa: E402
import build_ex_co_graph as ex_co_producer  # noqa: E402
import build_chapter_richness_matrix as richness_producer  # noqa: E402
import build_human_review_queue as human_queue_producer  # noqa: E402
import build_nsi_cross_discipline_ledger as cross_discipline_producer  # noqa: E402
import build_qcm_independent_evidence_v2 as evidence_v2  # noqa: E402
import build_true_pedagogical_coverage as coverage_producer  # noqa: E402
import capacity_identity  # noqa: E402
import human_review_governance as governance  # noqa: E402
import qcm_independent_solver as solver  # noqa: E402

JSON_TARGET = ROOT / "audit" / "PUBLISH_READINESS_CHAPTER_MATRIX.json"
MD_TARGET = ROOT / "audit" / "PUBLISH_READINESS_CHAPTER_MATRIX.md"
INVENTORY = ROOT / "audit" / "INVENTAIRE_COLLECTION.json"
COVERAGE_DIR = ROOT / "audit" / "official_program_coverage"
MATH_CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
NSI_CHAPTERS = ROOT / "NSI" / "chapitres"
RICHNESS_MATRIX = ROOT / "audit" / "CHAPTER_RICHNESS_MATRIX.json"
SEMANTIC_ALIGNMENT_LEDGER = ROOT / "audit" / "SEMANTIC_ALIGNMENT_LEDGER.json"

#: Contrat editorial Nexus de distribution des cles. Ce n'est pas une exigence
#: du B.O. : c'est une regle de qualite du manuel.
KEY_SPREAD_MAX = 1
KEY_RUN_MAX = 2


class ReadinessError(RuntimeError):
    """Une entrée transversale est contradictoire ou périmée."""


def _set_digest(values: list[str] | set[str]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(sorted(values), ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _payload_digest(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _capacity_truth(
    chapter: str,
    coverage: dict[str, Any],
    clone_ledger: dict[str, Any],
    *,
    alignment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Vérité capacité d'un chapitre, dérivée de producteurs cohérents.

    `alignment` est le registre d'alignement sémantique. Sans lui, une cellule
    au seul META déclaré reste inclassable : c'est le comportement d'origine,
    et il est conservé. Avec lui, la règle appliquée est celle de l'oracle
    SymPy -- la machine est complète quand il ne lui reste rien à classer,
    jamais quand plus aucun jugement humain n'est requis.

    Le rapprochement se fait par IDENTITÉ de cellule, jamais par comptage : un
    registre qui routerait une cellule étrangère ne verdit rien.
    """

    invalid = sorted(set(clone_ledger["objects_on_invalid_credit"]))
    indeterminate_paths = sorted(
        set(clone_ledger["objects_with_indeterminate_credit"])
    )
    if coverage.get("invalid_credit_paths_digest") != _set_digest(invalid):
        raise ReadinessError("invalid_credit: coverage et clone ledger divergent")
    if coverage.get("indeterminate_credit_paths_digest") != _set_digest(
        indeterminate_paths
    ):
        raise ReadinessError(
            "indeterminate_credit: coverage et clone ledger divergent"
        )

    rows = [row for row in coverage["rows"] if row["chapter"] == chapter]
    cell_ids = sorted(
        f"{row['canonical_capacity_uid']}::{row['role']}::{row['state']}"
        for row in rows
    )
    if "capacity_identity_blockers" in coverage:
        marker = f"/chapitres/{chapter}/"
        chapter_identity_blockers = [
            blocker
            for blocker in coverage.get("capacity_identity_blockers", [])
            if marker in f"/{blocker.get('path', '')}"
        ]
        identity_counts = {
            "ambiguous": sum(
                blocker.get("classification") == "AMBIGUOUS_CAPACITY_IDENTITY"
                for blocker in chapter_identity_blockers
            ),
            "unresolved": sum(
                blocker.get("classification") == "UNRESOLVED_CAPACITY_IDENTITY"
                for blocker in chapter_identity_blockers
            ),
            "unknown": sum(
                blocker.get("classification")
                not in {
                    "AMBIGUOUS_CAPACITY_IDENTITY",
                    "UNRESOLVED_CAPACITY_IDENTITY",
                }
                for blocker in chapter_identity_blockers
            ),
        }
    else:
        chapter_identity_blockers = []
        identity_counts = dict(coverage["capacity_identity_resolution"])
    identity_complete = (
        bool(rows)
        and all(identity_counts.get(key, 0) == 0 for key in ("ambiguous", "unresolved", "unknown"))
        and all(row.get("canonical_capacity_uid") for row in rows)
    )

    missing_ids = sorted(
        f"{row['canonical_capacity_uid']}::{row['role']}"
        for row in rows
        if row["state"] == "MISSING"
    )
    indeterminate_ids = sorted(
        f"{row['canonical_capacity_uid']}::{row['role']}"
        for row in rows
        if row["state"] == "INDETERMINATE_CLONE_CREDIT"
    )
    semantically_unvalidated_ids = sorted(
        f"{row['canonical_capacity_uid']}::{row['role']}"
        for row in rows
        if row["state"]
        == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    )

    # Chaque cellule au seul META declare doit avoir une disposition terminale
    # dans le registre d'alignement, rapprochee par identite exacte de cellule.
    # Ce qui n'y figure pas reste INCLASSABLE, et rougit.
    dispositions: dict[str, str] = {}
    for record in (alignment or {}).get("records", []):
        if record.get("chapter") != chapter:
            continue
        # Identite par EGALITE EXACTE de l'UID canonique et du role, jamais par
        # la chaine composite `cell_id` : c'est la meme regle que
        # `capacity_identity.py`, qui interdit de reconnaitre une capacite
        # autrement que par egalite.
        uid = str((record.get("official_capacity") or {}).get("canonical_uid") or "")
        role = str(record.get("pedagogical_role") or "")
        verdict = (record.get("semantic_alignment") or {}).get("disposition")
        if uid and role and verdict:
            dispositions[f"{uid}::{role}"] = str(verdict)
    routed_human = {
        cell
        for cell in semantically_unvalidated_ids
        if dispositions.get(cell) == "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"
    }
    routed_defect = {
        cell
        for cell in semantically_unvalidated_ids
        if dispositions.get(cell) == "DEFAUT_ETABLI"
    }
    unclassified_ids = sorted(
        cell
        for cell in semantically_unvalidated_ids
        if cell not in routed_human and cell not in routed_defect
    )

    marker = f"/chapitres/{chapter}/"
    invalid_paths = sorted(path for path in invalid if marker in f"/{path}")
    ambiguous_groups: list[str] = []
    unknown_groups: list[str] = []
    for group in clone_ledger["groups"]:
        if chapter not in {member["chapter"] for member in group["members"]}:
            continue
        status = group["canonical_selection"]["status"]
        if status == "AMBIGUOUS":
            ambiguous_groups.append(group["clone_group_id"])
        elif status == "UNKNOWN":
            unknown_groups.append(group["clone_group_id"])

    clone_complete = not invalid_paths and not ambiguous_groups and not unknown_groups
    return {
        "capacity_identity": {
            **identity_counts,
            "blockers": chapter_identity_blockers,
            "blockers_digest": _set_digest(
                {
                    f"{row.get('classification')}::{row.get('path')}::{row.get('reason')}"
                    for row in chapter_identity_blockers
                }
            ),
            "cells": len(rows),
            "cell_state_set_digest": _set_digest(cell_ids),
            "status": "COMPLETE" if identity_complete else "GAP",
        },
        "pedagogical_role_coverage": {
            "missing": len(missing_ids),
            "missing_ids": missing_ids,
            "missing_set_digest": _set_digest(missing_ids),
            "indeterminate": len(indeterminate_ids),
            "indeterminate_ids": indeterminate_ids,
            "indeterminate_set_digest": _set_digest(indeterminate_ids),
            "semantically_unvalidated": len(semantically_unvalidated_ids),
            "semantically_unvalidated_ids": semantically_unvalidated_ids,
            "semantically_unvalidated_set_digest": _set_digest(
                semantically_unvalidated_ids
            ),
            "routed_to_human": len(routed_human),
            "defects": len(routed_defect),
            "defect_ids": sorted(routed_defect),
            "machine_unclassified": len(unclassified_ids),
            "machine_unclassified_ids": unclassified_ids,
            "status": (
                "COMPLETE"
                if rows
                and not missing_ids
                and not indeterminate_ids
                and not routed_defect
                and not unclassified_ids
                else "GAP"
            ),
        },
        "clone_capacity_integrity": {
            "false_copy_count": len(invalid_paths),
            "false_copy_paths": invalid_paths,
            "false_copy_paths_digest": _set_digest(invalid_paths),
            "ambiguous_groups": len(ambiguous_groups),
            "ambiguous_group_ids": sorted(ambiguous_groups),
            "ambiguous_group_ids_digest": _set_digest(ambiguous_groups),
            "unknown_groups": len(unknown_groups),
            "unknown_group_ids": sorted(unknown_groups),
            "unknown_group_ids_digest": _set_digest(unknown_groups),
            "status": "COMPLETE" if clone_complete else "GAP",
        },
    }


def _cross_discipline_truth(
    chapter: str, ledger: dict[str, Any]
) -> dict[str, Any]:
    counts = dict(ledger.get("per_chapter", {}).get(chapter, {}))
    cross = int(counts.get("CROSS_DISCIPLINE_TERMINALE_MATHS", 0))
    unknown = int(counts.get("REQUIRES_EXPLICIT_ADJUDICATION", 0))
    if counts:
        status = "COMPLETE" if not cross and not unknown else "GAP"
    elif chapter.startswith(("1NSI-", "TNSI-")):
        status = "NOT_AUDITED"
    else:
        status = "NOT_APPLICABLE"
    return {
        "cross_discipline_count": cross,
        "unknown": unknown,
        "status": status,
    }


def _course_assembly_truth(
    chapter: str, ownership_map: dict[str, Any]
) -> dict[str, Any]:
    row = ownership_map.get("chapters", {}).get(chapter)
    if not isinstance(row, dict):
        return {
            "foreign": None,
            "duplicated": None,
            "missing": None,
            "ambiguous": None,
            "unknown": None,
            "status": "NOT_AUDITED",
        }
    if row.get("assembly_authority") not in {"CANONICAL_NSI_ASSEMBLER", "CANONICAL_MATHS_ASSEMBLER"}:
        return {
            "foreign": None,
            "duplicated": None,
            "missing": None,
            "ambiguous": None,
            "unknown": None,
            "status": "NOT_AUDITED",
        }
    bodies = row.get("assembled_bodies") or []
    ambiguous = sum(
        1 for body in bodies if body.get("ownership_status") == "AMBIGUOUS"
    )
    unknown = sum(1 for body in bodies if body.get("ownership_status") == "UNKNOWN")
    foreign = len(row.get("foreign_course_bodies") or [])
    duplicated = int(row.get("duplicated_course_body_count") or 0)
    missing = len(row.get("missing_expected_course_capacities") or [])
    complete = not any((foreign, duplicated, missing, ambiguous, unknown))
    return {
        "foreign": foreign,
        "duplicated": duplicated,
        "missing": missing,
        "ambiguous": ambiguous,
        "unknown": unknown,
        "status": "COMPLETE" if complete else "GAP",
    }


def _richness_truth(chapter: str, matrix: dict[str, Any]) -> dict[str, Any]:
    row = matrix.get("chapters", {}).get(chapter)
    if not isinstance(row, dict):
        return {
            "unknown": None,
            "insufficient": None,
            "capacity_identity_blockers": None,
            "excluded_credit_objects": None,
            "capacities_digest": None,
            "status": "NOT_AUDITED",
        }
    unknown = int(row.get("unknown") or 0)
    insufficient = len(row.get("insufficient") or [])
    blockers = len(row.get("capacity_identity_blockers") or [])
    excluded = len(row.get("excluded_credit_objects") or [])
    complete = bool(
        row.get("machine_status") == "COMPLETE"
        and row.get("semantic_validation_status") in {"COMPLETE", "ROUTED_TO_HUMAN"}
        and not unknown
        and not insufficient
        and not blockers
        and not excluded
    )
    return {
        "unknown": unknown,
        "insufficient": insufficient,
        "capacity_identity_blockers": blockers,
        "excluded_credit_objects": excluded,
        "capacities_digest": row.get("capacities_digest"),
        "status": "COMPLETE" if complete else "GAP",
    }


def _ex_co_truth(chapter: str, graph: dict[str, Any]) -> dict[str, Any]:
    relations = [
        row
        for row in graph.get("relations", [])
        if row.get("correction_chapter") == chapter
    ]
    exercises = [
        row
        for row in graph.get("exercise_cardinality", [])
        if row.get("exercise_chapter") == chapter
    ]
    classifications = Counter(
        classification
        for row in relations
        for classification in row.get("classifications", [])
    )
    cardinality = Counter(row.get("classification") for row in exercises)
    # `ANSWER_COVERAGE_ESTABLISHED` est le seul verdict semantique qui ne
    # denonce pas un defaut : le corrige repond a chaque question de son
    # exercice. Il ne vaut que COUVERTURE -- l'exactitude scientifique est
    # prouvee par l'oracle, pas ici -- mais il n'est pas un echec structurel.
    NOT_A_FAILURE = {"UNKNOWN", "ANSWER_COVERAGE_ESTABLISHED"}
    structural_failures = sum(
        count
        for classification, count in classifications.items()
        if classification not in NOT_A_FAILURE
    )
    cardinality_failures = sum(
        count
        for classification, count in cardinality.items()
        if classification != "MATCH"
    )
    unknown = classifications.get("UNKNOWN", 0)
    if relations or exercises:
        status = (
            "COMPLETE"
            if not structural_failures and not cardinality_failures and not unknown
            else "GAP"
        )
    else:
        status = "NOT_AUDITED"
    relation_ids = sorted(
        f"{row.get('correction_id')}->{row.get('exercise_id')}"
        for row in relations
    )
    exercise_ids = sorted(str(row.get("exercise_id")) for row in exercises)
    return {
        "relations": len(relations),
        "exercises": len(exercises),
        "classifications": dict(sorted(classifications.items())),
        "exercise_cardinality": dict(sorted(cardinality.items())),
        "structural_failures": structural_failures,
        "cardinality_failures": cardinality_failures,
        "unknown": unknown,
        "relation_ids_digest": _set_digest(relation_ids),
        "exercise_ids_digest": _set_digest(exercise_ids),
        "status": status,
    }


def _chapter_dir(chapter: str) -> Path | None:
    for root in (MATH_CHAPTERS, NSI_CHAPTERS):
        candidate = root / chapter
        if candidate.is_dir():
            return candidate
    return None


#: L'inventaire nomme le manuel TSPE_2026_2027, l'artefact de couverture
#: TSPE. Sans cette correspondance, onze chapitres paraissent sans programme.
COVERAGE_FILE_BY_MANUAL = {"TSPE_2026_2027": "TSPE"}


def _programme_capacity_tokens(raw: str) -> list[str]:
    """Format autoritaire observé : `/` ou ` + ` séparent des refs exactes."""

    return [token.strip() for token in re.split(r"\s*(?:/|\+)\s*", raw) if token.strip()]


def _programme_chapters(raw: Any) -> set[str]:
    """Exact chapter scopes declared by an official coverage row."""

    return {
        token.strip()
        for token in str(raw or "").split(" + ")
        if token.strip()
    }


def _resolve_programme_token(
    resolver: capacity_identity.CapacityIdentityResolver,
    chapter: str,
    token: str,
) -> str:
    """Resolve an exact alias and require ownership by the requested chapter."""

    resolution = resolver.resolve_collection_alias(token)
    if resolution.identity.chapter != chapter:
        raise capacity_identity.UnresolvedCapacityIdentity(
            f"{chapter}: {token} appartient a {resolution.identity.chapter}"
        )
    return resolution.identity.uid


def _programme(
    chapter: str,
    manual: str,
    resolver: capacity_identity.CapacityIdentityResolver,
    coverage_dir: Path = COVERAGE_DIR,
) -> dict[str, Any]:
    path = coverage_dir / f"{COVERAGE_FILE_BY_MANUAL.get(manual, manual)}.json"
    if not path.is_file():
        return {
            "official_atoms": None,
            "mapped": None,
            "missing": None,
            "wrong_year": None,
            "status": "NO_COVERAGE_ARTIFACT",
        }
    rows = [
        row
        for row in json.loads(path.read_text(encoding="utf-8"))["rows"]
        if chapter in _programme_chapters(row.get("chapter"))
    ]
    mandatory = [row for row in rows if row.get("mandatory") == "YES"]
    mapped: list[dict[str, Any]] = []
    unresolved_mappings: list[str] = []
    resolved_mapping_uids: set[str] = set()
    for row in mandatory:
        raw = str(row.get("contract_capacity") or "").strip()
        tokens = _programme_capacity_tokens(raw)
        row_uids: list[str] = []
        declared_chapters = _programme_chapters(row.get("chapter"))
        try:
            for token in tokens:
                resolution = resolver.resolve_collection_alias(token)
                if resolution.identity.chapter not in declared_chapters:
                    raise capacity_identity.UnresolvedCapacityIdentity(
                        f"{token}: proprietaire {resolution.identity.chapter} "
                        f"hors portee {sorted(declared_chapters)}"
                    )
                if resolution.identity.chapter == chapter:
                    row_uids.append(resolution.identity.uid)
        except capacity_identity.CapacityIdentityError:
            row_uids = []
        if tokens and row_uids:
            mapped.append(row)
            resolved_mapping_uids.update(row_uids)
        else:
            unresolved_mappings.append(
                f"{row.get('atom_id') or row.get('official_atom_id') or '?'}:{raw or 'EMPTY'}"
            )
    wrong_year = [row for row in rows if row.get("wrong_programme_year") is True]
    return {
        "official_atoms": len(rows),
        "mandatory_atoms": len(mandatory),
        "mapped": len(mapped),
        "missing": len(mandatory) - len(mapped),
        "unresolved_mappings": sorted(unresolved_mappings),
        "resolved_mapping_uids": sorted(resolved_mapping_uids),
        "resolved_mapping_uids_digest": _set_digest(resolved_mapping_uids),
        "mapping_format": (
            "une reference exacte, ou plusieurs references exactes separees "
            "par '/' ou ' + ' comme declare dans la matrice officielle"
        ),
        "wrong_year": len(wrong_year),
        "status": (
            "NO_OFFICIAL_ATOMS"
            if not rows
            else "COMPLETE"
            if len(mapped) == len(mandatory) and not wrong_year
            else "GAP"
        ),
    }


def _qcm(
    chapter: str,
    directory: Path,
    resolver: capacity_identity.CapacityIdentityResolver,
) -> dict[str, Any]:
    candidates = sorted((directory / "qcm").glob("*-QCM.json")) if directory else []
    if not candidates:
        return {"present": False, "status": "NO_QCM"}
    if len(candidates) != 1:
        raise ReadinessError(
            f"{chapter}: MULTIPLE_QCM_SOURCES: "
            + ", ".join(path.name for path in candidates)
        )
    document = json.loads(candidates[0].read_text(encoding="utf-8"))
    if document.get("chapitre") != chapter:
        raise ReadinessError(
            f"QCM {candidates[0].relative_to(ROOT)}: chapitre incoherent"
        )
    questions = document.get("questions", [])
    resolved_capacities: list[str] = []
    for question in questions:
        resolution = resolver.resolve(chapter, question.get("capacite"))
        if resolution.rule == capacity_identity.PREREQUISITE:
            raise capacity_identity.UnresolvedCapacityIdentity(
                f"{chapter}/{question.get('id')}: un prerequis ne peut pas "
                "etre credite comme capacite QCM"
            )
        resolved_capacities.append(resolution.identity.local_code)
    keys = Counter(q["correcte"] for q in questions)
    for letter in "ABCD":
        keys.setdefault(letter, 0)
    sequence = [q["correcte"] for q in questions]
    run = longest = 1
    for index in range(1, len(sequence)):
        run = run + 1 if sequence[index] == sequence[index - 1] else 1
        longest = max(longest, run)
    spread = max(keys.values()) - min(keys.values()) if keys else 0
    coverage_gaps = [
        q["id"]
        for q in questions
        if not evidence_v2._diagnostic_coverage(q)["complete"]
    ]
    equivalent = [
        q["id"] for q in questions if evidence_v2._equivalent_option_groups(q)
    ]
    expected_capacities = sorted(
        identity.local_code for identity in resolver.capacities_of(chapter)
    )
    assessed_capacities = sorted(set(resolved_capacities))
    missing_capacities = sorted(set(expected_capacities) - set(assessed_capacities))
    question_identities = sorted(
        f"{question['id']}::{evidence_v2.reconciliation.semantic_question_digest(evidence_v2.reconciliation._semantic_fields_from_source(question))}"
        for question in questions
    )
    return {
        "present": True,
        "questions": len(questions),
        "question_identities": question_identities,
        "question_identities_digest": _set_digest(question_identities),
        "key_distribution": dict(sorted(keys.items())),
        "key_spread": spread,
        "longest_identical_run": longest if questions else 0,
        "distribution_contract_met": bool(
            questions
            and spread <= KEY_SPREAD_MAX
            and longest <= KEY_RUN_MAX
            and all(keys[letter] for letter in "ABCD")
        ),
        "equivalent_option_questions": equivalent,
        "diagnostic_or_remediation_gaps": coverage_gaps,
        "capacities_expected": expected_capacities,
        "capacities_assessed": assessed_capacities,
        "missing_capacities": missing_capacities,
        "missing_capacities_digest": _set_digest(missing_capacities),
        "status": (
            "COMPLETE"
            if questions
            and spread <= KEY_SPREAD_MAX
            and longest <= KEY_RUN_MAX
            and all(keys[letter] for letter in "ABCD")
            and not equivalent
            and not coverage_gaps
            and not missing_capacities
            else "GAP"
        ),
    }


def _diacritics(directory: Path) -> dict[str, Any]:
    if directory is None:
        return {"unambiguous": None, "ambiguous": None, "status": "NO_SOURCE"}
    report = diacritics.scan_paths(sorted(directory.rglob("*.tex")))
    return {
        "unambiguous": report["UNAMBIGUOUS_DIACRITICS_DEBT"],
        "ambiguous": report["AMBIGUOUS_REQUIRING_CONTEXT"],
        "status": "COMPLETE" if report["UNAMBIGUOUS_DIACRITICS_DEBT"] == 0 else "GAP",
    }


def _oracle(directory: Path, dispositions: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verdicts de l'oracle SymPy, lus dans les recus du chapitre.

    `manual_review` n'est pas un echec : c'est le motif unique que rend
    l'oracle quand un objet ne porte pas de bloc VERIFY, et il recouvre des
    situations sans rapport -- un coup de pouce sans calcul, un QCM engendre
    depuis un JSON autoritaire, un cours qui enonce une formule que rien ne
    verifie. Le registre de disposition les route. L'axe est donc satisfait
    quand la machine n'a plus rien a classer (MACHINE_UNCLASSIFIED = 0) et
    qu'aucun objet n'echoue -- jamais quand MANUAL_REVIEW vaut zero, ce qui
    reviendrait a exiger qu'aucune science humaine ne soit requise.

    Ce qui reste a un humain n'est pas efface : il sort dans
    `human_science_required`, et le dossier de relecture le porte.
    """

    if directory is None:
        return {"pass": None, "manual_review": None, "fail": None, "status": "NO_SOURCE"}
    verdicts: Counter = Counter()
    for receipt in sorted((directory / "validations").glob("*.sympy.json")):
        try:
            verdicts[json.loads(receipt.read_text(encoding="utf-8"))["verdict"]] += 1
        except (json.JSONDecodeError, KeyError, OSError):
            verdicts["unreadable"] += 1
    receipts = sum(verdicts.values())
    routed = [
        row
        for row in (dispositions or {}).get("objects", [])
        if row.get("chapter") == directory.name
    ]
    unclassified = verdicts.get("manual_review", 0) - len(routed)
    human = sum(1 for row in routed if row["disposition"] != "AUCUNE_AFFIRMATION_CALCULABLE")
    if not receipts:
        status = "NO_RECEIPTS"
    elif verdicts.get("fail") or verdicts.get("unreadable"):
        status = "GAP"
    elif unclassified:
        status = "GAP"
    else:
        status = "COMPLETE"
    return {
        "pass": verdicts.get("pass", 0),
        "manual_review": verdicts.get("manual_review", 0),
        "machine_unclassified": unclassified,
        "human_science_required": human,
        "fail": verdicts.get("fail", 0) + verdicts.get("unreadable", 0),
        "receipts": receipts,
        "status": status,
    }


def _machine_science_current(source: Path, chapter_dir: Path) -> bool:
    """La preuve scientifique CURRENT de cet objet, ou son absence.

    Trois conditions, toutes necessaires. Le recu doit exister ; il doit
    nommer la source qu'il atteste ET correspondre a son contenu actuel --
    sinon un « pass » d'il y a trois mois certifierait un texte reecrit
    depuis ; et son verdict doit etre `pass`.

    Un objet dont le recu est absent, delie, perime ou orphelin n'est pas
    prouve, quel que soit le `status` inscrit dans sa META.
    """

    receipt_path = chapter_dir / "validations" / f"{source.stem}.sympy.json"
    if not receipt_path.is_file():
        return False
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if receipt.get("verdict") != "pass":
        return False
    declared = receipt.get("source_sha256")
    if not declared:
        return False
    digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
    return digest == declared


def _assessments(
    chapter: str,
    directory: Path,
    resolver: capacity_identity.CapacityIdentityResolver,
) -> dict[str, Any]:
    if directory is None:
        return {"variants": [], "status": "NO_SOURCE"}
    evaluation_dir = directory / "evaluations"
    paths = sorted(evaluation_dir.glob("*.tex")) if evaluation_dir.is_dir() else []
    subjects: dict[str, dict[str, Any]] = {}
    corrections: dict[str, dict[str, Any]] = {}
    invalid_status: list[str] = []
    duplicate_ids: list[str] = []
    seen_ids: set[str] = set()
    # Un STATUT n'est pas une PREUVE. `approved` herite d'une campagne
    # ancienne ne vaut pas mieux qu'un objet `generated` dont l'oracle passe
    # aujourd'hui sur la source courante -- et il vaut moins, puisque rien ne
    # le rattache au contenu actuel. Ce gate lit donc la preuve d'execution
    # CURRENT : recu present, lie a la source courante, verdict pass.
    allowed_statuses = {"verified", "ready", "approved"}
    for path in paths:
        meta = clone_producer.read_meta(path.read_text(encoding="utf-8"))
        object_id = str(meta.get("id") or "").strip()
        object_type = str(meta.get("type_objet") or "").strip()
        if not object_id:
            raise ReadinessError(f"evaluation sans id: {path.relative_to(ROOT)}")
        if meta.get("chapitre") != chapter:
            raise ReadinessError(
                f"evaluation {path.relative_to(ROOT)}: chapitre incoherent"
            )
        capacities = resolver.resolve_meta_codes(chapter, meta)
        if not capacities:
            raise capacity_identity.UnresolvedCapacityIdentity(
                f"{chapter}/{object_id}: aucune capacite d'evaluation"
            )
        if object_id in seen_ids:
            duplicate_ids.append(object_id)
        seen_ids.add(object_id)
        status = str(meta.get("status") or "").strip().lower()
        if not _machine_science_current(path, directory):
            invalid_status.append(object_id)
        if object_type == "evaluation":
            if object_id in subjects:
                duplicate_ids.append(object_id)
            version = str(meta.get("version") or "").strip().upper()
            subjects[object_id] = {"capacities": capacities, "version": version}
        elif object_type in {"corrige_evaluation", "evaluation_corrige"}:
            if object_id in corrections:
                duplicate_ids.append(object_id)
            corrections[object_id] = {
                "evaluation_ref": str(meta.get("evaluation_ref") or "").strip(),
                "capacities": capacities,
            }
        else:
            raise ReadinessError(
                f"{chapter}/{object_id}: type evaluation inconnu {object_type!r}"
            )

    orphan_corrections = sorted(
        correction_id
        for correction_id, correction in corrections.items()
        if correction["evaluation_ref"] not in subjects
    )
    corrected_subjects = {
        correction["evaluation_ref"]
        for correction in corrections.values()
        if correction["evaluation_ref"] in subjects
    }
    subjects_without_correction = sorted(set(subjects) - corrected_subjects)
    target_counts = Counter(
        correction["evaluation_ref"]
        for correction in corrections.values()
        if correction["evaluation_ref"]
    )
    duplicate_correction_targets = sorted(
        target for target, count in target_counts.items() if count > 1
    )
    mismatched_capacity = sorted(
        correction_id
        for correction_id, correction in corrections.items()
        if correction["evaluation_ref"] in subjects
        and tuple(correction["capacities"])
        != tuple(subjects[correction["evaluation_ref"]]["capacities"])
    )
    expected_capacities = {
        identity.local_code for identity in resolver.capacities_of(chapter)
    }
    assessed_capacities = {
        capacity
        for subject in subjects.values()
        for capacity in subject["capacities"]
    }
    missing_capacities = sorted(expected_capacities - assessed_capacities)
    invalid_variants = sorted(
        object_id
        for object_id, subject in subjects.items()
        if subject["version"] not in {"A", "B"}
    )
    variant_counts = Counter(
        subject["version"]
        for subject in subjects.values()
        if subject["version"] in {"A", "B"}
    )
    duplicate_variants = sorted(
        version for version, count in variant_counts.items() if count > 1
    )
    missing_variants = sorted({"A", "B"} - set(variant_counts))
    complete = bool(
        len(subjects) == 2
        and not orphan_corrections
        and not subjects_without_correction
        and not mismatched_capacity
        and not missing_capacities
        and not invalid_status
        and not duplicate_ids
        and not duplicate_correction_targets
        and not invalid_variants
        and not duplicate_variants
        and not missing_variants
    )
    return {
        "subjects": sorted(subjects),
        "corrections": sorted(corrections),
        "orphan_corrections": orphan_corrections,
        "subjects_without_correction": subjects_without_correction,
        "mismatched_capacity": mismatched_capacity,
        "missing_capacities": missing_capacities,
        "invalid_status": sorted(invalid_status),
        "duplicate_ids": sorted(duplicate_ids),
        "duplicate_correction_targets": duplicate_correction_targets,
        "invalid_variants": invalid_variants,
        "duplicate_variants": duplicate_variants,
        "missing_variants": missing_variants,
        "status": "COMPLETE" if complete else "GAP",
    }


def _machine_dimensions_complete(dimensions: dict[str, str]) -> bool:
    """Only unaudited/gap dimensions block; non-applicable is a valid terminal state."""

    return bool(dimensions) and all(
        value in {"COMPLETE", "NO_QCM", "NOT_APPLICABLE"}
        for value in dimensions.values()
    )


def _evidence_routing(
    chapter: str,
    routed: dict[str, list[dict[str, Any]]],
    *,
    expected_question_identities: list[str],
) -> dict[str, Any]:
    entries = routed.get(chapter, [])
    counts = Counter(entry.get("evidence_status") for entry in entries)
    total = len(entries)
    known = {
        "CARRIED_FORWARD_IDENTICAL",
        "MACHINE_RECALCULATED",
        "HUMAN_REVIEW_REQUIRED",
    }
    unknown = sum(value for key, value in counts.items() if key not in known)
    human_review_required = counts.get("HUMAN_REVIEW_REQUIRED", 0)
    observed_identities = sorted(
        f"{entry.get('question_id')}::{entry.get('semantic_question_digest')}"
        for entry in entries
    )
    identity_matches = observed_identities == sorted(expected_question_identities)
    count_matches = total == len(expected_question_identities)
    if not expected_question_identities and not total:
        status = "NO_QCM"
    elif identity_matches and not unknown:
        # Une question reservee a l'humain est un CONSTAT, pas une lacune : la
        # meme regle que l'oracle SymPy, qui est COMPLETE avec 148 sciences
        # humaines requises. Ce qui rougit est l'inconnu.
        status = "COMPLETE"
    else:
        status = "GAP"
    return {
        "questions_routed": total,
        "questions_expected": len(expected_question_identities),
        "count_matches_qcm": count_matches,
        "identity_set_matches_qcm": identity_matches,
        "evidence_question_identities": observed_identities,
        "evidence_question_identities_digest": _set_digest(observed_identities),
        "carried_forward": counts.get("CARRIED_FORWARD_IDENTICAL", 0),
        "machine_recalculated": counts.get("MACHINE_RECALCULATED", 0),
        "human_review_required": human_review_required,
        "unknown": unknown,
        "status": status,
    }


def _declared_debt(
    queue: dict[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    queue = queue or human_queue_producer.build_queue()
    if queue.get("unknown_count") != 0:
        raise ReadinessError("file humaine avec inconnues")
    if queue.get("status") not in {"HUMAN_REVIEW_ACTION_REQUIRED", "CLOSED"}:
        raise ReadinessError("statut de file humaine inconnu")
    by_chapter: dict[str, list[dict[str, Any]]] = {}
    seen: set[str] = set()
    for item in queue.get("items") or []:
        if item.get("release_blocking") is not True:
            raise ReadinessError(f"dette humaine non bloquante: {item.get('item_id')}")
        unit_ids = item.get("unit_ids") or []
        if item.get("count") != len(unit_ids) or item.get("set_digest") != _set_digest(unit_ids):
            raise ReadinessError(f"file humaine incohérente: {item.get('item_id')}")
        overlap = seen & set(unit_ids)
        if overlap:
            raise ReadinessError(f"dette humaine double-comptée: {sorted(overlap)[:3]}")
        seen.update(unit_ids)
        routed: set[str] = set()
        for chapter, bucket in sorted((item.get("units_by_chapter") or {}).items()):
            chapter_units = bucket.get("unit_ids") or []
            if (
                bucket.get("count") != len(chapter_units)
                or bucket.get("set_digest") != _set_digest(chapter_units)
                or not set(chapter_units) <= set(unit_ids)
            ):
                raise ReadinessError(
                    f"routage humain incohérent: {item.get('item_id')}:{chapter}"
                )
            if routed & set(chapter_units):
                raise ReadinessError(
                    f"dette humaine double-routée: {item.get('item_id')}:{chapter}"
                )
            routed.update(chapter_units)
            provenance_counts: dict[str, int]
            if item.get("item_id") in {"TSPE_GEO_NEW_40", "NSI_COUPLED_NEW_32"}:
                provenance_counts = {"NEW_AUTHORED_UNREVIEWED": len(chapter_units)}
            elif item.get("item_id") in {
                "TSPE_GEO_REWRITTEN_STALE_APPROVAL_5",
            }:
                provenance_counts = {
                    "REWRITTEN_PREVIOUSLY_APPROVED_STALE": len(chapter_units)
                }
            elif (
                item.get("item_id")
                == "NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4"
            ):
                provenance_counts = {
                    "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED": len(chapter_units)
                }
            else:
                provenance_counts = {str(item.get("category")): len(chapter_units)}
            by_chapter.setdefault(chapter, []).append(
                {
                    "ledger_id": item["item_id"],
                    "category": item.get("category"),
                    "count": len(chapter_units),
                    "unit_ids_digest": _set_digest(chapter_units),
                    "provenance_counts": dict(sorted(provenance_counts.items())),
                    "release_blocking": True,
                }
            )
        if routed != set(unit_ids):
            raise ReadinessError(f"file humaine non entièrement routée: {item.get('item_id')}")
    expected_total = int((queue.get("counts") or {}).get("TOTAL", -1))
    if len(seen) != expected_total:
        raise ReadinessError("total file humaine incohérent")
    return by_chapter


def _human_closure_status(
    human: Mapping[str, Any], declared_review_debt: list[dict[str, Any]]
) -> str:
    return (
        "CLOSED"
        if human.get("review_a") == "APPROVED"
        and human.get("review_b") == "APPROVED"
        and human.get("qcm_human_approval") in {"APPROVED", "SATISFIED", "NOT_APPLICABLE"}
        and human.get("publication_approval") is True
        and not any(
            debt.get("release_blocking") is True and int(debt.get("count", 0)) > 0
            for debt in declared_review_debt
        )
        else "PENDING"
    )


def _risk_score(row: dict[str, Any]) -> int:
    """Priorite de traitement. Plus haut = plus risque."""

    score = 0
    programme = row["programme"]
    if programme.get("status") != "COMPLETE":
        score += 40 * max(1, programme.get("missing") or 0)
    score += 60 * (programme.get("wrong_year") or 0)
    qcm = row["qcm"]
    if qcm.get("present"):
        if not qcm["distribution_contract_met"]:
            score += 10 + 3 * qcm["key_spread"]
            if min(qcm["key_distribution"].values()) == 0:
                score += 15
        score += 12 * len(qcm["diagnostic_or_remediation_gaps"])
        score += 25 * len(qcm["equivalent_option_questions"])
        score += 35 * len(qcm.get("missing_capacities") or [])
    else:
        score += 30
    score += 2 * (row["diacritics"].get("unambiguous") or 0)
    oracle = row["oracle"]
    score += 50 * (oracle.get("fail") or 0)
    score += 30 * (oracle.get("manual_review") or 0)
    if oracle.get("status") == "NO_RECEIPTS":
        score += 50
    if row["assessments"].get("status") == "GAP":
        score += 20
    evidence = row.get("evidence_routing", {})
    score += 45 * (evidence.get("human_review_required") or 0)
    if evidence.get("identity_set_matches_qcm") is False:
        score += 80
    cross = row.get("cross_discipline_content", {})
    score += 100 * (cross.get("cross_discipline_count") or 0)
    score += 70 * (cross.get("unknown") or 0)
    assembly = row.get("course_assembly_truth", {})
    score += 90 * (assembly.get("foreign") or 0)
    score += 50 * (assembly.get("duplicated") or 0)
    score += 70 * (assembly.get("ambiguous") or 0)
    score += 80 * (assembly.get("unknown") or 0)
    ex_co = row.get("ex_co_graph", {})
    score += 80 * (ex_co.get("structural_failures") or 0)
    score += 70 * (ex_co.get("cardinality_failures") or 0)
    score += 50 * (ex_co.get("unknown") or 0)
    richness = row.get("pedagogical_richness", {})
    score += 70 * (richness.get("insufficient") or 0)
    score += 60 * (richness.get("unknown") or 0)
    score += 50 * (richness.get("capacity_identity_blockers") or 0)
    score += 40 * (richness.get("excluded_credit_objects") or 0)
    role_coverage = row.get("pedagogical_role_coverage", {})
    score += 80 * (role_coverage.get("missing") or 0)
    score += 45 * (role_coverage.get("indeterminate") or 0)
    score += 45 * (role_coverage.get("semantically_unvalidated") or 0)
    clone_integrity = row.get("clone_capacity_integrity", {})
    score += 60 * (clone_integrity.get("false_copy_count") or 0)
    score += 50 * (
        (clone_integrity.get("ambiguous_groups") or 0)
        + (clone_integrity.get("unknown_groups") or 0)
    )
    if row["human"]["review_a"] != "PENDING_UNASSIGNED" or row["human"]["review_b"] != "PENDING_UNASSIGNED":
        score += 0
    return score


_POLICY_CACHE: dict[str, Any] = {}


def _policy() -> dict[str, Any]:
    if not _POLICY_CACHE:
        _POLICY_CACHE.update(governance.load_policy(ROOT))
    return _POLICY_CACHE


def build_matrix(
    *,
    clone_ledger: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # Les deux producteurs sont recalculés dans le même appel. Joindre deux
    # JSON historiques permettrait à un ancien resolver d'alimenter un gate
    # courant ; `_capacity_truth` vérifie en plus l'égalité de leurs sets de
    # crédit invalides et indéterminés.
    capacity_resolver = capacity_identity.CapacityIdentityResolver.from_corpora()
    clone_ledger = clone_ledger or clone_producer.build_ledger()
    coverage = coverage or coverage_producer.build_coverage(
        resolver=capacity_resolver,
        clone_ledger=clone_ledger,
    )
    alias_map = capacity_identity.build_alias_map(capacity_resolver)
    cross_discipline = cross_discipline_producer.build_ledger()
    course_ownership = course_truth_producer.build_map()
    ex_co_graph = ex_co_producer.build_graph(
        resolver=capacity_resolver,
        clone_ledger=clone_ledger,
        cross_discipline_ledger=cross_discipline,
    )
    richness = richness_producer.build_collection(
        resolver=capacity_resolver,
        clone_ledger=clone_ledger,
    )
    human_queue = human_queue_producer.build_queue()
    dispositions = disposition_producer.build_ledger()
    cross_path = ROOT / "audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json"
    course_path = ROOT / "audit/COURSE_BODY_OWNERSHIP_MAP.json"
    ex_co_path = ROOT / "audit/EX_CO_GRAPH.json"
    # Le registre d'alignement appelle lui-meme `build_coverage()` : le
    # recalculer ici creerait une dependance circulaire. Il est donc lu dans
    # son artefact, et sa fraicheur est garantie par son propre `--check` et
    # par le fait qu'il porte le sha256 du corps de chaque objet -- il perime
    # des que le contenu bouge.
    alignment_ledger = json.loads(
        SEMANTIC_ALIGNMENT_LEDGER.read_text(encoding="utf-8")
    )
    for name, current, path in (
        ("NSI_CROSS_DISCIPLINE_CONTENT_LEDGER", cross_discipline, cross_path),
        ("COURSE_BODY_OWNERSHIP_MAP", course_ownership, course_path),
        ("EX_CO_GRAPH", ex_co_graph, ex_co_path),
        ("CHAPTER_RICHNESS_MATRIX", richness, RICHNESS_MATRIX),
        (
            "HUMAN_REVIEW_QUEUE",
            human_queue,
            ROOT / "audit/HUMAN_REVIEW_QUEUE.json",
        ),
    ):
        committed = json.loads(path.read_text(encoding="utf-8"))
        if _payload_digest(current) != _payload_digest(committed):
            raise ReadinessError(f"{name} stale")
    input_digests = {
        "capacity_alias_map": alias_map["alias_digest"],
        "clone_ledger": _payload_digest(clone_ledger),
        "true_coverage": _payload_digest(coverage),
        "cross_discipline_ledger": _payload_digest(cross_discipline),
        "course_body_ownership_map": _payload_digest(course_ownership),
        "ex_co_graph": _payload_digest(ex_co_graph),
        "chapter_richness": _payload_digest(richness),
        "semantic_alignment_ledger": _payload_digest(alignment_ledger),
        "human_review_queue": _payload_digest(human_queue),
        "official_programme_sources": _set_digest(
            {
                f"{path.relative_to(ROOT)}::{hashlib.sha256(path.read_bytes()).hexdigest()}"
                for path in (
                    ROOT / "audit/OFFICIAL_PROGRAM_ATOMS_2026_2027.json",
                    *(COVERAGE_DIR / f"{manual}.json" for manual in ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")),
                )
            }
        ),
    }
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    evidence = evidence_v2.build_evidence()
    evidence_path = ROOT / "audit" / "QCM_INDEPENDENT_EVIDENCE_V2.json"
    committed_evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if _payload_digest(evidence) != _payload_digest(committed_evidence):
        raise ReadinessError("QCM_INDEPENDENT_EVIDENCE_V2 stale")
    routed: dict[str, list[dict[str, Any]]] = {}
    for entry in evidence["questions"]:
        routed.setdefault(entry["chapter"], []).append(entry)
    declared_debt = _declared_debt(human_queue)

    rows: list[dict[str, Any]] = []
    for manual_id, manual in sorted(inventory["manuals"].items()):
        for chapter in sorted(manual["chapters"]):
            directory = _chapter_dir(chapter)
            try:
                scope = governance.build_scope(chapter, ROOT)
                object_count = scope.object_count
                object_digest = scope.object_set_digest
                unassembled = scope.unassembled_object_ids()
            except Exception as error:  # noqa: BLE001 - un chapitre non gouverne se voit
                object_count = None
                object_digest = None
                unassembled = [f"SCOPE_ERROR:{type(error).__name__}"]
            state = {}
            try:
                state = governance.evaluate_state(chapter, _policy(), ROOT)
            except Exception:  # noqa: BLE001 - un chapitre non gouverne se voit
                state = {}
            qcm_summary = _qcm(chapter, directory, capacity_resolver)
            row = {
                "manual": manual_id,
                "chapter": chapter,
                "object_count": object_count,
                "object_set_digest": object_digest,
                "unassembled_object_ids": unassembled,
                "programme": _programme(
                    chapter, manual_id, capacity_resolver
                ),
                "oracle": _oracle(directory, dispositions),
                "qcm": qcm_summary,
                "evidence_routing": _evidence_routing(
                    chapter,
                    routed,
                    expected_question_identities=list(
                        qcm_summary.get("question_identities") or []
                    ),
                ),
                "diacritics": _diacritics(directory),
                "assessments": _assessments(
                    chapter, directory, capacity_resolver
                ),
                "declared_review_debt": declared_debt.get(chapter, []),
                "human": {
                    "review_a": (state.get("review_a") or {}).get("state", "UNKNOWN"),
                    "review_b": (state.get("review_b") or {}).get("state", "UNKNOWN"),
                    "qcm_human_approval": state.get("qcm_human_approval", "UNKNOWN"),
                    "publication_approval": state.get("publication_approval", False),
                },
            }
            capacity_truth = _capacity_truth(
                chapter, coverage, clone_ledger, alignment=alignment_ledger
            )
            row.update(capacity_truth)
            row["cross_discipline_content"] = _cross_discipline_truth(
                chapter, cross_discipline
            )
            row["course_assembly_truth"] = _course_assembly_truth(
                chapter, course_ownership
            )
            row["ex_co_graph"] = _ex_co_truth(chapter, ex_co_graph)
            row["pedagogical_richness"] = _richness_truth(chapter, richness)
            row["machine_dimensions"] = {
                "programme": row["programme"]["status"],
                "oracle": row["oracle"]["status"],
                "qcm": row["qcm"].get("status", "NO_QCM"),
                "diacritics": row["diacritics"]["status"],
                "assessments": row["assessments"]["status"],
                "evidence_routing": row["evidence_routing"]["status"],
                "capacity_identity": row["capacity_identity"]["status"],
                "pedagogical_role_coverage": row[
                    "pedagogical_role_coverage"
                ]["status"],
                "clone_capacity_integrity": row["clone_capacity_integrity"][
                    "status"
                ],
                "cross_discipline_content": row["cross_discipline_content"][
                    "status"
                ],
                "course_assembly_truth": row["course_assembly_truth"]["status"],
                "ex_co_graph": row["ex_co_graph"]["status"],
                "pedagogical_richness": row["pedagogical_richness"]["status"],
            }
            row["vertical_machine_status"] = (
                "MACHINE_REVIEW_COMPLETE"
                if _machine_dimensions_complete(row["machine_dimensions"])
                and not unassembled
                else "INCOMPLETE"
            )
            row["human_closure_status"] = _human_closure_status(
                row["human"], row["declared_review_debt"]
            )
            row["risk_score"] = _risk_score(row)
            rows.append(row)

    complete = [r for r in rows if r["vertical_machine_status"] == "MACHINE_REVIEW_COMPLETE"]
    return {
        "artifact_type": "publish_readiness_chapter_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_publish_readiness_chapter_matrix.py",
        "approves_nothing": True,
        "input_digests": input_digests,
        "manuals": sorted(inventory["manuals"]),
        "counts": {
            "manuals": len(inventory["manuals"]),
            "chapters": len(rows),
            "machine_review_complete": len(complete),
            "machine_review_incomplete": len(rows) - len(complete),
            "human_closed": sum(1 for r in rows if r["human_closure_status"] == "CLOSED"),
        },
        "ALL_MACHINE_CONTENT_COMPLETE": len(complete) == len(rows),
        "next_by_risk": [
            {"chapter": r["chapter"], "manual": r["manual"], "risk_score": r["risk_score"]}
            for r in sorted(
                (r for r in rows if r["vertical_machine_status"] != "MACHINE_REVIEW_COMPLETE"),
                key=lambda item: (-item["risk_score"], item["chapter"]),
            )
        ],
        "chapters": rows,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    counts = payload["counts"]
    lines = [
        "<!-- generated by build_publish_readiness_chapter_matrix.py -->",
        "",
        "# Registre de campagne — lecture par chapitre",
        "",
        f"- Manuels : {counts['manuals']}",
        f"- Chapitres : {counts['chapters']}",
        f"- Machine review complete : {counts['machine_review_complete']}",
        f"- Machine review incomplete : {counts['machine_review_incomplete']}",
        f"- ALL_MACHINE_CONTENT_COMPLETE : {payload['ALL_MACHINE_CONTENT_COMPLETE']}",
        "",
        "| manuel | chapitre | objets | programme | couverture rôles | clones | EX/CO | cross-discipline | assemblage cours | oracle | QCM | diacritiques | evals | statut machine | risque |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in payload["chapters"]:
        dims = row["machine_dimensions"]
        lines.append(
            f"| {row['manual']} | {row['chapter']} | {row['object_count']} "
            f"| {dims['programme']} | {dims['pedagogical_role_coverage']} "
            f"| {dims['clone_capacity_integrity']} | {dims['ex_co_graph']} "
            f"| {dims['cross_discipline_content']} | {dims['course_assembly_truth']} "
            f"| {dims['oracle']} | {dims['qcm']} "
            f"| {dims['diacritics']} | {dims['assessments']} "
            f"| {row['vertical_machine_status']} | {row['risk_score']} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_matrix()
    rendered_json = render_json(payload)
    rendered_md = render_md(payload)
    if args.check:
        stale = [
            str(t.relative_to(ROOT))
            for t, r in ((JSON_TARGET, rendered_json), (MD_TARGET, rendered_md))
            if not t.is_file() or t.read_text(encoding="utf-8") != r
        ]
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print(
            f"PASS matrice: {payload['counts']['chapters']} chapitres, "
            f"{payload['counts']['machine_review_complete']} machine-complets"
        )
        return 0
    JSON_TARGET.write_text(rendered_json, encoding="utf-8")
    MD_TARGET.write_text(rendered_md, encoding="utf-8")
    print(
        f"wrote {JSON_TARGET.name}: {payload['counts']['chapters']} chapitres, "
        f"{payload['counts']['machine_review_complete']} machine-complets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
