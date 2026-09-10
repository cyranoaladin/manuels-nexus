#!/usr/bin/env python3
"""Les automatismes de premiere sont-ils introduits, puis entretenus ?

Le programme de 2026 fait des automatismes une partie a part entiere, et dit
comment ils doivent vivre : « Les capacites attendues enoncees ci-dessous n'ont
pas vocation a faire l'objet d'un chapitre d'enseignement specifique [...] et
doivent etre entretenues et consolidees au cours de l'annee. »

Deux constats se sont succede, et le second corrige le premier. Le referentiel
interne ne contient AUCUN atome pour ces dix-sept automatismes : rien, dans la
mecanique du projet, ne les suit. Mais l'absence d'atome n'est pas l'absence du
manuel -- et la recherche dans les objets montre que la plupart y sont bel et
bien travailles, dans les exercices, les evaluations, les pages transversales,
sans avoir jamais recu de code.

Cet audit ne se contente donc pas de dire « present » ou « absent ». Un
automatisme rassemble dans un seul chapitre n'est pas entretenu au sens du
programme, meme s'il est enseigne. Ce qui est mesure ici est la REPARTITION.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_objects import charger_contrats, charger_objets, charger_transversaux

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
OUT = ROOT / "audit" / "1SPE_AUTOMATISMS_AUDIT.json"

#: Ce que le BO exige, et ce que la collection ajoute -- il faut les separer.
#:
#: Le programme ecrit qu'un automatisme n'a « pas vocation a faire l'objet d'un
#: chapitre d'enseignement specifique » et doit etre « entretenu et consolide
#: au cours de l'annee ». Un automatisme present dans DEUX chapitres ne
#: contredit donc plus le texte : c'est le seuil officiel, et c'est lui que la
#: matrice de couverture applique.
#:
#: Exiger trois chapitres, avec entrainement et evaluation, est une exigence de
#: qualite que la collection se donne. Le ministere ne l'ecrit nulle part. Elle
#: porte donc son nom -- NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD -- pour qu'on ne
#: la prenne jamais pour une obligation reglementaire.
SEUIL_OFFICIEL_PAS_DE_CHAPITRE_DEDIE = 2
NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD = 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    couverture = json.loads(COVERAGE.read_text(encoding="utf-8"))
    contrats = charger_contrats()
    objets = {
        o.object_id: o for o in charger_objets(contrats) + charger_transversaux()
    }

    lignes: list[dict[str, Any]] = []
    for ligne in couverture["rows"]:
        if ligne["manual"] != "1SPE" or ligne["official_normativity"] != "REQUIRED_AUTOMATISM":
            continue
        par_role = ligne["objects_by_role"]
        servants = [
            objets[oid]
            for role in par_role
            for oid in par_role[role]
            if oid in objets
        ]
        chapitres = sorted({o.chapter for o in servants})
        introduction = sorted(
            o.object_id for o in servants if o.role == "PRIMARY_TEACHING"
        )
        appui = sorted(
            o.object_id for o in servants if o.role == "SUPPORTING_EVIDENCE"
        )
        pratique = sorted(o.object_id for o in servants if o.role == "REINVESTMENT")
        evaluation = sorted(o.object_id for o in servants if o.role == "ASSESSMENT")
        remediation = sorted(o.object_id for o in servants if o.role == "REMEDIATION")

        if not servants:
            verdict = "ABSENT"
            motif = "aucun objet du manuel ne travaille cet automatisme"
        elif len(chapitres) == 1:
            verdict = "PRESENT_BUT_NOT_DISTRIBUTED"
            motif = (
                f"travaille dans le seul chapitre {chapitres[0]} : le programme "
                "exclut qu'un automatisme fasse l'objet d'un chapitre "
                "specifique. C'est le seul cas ou le texte lui-meme est "
                "contredit."
            )
        elif len(chapitres) < NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD:
            verdict = "MEETS_OFFICIAL_MINIMUM_BELOW_NEXUS_STANDARD"
            motif = (
                f"present dans {len(chapitres)} chapitres : le programme est "
                "satisfait, mais la collection vise trois chapitres au moins"
            )
        elif not (pratique or evaluation):
            verdict = "MEETS_OFFICIAL_MINIMUM_BELOW_NEXUS_STANDARD"
            motif = (
                f"reparti sur {len(chapitres)} chapitres, donc conforme au "
                "programme, mais jamais mis en pratique ni evalue : la "
                "collection attend un entrainement"
            )
        else:
            verdict = "ADEQUATELY_REINVESTED"
            motif = (
                f"introduit, puis entretenu dans {len(chapitres)} chapitres, "
                f"avec {len(pratique)} objets d'entrainement et "
                f"{len(evaluation)} objets d'evaluation"
            )

        lignes.append({
            "automatism_id": ligne["official_id"],
            "official_wording": ligne["official_wording"],
            "official_domain": ligne["official_subsection"],
            "internal_atoms": ligne["internal_atoms"],
            "evidence_kind": ligne["evidence_kind"],
            "INTRODUCTION_EVIDENCE": introduction,
            "SUPPORTING_EVIDENCE": appui,
            "PRACTICE_EVIDENCE": pratique,
            "ASSESSMENT_EVIDENCE": evaluation,
            "REMEDIATION_EVIDENCE": remediation,
            "chapters_distribution": chapitres,
            "occurrence_count": len(servants),
            "verdict": verdict,
            "reason": motif,
        })

    compte = Counter(x["verdict"] for x in lignes)
    charge = {
        "artifact_type": "automatisms_audit",
        "schema_version": 1,
        "generated_by": "scripts/build_1spe_automatisms_audit.py",
        "manual": "1SPE",
        "authority_ref": "MENE2602917A",
        "basis": (
            "« Les capacites attendues enoncees ci-dessous n'ont pas vocation a "
            "faire l'objet d'un chapitre d'enseignement specifique [...] et "
            "doivent etre entretenues et consolidees au cours de l'annee. »"
        ),
        "summary": {
            "AUTOMATISMS_1SPE_OFFICIAL": len(lignes),
            "AUTOMATISMS_1SPE_WITH_AN_INTERNAL_ATOM": sum(
                1 for x in lignes if x["internal_atoms"]
            ),
            "AUTOMATISMS_1SPE_PRESENT": sum(
                1 for x in lignes if x["verdict"] != "ABSENT"
            ),
            "AUTOMATISMS_1SPE_ADEQUATELY_REINVESTED": compte.get(
                "ADEQUATELY_REINVESTED", 0
            ),
            "AUTOMATISM_NOT_REINVESTED": sum(
                1 for x in lignes if x["verdict"] == "PRESENT_BUT_NOT_DISTRIBUTED"
            ),
            "NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD": (
                f"{NEXUS_DISTRIBUTED_AUTOMATISM_STANDARD} chapitres au moins, "
                "avec entrainement ou evaluation — exigence de la collection, "
                "pas du programme"
            ),
            "AUTOMATISMS_BELOW_NEXUS_STANDARD": sum(
                1 for x in lignes
                if x["verdict"] == "MEETS_OFFICIAL_MINIMUM_BELOW_NEXUS_STANDARD"
            ),
            "verdict_counts": dict(sorted(compte.items())),
        },
        "automatisms": lignes,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Audit des automatismes conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    for x in lignes:
        print(f"  [{x['verdict']:28s}] {len(x['chapters_distribution']):2d} chap, "
              f"{x['occurrence_count']:3d} objets — {x['official_wording'][:56]}")
    print()
    resume = charge["summary"]
    assert isinstance(resume, dict)
    for cle, valeur in resume.items():
        if not isinstance(valeur, dict):
            print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
