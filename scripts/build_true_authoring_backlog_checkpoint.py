#!/usr/bin/env python3
"""Candidat au point de depart honnete de l'ecriture réelle.

Le backlog historique annonçait 460 unités. La correction de mesure en a
reclassé 136 ; neuf autres ont ensuite été réellement fermées par authoring.
Ces deux transitions sont disjointes et nommées ligne à ligne.

Ecrire contre un backlog gonfle de 30 pour cent, c'est recreer exactement le
remplissage que cette campagne repare. Ce checkpoint fige donc l'etat mesure
apres correction du resolveur, avec son SHA et le digest de son ensemble.

Il reste EVOLUTIF : chaque faux credit retire ensuite le fera bouger. Ce n'est
pas un objectif de production, c'est une reference verifiable.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
DELTA = ROOT / "audit/FALSE_MISSING_GAP_DELTA.json"
CLONE = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
OUTPUT = ROOT / "audit/TRUE_AUTHORING_BACKLOG_ESTABLISHED.json"

#: Run complet vert observé sur un arbre propre après correction du resolver et
#: de tous ses consumers connus. Il lève le blocker technique sans valoir
#: approbation sémantique des contenus.
VALIDATING_RUN: dict[str, Any] | None = {
    "source_sha": "6724cbf366df923e228b494e05157676780f2578",
    "command": "python3 -m pytest -q --no-header -p no:randomly",
    "collected": 9358,
    "passed": 9358,
    "failed": 0,
    "errors": 0,
    "warnings": 4,
    "rc": 0,
    "duration_seconds": 2940.37,
    "log_sha256": "a54a2d5e7eca94daf33b7029e6fc163f2fbd8eeb6d6f669c6cf625e1a66c770d",
    "tree_clean_before": True,
    "tree_clean_after": True,
    "run_record": "audit/FULL_SUPPORTED_SUITE_RUN_6724CBF3.json",
}


def _set_digest(values: set[str]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(sorted(values), ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _projection(
    backlog: list[dict[str, Any]], key_name: str
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, set[str]] = collections.defaultdict(set)
    for row in backlog:
        unit = f"{row['chapter']}/{row['capacity']}/{row['role']}"
        buckets[str(row[key_name])].add(unit)
    return {
        key: {
            "count": len(units),
            "unit_ids": sorted(units),
            "set_digest": _set_digest(units),
        }
        for key, units in sorted(buckets.items())
    }


def build_checkpoint() -> dict[str, Any]:
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    delta = json.loads(DELTA.read_text(encoding="utf-8"))
    clone = json.loads(CLONE.read_text(encoding="utf-8"))
    backlog = coverage["authoring_backlog"]

    per_manual = collections.Counter(row["manual"] for row in backlog)
    per_chapter = collections.Counter(row["chapter"] for row in backlog)
    per_role = collections.Counter(row["role"] for row in backlog)
    per_capacity = collections.Counter(
        f"{row['chapter']}::{row['capacity']}" for row in backlog
    )
    identifiers = sorted(
        f"{row['chapter']}/{row['capacity']}/{row['role']}" for row in backlog
    )
    projections = {
        "per_manual": _projection(backlog, "manual"),
        "per_chapter": _projection(backlog, "chapter"),
        "per_capacity": _projection(backlog, "canonical_capacity_uid"),
        "per_role": _projection(backlog, "role"),
    }
    semantic = coverage.get("semantic_alignment") or {}
    semantic_established = (
        semantic.get("status") == "ESTABLISHED_COLLECTION_WIDE"
        and semantic.get("false_positive_credits") == 0
    )
    established = VALIDATING_RUN is not None and semantic_established
    return {
        "artifact_type": "true_authoring_backlog_established",
        "schema_version": 1,
        "generated_by": "scripts/build_true_authoring_backlog_checkpoint.py",
        "checkpoint": (
            "TRUE_AUTHORING_BACKLOG_ESTABLISHED"
            if established
            else "TRUE_AUTHORING_BACKLOG_CANDIDATE"
        ),
        "checkpoint_status": (
            "ESTABLISHED" if established else "CANDIDATE_UNVALIDATED"
        ),
        "freshness_authority": "backlog_set_digest",
        "why_no_head_sha": (
            "un checkpoint qui epingle le HEAD courant devient perime des le "
            "commit qui le publie, sans qu'aucune valeur ait bouge. "
            "L'ancrage est donc le SHA du run complet qui le valide, plus le "
            "digest de l'ensemble des unites."
        ),
        "validating_full_run": VALIDATING_RUN,
        "semantic_alignment": semantic,
        "establishment_blockers": (
            []
            if established
            else [
                reason
                for reason, blocked in (
                    ("FULL_SUPPORTED_SUITE_NOT_GREEN", VALIDATING_RUN is None),
                    (
                        "SEMANTIC_ALIGNMENT_NOT_ESTABLISHED_COLLECTION_WIDE",
                        not semantic_established,
                    ),
                )
                if blocked
            ]
        ),
        "definition": (
            "une unite d'ecriture est un couple (capacite, role) qu'aucun "
            "contenu ne sert ; jamais un fichier a produire"
        ),
        "what_is_excluded": {
            "INDETERMINATE_CLONE_CREDIT": (
                "cellules servies par des clones dont le proprietaire "
                "semantique n'est pas demontrable : elles relevent de la revue "
                "humaine, pas de l'ecriture"
            )
        },
        "totals": {
            "cells": coverage["inventory"]["cells"],
            "cells_with_declared_exact_identity": coverage["inventory"][
                "cells_with_declared_exact_identity"
            ],
            "cells_with_indeterminate_credit": coverage["inventory"][
                "cells_with_indeterminate_credit"
            ],
            "AUTHORING_UNITS_REQUIRED_CURRENT": len(backlog),
        },
        "previous_measure": {
            "scope": "projection historique des cinq roles META comparables",
            "authoring_units_required": delta["before_authoring_units"],
            "removed_as_false": delta["false_missing_gaps_removed"],
            "removal_classes": delta["per_removal_class"],
            "after_measurement_authoring_units": delta[
                "after_measurement_authoring_units"
            ],
            "ledger": "audit/FALSE_MISSING_GAP_DELTA.json",
        },
        "real_authoring_closure": {
            "count": delta["real_authoring_closure"]["count"],
            "set_digest": delta["real_authoring_closure"]["set_digest"],
            "ledger": "audit/FALSE_MISSING_GAP_DELTA.json",
        },
        "per_manual": dict(sorted(per_manual.items())),
        "per_role": dict(sorted(per_role.items())),
        "per_chapter": dict(
            sorted(per_chapter.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "per_capacity": dict(
            sorted(per_capacity.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "authoring_unit_projections": projections,
        "open_clone_debt": {
            "objects_on_invalid_credit": clone["inventory"][
                "objects_on_invalid_credit"
            ],
            "objects_with_indeterminate_credit": clone["inventory"][
                "objects_with_indeterminate_credit"
            ],
            "ambiguous_canonical_groups": clone["inventory"][
                "ambiguous_canonical_groups"
            ],
        },
        "backlog_set_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(identifiers, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "authoring_units": identifiers,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    payload = build_checkpoint()
    rendered = render(payload)
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {payload['per_manual']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
