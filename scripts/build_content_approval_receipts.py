#!/usr/bin/env python3
"""Recus d'approbation : ce qu'un humain a valide, et si cela tient encore.

Un objet qui porte `status: approved` affirme qu'un humain a relu ce que
l'eleve lira. Si le texte a change depuis, l'affirmation est fausse -- et
personne ne s'en apercoit, parce que le champ, lui, n'a pas bouge.

Ce producteur remonte l'historique de chaque objet jusqu'au commit ou le
statut approbatif a ete pose, et compare le contenu visible d'alors a celui
d'aujourd'hui. Les regles de neutralite -- commentaires, typographie,
reparation d'une sequence de controle cassee -- sont declarees dans
`scripts/content_approval.py`, pas devinees ici.

Il n'approuve rien et ne promeut aucun statut. Il constate.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_approval import (  # noqa: E402
    APPROBATION_PERIMEE,
    ROOT,
    STATUTS_PORTANT_APPROBATION,
    empreinte_visible,
    historique_des_objets,
    jetons_visibles,
    lire_blobs,
    meta_de,
    reparation_de_sequence_latex,
)

OUT = ROOT / "audit" / "CONTENT_APPROVAL_RECEIPTS.json"


def _objets_suivis() -> dict[str, str]:
    import subprocess

    fichiers = subprocess.run(
        ["git", "ls-files", "*.tex"], cwd=ROOT, capture_output=True, text=True,
        check=True,
    ).stdout.split()
    return {
        f: (ROOT / f).read_text(encoding="utf-8", errors="replace")
        for f in fichiers
        if (ROOT / f).exists()
    }


def analyser() -> dict[str, Any]:
    textes = _objets_suivis()
    histoire = historique_des_objets()

    revendiquent = {
        chemin: texte
        for chemin, texte in textes.items()
        if meta_de(texte).get("status") in STATUTS_PORTANT_APPROBATION
    }
    invalidees = {
        chemin: texte
        for chemin, texte in textes.items()
        if meta_de(texte).get("approval_state") == APPROBATION_PERIMEE
    }
    blobs = {b for chemin in revendiquent for _, b in histoire.get(chemin, [])}
    contenu = lire_blobs(blobs)

    lignes: list[dict[str, Any]] = []
    for chemin, texte in sorted(revendiquent.items()):
        blob_approuve = ""
        commit_approuve = ""
        for commit, blob in histoire.get(chemin, []):
            statut = meta_de(contenu.get(blob, "")).get("status")
            if statut in STATUTS_PORTANT_APPROBATION:
                commit_approuve, blob_approuve = commit, blob
            else:
                break
        if not blob_approuve:
            etat = "APPROVAL_ORIGIN_NOT_IN_HISTORY"
            motif = (
                "aucun commit de l'historique ne montre cet objet sans son "
                "statut approbatif : l'origine de l'approbation ne peut pas "
                "etre etablie"
            )
        else:
            avant = jetons_visibles(contenu[blob_approuve])
            apres = jetons_visibles(texte)
            if avant == apres:
                etat, motif = "FRESH", "le contenu visible est celui qui a ete approuve"
            elif reparation_de_sequence_latex(avant, apres):
                etat = "NEUTRAL_LATEX_CONTROL_SEQUENCE_REPAIR"
                motif = (
                    "seul ecart : une sequence de controle LaTeX cassee par la "
                    "campagne de diacritiques a ete retablie ; le sens vise par "
                    "l'approbation est restitue, pas modifie"
                )
            else:
                etat = "STALE_AFTER_SEMANTIC_EDIT"
                motif = (
                    "le contenu visible a change apres l'approbation : "
                    "l'approbation ne couvre plus ce que l'eleve lira"
                )
        lignes.append({
            "path": chemin,
            "object_id": meta_de(texte).get("id", ""),
            "claimed_status": meta_de(texte).get("status"),
            "approved_at_commit": commit_approuve,
            "approved_visible_digest": (
                empreinte_visible(contenu[blob_approuve]) if blob_approuve else ""
            ),
            "current_visible_digest": empreinte_visible(texte),
            "receipt_state": etat,
            "reason": motif,
        })

    en_attente = [
        {
            "path": chemin,
            "object_id": meta_de(texte).get("id", ""),
            "status": meta_de(texte).get("status"),
            "approval_state": APPROBATION_PERIMEE,
        }
        for chemin, texte in sorted(invalidees.items())
    ]

    compte = Counter(x["receipt_state"] for x in lignes)
    perimees = compte.get("STALE_AFTER_SEMANTIC_EDIT", 0)
    return {
        "artifact_type": "content_approval_receipts",
        "schema_version": 1,
        "generated_by": "scripts/build_content_approval_receipts.py",
        "approves_no_content": True,
        "promotes_no_status": True,
        "question": (
            "Chaque objet qui se dit approuve porte-t-il encore le contenu "
            "qu'un humain a relu ?"
        ),
        "neutrality_rules": {
            "COMMENTS_AND_VERIFY_BLOCKS": (
                "un bloc BEGIN-VERIFY prouve au producteur ; il ne change pas "
                "une ligne de ce qui est imprime"
            ),
            "TYPOGRAPHY": (
                "diacritiques, apostrophes, guillemets, tirets et espaces : le "
                "depot a deja tranche ce point par un recu humain de "
                "requalification diacritique"
            ),
            "LATEX_CONTROL_SEQUENCE_REPAIR": (
                "la campagne de diacritiques avait coupe des \\neq ; les "
                "retablir restitue le sens vise, il ne le modifie pas"
            ),
        },
        "summary": {
            "OBJECTS_CLAIMING_HUMAN_APPROVAL": len(lignes),
            "APPROVAL_RECEIPT_FRESH": compte.get("FRESH", 0),
            "APPROVAL_RECEIPT_NEUTRAL_REPAIR": compte.get(
                "NEUTRAL_LATEX_CONTROL_SEQUENCE_REPAIR", 0
            ),
            "STALE_APPROVAL_AFTER_SEMANTIC_EDIT": perimees,
            "APPROVAL_ORIGIN_NOT_IN_HISTORY": compte.get(
                "APPROVAL_ORIGIN_NOT_IN_HISTORY", 0
            ),
            "SEMANTIC_CHANGE_PRESERVES_OLD_HUMAN_APPROVAL": (
                "FAIL" if perimees else "PASS"
            ),
            "SEMANTIC_CHANGE_INVALIDATES_REVIEW_RECEIPT": (
                "FAIL" if perimees else "PASS"
            ),
            "INVALIDATED_APPROVALS_AWAITING_HUMAN_REVIEW": len(en_attente),
        },
        "receipts": lignes,
        "invalidated_awaiting_human_review": en_attente,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    charge = analyser()
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Recus d'approbation conformes au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    for cle, valeur in charge["summary"].items():
        print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
