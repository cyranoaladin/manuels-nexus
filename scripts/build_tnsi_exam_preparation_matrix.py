#!/usr/bin/env python3
"""Le manuel de terminale NSI prepare-t-il a l'epreuve, sans l'ajouter au programme ?

Deux autorites, deux matrices, et il ne faut jamais les confondre. Le programme
(MENE1921247A) dit ce qui doit etre enseigne. La definition d'epreuve
(MENE2516123N) dit comment cela sera evalue : un ecrit de 210 minutes comptant
pour trois quarts, une epreuve pratique de 60 minutes comptant pour un quart,
le tout au coefficient 16.

Une definition d'epreuve n'ajoute jamais une notion au programme. Elle impose
des formats, des durees, des ponderations et des modalites -- et c'est
precisement le risque : un manuel peut, a force de preparer l'epreuve,
introduire des attendus que le programme ne porte pas. Le dernier controle de
cette matrice verifie donc que chaque objet de preparation se rattache a une
capacite du PROGRAMME, et non a l'epreuve seule.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_objects import charger_contrats, charger_objets

ROOT = Path(__file__).resolve().parents[1]
AUTORITES = ROOT / "audit" / "OFFICIAL_AUTHORITIES_2026_2027.json"
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"
OUT = ROOT / "audit" / "TNSI_EXAM_PREPARATION_MATRIX.json"

#: Le sujet ecrit se compose de plusieurs exercices ; le manuel s'aligne sur ce
#: format en organisant sa banque par sujets. Un sujet isole ne prepare pas a
#: une epreuve de 210 minutes.
SUJETS_ECRITS_MINIMAUX = 3
SUJETS_PRATIQUES_MINIMAUX = 3
SUJET = re.compile(r"TNSI-ECRIT-(S\d+)-", re.I)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    autorites = json.loads(AUTORITES.read_text(encoding="utf-8"))
    epreuve = autorites["manuals"]["TNSI"]["DEFINITION_D_EPREUVE"]
    programme = autorites["manuals"]["TNSI"]["PROGRAMME_D_ENSEIGNEMENT"]
    couverture = json.loads(COVERAGE.read_text(encoding="utf-8"))
    liaison = json.loads(BINDING.read_text(encoding="utf-8"))
    objets = [o for o in charger_objets(charger_contrats()) if o.manual == "TNSI"]

    ecrits = [o for o in objets if o.kind == "banque_ecrite"]
    pratiques = [o for o in objets if o.kind == "banque_pratique"]
    sujets = sorted({m.group(1).upper() for o in ecrits if (m := SUJET.match(o.object_id))})

    # Un objet de preparation qui ne se rattache a aucune capacite du programme
    # ferait entrer l'epreuve dans le contenu enseigne.
    atomes_du_programme = {
        lien["atom_id"]
        for lien in liaison["bindings"]
        if lien["manual"] == "TNSI"
        and lien["binding_method"] in ("ANCHOR", "VERBATIM", "CONTEXT")
    }
    orphelins = [
        o.object_id
        for o in ecrits + pratiques
        if not (set(o.atoms) & atomes_du_programme)
    ]

    # Quelles parties du programme la banque ecrite touche-t-elle ?
    par_atome: dict[str, set[str]] = defaultdict(set)
    for ligne in couverture["rows"]:
        if ligne["manual"] != "TNSI":
            continue
        for atome in ligne["internal_atoms"]:
            par_atome[atome].add(
                ligne["official_subsection"] or ligne["official_section"] or ""
            )
    parties_ecrites = sorted(
        {p for o in ecrits for a in o.atoms for p in par_atome.get(a, ())}
    )
    parties_programme = sorted(
        {
            ligne["official_subsection"] or ligne["official_section"] or ""
            for ligne in couverture["rows"]
            if ligne["manual"] == "TNSI" and ligne["mandatory"]
        }
    )

    exigences: list[dict[str, Any]] = [
        {
            "requirement_id": "WRITTEN_EXAM_FORMAT",
            "from_authority": epreuve["NOR"],
            "official_basis": (
                f"epreuve ecrite de {epreuve['written_duration_minutes']} minutes, "
                f"notee sur {epreuve['written_raw_scale']}, comptant pour "
                f"{epreuve['written_weight']:.0%} de la note finale"
            ),
            "evidence_objects": sorted(o.object_id for o in ecrits),
            "evidence_count": len(ecrits),
            "subjects": sujets,
            "status": "COMPLETE" if len(sujets) >= SUJETS_ECRITS_MINIMAUX else "PARTIAL",
            "reason": (
                f"{len(sujets)} sujets ecrits complets dans la banque"
                if len(sujets) >= SUJETS_ECRITS_MINIMAUX
                else "trop peu de sujets pour entrainer a une epreuve de cette duree"
            ),
        },
        {
            "requirement_id": "PRACTICAL_EXAM_FORMAT",
            "from_authority": epreuve["NOR"],
            "official_basis": (
                f"epreuve pratique de {epreuve['practical_duration_minutes']} minutes, "
                f"notee sur {epreuve['practical_raw_scale']}, comptant pour "
                f"{epreuve['practical_weight']:.0%}"
            ),
            "evidence_objects": sorted(o.object_id for o in pratiques),
            "evidence_count": len(pratiques),
            "status": (
                "COMPLETE" if len(pratiques) >= SUJETS_PRATIQUES_MINIMAUX else "PARTIAL"
            ),
            "reason": f"{len(pratiques)} sujets pratiques dans la banque",
        },
        {
            "requirement_id": "PRACTICAL_IS_DONE_ON_A_MACHINE",
            "from_authority": epreuve["NOR"],
            "official_basis": (
                "l'epreuve pratique se passe sur machine : un sujet pratique "
                "sans programme a ecrire ou a mettre au point ne l'entraine pas"
            ),
            "evidence_objects": sorted(
                o.object_id for o in pratiques if o.has_algorithmic_work
            ),
            "evidence_count": sum(1 for o in pratiques if o.has_algorithmic_work),
            "status": (
                "COMPLETE"
                if pratiques and all(o.has_algorithmic_work for o in pratiques)
                else "PARTIAL"
            ),
            "reason": (
                "tous les sujets pratiques comportent un travail sur machine"
                if pratiques and all(o.has_algorithmic_work for o in pratiques)
                else "des sujets pratiques ne comportent aucun travail sur machine"
            ),
        },
        {
            "requirement_id": "WRITTEN_BANK_SPANS_THE_PROGRAMME",
            "from_authority": epreuve["NOR"],
            "official_basis": (
                "l'epreuve ecrite porte sur le programme : une banque "
                "concentree sur quelques rubriques n'y prepare pas"
            ),
            "evidence_objects": parties_ecrites,
            "evidence_count": len(parties_ecrites),
            "status": (
                "COMPLETE"
                if len(parties_ecrites) >= max(1, len(parties_programme) // 2)
                else "PARTIAL"
            ),
            "reason": (
                f"{len(parties_ecrites)} parties du programme touchees sur "
                f"{len(parties_programme)}"
            ),
        },
        {
            "requirement_id": "EXAM_ADDS_NO_NOTION_TO_THE_PROGRAMME",
            "from_authority": programme["NOR"],
            "official_basis": (
                "une definition d'epreuve fixe des modalites, jamais des "
                "contenus : chaque objet de preparation doit se rattacher a une "
                "capacite du programme"
            ),
            "evidence_objects": orphelins,
            "evidence_count": len(orphelins),
            "status": "COMPLETE" if not orphelins else "MISSING",
            "reason": (
                "tous les objets de preparation se rattachent au programme"
                if not orphelins
                else f"{len(orphelins)} objets de preparation ne se rattachent "
                "a aucune capacite du programme"
            ),
        },
    ]

    manquants_programme = [
        ligne for ligne in couverture["rows"]
        if ligne["manual"] == "TNSI"
        and ligne["mandatory"]
        and ligne["coverage_status"] == "MISSING"
    ]
    charge = {
        "artifact_type": "tnsi_two_matrices",
        "schema_version": 1,
        "generated_by": "scripts/build_tnsi_exam_preparation_matrix.py",
        "manual": "TNSI",
        "programme_authority": programme["NOR"],
        "exam_authority": epreuve["NOR"],
        "separation_rule": (
            "Le programme dit ce qui doit etre enseigne ; la definition "
            "d'epreuve dit comment cela sera evalue. L'epreuve n'ajoute jamais "
            "une notion au programme."
        ),
        "summary": {
            "TNSI_PROGRAMME_MATRIX": "PASS" if not manquants_programme else "FAIL",
            "TNSI_PROGRAMME_MANDATORY_MISSING": len(manquants_programme),
            "TNSI_EXAM_PREPARATION_MATRIX": (
                "PASS"
                if all(e["status"] == "COMPLETE" for e in exigences)
                else "FAIL"
            ),
            "EXAM_REQUIREMENTS": len(exigences),
            "EXAM_REQUIREMENTS_COMPLETE": sum(
                1 for e in exigences if e["status"] == "COMPLETE"
            ),
            "EXAM_ONLY_NOTIONS": len(orphelins),
        },
        "programme_mandatory_missing": [
            {
                "official_id": ligne["official_id"],
                "official_wording": ligne["official_wording"],
                "official_normativity": ligne["official_normativity"],
            }
            for ligne in manquants_programme
        ],
        "exam_requirements": exigences,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Matrices TNSI conformes au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    for exigence in exigences:
        print(f"  [{exigence['status']:8s}] {exigence['requirement_id']:38s} "
              f"{exigence['reason'][:56]}")
    print()
    resume = charge["summary"]
    assert isinstance(resume, dict)
    for cle, valeur in resume.items():
        print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
