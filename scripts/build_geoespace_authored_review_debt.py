#!/usr/bin/env python3
"""Dette de revue humaine des objets ecrits pour TSPE-GEOMETRIE-ESPACE.

La reconstruction du chapitre a produit quarante objets : seize fiches de
remediation, neuf methodes, huit exercices et leurs huit corriges. Ils sont
verifies par machine -- oracles SymPy verts, zero clone, build RC 0 -- mais
AUCUN humain ne les a relus. Leur statut est donc `generated`, et l'inventaire
les compte, a juste titre, comme des anomalies bloquantes.

Ce registre les declare. Il ne les approuve pas.

C'est la difference que le P0 de clonage a rendue couteuse : ce qui a ete
verifie par une machine n'est pas ce qui a ete valide par un professeur. Le
registre porte donc `in_approved_baseline = false` et `release_blocking =
true`. Les gates restent ROUGES sur ces quarante empreintes, et le seul moyen
de les fermer est le cycle de statut apres revue humaine -- pas ce fichier.

Les empreintes ne sont pas recopiees a la main : elles sont recalculees depuis
l'inventaire par la fonction de l'inventaire lui-meme. Une empreinte ecrite en
dur cesserait un jour de designer l'objet qu'elle nomme.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
OUTPUT = ROOT / "audit/TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_40.json"
CHAPTER = "TSPE-GEOMETRIE-ESPACE"

#: Les objets ecrits pendant la reconstruction. `RE-C7` et `ME-001`
#: preexistaient : ils ne figurent pas ici, et leur dette eventuelle reste ou
#: elle etait. La liste est explicite pour qu'un objet ecrit demain n'entre pas
#: dans cette dette sans decision.
AUTHORED_STEMS = frozenset(
    [f"{CHAPTER}-RE-C{n}" for n in range(1, 17) if n != 7]
    + [f"TSPE-GEOESPACE-ME-{n:03d}" for n in range(2, 11)]
    + [f"TSPE-GEOESPACE-EX-{n:03d}" for n in range(51, 59)]
    + [f"TSPE-GEOESPACE-CO-{n:03d}" for n in range(51, 59)]
)


def _inventory_module():
    spec = importlib.util.spec_from_file_location(
        "inventory_collection", ROOT / "scripts/inventory_collection.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_ledger() -> dict[str, Any]:
    inventory_module = _inventory_module()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    entries: list[dict[str, Any]] = []
    for anomaly in inventory["anomalies"]["blocking_statuses"]:
        path = str(anomaly.get("path") or "")
        if Path(path).stem not in AUTHORED_STEMS:
            continue
        if anomaly.get("chapter") != CHAPTER:
            continue
        fingerprint = inventory_module._anomaly_fingerprint(
            anomaly, category="blocking_statuses", repository_root=ROOT
        )
        entries.append(
            {
                "object_id": anomaly.get("id") or Path(path).stem,
                "path": path,
                "category": "blocking_statuses",
                "status": anomaly.get("status"),
                "scope": anomaly.get("scope"),
                "fingerprint": fingerprint,
                "logical_owner": "direction_scientifique_programme",
                "policy_disposition": "open_debt",
                "in_approved_baseline": False,
                "human_review_required": True,
                "release_blocking": True,
                "release_acceptance": False,
            }
        )

    entries.sort(key=lambda row: row["path"])
    missing = AUTHORED_STEMS - {Path(row["path"]).stem for row in entries}
    if missing:
        raise ValueError(f"objets ecrits absents des anomalies: {sorted(missing)}")

    fingerprints = sorted(row["fingerprint"] for row in entries)
    if len(set(fingerprints)) != len(entries):
        raise ValueError("empreintes non univoques")

    return {
        "artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER",
        "ledger_id": "TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_40",
        "schema_version": 1,
        "generated_by": "scripts/build_geoespace_authored_review_debt.py",
        "chapter": CHAPTER,
        "count": len(entries),
        "fingerprint_set_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(fingerprints, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "human_review_required": True,
        "release_blocking": True,
        "release_acceptance": False,
        "in_approved_baseline": False,
        "is_baseline_qualification": False,
        "is_gate_exception": False,
        "semantics": (
            "Registre d'observation. Il n'inscrit rien dans la baseline "
            "approuvee, ne materialise aucune qualification, et ne doit rendre "
            "vert ni validate-model ni fail-on-new. La fermeture doit venir du "
            "cycle de statut apres revue humaine."
        ),
        "why_created": (
            "La reconstruction du chapitre a produit quarante objets verifies "
            "par machine -- oracles SymPy verts, zero clone, build RC 0 -- que "
            "personne n'a relus. Ce qui est verifie par une machine n'est pas "
            "ce qui est valide par un professeur : ces objets restent "
            "bloquants jusqu'a la revue humaine."
        ),
        "machine_verification_performed": {
            "sympy_oracles": "56/56 verts",
            "content_clones": 0,
            "near_clones_above_0_50": 0,
            "build_rc": 0,
            "note": (
                "aucune de ces verifications ne remplace la lecture par un "
                "professeur de la discipline"
            ),
        },
        "human_review_packets": {
            "EXPERT_MATHEMATIQUE": "PENDING_UNASSIGNED",
            "EXPERT_PROGRAMME_PEDAGOGIE": "PENDING_UNASSIGNED",
        },
        "expected_gate_behaviour": {
            "check": "rouge sur ces empreintes",
            "validate-model": "rouge sur ces empreintes",
            "fail-on-new": "rouge sur ces empreintes",
            "release-strict": "rouge",
        },
        "entries": entries,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)

    rendered = render(build_ledger())
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {json.loads(rendered)['count']} lignes")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
