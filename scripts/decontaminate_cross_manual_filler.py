#!/usr/bin/env python3
"""Retirer les objets contamines, et garder la trace de ce qui est retire.

Neuf cent quatre objets pedagogiques sont des copies exactes d'un contenu
appartenant a un autre chapitre, crediteurs de capacites qu'ils ne servent
pas. L'archeologie a etabli qu'AUCUN n'a jamais porte autre chose : il n'y a
rien a restaurer, seulement a retirer.

CE N'EST PAS UN SLOT A REMPLIR. Un fichier `EX-037` qui n'a jamais contenu de
pedagogie ne cree pas le devoir d'ecrire un nouvel `EX-037`. Le besoin
pedagogique sera recalcule APRES le retrait, sur le contrat du chapitre, et
les identifiants n'ont pas a rester continus. Ce producteur conserve donc un
registre `RETIRED_SYNTHETIC_OBJECT_IDS` -- pour que l'historique reste
lisible -- et rien d'autre : aucun gabarit vide n'est laisse derriere.

Les recus de validation d'un objet retire partent avec lui : une preuve
d'execution qui ne designe plus rien est un mensonge en attente.
"""

from __future__ import annotations

import argparse
import collections
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "audit/CROSS_MANUAL_CONTAMINATION_MATRIX.json"
APPROVALS = ROOT / "audit/CONTAMINATED_APPROVAL_AUDIT.json"
REGISTRY = ROOT / "audit/RETIRED_SYNTHETIC_OBJECT_IDS.json"
GENERATED_BY = "scripts/decontaminate_cross_manual_filler.py"

RECEIPT_SUFFIXES = (".sympy.json", ".execution.json")


def plan(root: Path = ROOT) -> dict[str, Any]:
    """Le retrait courant, CUMULE avec les vagues precedentes.

    La detection s'est affinee en cours de route : les copies d'exercices se
    voyaient des que l'identite de l'objet quittait le corps compare, celles
    des fiches de remediation seulement quand les identifiants de leurs
    SOUS-objets l'ont quittee aussi. Le registre garde les deux vagues : un
    identifiant retire ne doit jamais disparaitre de la trace parce qu'une
    vague ulterieure ne le voit plus.
    """

    matrice = json.loads(MATRIX.read_text(encoding="utf-8"))
    approbations = {
        r["path"]: r for r in json.loads(APPROVALS.read_text(encoding="utf-8"))["records"]
    }
    contamines = [r for r in matrice["rows"] if not r["IS_CANONICAL_SOURCE"]]

    entrees: list[dict[str, Any]] = []
    for row in sorted(contamines, key=lambda r: r["OBJECT_PATH"]):
        chemin = Path(row["OBJECT_PATH"])
        recus = []
        for suffixe in RECEIPT_SUFFIXES:
            recu = chemin.parent.parent / "validations" / (chemin.stem + suffixe)
            if (root / recu).is_file():
                recus.append(str(recu))
        approbation = approbations.get(row["OBJECT_PATH"], {})
        entrees.append({
            "object_id": row["OBJECT_ID"],
            "path": row["OBJECT_PATH"],
            "manual": row["TARGET_MANUAL"],
            "chapter": row["TARGET_CHAPTER"],
            "object_type": row["OBJECT_TYPE"],
            "declared_capacity": row["CAPACITY"],
            "group_id": row["GROUP_ID"],
            "copied_from_chapter": row["ORIGINAL_LINEAGE_CHAPTER"],
            "copied_from_object": row["ORIGINAL_LINEAGE"],
            "introduced_commit": row["INTRODUCED_COMMIT"],
            "historical_status": row["STATUS"],
            "invalidated_status": approbation.get(
                "invalidated_status", "HISTORICAL_INVALIDATED_BY_CONTAMINATION"
            ),
            "approval_provenance": approbation.get("classification"),
            "validation_receipts_removed": recus,
            "retirement_reason": "CROSS_MANUAL_PEDAGOGICAL_CONTAMINATION",
            "authentic_content_available": False,
            "replacement_obligation": (
                "aucune : le besoin pedagogique est recalcule sur le contrat "
                "du chapitre, pas sur le nombre de fichiers retires"
            ),
        })

    if REGISTRY.is_file():
        deja = json.loads(REGISTRY.read_text(encoding="utf-8")).get("retired", [])
        connus = {e["path"] for e in entrees}
        entrees.extend(e for e in deja if e["path"] not in connus)
        entrees.sort(key=lambda e: e["path"])

    par_chapitre: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for entree in entrees:
        par_chapitre[entree["chapter"]][entree["object_type"]] += 1

    return {
        "artifact_type": "retired_synthetic_object_ids",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "finding": "CROSS_MANUAL_PEDAGOGICAL_CONTAMINATION",
        "root_cause_id": "533d1919_SYNTHETIC_CROSS_MANUAL_FILLER",
        "policy": (
            "un identifiant retire n'est pas un emplacement a repourvoir ; les "
            "identifiants n'ont pas a rester continus, et aucun gabarit vide "
            "n'est laisse dans le manuel"
        ),
        "summary": {
            "RETIRED_OBJECTS": len(entrees),
            "RETIRED_VALIDATION_RECEIPTS": sum(
                len(e["validation_receipts_removed"]) for e in entrees
            ),
            "RETIRED_BY_TYPE": dict(sorted(
                collections.Counter(e["object_type"] for e in entrees).items()
            )),
            "CHAPTERS_TOUCHED": len(par_chapitre),
            "APPROVES_NOTHING": True,
        },
        "per_chapter": {
            ch: dict(sorted(compte.items())) for ch, compte in sorted(par_chapitre.items())
        },
        "retired": entrees,
    }


def apply(root: Path, payload: dict[str, Any]) -> list[str]:
    chemins = [e["path"] for e in payload["retired"]]
    chemins += [
        recu for e in payload["retired"] for recu in e["validation_receipts_removed"]
    ]
    existants = [c for c in chemins if (root / c).is_file()]
    for lot in range(0, len(existants), 200):
        subprocess.run(
            ["git", "rm", "-q", "--", *existants[lot : lot + 200]],
            cwd=root, check=True,
        )
    return existants


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="retirer reellement")
    args = parser.parse_args(argv)
    payload = plan(ROOT)
    REGISTRY.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {REGISTRY.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    if args.apply:
        retires = apply(ROOT, payload)
        print(f"retires du depot : {len(retires)} fichiers")
    else:
        print("(--apply non passe : rien n'a ete retire)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
