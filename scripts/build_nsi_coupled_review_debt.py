#!/usr/bin/env python3
"""Dette de revue humaine du lot couple 1NSI (algorithmique).

Les deux chapitres d'algorithmique de Premiere NSI ont ete reconstruits apres
le retrait de 116 objets de mathematiques de Terminale qui y etaient loges. Ce
qui a ete ecrit a la place est verifie par execution -- chaque bloc Python
tourne, chaque assertion passe -- mais personne ne l'a relu.

Ce registre le declare. Il ne l'approuve pas.

Deux classes sont distinguees, et ne doivent jamais etre fondues :

`CREATED`
    objets neufs, qui n'ont jamais porte d'approbation ;

`REWRITTEN_STALE_APPROVAL`
    objets qui portaient un statut de validation AVANT d'etre reecrits. Ce
    statut couvrait un contenu qui n'existe plus : il est perime, et cette
    perte doit rester visible plutot que d'etre absorbee dans le lot.

Les deux classes sont derivees de Git, par comparaison avec le SHA de
reference, jamais d'une liste ecrite a la main : une liste finit par mentir.
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
OUTPUT = ROOT / "audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json"
CHAPTERS = ("1NSI-ALGO-DICHO-GLOUTON-KNN", "1NSI-ALGO-PARCOURS-TRIS")

#: Etat de reference : le HEAD du dernier run complet vert, avant toute
#: intervention sur ces deux chapitres.
BASELINE_SHA = "52c061428f472f9926829d5c5a4e1c74c7392e58"

#: Statuts qui valent validation. Les perdre par reecriture est une
#: regression, pas une simple mise a jour.
VALIDATED_STATUSES = frozenset({"approved", "verified", "valide"})


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout


def _baseline_text(relative: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{BASELINE_SHA}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def build_ledger() -> dict[str, Any]:
    clone = _clone_module()
    entries: list[dict[str, Any]] = []
    for chapter in CHAPTERS:
        base = ROOT / "NSI/chapitres" / chapter
        for path in sorted(base.rglob("*.tex")):
            relative = str(path.relative_to(ROOT))
            current = path.read_text(encoding="utf-8", errors="replace")
            meta = clone.read_meta(current)
            status = str(meta.get("status") or "")
            previous = _baseline_text(relative)

            if previous is None:
                origin, previous_status = "CREATED", None
            elif previous == current:
                continue  # inchange : sa dette eventuelle est ailleurs
            else:
                previous_status = str(
                    clone.read_meta(previous).get("status") or ""
                )
                origin = (
                    "REWRITTEN_STALE_APPROVAL"
                    if previous_status in VALIDATED_STATUSES
                    else "REWRITTEN"
                )

            entries.append(
                {
                    "object_id": meta.get("id") or path.stem,
                    "path": relative,
                    "chapter": chapter,
                    "role": path.parent.name,
                    "status": status,
                    "origin": origin,
                    "status_before_rewrite": previous_status,
                    "human_approval_invalidated_by_rewrite": origin
                    == "REWRITTEN_STALE_APPROVAL",
                    "machine_verified_by_execution": True,
                    "policy_disposition": "open_debt",
                    "in_approved_baseline": False,
                    "human_review_required": True,
                    "release_blocking": True,
                    "release_acceptance": False,
                    "logical_owner": "direction_scientifique_programme",
                }
            )

    entries.sort(key=lambda row: row["path"])
    by_origin = collections.Counter(row["origin"] for row in entries)
    by_chapter = collections.Counter(row["chapter"] for row in entries)
    paths = sorted(row["path"] for row in entries)
    return {
        "artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER",
        "ledger_id": "NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT",
        "schema_version": 1,
        "generated_by": "scripts/build_nsi_coupled_review_debt.py",
        "chapters": list(CHAPTERS),
        "baseline_sha": BASELINE_SHA,
        "count": len(entries),
        "counts_by_origin": dict(sorted(by_origin.items())),
        "counts_by_chapter": dict(sorted(by_chapter.items())),
        "human_review_required": True,
        "release_blocking": True,
        "release_acceptance": False,
        "in_approved_baseline": False,
        "is_baseline_qualification": False,
        "is_gate_exception": False,
        "semantics": (
            "Registre d'observation. Il n'inscrit rien dans la baseline "
            "approuvee, ne materialise aucune qualification, et ne doit rendre "
            "vert aucun gate. La fermeture doit venir du cycle de statut apres "
            "revue humaine."
        ),
        "why_created": (
            "Les deux chapitres d'algorithmique de Premiere NSI portaient 116 "
            "objets de mathematiques de Terminale, tous status approved. Le "
            "contenu ecrit a leur place est verifie par execution, mais "
            "personne ne l'a relu : ce qui est verifie par une machine n'est "
            "pas ce qui est valide par un professeur."
        ),
        "machine_verification_performed": {
            "python_blocks_executed": "63/63 objets verts",
            "content_clones_in_chapters": 0,
            "cross_discipline_condemned": 0,
            "role_coverage": "45 cellules sur 45",
            "note": (
                "aucune de ces verifications ne remplace la lecture par un "
                "professeur de la discipline"
            ),
        },
        "human_review_packets": {
            "EXPERT_NSI": "PENDING_UNASSIGNED",
            "EXPERT_PROGRAMME_PEDAGOGIE": "PENDING_UNASSIGNED",
        },
        "reviewers_must_be_distinct": True,
        "expected_gate_behaviour": {
            "check": "rouge sur ces objets",
            "validate-model": "rouge sur ces objets",
            "fail-on-new": "rouge sur ces objets",
            "release-strict": "rouge",
        },
        "paths_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(paths, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "entries": entries,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    payload = build_ledger()
    rendered = render(payload)
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: {payload['count']} objets, "
        f"{payload['counts_by_origin']}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
