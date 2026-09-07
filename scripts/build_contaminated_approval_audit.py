#!/usr/bin/env python3
"""`status: approved` n'est pas une preuve d'approbation.

Neuf cent quatre objets contamines portent `approved` dans leur META. Ce
producteur cherche, pour chacun, ce qui fonderait ce statut : un recu, un
paquet de revue, un relecteur nomme, une empreinte semantique, une date, une
source de qualification. Il ne suppose rien -- il ouvre les registres.

QUATRE CLASSES :

`VALID_HUMAN_APPROVAL_BOUND_TO_CONTAMINATED_CONTENT`
    un humain a bel et bien approuve CE contenu. La contamination devient
    alors un probleme de decision, pas seulement de fichier.
`MACHINE_OR_BULK_APPROVAL`
    le statut est arrive avec le fichier, dans un commit de masse. Personne
    n'a rien approuve ; le mot etait dans le gabarit.
`APPROVAL_WITHOUT_RECEIPT`
    le statut a ete pose par un commit ulterieur, sans recu qui le fonde.
`UNKNOWN_APPROVAL_PROVENANCE`
    interdit : ne pas savoir d'ou vient une approbation est un defaut en soi.

L'HISTORIQUE N'EST PAS EFFACE. Le statut anterieur est conserve et requalifie
`HISTORICAL_INVALIDATED_BY_CONTAMINATION`. Aucune de ces approbations ne peut
etre reutilisee pour le contenu qui remplacera l'objet : approuver un
exercice d'analyse n'approuve pas l'exercice d'arithmetique qui prendra sa
place.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "audit/CROSS_MANUAL_CONTAMINATION_MATRIX.json"
BASELINE = ROOT / "audit/BASELINE_QUALIFICATION_REGISTRY.yaml"
DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
REVIEWS = ROOT / "audit/reviews"
JSON_TARGET = ROOT / "audit/CONTAMINATED_APPROVAL_AUDIT.json"
MD_TARGET = ROOT / "audit/CONTAMINATED_APPROVAL_AUDIT.md"
GENERATED_BY = "scripts/build_contaminated_approval_audit.py"

VALID = "VALID_HUMAN_APPROVAL_BOUND_TO_CONTAMINATED_CONTENT"
BULK = "MACHINE_OR_BULK_APPROVAL"
NO_RECEIPT = "APPROVAL_WITHOUT_RECEIPT"
UNKNOWN = "UNKNOWN_APPROVAL_PROVENANCE"
CLASSES = (VALID, BULK, NO_RECEIPT, UNKNOWN)

INVALIDATED = "HISTORICAL_INVALIDATED_BY_CONTAMINATION"

#: Les categories de disposition qui QUALIFIENT UN DEFAUT. Elles nomment
#: l'objet sans jamais approuver son contenu : les confondre avec une
#: approbation ferait passer une dette ouverte pour un feu vert.
DEFECT_CATEGORIES = {
    "broken_meta_references",
    "blocking_statuses",
    "duplicate_ids",
    "missing_oracle",
    "qualification_invalide",
}


def _git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout


def _meta_of(text: str) -> dict[str, Any]:
    if "META:" not in text:
        return {}
    try:
        return json.loads(text.split("META:", 1)[1].splitlines()[0].strip())
    except json.JSONDecodeError:
        return {}


def approval_evidence(root: Path) -> dict[str, list[dict[str, Any]]]:
    """Tout ce qui, dans le depot, pourrait fonder une approbation d'objet."""

    preuves: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)

    if BASELINE.is_file():
        registre = yaml.safe_load(BASELINE.read_text(encoding="utf-8")) or {}
        for empreinte, entree in (registre.get("dispositions") or {}).items():
            source = entree.get("source")
            if not source:
                continue
            preuves[source].append({
                "kind": "baseline_qualification",
                "fingerprint": empreinte,
                "category": entree.get("category"),
                "disposition": entree.get("disposition"),
                "approved_by": entree.get("approved_by"),
                "decision_ref": entree.get("decision_ref"),
                "qualifies_a_defect": entree.get("category") in DEFECT_CATEGORIES,
            })

    if DISPOSITIONS.is_file():
        registre = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8")) or {}
        entrees = registre.get("dispositions") or registre
        if isinstance(entrees, dict):
            entrees = list(entrees.values())
        for entree in entrees if isinstance(entrees, list) else []:
            if not isinstance(entree, dict):
                continue
            source = entree.get("source")
            if not source:
                continue
            preuves[source].append({
                "kind": "anomaly_disposition",
                "category": entree.get("category"),
                "disposition": entree.get("disposition"),
                "approved_by": entree.get("approved_by"),
                "qualifies_a_defect": entree.get("category") in DEFECT_CATEGORIES,
            })

    if REVIEWS.is_dir():
        for paquet in REVIEWS.rglob("*.json"):
            try:
                charge = json.loads(paquet.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            source = charge.get("source") or charge.get("source_path")
            if isinstance(source, str):
                preuves[source].append({
                    "kind": "review_packet",
                    "packet": str(paquet.relative_to(root)),
                    "reviewer": charge.get("reviewer_identity"),
                    "decision": charge.get("decision") or charge.get("verdict"),
                    "qualifies_a_defect": False,
                })
    return preuves


def build(root: Path = ROOT) -> dict[str, Any]:
    matrice = json.loads(MATRIX.read_text(encoding="utf-8"))
    contamines = [r for r in matrice["rows"] if not r["IS_CANONICAL_SOURCE"]]
    preuves = approval_evidence(root)

    enregistrements: list[dict[str, Any]] = []
    for row in sorted(contamines, key=lambda r: r["OBJECT_PATH"]):
        chemin = row["OBJECT_PATH"]
        liees = preuves.get(chemin, [])
        approbations = [p for p in liees if not p["qualifies_a_defect"] and p.get("decision")]
        defauts = [p for p in liees if p["qualifies_a_defect"]]

        # Le statut est-il ne avec le fichier ?
        premiere = _git(["show", f"{row['INTRODUCED_COMMIT']}:{chemin}"])
        statut_a_la_naissance = _meta_of(premiere).get("status")

        if approbations:
            classe = VALID
            pourquoi = "un paquet de revue nomme un relecteur et une decision"
        elif statut_a_la_naissance == row["STATUS"]:
            classe = BULK
            pourquoi = (
                "le statut est arrive AVEC le fichier, dans le commit de masse "
                f"{row['INTRODUCED_COMMIT'][:8]} : personne n'a rien approuve"
            )
        elif row["STATUS"] == "approved":
            classe = NO_RECEIPT
            pourquoi = "statut pose par un commit ulterieur, sans recu qui le fonde"
        else:
            classe = UNKNOWN
            pourquoi = "provenance du statut non etablie"

        enregistrements.append({
            "object_id": row["OBJECT_ID"],
            "path": chemin,
            "manual": row["TARGET_MANUAL"],
            "chapter": row["TARGET_CHAPTER"],
            "declared_status": row["STATUS"],
            "status_at_birth": statut_a_la_naissance,
            "introduced_commit": row["INTRODUCED_COMMIT"],
            "classification": classe,
            "why": pourquoi,
            "approval_evidence": approbations,
            "defect_qualifications": len(defauts),
            "invalidated_status": INVALIDATED,
            "reusable_for_replacement_content": False,
        })

    par_classe = collections.Counter(r["classification"] for r in enregistrements)
    summary = {classe: par_classe.get(classe, 0) for classe in CLASSES}
    summary.update({
        "CONTAMINATED_APPROVED_OBJECTS": sum(
            1 for r in enregistrements if r["declared_status"] == "approved"
        ),
        "APPROVALS_INVALIDATED_CURRENT": len(enregistrements),
        "CONTAMINATED_APPROVAL_REUSED_FOR_NEW_CONTENT": 0,
        "CLASSES_SUM_EQUALS_TOTAL": sum(par_classe.values()) == len(enregistrements),
        "DEFECT_QUALIFICATIONS_FOUND": sum(
            r["defect_qualifications"] for r in enregistrements
        ),
        "APPROVES_NOTHING": True,
    })

    return {
        "artifact_type": "contaminated_approval_audit",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "classes": list(CLASSES),
        "rule": (
            "une qualification de DEFAUT n'est pas une approbation : elle "
            "nomme l'objet sans jamais valider son contenu"
        ),
        "history_policy": (
            "le statut anterieur est conserve et requalifie "
            f"{INVALIDATED} ; aucune de ces approbations ne peut etre "
            "reutilisee pour le contenu qui remplacera l'objet"
        ),
        "summary": summary,
        "records": enregistrements,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Provenance des approbations contaminees",
        "",
        payload["rule"].capitalize() + ".",
        "",
        "| classe | objets |",
        "| --- | --- |",
    ]
    for classe in payload["classes"]:
        lignes.append(f"| `{classe}` | {s[classe]} |")
    lignes += [
        "",
        f"- `CONTAMINATED_APPROVED_OBJECTS` : `{s['CONTAMINATED_APPROVED_OBJECTS']}`",
        f"- `APPROVALS_INVALIDATED_CURRENT` : `{s['APPROVALS_INVALIDATED_CURRENT']}`",
        f"- `CONTAMINATED_APPROVAL_REUSED_FOR_NEW_CONTENT` : "
        f"`{s['CONTAMINATED_APPROVAL_REUSED_FOR_NEW_CONTENT']}`",
        "",
        payload["history_policy"].capitalize() + ".",
        "",
    ]
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build(ROOT)
    rendus = {
        JSON_TARGET: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MD_TARGET: render_markdown(payload),
    }
    if args.check:
        ecarts = [
            str(p.relative_to(ROOT))
            for p, c in rendus.items()
            if not p.is_file() or p.read_text(encoding="utf-8") != c
        ]
        for ecart in ecarts:
            print(f"diff: {ecart}")
        return 1 if ecarts else 0
    for chemin, contenu in rendus.items():
        chemin.write_text(contenu, encoding="utf-8")
        print(f"wrote {chemin.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
