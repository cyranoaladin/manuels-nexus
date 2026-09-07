#!/usr/bin/env python3
"""Registre de la dette de revue créée par l'écriture de cette branche.

`fail-on-new` compare la dette active à la baseline approuvée et refuse toute
nouveauté NON DÉCLARÉE. C'est la bonne règle : écrire un objet ne le fait pas
relire, et un compteur qui ne bougerait pas quand on écrit soixante fiches
serait un compteur menteur.

Ce producteur ne rend rien vert. Il DÉCLARE : voici les empreintes que
l'écriture de cette branche a créées, voici les fichiers qui les portent, et
voici pourquoi chacun reste bloquant jusqu'à revue humaine.

CRITÈRE D'APPARTENANCE, VÉRIFIABLE. Un objet entre dans ce registre si et
seulement si son fichier a été AJOUTÉ depuis la base de branche — `git diff
--diff-filter=A base..HEAD` — et s'il porte une dette active. Aucune liste
recopiée à la main : le registre est dérivé, et une dette qui viendrait
d'ailleurs n'y entre pas.

CE QUE LE REGISTRE N'EST PAS. Il n'inscrit rien dans la baseline approuvée,
ne matérialise aucune qualification, n'accorde aucune acceptation de release.
La fermeture viendra du cycle de statut après revue humaine, jamais d'ici.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import inventory_collection as ic  # noqa: E402

OUTPUT = ROOT / "audit/T3_AUTHORED_REVIEW_DEBT.json"
LEDGER_ID = "T3_AUTHORED_REVIEW_DEBT"
BASELINE_SHA = "58f23b71"

#: Registres déjà déposés. Une empreinte déclarée ailleurs n'est pas redéclarée
#: ici : les consommateurs exigent des ensembles DISJOINTS, et une empreinte
#: comptée deux fois gonflerait la dette sans qu'aucun objet ne soit ajouté.
#:
#: Cette liste est celle de `build_residual_true_new_forensics.py`, qui est
#: l'autorité : une première version n'en reprenait que six, celles que le
#: test d'inventaire citait, et redéclarait donc les entrées des cinq autres.
OTHER_LEDGERS = tuple(
    str(path) for path in __import__(
        "importlib"
    ).import_module("build_residual_true_new_forensics").DECLARED_DEBT_LEDGERS
    if str(path) != "audit/T3_AUTHORED_REVIEW_DEBT.json"
)

ROLE_OF_DIRECTORY = {
    "cours": "cours",
    "exercices": "exercices",
    "corriges": "corriges",
    "methodes": "methodes",
    "evaluations": "evaluations",
    "remediation": "remediation",
    "qcm": "qcm",
    "amenagee": "amenagee",
    "banque_ecrite": "banque_ecrite",
    "banque_pratique": "banque_pratique",
    "projets": "projets",
}


def _added_paths(root: Path, baseline: str) -> set[str]:
    completed = subprocess.run(
        ["git", "diff", "--diff-filter=A", "--name-only", f"{baseline}..HEAD"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def _role(path: str) -> str:
    for part in Path(path).parts:
        if part in ROLE_OF_DIRECTORY:
            return ROLE_OF_DIRECTORY[part]
    return "autre"


def _digest(root: Path, relative: str) -> str | None:
    candidate = root / relative
    if not candidate.is_file():
        return None
    return "sha256:" + hashlib.sha256(candidate.read_bytes()).hexdigest()


def _declared_elsewhere(root: Path) -> set[str]:
    declared: set[str] = set()
    for relative in OTHER_LEDGERS:
        payload = json.loads((root / relative).read_text(encoding="utf-8"))
        declared |= {str(e["fingerprint"]) for e in payload["entries"]}
    return declared


def build(root: Path = ROOT, baseline: str = BASELINE_SHA) -> dict[str, Any]:
    added = _added_paths(root, baseline)
    inventory = ic.build_inventory(root)
    active = ic._current_active_debt(inventory)
    gate = ic._fail_on_new_gate(root)
    genuinely_new = set(gate.get("comparison", {}).get("new", ()))
    elsewhere = _declared_elsewhere(root)

    entries = []
    for row in active:
        fingerprint = str(row["fingerprint"])
        if fingerprint in elsewhere:
            continue
        locator = json.loads(row["locator_key"])
        source = str(locator.get("source") or "")
        if source not in added:
            continue
        if fingerprint not in genuinely_new:
            raise ValueError(
                f"{fingerprint} porté par un fichier ajouté mais absent des "
                "nouveautés du gate : le critère ne tient pas"
            )
        entries.append({
            "fingerprint": fingerprint,
            "object_id": locator.get("target_or_id"),
            "path": source,
            "chapter": locator.get("chapter"),
            "manual": locator.get("manual"),
            "role": _role(source),
            "category": row["category"],
            "origin": "CREATED",
            "source_sha256": _digest(root, source),
            "policy_disposition": "open_debt",
            "in_approved_baseline": False,
            "human_review_required": True,
            "release_blocking": True,
            "release_acceptance": False,
        })
    entries.sort(key=lambda e: e["fingerprint"])

    fingerprints = [e["fingerprint"] for e in entries]
    if len(set(fingerprints)) != len(fingerprints):
        raise ValueError("empreintes dupliquées dans le registre")

    by_chapter: dict[str, int] = {}
    by_role: dict[str, int] = {}
    for entry in entries:
        by_chapter[entry["chapter"]] = by_chapter.get(entry["chapter"], 0) + 1
        by_role[entry["role"]] = by_role.get(entry["role"], 0) + 1

    payload = {
        "artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER",
        "ledger_id": LEDGER_ID,
        "schema_version": 1,
        "generated_by": "scripts/build_t3_authored_review_debt.py",
        "baseline_sha": baseline,
        "membership_rule": (
            "Fichier AJOUTÉ depuis la base de branche (git diff "
            "--diff-filter=A) ET porteur d'une dette active non déclarée "
            "ailleurs."
        ),
        "count": len(entries),
        "counts_by_chapter": dict(sorted(by_chapter.items())),
        "counts_by_role": dict(sorted(by_role.items())),
        "counts_by_origin": {"CREATED": len(entries)},
        "human_review_required": True,
        "release_blocking": True,
        "release_acceptance": False,
        "in_approved_baseline": False,
        "is_baseline_qualification": False,
        "is_gate_exception": False,
        "semantics": (
            "Registre d'observation. Il n'inscrit rien dans la baseline "
            "approuvée, ne matérialise aucune qualification, et ne rend vert "
            "aucun gate. La fermeture doit venir du cycle de statut après "
            "revue humaine."
        ),
        "why_created": (
            "L'écriture de cette branche a produit des objets pédagogiques "
            "qui n'ont pas encore été relus : fiches méthode, versions "
            "aménagées, banques d'entraînement, et les capacités que les "
            "contrats promettaient sans que rien ne les enseigne. Chacun est "
            "bloquant jusqu'à revue, et `fail-on-new` doit le voir."
        ),
        "expected_gate_behaviour": (
            "fail-on-new reste ROUGE tant que ces objets n'ont pas été relus."
        ),
        "entries": entries,
    }
    payload["fingerprint_set_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(sorted(fingerprints), separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload["paths_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(sorted(e["path"] for e in entries),
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--baseline", default=BASELINE_SHA)
    args = parser.parse_args()

    payload = build(baseline=args.baseline)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT.is_file():
            print(f"{LEDGER_ID} check: MISSING")
            return 1
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"{LEDGER_ID} check: STALE")
            return 1
        print(f"{LEDGER_ID} check: OK")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "count": payload["count"],
        "counts_by_role": payload["counts_by_role"],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
