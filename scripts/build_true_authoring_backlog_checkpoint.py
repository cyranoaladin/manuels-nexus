#!/usr/bin/env python3
"""Le point de depart honnete de l'ecriture : ce qui manque REELLEMENT.

Le backlog annonce 460 unites d'ecriture. Il en comptait 136 qui n'existaient
pas : du contenu present que la mesure ne savait pas reconnaitre, faute de
resoudre l'identite des capacites, et des clones dont le proprietaire n'etant
pas demontrable ne relevent pas de l'ecriture mais de la revue.

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
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
DELTA = ROOT / "audit/FALSE_MISSING_GAP_DELTA.json"
CLONE = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
OUTPUT = ROOT / "audit/TRUE_AUTHORING_BACKLOG_ESTABLISHED.json"

#: Run complet vert qui autorise le gel. Sans lui le chiffre n'a pas d'autorite.
VALIDATING_RUN = {
    "source_sha": "52c061428f472f9926829d5c5a4e1c74c7392e58",
    "collected": 9277,
    "passed": 9277,
    "failed": 0,
    "errors": 0,
    "rc": 0,
    "log_sha256": (
        "be8bdc6d3dba6162385f9da5b11f6240ce47dbfeaa8eef0a109cb3c3437adeff"
    ),
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
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()

    return {
        "artifact_type": "true_authoring_backlog_established",
        "schema_version": 1,
        "generated_by": "scripts/build_true_authoring_backlog_checkpoint.py",
        "checkpoint": "TRUE_AUTHORING_BACKLOG_ESTABLISHED",
        "observed_source_sha": head,
        "validating_full_run": VALIDATING_RUN,
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
            "cells_with_valid_content": coverage["inventory"][
                "cells_with_valid_content"
            ],
            "cells_with_indeterminate_credit": coverage["inventory"][
                "cells_with_indeterminate_credit"
            ],
            "AUTHORING_UNITS_REQUIRED_CURRENT": len(backlog),
        },
        "previous_measure": {
            "authoring_units_required": delta["before_authoring_units"],
            "removed_as_false": delta["false_missing_gaps_removed"],
            "removal_classes": delta["per_removal_class"],
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
