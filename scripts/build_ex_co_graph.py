#!/usr/bin/env python3
"""Build the exact exercise/correction relationship graph collection-wide."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)
CLONE_LEDGER = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
OUTPUT = ROOT / "audit/EX_CO_GRAPH.json"


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _path_key(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _digest(values: Iterable[str]) -> str:
    encoded = json.dumps(
        sorted(str(value) for value in values), separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _sources(corpora: tuple[Path, ...]) -> list[Path]:
    return sorted(
        path
        for corpus in corpora
        if corpus.is_dir()
        for path in corpus.rglob("*.tex")
        if "_harvest" not in path.parts
    )


def build_graph(
    *,
    corpora: tuple[Path, ...] = CORPORA,
    source_paths: list[Path] | None = None,
    clone_ledger: Mapping[str, Any] | None = None,
    cross_discipline_ledger: Mapping[str, Any] | None = None,
    resolver=None,
) -> dict[str, Any]:
    clone = _module(
        "ex_co_clone_reader", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    identity = _module("ex_co_capacity_identity", ROOT / "scripts/capacity_identity.py")
    resolver = resolver or identity.CapacityIdentityResolver.from_corpora(corpora)
    ledger = dict(clone_ledger) if clone_ledger is not None else json.loads(
        CLONE_LEDGER.read_text(encoding="utf-8")
    )
    clone_paths = set(ledger.get("objects_on_invalid_credit", [])) | set(
        ledger.get("objects_with_indeterminate_credit", [])
    )
    if cross_discipline_ledger is None:
        cross_module = _module(
            "ex_co_cross_discipline",
            ROOT / "scripts/build_nsi_cross_discipline_ledger.py",
        )
        cross_discipline_ledger = cross_module.build_ledger()
    condemned_paths = set(cross_discipline_ledger.get("condemned_paths", []))

    paths = list(source_paths) if source_paths is not None else _sources(corpora)
    exercises: dict[str, dict[str, Any]] = {}
    corrections: list[dict[str, Any]] = []
    all_ids: dict[str, str] = {}
    for path in paths:
        parts = path.parts
        if "chapitres" not in parts:
            continue
        index = parts.index("chapitres") + 1
        if len(parts) <= index + 1:
            continue
        chapter, role = parts[index], parts[index + 1]
        if role not in {"exercices", "corriges"}:
            continue
        meta = clone.read_meta(path.read_text(encoding="utf-8", errors="replace"))
        object_type = str(meta.get("type_objet") or "").strip()
        if role == "exercices" and object_type != "exercice":
            continue
        if role == "corriges" and object_type not in {"corrige", "correction"}:
            continue
        relative = _path_key(path)
        object_id = str(meta.get("id") or relative).strip()
        if object_id in all_ids:
            raise ValueError(
                f"identifiant EX/CO dupliqué {object_id}: {all_ids[object_id]} et {relative}"
            )
        all_ids[object_id] = relative
        capacity_error = None
        try:
            capacities = list(resolver.resolve_meta_codes(chapter, meta))
        except identity.CapacityIdentityError as exc:
            capacities = []
            capacity_error = str(exc)
        row = {
            "id": object_id,
            "path": relative,
            "chapter": chapter,
            "manual": identity.manual_of(chapter),
            "capacities": capacities,
            "capacity_error": capacity_error,
            "body_sha256": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
            "is_clone_candidate": relative in clone_paths,
            "meta": meta,
        }
        if role == "exercices":
            exercises[object_id] = row
        else:
            corrections.append(row)

    relations: list[dict[str, Any]] = []
    linked: dict[str, list[str]] = collections.defaultdict(list)
    for correction in sorted(corrections, key=lambda row: row["path"]):
        meta = correction["meta"]
        references = sorted(
            {
                str(meta[key]).strip()
                for key in ("exercice_id", "exercice_ref")
                if isinstance(meta.get(key), str) and str(meta[key]).strip()
            }
        )
        classes: list[str] = []
        exercise = exercises.get(references[0]) if len(references) == 1 else None
        if not references:
            classes.append("ORPHAN_CO")
        elif len(references) > 1:
            classes.append("MISMATCHED_CONTENT")
        elif exercise is None:
            classes.append("ORPHAN_CO")
        else:
            if (
                correction["path"] in condemned_paths
                or exercise["path"] in condemned_paths
                or correction["manual"] != exercise["manual"]
            ):
                classes.append("CROSS_DISCIPLINE")
            elif correction["chapter"] != exercise["chapter"]:
                classes.append("MISMATCHED_CONTENT")
            if (
                correction["capacity_error"]
                or exercise["capacity_error"]
                or not exercise["capacities"]
            ):
                classes.append("MISMATCHED_CAPACITY")
            elif correction["capacities"] and set(correction["capacities"]) != set(
                exercise["capacities"]
            ):
                classes.append("MISMATCHED_CAPACITY")
            if correction["is_clone_candidate"] or exercise["is_clone_candidate"]:
                classes.append("CLONE")
        if exercise is not None and not classes:
            linked[exercise["id"]].append(correction["id"])
        structural_status = "FAIL" if classes else "MATCH"
        if not classes:
            # Identity, cardinality and scope do not prove that the correction
            # actually answers the exercise body.  Until a separate semantic
            # ledger establishes that relation, fail closed as UNKNOWN.
            classes = ["UNKNOWN"]
        order = {
            "ORPHAN_CO": 0,
            "CROSS_DISCIPLINE": 1,
            "MISMATCHED_CONTENT": 2,
            "MISMATCHED_CAPACITY": 3,
            "CLONE": 4,
            "UNKNOWN": 5,
        }
        classes = sorted(set(classes), key=order.__getitem__)
        relations.append(
            {
                "correction_id": correction["id"],
                "correction_path": correction["path"],
                "correction_chapter": correction["chapter"],
                "correction_capacities": correction["capacities"],
                "correction_body_sha256": correction["body_sha256"],
                "exercise_id": references[0] if len(references) == 1 else None,
                "exercise_path": exercise["path"] if exercise else None,
                "exercise_chapter": exercise["chapter"] if exercise else None,
                "exercise_capacities": exercise["capacities"] if exercise else [],
                "exercise_body_sha256": exercise["body_sha256"] if exercise else None,
                "classifications": classes,
                "structural_status": structural_status,
                "semantic_alignment": (
                    "NOT_ESTABLISHED"
                    if classes == ["UNKNOWN"]
                    else "INVALIDATED_BY_STRUCTURAL_EVIDENCE"
                ),
                "capacity_errors": sorted(
                    value
                    for value in (
                        correction["capacity_error"],
                        exercise["capacity_error"] if exercise else None,
                    )
                    if value
                ),
            }
        )

    cardinality = []
    for exercise_id, exercise in sorted(exercises.items(), key=lambda item: item[1]["path"]):
        correction_ids = sorted(linked.get(exercise_id, []))
        classification = (
            "ORPHAN_EX"
            if not correction_ids
            else "MATCH"
            if len(correction_ids) == 1
            else "MISMATCHED_CONTENT"
        )
        cardinality.append(
            {
                "exercise_id": exercise_id,
                "exercise_path": exercise["path"],
                "exercise_chapter": exercise["chapter"],
                "exercise_capacities": exercise["capacities"],
                "correction_count": len(correction_ids),
                "correction_ids": correction_ids,
                "correction_ids_digest": _digest(correction_ids),
                "classification": classification,
            }
        )

    relation_counts = collections.Counter(
        classification
        for row in relations
        for classification in row["classifications"]
    )
    exercise_counts = collections.Counter(row["classification"] for row in cardinality)
    relation_keys = [
        f"{row['correction_id']}->{row['exercise_id']}:{'+'.join(row['classifications'])}"
        for row in relations
    ]
    exercise_keys = [
        f"{row['exercise_id']}:{row['correction_count']}:{row['classification']}"
        for row in cardinality
    ]
    return {
        "schema_version": 1,
        "artifact_type": "ex_co_graph",
        "generated_by": "scripts/build_ex_co_graph.py",
        "relationship_rule": (
            "each correction names exactly one exercise in the same chapter and "
            "declares the same exact canonical capacity set when it declares one"
        ),
        "exercise_count": len(exercises),
        "correction_count": len(corrections),
        "relation_counts": dict(sorted(relation_counts.items())),
        "exercise_cardinality_counts": dict(sorted(exercise_counts.items())),
        "relations_digest": _digest(relation_keys),
        "exercise_cardinality_digest": _digest(exercise_keys),
        "relations": relations,
        "exercise_cardinality": cardinality,
        "unknown_count": relation_counts["UNKNOWN"],
    }


def render(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_graph()
    rendered = render(payload)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        print(
            f"EX_CO_GRAPH current: {payload['exercise_count']} EX, "
            f"{payload['correction_count']} CO"
        )
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: {payload['exercise_count']} EX, "
        f"{payload['correction_count']} CO"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
