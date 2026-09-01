#!/usr/bin/env python3
"""Expliquer le delta 460 -> courant sans confondre mesure et authoring.

Le backlog historique comptait 460 cellules. Deux événements distincts l'ont
ensuite réduit :

* la correction de l'identité des capacités et de la gouvernance des clones
  a reclassé 136 cellules sans écrire de nouveau contenu ;
* la reconstruction 1NSI a réellement fermé neuf cellules par authoring.
* le retrait ultérieur de l'inférence lexicale `C<n>` dans les corps a
  reclassé 107 autres cellules sans authoring.

Ces deux ensembles doivent rester séparés. Une cellule alimentée seulement
par un clone au propriétaire indéterminé est une dette de revue, pas un crédit
valide. Ce producteur conserve donc les trois snapshots, les ensembles exacts
et une preuve objet par objet pour chaque sortie du backlog.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COVERAGE_REL = "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
OUTPUT = ROOT / "audit/FALSE_MISSING_GAP_DELTA.json"

LEGACY_SHA = "289daa61dadfd977fec668d8405c98c4d9f10d34"
RESOLVER_SHA = "af6113f862569f5e58b4c40caf14b26c0e8a4673"
AUTHORING_SHA = "fa9ff89466841cb5187e77a42790992a819e3764"
COMPARABLE_ROLES = ("cours", "methodes", "exercices", "corriges", "remediation")


def _load(module_name: str, relative: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _coverage_at(sha: str) -> tuple[dict[str, Any], str]:
    blob = subprocess.run(
        ["git", "show", f"{sha}:{COVERAGE_REL}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    return json.loads(blob), "sha256:" + hashlib.sha256(blob).hexdigest()


def _key(row: dict[str, Any]) -> tuple[str, str, str]:
    return row["chapter"], row["capacity"], row["role"]


def _backlog(payload: dict[str, Any]) -> set[tuple[str, str, str]]:
    return {
        _key(row)
        for row in payload["authoring_backlog"]
        if row["role"] in COMPARABLE_ROLES
    }


def _set_digest(values: list[str] | set[str]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(sorted(values), ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _unit_ids(units: set[tuple[str, str, str]]) -> list[str]:
    return sorted(f"{chapter}/{capacity}/{role}" for chapter, capacity, role in units)


def _stage(
    name: str,
    payload: dict[str, Any],
    *,
    source_sha: str,
    artifact_digest: str,
) -> dict[str, Any]:
    units = _unit_ids(_backlog(payload))
    return {
        "name": name,
        "source_sha": source_sha,
        "coverage_artifact_digest": artifact_digest,
        "authoring_units": len(units),
        "backlog_set_digest": _set_digest(units),
    }


def _evidence(row: dict[str, Any]) -> tuple[list[str], list[str]]:
    ids = sorted(
        set(row.get("valid_object_ids") or [])
        | set(row.get("indeterminate_object_ids") or [])
    )
    paths = sorted(
        set(row.get("valid_object_paths") or [])
        | set(row.get("indeterminate_object_paths") or [])
    )
    return ids, paths


def _row(
    unit: tuple[str, str, str],
    *,
    before_state: str,
    transition_result_state: str,
    transition_row: dict[str, Any],
    current_row: dict[str, Any],
    classification: str,
    why: str,
    valid_capacity_credit_claimed: bool,
) -> dict[str, Any]:
    chapter, capacity, role = unit
    transition_ids, transition_paths = _evidence(transition_row)
    current_ids, current_paths = _evidence(current_row)
    transition_row_digest = "sha256:" + hashlib.sha256(
        json.dumps(
            transition_row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return {
        "chapter": chapter,
        "manual": current_row["manual"],
        "capacity": capacity,
        "role": role,
        "canonical_capacity_uid": current_row["canonical_capacity_uid"],
        "classification": classification,
        "before_state": before_state,
        "transition_result_state": transition_result_state,
        "current_state": current_row["state"],
        "why_it_left_the_backlog": why,
        "valid_capacity_credit_claimed": valid_capacity_credit_claimed,
        "transition_object_ids": transition_ids,
        "transition_object_paths": transition_paths,
        "transition_object_ids_digest": _set_digest(transition_ids),
        "transition_object_paths_digest": _set_digest(transition_paths),
        "transition_row_digest": transition_row_digest,
        "current_object_ids": current_ids,
        "current_object_paths": current_paths,
        "current_object_ids_digest": _set_digest(current_ids),
        "current_object_paths_digest": _set_digest(current_paths),
        "transition_evidence_still_identical_current": (
            transition_ids == current_ids and transition_paths == current_paths
        ),
    }


def _transition(
    before: set[tuple[str, str, str]],
    after: set[tuple[str, str, str]],
) -> tuple[set[tuple[str, str, str]], list[dict[str, str]]]:
    removed = before - after
    added = [
        {"chapter": chapter, "capacity": capacity, "role": role}
        for chapter, capacity, role in sorted(after - before)
    ]
    return removed, added


def _partition_measurement_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Separate proved false gaps from decisions merely deferred for review."""

    proven = [row for row in rows if row["valid_capacity_credit_claimed"] is True]
    deferred = [row for row in rows if row["valid_capacity_credit_claimed"] is not True]
    return proven, deferred


