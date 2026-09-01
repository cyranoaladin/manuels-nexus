#!/usr/bin/env python3
"""Couverture pedagogique REELLE, une fois le faux credit retire.

Un objet ne credite une capacite que si son CORPS la sert. Le seul META ne
donne aucun credit : c'est precisement ce que le P0 de clonage a exploite --
dix-sept fiches identiques declarees C1 a C16 creditaient seize capacites
alors qu'une seule, C7, etait reellement traitee.

Ce producteur retire logiquement les credits invalides recenses par
`build_p0_content_clone_ledger.py`, puis mesure ce qui reste, capacite par
capacite et role par role. Il n'enleve aucun fichier.

TROIS PIEGES EVITES.

Identite des capacites. Un objet ne declare pas toujours le code local du
contrat : il declare parfois la reference officielle du programme
(`P-ALGO-01A`) ou la forme qualifiee (`1NSI-ALGO-PARCOURS-TRIS-C1`). Les
rapprocher par extraction de jeton lisait `TSPE-CONCLGN-C1` comme `C1` et
donnait a une capacite le credit de sa voisine. La resolution passe donc par
`capacity_identity.py`, qui n'admet que des egalites exactes dans la portee du
chapitre.

Heritage des corriges. Un corrige ne declare pas toujours de capacite : il la
tient de l'exercice qu'il corrige, via `META.exercice_id`. Les compter sans
cet heritage inventerait des lacunes -- 1SPE en affichait vingt qui n'existent
pas.

Roles mesurables. Les cinq roles editoriaux ordinaires et les evaluations
portent leurs capacites dans le META du `.tex`. Les QCM les portent question
par question dans leur JSON source. La matrice collection-wide lit chaque
role dans sa source autoritaire : elle ne credite jamais le META du `.tex`
genere pour un QCM.

Le backlog qui en decoule se compte en unites d'ecriture -- un couple
(capacite, role) sans contenu valide -- jamais en fichiers a remplacer. Le
volume clone d'hier n'est pas un quota pour demain.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLONE_LEDGER = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
OUTPUT_JSON = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
OUTPUT_MD = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.md"

CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)
UNPUBLISHED = ("_harvest",)

CORE_META_ROLES = ("cours", "methodes", "exercices", "corriges", "remediation")
TEX_META_ROLES = CORE_META_ROLES + ("evaluations",)
MEASURED_ROLES = CORE_META_ROLES + ("qcm", "evaluations")
ROLE_OBJECT_TYPES = {
    "cours": {"cours"},
    "methodes": {"methode"},
    "exercices": {"exercice"},
    "corriges": {"corrige", "correction"},
    "remediation": {"remediation"},
    "evaluations": {"evaluation"},
}


def _resolver_module():
    spec = importlib.util.spec_from_file_location(
        "capacity_identity", ROOT / "scripts/capacity_identity.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CoverageError(RuntimeError):
    """La mesure ne peut pas être produite sans inventer un crédit."""


def _capacity_error_classification(error: Exception) -> str | None:
    names = {cls.__name__ for cls in type(error).__mro__}
    if "AmbiguousCapacityIdentity" in names:
        return "AMBIGUOUS_CAPACITY_IDENTITY"
    if names & {"UnresolvedCapacityIdentity", "CapacityIdentityError"}:
        return "UNRESOLVED_CAPACITY_IDENTITY"
    return None


def _sources(corpora: tuple[Path, ...] = CORPORA) -> list[Path]:
    paths: list[Path] = []
    for corpus in corpora:
        if corpus.is_dir():
            paths += [
                p
                for p in sorted(corpus.rglob("*.tex"))
                if not any(part in UNPUBLISHED for part in p.parts)
            ]
    return paths


def _qcm_sources(corpora: tuple[Path, ...] = CORPORA) -> list[Path]:
    return sorted(
        path
        for corpus in corpora
        if corpus.is_dir()
        for path in corpus.glob("*/qcm/*-QCM.json")
    )


def _set_digest(values: list[str] | set[str]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(sorted(values), ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _path_key(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _unit_id(row: dict[str, Any]) -> str:
    return f"{row['chapter']}/{row['capacity']}/{row['role']}"


def _projection(
    backlog: list[dict[str, Any]], key_name: str
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, set[str]] = collections.defaultdict(set)
    for row in backlog:
        buckets[str(row[key_name])].add(_unit_id(row))
    return {
        key: {
            "count": len(units),
            "unit_ids": sorted(units),
            "set_digest": _set_digest(units),
        }
        for key, units in sorted(buckets.items())
    }


def _projection_invariant(
    projection: dict[str, dict[str, Any]], expected: set[str]
) -> dict[str, Any]:
    buckets = [set(bucket["unit_ids"]) for bucket in projection.values()]
    intersections = sum(
        len(left & right)
        for index, left in enumerate(buckets)
        for right in buckets[index + 1 :]
    )
    union = set().union(*buckets) if buckets else set()
    return {
        "pairwise_intersections": intersections,
        "union_matches_authoring_backlog": union == expected,
    }


def build_coverage(
    *,
    resolver=None,
    clone_ledger: dict[str, Any] | None = None,
    corpora: tuple[Path, ...] = CORPORA,
    source_paths: list[Path] | None = None,
    qcm_paths: list[Path] | None = None,
) -> dict[str, Any]:
    clone = _clone_module()
    identity = _resolver_module()
    resolver = resolver or identity.CapacityIdentityResolver.from_corpora(corpora)

    ledger = clone_ledger or json.loads(CLONE_LEDGER.read_text(encoding="utf-8"))
    invalid_credit = set(ledger["objects_on_invalid_credit"])
    # Un clone dont le proprietaire semantique n'est pas demontrable ne prouve
    # rien : il ne credite pas, mais son absence de credit n'est pas une
    # lacune non plus -- le contenu est la, c'est sa capacite qui est
    # indeterminee. Le confondre avec du vide enverrait reecrire un objet qui
    # existe ; le compter comme valide crediterait une capacite au hasard.
    indeterminate_credit = set(ledger["objects_with_indeterminate_credit"])
    overlap = invalid_credit & indeterminate_credit
    if overlap:
        raise CoverageError(
            "credits invalides et indetermines non disjoints: "
            + ", ".join(sorted(overlap)[:5])
        )
    paths = list(source_paths) if source_paths is not None else _sources(corpora)

    # Première passe : identité, capacité et état de crédit de chaque objet.
    objects_by_id: dict[str, dict[str, Any]] = {}
    metas: dict[Path, dict[str, Any]] = {}
    capacities_by_path: dict[Path, tuple[str, ...]] = {}
    capacity_declaration_invalid: set[Path] = set()
    capacity_identity_blockers: list[dict[str, str]] = []
    for path in paths:
        meta = clone.read_meta(path.read_text(encoding="utf-8", errors="replace"))
        metas[path] = meta
        chapter = path.parts[path.parts.index("chapitres") + 1]
        try:
            capacities = resolver.resolve_meta_codes(chapter, meta)
        except Exception as exc:  # exception may come from a separately loaded resolver
            classification = _capacity_error_classification(exc)
            if classification is None:
                raise
            capacities = ()
            capacity_declaration_invalid.add(path)
            capacity_identity_blockers.append(
                {
                    "classification": classification,
                    "path": _path_key(path),
                    "object_id": str(meta.get("id") or ""),
                    "reason": str(exc),
                }
            )
        capacities_by_path[path] = capacities
        object_id = str(meta.get("id") or "").strip()
        if not object_id:
            continue
        if object_id in objects_by_id:
            raise CoverageError(
                f"identifiant objet duplique {object_id}: "
                f"{objects_by_id[object_id]['path']} et {_path_key(path)}"
            )
        relative = _path_key(path)
        state = (
            "INVALID"
            if relative in invalid_credit
            else "INDETERMINATE"
            if relative in indeterminate_credit
            else "VALID"
        )
        objects_by_id[object_id] = {
            "capacities": capacities,
            "chapter": chapter,
            "object_type": str(meta.get("type_objet") or "").strip(),
            "role": path.parts[path.parts.index("chapitres") + 2],
            "state": state,
            "path": relative,
        }

    ex_co_relationship_blockers: list[dict[str, Any]] = []

    def resolved_credit(path: Path, role: str) -> tuple[tuple[str, ...], str]:
        meta = metas[path]
        chapter = path.parts[path.parts.index("chapitres") + 1]
        relative = _path_key(path)
        state = (
            "INVALID"
            if relative in invalid_credit
            else "INDETERMINATE"
            if relative in indeterminate_credit
            else "VALID"
        )
        references: list[str] = []
        for key in ("exercice_id", "exercice_ref"):
            raw_reference = meta.get(key)
            if raw_reference is None:
                continue
            if not isinstance(raw_reference, str) or not raw_reference.strip():
                raise CoverageError(
                    f"corrige {_path_key(path)}: {key} invalide"
                )
            references.append(raw_reference.strip())
        if len(set(references)) > 1:
            raise CoverageError(
                f"corrige {_path_key(path)}: heritage contradictoire "
                f"exercice_id/exercice_ref {sorted(set(references))}"
            )
        declared = capacities_by_path[path]
        # Une déclaration présente mais irrésoluble n'est pas équivalente à
        # l'absence de déclaration. En particulier un corrigé ne peut pas
        # effacer son erreur puis récupérer silencieusement la capacité de
        # l'exercice référencé.
        if path in capacity_declaration_invalid:
            return (), state
        if role == "corriges" and references:
            exercise_id = references[0]
            inherited = objects_by_id.get(exercise_id)
            if inherited is None:
                raise CoverageError(
                    f"corrige {_path_key(path)}: exercice_id introuvable {exercise_id}"
                )
            if inherited["chapter"] != chapter:
                raise CoverageError(
                    f"corrige {_path_key(path)}: exercice_id {exercise_id} "
                    f"appartient a un autre chapitre ({inherited['chapter']})"
                )
            if (
                inherited["role"] != "exercices"
                or inherited["object_type"] != "exercice"
            ):
                ex_co_relationship_blockers.append(
                    {
                        "classification": "MISMATCHED_CONTENT",
                        "correction_id": str(meta.get("id") or ""),
                        "correction_path": relative,
                        "correction_capacities": list(declared),
                        "exercise_id": exercise_id,
                        "exercise_path": inherited["path"],
                        "exercise_capacities": list(inherited["capacities"]),
                    }
                )
                return (), state
            if declared and set(declared) != set(inherited["capacities"]):
                ex_co_relationship_blockers.append(
                    {
                        "classification": "MISMATCHED_CAPACITY",
                        "correction_id": str(meta.get("id") or ""),
                        "correction_path": relative,
                        "correction_capacities": list(declared),
                        "exercise_id": exercise_id,
                        "exercise_path": inherited["path"],
                        "exercise_capacities": list(inherited["capacities"]),
                    }
                )
                return (), state
            if inherited["state"] == "INVALID":
                state = "INVALID"
            elif inherited["state"] == "INDETERMINATE" and state == "VALID":
                state = "INDETERMINATE"
            return tuple(declared or inherited["capacities"]), state
        if declared:
            return declared, state
        return (), state

    without_declaration: list[str] = []
    role_type_mismatches: list[dict[str, str]] = []
    valid: dict[tuple[str, str, str], list[dict[str, str]]] = collections.defaultdict(list)
    indeterminate: dict[
        tuple[str, str, str], list[dict[str, str]]
    ] = collections.defaultdict(list)
    for path in paths:
        index = path.parts.index("chapitres") + 1
        chapter, role = path.parts[index], path.parts[index + 1]
        if role not in TEX_META_ROLES:
            continue
        object_type = str(metas[path].get("type_objet") or "").strip()
        if object_type not in ROLE_OBJECT_TYPES[role]:
            role_type_mismatches.append(
                {
                    "path": _path_key(path),
                    "role": role,
                    "type_objet": object_type,
                }
            )
            continue
        capacities, credit_state = resolved_credit(path, role)
        relative = _path_key(path)
        if not capacities:
            without_declaration.append(relative)
            continue
        if credit_state == "INVALID":
            continue
        object_id = str(metas[path].get("id") or relative)
        for capacity in capacities:
            target = indeterminate if credit_state == "INDETERMINATE" else valid
            target[(chapter, capacity, role)].append(
                {"id": object_id, "path": relative}
            )

    # Le QCM a une granularite plus fine que son `.tex` genere : une question
    # credite exactement une capacite, resolue par la meme table autoritaire.
    qcm_source_paths = (
        list(qcm_paths) if qcm_paths is not None else _qcm_sources(corpora)
    )
    qcm_counts = collections.Counter(path.parent.parent.name for path in qcm_source_paths)
    duplicate_qcm_chapters = sorted(
        chapter for chapter, count in qcm_counts.items() if count > 1
    )
    if duplicate_qcm_chapters:
        raise CoverageError(
            "MULTIPLE_QCM_SOURCES: " + ", ".join(duplicate_qcm_chapters)
        )
    seen_questions: set[str] = set()
    for path in qcm_source_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CoverageError(f"QCM illisible {_path_key(path)}: {exc}") from exc
        chapter = path.parent.parent.name
        if payload.get("chapitre") != chapter:
            raise CoverageError(
                f"QCM {_path_key(path)}: chapitre declare "
                f"{payload.get('chapitre')!r}, attendu {chapter!r}"
            )
        questions = payload.get("questions")
        if not isinstance(questions, list):
            raise CoverageError(f"QCM {_path_key(path)}: questions absentes")
        for question in questions:
            if not isinstance(question, dict):
                raise CoverageError(f"QCM {_path_key(path)}: question invalide")
            question_id = str(question.get("id") or "").strip()
            if not question_id:
                raise CoverageError(f"QCM {_path_key(path)}: id question absent")
            object_id = f"{chapter}/{path.name}#{question_id}"
            if object_id in seen_questions:
                raise CoverageError(f"identifiant question QCM duplique {object_id}")
            seen_questions.add(object_id)
            try:
                resolution = resolver.resolve(chapter, question.get("capacite"))
            except identity.CapacityIdentityError as exc:
                raise CoverageError(
                    f"QCM {_path_key(path)}#{question_id}: capacite non resolue"
                ) from exc
            if resolution.rule == identity.PREREQUISITE:
                raise CoverageError(
                    f"QCM {_path_key(path)}#{question_id}: prerequis utilise "
                    "comme capacite"
                )
            relative = _path_key(path)
            valid[(chapter, resolution.identity.local_code, "qcm")].append(
                {"id": object_id, "path": f"{relative}#{question_id}"}
            )

    rows: list[dict[str, Any]] = []
    for chapter in resolver.chapters:
        identities = resolver.capacities_of(chapter)
        for capacity_identity in identities:
            capacity = capacity_identity.local_code
            for role in MEASURED_ROLES:
                valid_entries = valid[(chapter, capacity, role)]
                pending_entries = indeterminate[(chapter, capacity, role)]
                valid_ids = sorted(entry["id"] for entry in valid_entries)
                valid_paths = sorted(entry["path"] for entry in valid_entries)
                pending_ids = sorted(entry["id"] for entry in pending_entries)
                pending_paths = sorted(entry["path"] for entry in pending_entries)
                count = len(valid_entries)
                pending = len(pending_entries)
                if count:
                    state = "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
                elif pending:
                    state = "INDETERMINATE_CLONE_CREDIT"
                else:
                    state = "MISSING"
                rows.append(
                    {
                        "manual": capacity_identity.manual,
                        "chapter": chapter,
                        "capacity": capacity,
                        "canonical_capacity_uid": capacity_identity.uid,
                        "role": role,
                        "valid_objects": count,
                        "indeterminate_objects": pending,
                        "valid_object_ids": valid_ids,
                        "valid_object_paths": valid_paths,
                        "valid_object_ids_digest": _set_digest(valid_ids),
                        "valid_object_paths_digest": _set_digest(valid_paths),
                        "indeterminate_object_ids": pending_ids,
                        "indeterminate_object_paths": pending_paths,
                        "indeterminate_object_ids_digest": _set_digest(pending_ids),
                        "indeterminate_object_paths_digest": _set_digest(
                            pending_paths
                        ),
                        "state": state,
                    }
                )

    backlog = [row for row in rows if row["state"] == "MISSING"]
    per_manual: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    per_chapter: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for row in backlog:
        per_manual[row["manual"]][row["role"]] += 1
        per_manual[row["manual"]]["TOTAL"] += 1
        per_chapter[row["chapter"]][row["role"]] += 1
        per_chapter[row["chapter"]]["TOTAL"] += 1

    identifiers = sorted(_unit_id(row) for row in backlog)
    backlog_projection_keys = {
        "per_manual": "manual",
        "per_chapter": "chapter",
        "per_capacity": "canonical_capacity_uid",
        "per_role": "role",
    }
    projections = {
        name: _projection(backlog, key)
        for name, key in backlog_projection_keys.items()
    }
    expected_units = set(identifiers)
    projection_invariants = {
        name: _projection_invariant(projection, expected_units)
        for name, projection in projections.items()
    }
    return {
        "artifact_type": "true_pedagogical_coverage",
        "schema_version": 1,
        "generated_by": "scripts/build_true_pedagogical_coverage.py",
        "capacity_identity": (
            "resolue par scripts/capacity_identity.py : egalites exactes dans "
            "la portee du chapitre, jamais par extraction de jeton"
        ),
        "credit_rule": (
            "le META et sa resolution exacte prouvent seulement l'identite "
            "DECLAREE, pas l'alignement semantique du corps ; aucun credit "
            "semantique n'est revendique sans ledger de preuve distinct"
        ),
        "semantic_alignment": {
            "status": "NOT_ESTABLISHED_COLLECTION_WIDE",
            "false_positive_credits": "UNKNOWN",
            "authoring_backlog_authority": "CANDIDATE_LOWER_BOUND",
        },
        "cell_states": {
            "SEMANTICALLY_VALIDATED_CONTENT": (
                "au moins une preuve séparée atteste que le corps sert cet UID"
            ),
            "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED": (
                "au moins un objet declare exactement cette capacite, mais son "
                "corps n'a pas encore une preuve semantique autoritaire"
            ),
            "INDETERMINATE_CLONE_CREDIT": (
                "le contenu existe mais appartient a un groupe de clones dont "
                "le proprietaire semantique n'est pas demontrable : ce n'est "
                "ni un credit ni une lacune, c'est une revue a faire"
            ),
            "MISSING": "aucun contenu, valide ou indetermine",
        },
        "measured_roles": list(MEASURED_ROLES),
        "role_sources": {
            "cours": "META soumis au ledger de clones",
            "methodes": "META soumis au ledger de clones",
            "exercices": "META soumis au ledger de clones",
            "corriges": "META ou heritage exact de l'exercice soumis au ledger de clones",
            "remediation": "META soumis au ledger de clones",
            "qcm": "question JSON resolue exactement",
            "evaluations": "META de l'evaluation soumis au ledger de clones",
        },
        "correction_capacity_inheritance": (
            "un corrige sans capacite declaree herite de celle de son "
            "exercice via META.exercice_id"
        ),
        "inventory": {
            "capacities": len({(r["chapter"], r["capacity"]) for r in rows}),
            "cells": len(rows),
            "cells_with_declared_exact_identity": sum(
                1
                for r in rows
                if r["state"]
                == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
            ),
            "cells_with_indeterminate_credit": sum(
                1 for r in rows if r["state"] == "INDETERMINATE_CLONE_CREDIT"
            ),
            "authoring_units_required": len(backlog),
            "objects_without_capacity_declaration": len(without_declaration),
        },
        "capacity_identity_resolution": {
            "ambiguous": sum(
                row["classification"] == "AMBIGUOUS_CAPACITY_IDENTITY"
                for row in capacity_identity_blockers
            ),
            "unresolved": sum(
                row["classification"] == "UNRESOLVED_CAPACITY_IDENTITY"
                for row in capacity_identity_blockers
            ),
            "unknown": sum(
                row["classification"]
                not in {
                    "AMBIGUOUS_CAPACITY_IDENTITY",
                    "UNRESOLVED_CAPACITY_IDENTITY",
                }
                for row in capacity_identity_blockers
            ),
        },
        "invariants": {
            "invalid_and_indeterminate_disjoint": not bool(overlap),
            "duplicate_object_ids": 0,
            "ex_co_relationship_blockers": len(ex_co_relationship_blockers),
        },
        "authoring_units_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(identifiers, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "per_manual": {k: dict(v) for k, v in sorted(per_manual.items())},
        "per_chapter": {
            k: dict(v)
            for k, v in sorted(
                per_chapter.items(), key=lambda kv: (-kv[1]["TOTAL"], kv[0])
            )
        },
        "authoring_backlog_projections": projections,
        "projection_invariants": projection_invariants,
        "rows": rows,
        "authoring_backlog": sorted(
            backlog, key=lambda r: (r["manual"], r["chapter"], r["capacity"], r["role"])
        ),
        "objects_without_capacity_declaration": sorted(without_declaration),
        "capacity_identity_blockers": sorted(
            capacity_identity_blockers,
            key=lambda row: (row["path"], row["object_id"], row["reason"]),
        ),
        "capacity_identity_blockers_digest": _set_digest(
            {
                f"{row['classification']}::{row['path']}::{row['object_id']}::{row['reason']}"
                for row in capacity_identity_blockers
            }
        ),
        "ex_co_relationship_blockers": sorted(
            ex_co_relationship_blockers,
            key=lambda row: (
                row["classification"],
                row["correction_path"],
                row["exercise_id"],
            ),
        ),
        "role_type_mismatches": sorted(
            role_type_mismatches,
            key=lambda row: (row["path"], row["role"], row["type_objet"]),
        ),
        "role_type_mismatches_digest": _set_digest(
            {
                f"{row['path']}::{row['role']}::{row['type_objet']}"
                for row in role_type_mismatches
            }
        ),
        "objects_without_capacity_declaration_digest": _set_digest(
            without_declaration
        ),
        "invalid_credit_paths_digest": _set_digest(invalid_credit),
        "indeterminate_credit_paths_digest": _set_digest(indeterminate_credit),
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    inventory = payload["inventory"]
    lines = [
        "# Couverture pédagogique réelle",
        "",
        "Un objet ne crédite une capacité que si son **corps** la sert. Le seul",
        "`META` ne donne aucun crédit : c'est exactement ce que le P0 de clonage",
        "exploitait — dix-sept fiches identiques déclarées `C1` à `C16` créditaient",
        "seize capacités alors qu'une seule, `C7`, était traitée.",
        "",
        f"- capacités contractuelles : `{inventory['capacities']}`",
        f"- cellules (capacité × rôle) : `{inventory['cells']}`",
        f"- cellules avec déclaration exacte (alignement sémantique à établir) : "
        f"`{inventory['cells_with_declared_exact_identity']}`",
        f"- **unités d'écriture requises** : `{inventory['authoring_units_required']}`",
        "",
        "| Manuel | " + " | ".join(payload["measured_roles"]) + " | Total |",
        "|---|" + "---:|" * (len(payload["measured_roles"]) + 1),
    ]
    for manual, counts in sorted(
        payload["per_manual"].items(), key=lambda kv: -kv[1].get("TOTAL", 0)
    ):
        cells = " | ".join(
            str(counts.get(role, 0)) for role in payload["measured_roles"]
        )
        lines.append(f"| `{manual}` | {cells} | **{counts.get('TOTAL', 0)}** |")
    lines += [
        "",
        "Ce backlog se compte en unités d'écriture — un couple (capacité, rôle)",
        "sans contenu valide — jamais en fichiers à remplacer. Le volume cloné",
        "d'hier n'est pas un quota pour demain.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="comparer sans écrire")
    arguments = parser.parse_args(argv)

    payload = build_coverage()
    targets = ((OUTPUT_JSON, render_json(payload)), (OUTPUT_MD, render_md(payload)))
    stale = []
    for path, rendered in targets:
        if arguments.check:
            current = path.read_text(encoding="utf-8") if path.is_file() else ""
            if current != rendered:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.write_text(rendered, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for name in stale:
        print(f"STALE: {name}")
    return 1 if stale else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
