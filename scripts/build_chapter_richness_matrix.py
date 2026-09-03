#!/usr/bin/env python3
"""Richesse pedagogique d'un chapitre, mesuree en occasions et en gestes.

Le P0 de clonage a montre ce que vaut un compteur de fichiers : cinquante
exercices dont sept seulement etaient les copies de personne. Compter les
fichiers mesure le volume, pas ce que l'eleve peut faire.

Ce producteur mesure autre chose. Pour chaque capacite du contrat il recense
les OCCASIONS distinctes de mobilisation -- pratique ciblee, evaluation, QCM,
remediation, methode -- et les GESTES de raisonnement que ces occasions
demandent. Les gestes ne sont pas devines : chaque exercice les declare dans
son META, ou ils restent relisibles et contestables.

La regle de statut depend de la NATURE de la capacite, jamais d'un quota :

* une capacite composite ou de synthese exige au moins deux gestes distincts,
  parce qu'un seul chemin de raisonnement ne prepare pas au transfert ;
* une capacite procedurale ou de support est servie des lors qu'elle dispose
  d'une pratique ciblee, d'une remediation et d'une methode.

Exiger « deux exercices par capacite » recreerait le remplissage qu'on repare.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
CHAPTER_ROOTS = (CHAPTERS, ROOT / "NSI" / "chapitres")
CLONE_LEDGER = ROOT / "audit" / "P0_CONTENT_CLONE_LEDGER.json"
COLLECTION_TARGET = ROOT / "audit" / "CHAPTER_RICHNESS_MATRIX.json"

#: Nature d'une capacite, deduite de son libelle contractuel. Elle commande
#: l'exigence appliquee : on ne demande pas la meme chose a « lire des
#: coordonnees » et a « resoudre des problemes de configuration ».
COMPOSITE_MARKERS = (
    "résoudre des problèmes",
    "resoudre des problemes",
    "étudier des problèmes",
    "etudier des problemes",
    "traduire un problème",
    "traduire un probleme",
)
CONCEPTUAL_MARKERS = ("démontrer", "demontrer", "déterminer sur une figure si")

#: Une capacite composite ou conceptuelle demande plus d'un chemin de
#: raisonnement ; les autres sont servies par une chaine complete.
MULTI_GESTURE_TYPES = {"COMPOSITE_REASONING", "SYNTHESIS_HEAVY"}


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _identity_module():
    spec = importlib.util.spec_from_file_location(
        "capacity_identity_richness", ROOT / "scripts/capacity_identity.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def capacity_type(libelle: str) -> str:
    lowered = libelle.lower()
    if any(marker in lowered for marker in COMPOSITE_MARKERS):
        return "COMPOSITE_REASONING"
    if any(marker in lowered for marker in CONCEPTUAL_MARKERS):
        return "CONCEPTUAL"
    if "lire" in lowered or "représenter" in lowered or "representer" in lowered:
        return "ATOMIC_SUPPORT"
    return "PROCEDURAL"


def _path_key(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _richness_digest(
    capacities: dict[str, Any],
    capacity_identity_blockers: list[dict[str, Any]],
    excluded_credit_objects: list[dict[str, str]],
) -> str:
    payload = {
        "capacities": capacities,
        "capacity_identity_blockers": capacity_identity_blockers,
        "excluded_credit_objects": excluded_credit_objects,
    }
    return "sha256:" + hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _is_capacity_identity_error(error: Exception) -> bool:
    return type(error).__name__ in {
        "CapacityIdentityError",
        "AmbiguousCapacityIdentity",
        "UnresolvedCapacityIdentity",
    }


def machine_status_of(matrix: dict[str, Any]) -> str:
    """La dimension est-elle complete du point de vue de la MACHINE ?

    Meme regle que l'oracle SymPy : la dimension est satisfaite quand la
    machine n'a plus rien a classer et qu'aucun defaut ne subsiste -- jamais
    quand plus aucune science humaine n'est requise, ce qui reviendrait a
    exiger qu'un manuel se relise tout seul.

    Quatre constats la rougissent, et aucun n'est absorbe par le routage :

    `insufficient`
        une capacite n'offre pas les occasions pedagogiques requises. C'est un
        defaut declaratif, mesure, et il reste bloquant.

    `capacity_identity_blockers`
        la capacite servie n'est pas resolue. On ne route pas vers un humain
        une cellule dont la machine ignore ce qu'elle sert.

    `excluded_credit_objects`
        un objet a ete ecarte du credit ; sa richesse n'est pas mesuree.

    `unknown`
        il reste des capacites sans disposition terminale.
    """

    if matrix.get("insufficient"):
        return "GAP"
    if matrix.get("capacity_identity_blockers"):
        return "GAP"
    if matrix.get("excluded_credit_objects"):
        return "GAP"
    if int(matrix.get("unknown") or 0):
        return "GAP"
    return "COMPLETE"


def build_matrix(
    chapter: str,
    *,
    chapter_root: Path | None = None,
    resolver=None,
    clone_ledger: dict[str, Any] | None = None,
) -> dict[str, Any]:
    clone = _clone_module()
    identity = _identity_module()
    roots = (chapter_root,) if chapter_root is not None else CHAPTER_ROOTS
    base = next((root / chapter for root in roots if (root / chapter).is_dir()), None)
    if base is None:
        raise FileNotFoundError(f"chapitre absent: {chapter}")
    resolver = resolver or identity.CapacityIdentityResolver.from_corpora(roots)
    clone_ledger = clone_ledger or json.loads(CLONE_LEDGER.read_text(encoding="utf-8"))
    invalid_credit = set(clone_ledger["objects_on_invalid_credit"])
    indeterminate_credit = set(clone_ledger["objects_with_indeterminate_credit"])
    if invalid_credit & indeterminate_credit:
        raise ValueError("clone credits invalides et indetermines non disjoints")
    contract = yaml.safe_load((base / "contrat.yaml").read_text(encoding="utf-8"))
    labels = {str(c["code"]): str(c["libelle_eleve"]) for c in contract["capacites"]}
    capacities = {
        capacity.local_code: labels[capacity.local_code]
        for capacity in resolver.capacities_of(chapter)
    }

    def meta(path: Path) -> dict[str, Any]:
        return clone.read_meta(path.read_text(encoding="utf-8"))

    capacity_identity_blockers: list[dict[str, Any]] = []
    excluded_credit_objects: list[dict[str, str]] = []
    excluded_paths: set[str] = set()

    def credit_allowed(path: Path) -> bool:
        key = _path_key(path)
        state = (
            "INVALID"
            if key in invalid_credit
            else "INDETERMINATE"
            if key in indeterminate_credit
            else None
        )
        if state and key not in excluded_paths:
            excluded_paths.add(key)
            excluded_credit_objects.append({"path": key, "state": state})
        return state is None

    def resolve_meta(path: Path, entry: dict[str, Any]) -> tuple[str, ...]:
        try:
            return resolver.resolve_meta_codes(chapter, entry)
        except Exception as exc:  # une instance peut venir d'un module charge separement
            if not _is_capacity_identity_error(exc):
                raise
            capacity_identity_blockers.append(
                {
                    "path": _path_key(path),
                    "object_id": str(entry.get("id") or ""),
                    "reason": str(exc),
                }
            )
            return ()

    practice: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    gestures: dict[str, set[str]] = collections.defaultdict(set)
    dominant = collections.Counter()
    for path in sorted((base / "exercices").glob("*.tex")):
        entry = meta(path)
        declared = resolve_meta(path, entry)
        if not declared or not credit_allowed(path):
            continue
        per_question = entry.get("capacites_par_question") or {}
        per_question_gestures = entry.get("gestes_par_question") or {}
        served_by_code: dict[str, list[str] | None] = {}
        try:
            for code in declared:
                served_by_code[code] = [
                    question
                    for question, raw_codes in per_question.items()
                    if code in resolver.resolve_codes(chapter, raw_codes)
                ] or None
        except Exception as exc:
            if not _is_capacity_identity_error(exc):
                raise
            capacity_identity_blockers.append(
                {
                    "path": _path_key(path),
                    "object_id": str(entry.get("id") or ""),
                    "reason": str(exc),
                }
            )
            continue
        for code in declared:
            served = served_by_code[code]
            practice[code].append(
                {
                    "id": entry["id"],
                    "parcours": entry.get("parcours"),
                    "duree_min": entry.get("duree_min"),
                    "questions_for_this_capacity": served,
                }
            )
            # Un exercice multi-capacites ne transmet pas TOUS ses gestes a
            # CHACUNE de ses capacites : ce serait le credit global que le
            # contrat interdit. Quand la sous-question est declaree, seul le
            # geste de cette sous-question compte pour cette capacite.
            if served and per_question_gestures:
                for question in served:
                    gestures[code] |= set(per_question_gestures.get(question, []))
            else:
                gestures[code] |= set(entry.get("gestes") or [])
        for gesture in entry.get("gestes") or []:
            dominant[gesture] += 1

    assessed: dict[str, list[str]] = collections.defaultdict(list)
    for path in sorted((base / "evaluations").glob("*.tex")):
        entry = meta(path)
        if entry.get("type_objet") != "evaluation":
            continue
        declared = resolve_meta(path, entry)
        if not declared or not credit_allowed(path):
            continue
        for code in declared:
            assessed[code].append(entry["id"])

    qcm_sources = sorted((base / "qcm").glob("*-QCM.json"))
    if len(qcm_sources) > 1:
        raise ValueError(f"{chapter}: MULTIPLE_QCM_SOURCES")
    qcm_file = qcm_sources[0] if qcm_sources else None
    qcm = collections.Counter()
    if qcm_file:
        document = json.loads(qcm_file.read_text(encoding="utf-8"))
        if document.get("chapitre") != chapter:
            raise ValueError(f"{chapter}: chapitre QCM incoherent")
        for question in document["questions"]:
            try:
                resolution = resolver.resolve(chapter, question.get("capacite"))
                if resolution.rule == identity.PREREQUISITE:
                    raise identity.UnresolvedCapacityIdentity(
                        f"{chapter}/{question.get('id')}: prerequis utilise comme QCM"
                    )
            except Exception as exc:
                if not _is_capacity_identity_error(exc):
                    raise
                capacity_identity_blockers.append(
                    {
                        "path": f"{_path_key(qcm_file)}#{question.get('id')}",
                        "object_id": str(question.get("id") or ""),
                        "reason": str(exc),
                    }
                )
                continue
            qcm[resolution.identity.local_code] += 1

    remediation = collections.Counter()
    for path in (base / "remediation").glob("*.tex"):
        entry = meta(path)
        declared = resolve_meta(path, entry)
        if not declared or not credit_allowed(path):
            continue
        for code in declared:
            remediation[code] += 1
    methods = collections.Counter()
    for path in (base / "methodes").glob("*.tex"):
        entry = meta(path)
        declared = resolve_meta(path, entry)
        if not declared or not credit_allowed(path):
            continue
        for code in declared:
            methods[code] += 1

    rows: dict[str, Any] = {}
    for code, libelle in capacities.items():
        kind = capacity_type(libelle)
        paths = sorted(gestures[code])
        opportunities = {
            "targeted_practice": len(practice[code]),
            "assessment": len(assessed[code]),
            "qcm": qcm[code],
            "remediation": remediation[code],
            "method": methods[code],
        }
        missing = []
        if not practice[code]:
            missing.append("NO_TARGETED_PRACTICE")
        if not remediation[code]:
            missing.append("NO_REMEDIATION")
        if not methods[code]:
            missing.append("NO_METHOD")
        if not qcm[code]:
            missing.append("NO_QCM")
        if kind in MULTI_GESTURE_TYPES and len(paths) < 2:
            missing.append("SINGLE_REASONING_PATH_FOR_COMPOSITE_CAPACITY")
        declarative_status = "SUFFICIENT" if not missing else "INSUFFICIENT"
        status = (
            "CANDIDATE_NON_SEMANTIC"
            if declarative_status == "SUFFICIENT"
            else "INSUFFICIENT"
        )
        rows[code] = {
            "libelle_eleve": libelle,
            "capacity_type": kind,
            "reasoning_paths": paths,
            "distinct_opportunities": sum(1 for v in opportunities.values() if v),
            "opportunities": opportunities,
            "practice": practice[code],
            "assessed_by": assessed[code],
            "missing_function": missing,
            "declarative_status": declarative_status,
            "semantic_validation_status": "UNKNOWN",
            "status": status,
        }

    all_paths = sorted({g for gs in gestures.values() for g in gs})
    declarative_diversity_status = (
        "SUFFICIENT"
        if len(all_paths) >= 4
        and max(dominant.values(), default=0) <= 0.5 * sum(dominant.values())
        else "INSUFFICIENT"
    )
    capacity_identity_blockers = sorted(
        capacity_identity_blockers,
        key=lambda row: (row["path"], row["object_id"], row["reason"]),
    )
    excluded_credit_objects = sorted(
        excluded_credit_objects, key=lambda row: (row["path"], row["state"])
    )
    statuses = collections.Counter(row["status"] for row in rows.values())
    payload = {
        "artifact_type": "chapter_richness_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_chapter_richness_matrix.py",
        "chapter": chapter,
        "rule": (
            "la richesse se mesure en occasions distinctes et en gestes de "
            "raisonnement declares ; jamais en nombre de fichiers"
        ),
        "capacities": rows,
        "diversity_profile": dict(sorted(dominant.items(), key=lambda kv: -kv[1])),
        "distinct_reasoning_paths": all_paths,
        "declarative_diversity_status": declarative_diversity_status,
        "diversity_status": (
            "CANDIDATE_NON_SEMANTIC"
            if declarative_diversity_status == "SUFFICIENT"
            else "INSUFFICIENT"
        ),
        "semantic_validation_status": "ROUTED_TO_HUMAN",
        "machine_status": None,  # renseigne ci-dessous par machine_status_of
        "capacity_identity_blockers": capacity_identity_blockers,
        "excluded_credit_objects": excluded_credit_objects,
        "counts": dict(statuses),
        "insufficient": sorted(
            c for c, r in rows.items() if r["declarative_status"] != "SUFFICIENT"
        ),
        # Ce que la machine ne sait pas classer -- et non ce qu'elle ne sait pas
        # PROUVER. La distinction est celle de l'oracle : `unknown` compte les
        # capacites sans disposition terminale, `routed_to_human` celles dont la
        # mesure declarative est faite et dont il ne reste qu'un jugement
        # pedagogique. Une capacite non resolue n'est pas routable : elle reste
        # inconnue, et elle rougit.
        "unknown": len(capacity_identity_blockers),
        "routed_to_human": len(rows),
        "capacities_digest": _richness_digest(
            rows, capacity_identity_blockers, excluded_credit_objects
        ),
    }
    payload["machine_status"] = machine_status_of(payload)
    return payload


def build_collection(*, resolver=None, clone_ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    identity = _identity_module()
    resolver = resolver or identity.CapacityIdentityResolver.from_corpora(CHAPTER_ROOTS)
    clone_ledger = clone_ledger or json.loads(CLONE_LEDGER.read_text(encoding="utf-8"))
    chapters = {
        chapter: build_matrix(
            chapter,
            resolver=resolver,
            clone_ledger=clone_ledger,
        )
        for chapter in resolver.chapters
    }
    unknown = sum(int(row["unknown"]) for row in chapters.values())
    incomplete = sorted(
        chapter
        for chapter, row in chapters.items()
        if row.get("machine_status") != "COMPLETE"
    )
    return {
        "artifact_type": "collection_chapter_richness_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_chapter_richness_matrix.py",
        "semantic_claim": (
            "les declarations fournissent une mesure candidate; aucune richesse "
            "semantique n'est complete sans preuve separee"
        ),
        "chapter_count": len(chapters),
        "capacity_count": sum(len(row["capacities"]) for row in chapters.values()),
        "unknown": unknown,
        "incomplete_chapters": incomplete,
        "machine_status": "COMPLETE" if not incomplete else "GAP",
        "chapters_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(
                chapters,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "chapters": chapters,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)

    payload = build_matrix(arguments.chapter) if arguments.chapter else build_collection()
    target = (
        ROOT / f"audit/CHAPTER_RICHNESS_{arguments.chapter}.json"
        if arguments.chapter
        else COLLECTION_TARGET
    )
    rendered = render(payload)
    if arguments.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != rendered:
            print(f"STALE: {target.relative_to(ROOT)}")
            return 1
        return 0
    target.write_text(rendered, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
