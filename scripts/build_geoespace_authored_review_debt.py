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
OUTPUT = ROOT / "audit/TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45.json"
CHAPTER = "TSPE-GEOMETRIE-ESPACE"

#: Objets CREES par la reconstruction. Ils n'ont jamais eu d'approbation.
#: `RE-C7` n'y figure pas : c'est la fiche originale, celle dont les seize
#: autres etaient la copie.
CREATED_STEMS = frozenset(
    [f"{CHAPTER}-RE-C{n}" for n in range(1, 17) if n != 7]
    + [f"TSPE-GEOESPACE-ME-{n:03d}" for n in range(2, 11)]
    + [f"TSPE-GEOESPACE-EX-{n:03d}" for n in range(51, 59)]
    + [f"TSPE-GEOESPACE-CO-{n:03d}" for n in range(51, 59)]
)

#: Objets REECRITS qui portaient `status: approved` au gel 447915e8. Les
#: reecrire a invalide cette approbation : elle avait ete donnee pour un
#: contenu qui n'existe plus. Leur statut est retombe a `generated`, et c'est
#: la seule issue correcte -- une approbation ne suit pas le chemin d'un
#: fichier, elle suit son contenu.
#:
#: Ils sont distingues des precedents parce que la perte d'une approbation
#: humaine acquise n'est pas la meme dette que l'absence d'approbation : elle
#: doit etre visible comme une regression assumee, pas fondue dans le lot.
REWRITTEN_PREVIOUSLY_APPROVED_STEMS = frozenset(
    {
        "TSPE-GEOESPACE-EV-A",
        "TSPE-GEOESPACE-EV-A-corrige",
        "TSPE-GEOESPACE-EV-B",
        "TSPE-GEOESPACE-EV-B-corrige",
        "TSPE-GEOESPACE-ME-001",
    }
)

APPROVAL_FREEZE_SHA = "447915e8fee6b59e1c248c805e28d0fcdd234f0d"
AUTHORED_STEMS = CREATED_STEMS | REWRITTEN_PREVIOUSLY_APPROVED_STEMS


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
        stem = Path(path).stem
        rewritten = stem in REWRITTEN_PREVIOUSLY_APPROVED_STEMS
        entries.append(
            {
                "object_id": anomaly.get("id") or stem,
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
                "origin": "REWRITTEN" if rewritten else "CREATED",
                "status_before_rewrite": "approved" if rewritten else None,
                "human_approval_invalidated_by_rewrite": rewritten,
            }
        )

    entries.sort(key=lambda row: row["path"])
    missing = AUTHORED_STEMS - {Path(row["path"]).stem for row in entries}
    if missing:
        raise ValueError(f"objets ecrits absents des anomalies: {sorted(missing)}")

    fingerprints = sorted(row["fingerprint"] for row in entries)
    if len(set(fingerprints)) != len(entries):
        raise ValueError("empreintes non univoques")

    if len(entries) != len(AUTHORED_STEMS):
        raise ValueError(f"attendu {len(AUTHORED_STEMS)} lignes, obtenu {len(entries)}")

    return {
        "artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER",
        "ledger_id": "TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45",
        "schema_version": 1,
        "generated_by": "scripts/build_geoespace_authored_review_debt.py",
        "chapter": CHAPTER,
        "count": len(entries),
        "counts_by_origin": {
            "CREATED": sum(1 for row in entries if row["origin"] == "CREATED"),
            "REWRITTEN": sum(1 for row in entries if row["origin"] == "REWRITTEN"),
        },
        "approval_freeze_sha": APPROVAL_FREEZE_SHA,
        "human_approvals_invalidated": sorted(
            row["path"] for row in entries if row["human_approval_invalidated_by_rewrite"]
        ),
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
            "La reconstruction du chapitre a produit quarante-cinq objets verifies "
            "par machine -- oracles SymPy verts, zero clone, build RC 0 -- que "
            "personne n'a relus. Ce qui est verifie par une machine n'est pas "
            "ce qui est valide par un professeur : ces objets restent "
            "bloquants jusqu'a la revue humaine. Cinq d'entre eux portaient "
            "deja `status: approved` au gel 447915e8 ; les reecrire a invalide "
            "cette approbation, qui avait ete donnee pour un contenu qui "
            "n'existe plus. Cette perte est declaree, pas absorbee."
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
