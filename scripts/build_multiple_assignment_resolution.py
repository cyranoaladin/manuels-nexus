#!/usr/bin/env python3
"""Un meme attendu revendique par deux chapitres : erreur, ou transversalite ?

Le compteur brut ne sait pas repondre. Il signale qu'un attendu officiel est
revendique par plusieurs themes internes, ce qui peut recouvrir trois
situations tres differentes : un chapitre enseigne et l'autre reinvestit, deux
chapitres enseignent chacun une facette, ou l'un des deux se declare sans rien
avoir derriere.

La reponse ne se lit pas dans le referentiel : elle se lit dans les objets. Ce
script regarde, chapitre par chapitre, qui ENSEIGNE l'attendu -- c'est-a-dire
qui possede un objet de cours -- et qui se contente de le faire pratiquer.

Le programme de l'option complementaire rend cette situation attendue plutot
qu'anormale : il est organise en themes d'etude, et rattache les memes
« Contenus associes » a plusieurs d'entre eux. Deux themes qui mobilisent la
meme notion ne se contredisent pas ; ils la rencontrent chacun dans leur
contexte. Ce qui doit rester vrai, c'est que l'attendu ne compte qu'une fois
dans la couverture -- sans quoi deux chapitres couvriraient deux fois le meme
programme.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_objects import charger_contrats, charger_objets, charger_transversaux

ROOT = Path(__file__).resolve().parents[1]
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
OUT = ROOT / "audit" / "MULTIPLE_ASSIGNMENT_RESOLUTION.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    liaison = json.loads(BINDING.read_text(encoding="utf-8"))
    couverture = json.loads(COVERAGE.read_text(encoding="utf-8"))
    par_id = {r["official_id"]: r for r in couverture["rows"]}
    contrats = charger_contrats()
    objets = {
        o.object_id: o for o in charger_objets(contrats) + charger_transversaux()
    }
    theme_du_chapitre = {c.chapter: c.theme for c in contrats.values()}

    resolutions: list[dict[str, Any]] = []
    for oid, themes in sorted(liaison["multiple_assignment"].items()):
        ligne = par_id.get(oid)
        if ligne is None:
            continue
        roles_par_chapitre: dict[str, Counter[str]] = defaultdict(Counter)
        objets_par_chapitre: dict[str, list[str]] = defaultdict(list)
        for role, ids in ligne["objects_by_role"].items():
            for identifiant in ids:
                objet = objets.get(identifiant)
                if objet is None:
                    continue
                roles_par_chapitre[objet.chapter][role] += 1
                objets_par_chapitre[objet.chapter].append(identifiant)

        enseignants = sorted(
            chap for chap, roles in roles_par_chapitre.items()
            if roles.get("PRIMARY_TEACHING")
        )
        reinvestisseurs = sorted(
            chap for chap, roles in roles_par_chapitre.items()
            if not roles.get("PRIMARY_TEACHING") and sum(roles.values()) > 0
        )
        revendiquants_sans_objet = sorted(
            theme for theme in themes
            if not any(
                theme_du_chapitre.get(chap) == theme.split("/", 1)[-1]
                for chap in roles_par_chapitre
            )
        )

        if revendiquants_sans_objet:
            verdict = "UNJUSTIFIED_DUPLICATE_BINDING"
            motif = (
                "un theme revendique cet attendu sans qu'aucun de ses objets "
                "ne le porte : le rattachement du referentiel est a corriger"
            )
        elif len(enseignants) >= 2:
            verdict = "JUSTIFIED_DISTRIBUTED_COVERAGE"
            motif = (
                f"{len(enseignants)} chapitres l'enseignent chacun dans leur "
                "contexte ; le programme de l'option rattache les memes "
                "contenus a plusieurs themes d'etude"
            )
        elif len(enseignants) == 1:
            verdict = "PRIMARY_TEACHING_PLUS_REINVESTMENT"
            motif = (
                f"{enseignants[0]} l'enseigne ; "
                f"{', '.join(reinvestisseurs) or 'aucun autre chapitre'} le "
                "reinvestit"
            )
        else:
            verdict = "PRACTISED_BUT_NEVER_TAUGHT"
            motif = (
                "aucun chapitre ne l'enseigne : il n'est que pratique ou evalue"
            )

        resolutions.append({
            "official_id": oid,
            "official_wording": ligne["official_wording"],
            "official_normativity": ligne["official_normativity"],
            "manual": ligne["manual"],
            "claiming_themes": themes,
            "PRIMARY_TEACHING": enseignants,
            "REINVESTMENT": reinvestisseurs,
            "objects_by_chapter": {
                chap: sorted(ids) for chap, ids in sorted(objets_par_chapitre.items())
            },
            "counted_once_in_coverage": True,
            "resolution": verdict,
            "reason": motif,
        })

    compte = Counter(r["resolution"] for r in resolutions)
    charge = {
        "artifact_type": "multiple_assignment_resolution",
        "schema_version": 1,
        "generated_by": "scripts/build_multiple_assignment_resolution.py",
        "rule": (
            "Un attendu revendique par plusieurs themes ne compte qu'une fois "
            "dans la couverture. Ce qui se decide ici n'est pas son poids, "
            "mais la nature du partage : enseignement distribue, enseignement "
            "puis reinvestissement, ou rattachement en trop."
        ),
        "summary": {
            "SHARED_OFFICIAL_ITEMS": len(resolutions),
            "JUSTIFIED_DISTRIBUTED_COVERAGE": compte.get(
                "JUSTIFIED_DISTRIBUTED_COVERAGE", 0
            ),
            "PRIMARY_TEACHING_PLUS_REINVESTMENT": compte.get(
                "PRIMARY_TEACHING_PLUS_REINVESTMENT", 0
            ),
            "UNJUSTIFIED_MULTIPLE_ASSIGNMENT": compte.get(
                "UNJUSTIFIED_DUPLICATE_BINDING", 0
            )
            + compte.get("PRACTISED_BUT_NEVER_TAUGHT", 0),
            "resolution_counts": dict(sorted(compte.items())),
        },
        "resolutions": resolutions,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Resolution des assignations multiples conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    for r in resolutions:
        print(f"  [{r['resolution']:36s}] {r['official_wording'][:52]}")
        print(f"        {r['reason'][:100]}")
    print()
    resume = charge["summary"]
    assert isinstance(resume, dict)
    for cle, valeur in resume.items():
        if not isinstance(valeur, dict):
            print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