def build_delta() -> dict[str, Any]:
    coverage = _load(
        "true_coverage_for_delta", "scripts/build_true_pedagogical_coverage.py"
    )

    legacy, legacy_digest = _coverage_at(LEGACY_SHA)
    resolver_stage, resolver_digest = _coverage_at(RESOLVER_SHA)
    authored_stage, authored_digest = _coverage_at(AUTHORING_SHA)
    current = coverage.build_coverage()
    current_blob = coverage.render_json(current).encode("utf-8")
    current_digest = "sha256:" + hashlib.sha256(current_blob).hexdigest()

    legacy_backlog = _backlog(legacy)
    resolver_backlog = _backlog(resolver_stage)
    authored_backlog = _backlog(authored_stage)
    current_backlog = _backlog(current)
    historical_measurement_units, historical_measurement_added = _transition(
        legacy_backlog, resolver_backlog
    )
    authoring_units, authoring_added = _transition(
        resolver_backlog, authored_backlog
    )
    current_measurement_units, current_measurement_added = _transition(
        authored_backlog, current_backlog
    )

    resolver_states = {_key(row): row["state"] for row in resolver_stage["rows"]}
    authored_states = {_key(row): row["state"] for row in authored_stage["rows"]}
    resolver_rows = {_key(row): row for row in resolver_stage["rows"]}
    authored_rows = {_key(row): row for row in authored_stage["rows"]}
    current_rows = {_key(row): row for row in current["rows"]}

    historical_measurement_rows: list[dict[str, Any]] = []
    for unit in sorted(historical_measurement_units):
        stage_state = resolver_states[unit]
        if stage_state == "VALID_ALIGNED_CONTENT":
            classification = "RECOVERED_EXACT_DECLARATION_SEMANTIC_REVIEW_PENDING"
            why = (
                "la résolution exacte relie la déclaration qualifiée à son UID "
                "contractuel sans extraction de suffixe"
            )
            valid_claim = False
        elif stage_state == "INDETERMINATE_CLONE_CREDIT":
            classification = "RECLASSIFIED_AS_REVIEW_DEBT"
            why = (
                "un corps existe mais son propriétaire sémantique n'est pas "
                "démontré ; la cellule relève de la revue, pas de l'authoring"
            )
            valid_claim = False
        else:
            classification = "UNEXPLAINED"
            why = "état inattendu au snapshot du resolver"
            valid_claim = False
        historical_measurement_rows.append(
            _row(
                unit,
                before_state="MISSING",
                transition_result_state=stage_state,
                transition_row=resolver_rows[unit],
                current_row=current_rows[unit],
                classification=classification,
                why=why,
                valid_capacity_credit_claimed=valid_claim,
            )
        )

    authoring_rows = [
        _row(
            unit,
            before_state=resolver_states[unit],
            transition_result_state=authored_states[unit],
            transition_row=authored_rows[unit],
            current_row=current_rows[unit],
            classification="REAL_AUTHORING_DECLARATION_CLOSURE_SEMANTIC_REVIEW_PENDING",
            why=(
                "la cellule était encore MISSING après correction de la mesure ; "
                "du contenu 1NSI courant la sert désormais"
            ),
            valid_capacity_credit_claimed=(
                current_rows[unit]["state"] == "SEMANTICALLY_VALIDATED_CONTENT"
            ),
        )
        for unit in sorted(authoring_units)
    ]

    current_measurement_rows: list[dict[str, Any]] = []
    for unit in sorted(current_measurement_units):
        current_state = current_rows[unit]["state"]
        if current_state == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED":
            classification = "RECOVERED_EXACT_DECLARATION_SEMANTIC_REVIEW_PENDING"
            valid_claim = False
        elif current_state == "INDETERMINATE_CLONE_CREDIT":
            classification = "RECLASSIFIED_AS_REVIEW_DEBT"
            valid_claim = False
        else:
            classification = "UNEXPLAINED"
            valid_claim = False
        current_measurement_rows.append(
            _row(
                unit,
                before_state="MISSING",
                transition_result_state=current_state,
                transition_row=current_rows[unit],
                current_row=current_rows[unit],
                classification=classification,
                why=(
                    "l'ancien ledger interprétait une occurrence lexicale C<n> "
                    "dans le corps comme preuve d'identité ; cette heuristique "
                    "non contractuelle a été supprimée"
                ),
                valid_capacity_credit_claimed=valid_claim,
            )
        )

    measurement_rows = historical_measurement_rows + current_measurement_rows
    proven_false_missing_rows, deferred_measurement_rows = _partition_measurement_rows(
        measurement_rows
    )

    per_class = collections.Counter(
        row["classification"] for row in measurement_rows
    )
    unexplained = [
        f"{row['chapter']}/{row['capacity']}/{row['role']}"
        for row in measurement_rows + authoring_rows
        if row["classification"] == "UNEXPLAINED"
        or not row["transition_object_ids"]
        or not row["transition_object_paths"]
    ]
    stages = [
        _stage(
            "LEGACY_MEASURE",
            legacy,
            source_sha=LEGACY_SHA,
            artifact_digest=legacy_digest,
        ),
        _stage(
            "CAPACITY_IDENTITY_CORRECTED",
            resolver_stage,
            source_sha=RESOLVER_SHA,
            artifact_digest=resolver_digest,
        ),
        _stage(
            "COUPLED_1NSI_AUTHORED",
            authored_stage,
            source_sha=AUTHORING_SHA,
            artifact_digest=authored_digest,
        ),
        _stage(
            "CURRENT",
            current,
            source_sha="WORKTREE",
            artifact_digest=current_digest,
        ),
    ]
    historical_measurement_count = len(historical_measurement_rows)
    current_measurement_count = len(current_measurement_rows)
    measurement_count = historical_measurement_count + current_measurement_count
    measurement_added_count = len(historical_measurement_added) + len(
        current_measurement_added
    )
    net_measurement_delta = measurement_count - measurement_added_count
    authoring_count = len(authoring_rows)
    return {
        "artifact_type": "false_missing_gap_delta",
        "schema_version": 2,
        "generated_by": "scripts/build_false_missing_gap_delta.py",
        "comparison_scope": {
            "roles": list(COMPARABLE_ROLES),
            "reason": "les snapshots historiques ne mesuraient que ces cinq roles",
        },
        "current_collection_wide_authoring_units": current["inventory"][
            "authoring_units_required"
        ],
        "interpretation": (
            "les transitions LEGACY→RESOLVER et AUTHORED→CURRENT corrigent la "
            "mesure ; seule RESOLVER→AUTHORED est de l'authoring réel"
        ),
        "stages": stages,
        "equation": (
            f"{len(legacy_backlog)} - {historical_measurement_count} - "
            f"{authoring_count} - {current_measurement_count} + "
            f"{measurement_added_count} = {len(current_backlog)}"
        ),
        "measurement_reclassification": {
            "count": measurement_count,
            "set_digest": _set_digest(
                _unit_ids(historical_measurement_units | current_measurement_units)
            ),
            "phases": [
                {
                    "name": "LEGACY_TO_CAPACITY_IDENTITY_CORRECTED",
                    "count": historical_measurement_count,
                    "set_digest": _set_digest(
                        _unit_ids(historical_measurement_units)
                    ),
                    "gaps_added": historical_measurement_added,
                },
                {
                    "name": "AUTHORED_TO_LEXICAL_HEURISTIC_REMOVED",
                    "count": current_measurement_count,
                    "set_digest": _set_digest(_unit_ids(current_measurement_units)),
                    "gaps_added": current_measurement_added,
                },
            ],
            "per_class": dict(sorted(per_class.items())),
            "per_manual": dict(
                sorted(
                    collections.Counter(
                        row["manual"] for row in measurement_rows
                    ).items()
                )
            ),
            "gaps_added": historical_measurement_added + current_measurement_added,
            "gross_removed": measurement_count,
            "added_by_stricter_false_positive_rejection": measurement_added_count,
            "net_backlog_reduction": net_measurement_delta,
            "units": measurement_rows,
        },
        "proven_false_missing": {
            "count": len(proven_false_missing_rows),
            "set_digest": _set_digest(
                [
                    f"{row['chapter']}/{row['capacity']}/{row['role']}"
                    for row in proven_false_missing_rows
                ]
            ),
            "units": proven_false_missing_rows,
        },
        "authoring_decision_deferred_pending_semantic_review": {
            "count": len(deferred_measurement_rows),
            "set_digest": _set_digest(
                [
                    f"{row['chapter']}/{row['capacity']}/{row['role']}"
                    for row in deferred_measurement_rows
                ]
            ),
            "units": deferred_measurement_rows,
        },
        "real_authoring_closure": {
            "count": authoring_count,
            "set_digest": _set_digest(_unit_ids(authoring_units)),
            "per_manual": dict(
                sorted(
                    collections.Counter(row["manual"] for row in authoring_rows).items()
                )
            ),
            "gaps_added": authoring_added,
            "units": authoring_rows,
        },
        "total_delta_to_current": len(legacy_backlog) - len(current_backlog),
        "delta_reconciliation": {
            "legacy": len(legacy_backlog),
            "gross_measurement_removals": measurement_count,
            "real_authoring_closures": authoring_count,
            "gaps_added_by_stricter_false_positive_rejection": measurement_added_count,
            "current": len(current_backlog),
            "holds": (
                len(legacy_backlog)
                - measurement_count
                - authoring_count
                + measurement_added_count
                == len(current_backlog)
            ),
        },
        "unexplained_units": sorted(unexplained),
        "status": "COMPLETE" if not unexplained else "GAP",
        # Compatibilité explicite des consumers historiques : ce champ ne
        # couvre que la correction de mesure, jamais les neuf authorings.
        "before_authoring_units": len(legacy_backlog),
        "after_measurement_authoring_units": len(resolver_backlog),
        "current_authoring_units": len(current_backlog),
        "false_missing_gaps_removed": len(proven_false_missing_rows),
        "per_removal_class": dict(
            sorted(
                collections.Counter(
                    row["classification"] for row in proven_false_missing_rows
                ).items()
            )
        ),
        "removed_units": proven_false_missing_rows,
        "unexplained_removals": len(unexplained),
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    payload = build_delta()
    rendered = render(payload)
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: "
        f"{payload['false_missing_gaps_removed']} faux gaps prouvés, "
        f"{payload['authoring_decision_deferred_pending_semantic_review']['count']} décisions différées, "
        f"{payload['real_authoring_closure']['count']} authorées"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
