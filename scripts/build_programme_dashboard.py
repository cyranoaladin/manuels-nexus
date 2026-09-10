#!/usr/bin/env python3
"""Tableau de bord de la couverture programme, entierement derive des artefacts.

Ce fichier n'est jamais redige a la main. Chaque ligne cite la valeur ET
l'artefact d'ou elle sort, de sorte qu'un rapport ne puisse plus afficher un
chiffre devenu faux sans que rien ne le signale.

Il ne donne deliberement pas de pourcentage global de couverture : un « 97,4 %
couvert » masque la nature des manques, et une demonstration exigible absente
ne se compense pas par dix connaissances presentes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from programme_metrics import ROOT, canonical_metrics

OUT_JSON = ROOT / "audit" / "PROGRAMME_DASHBOARD.json"
OUT_MD = ROOT / "audit" / "PROGRAMME_DASHBOARD.md"

#: Lecture de chaque compteur : ce qu'il mesure, et surtout ce qu'il ne mesure
#: pas. Un compteur sans mode d'emploi finit toujours par etre lu comme le
#: chiffre qu'on redoutait ou qu'on esperait.
LECTURES: dict[str, str] = {
    "OFFICIAL_REQUIRED_UNMAPPED": (
        "rattachement non encore etabli — PAS un contenu absent du manuel. "
        "Les referentiels internes encodent surtout des capacites ; une "
        "connaissance peut etre parfaitement traitee dans un fichier de cours "
        "sans posseder d'atome dedie."
    ),
    "INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT": (
        "atomes internes dont le parent officiel n'est pas etabli : la somme "
        "des propositions en attente et des atomes sans candidat."
    ),
    "INTERNAL_ATOMS_CONFIRMED_BY_CONTEXT": (
        "rattachements etablis par la structure des deux sources : la partie "
        "du programme que le chapitre traite, et le libelle de l'attendu a "
        "l'interieur de cette partie. Ce n'est pas une approbation humaine ; "
        "la preuve est publiee avec chaque lien."
    ),
    "INTERNAL_ATOMS_AMBIGUOUS_REQUIRES_HUMAN": (
        "atomes qu'aucune preuve objective ne tranche. Ils ne portent aucun "
        "parent et attendent un arbitrage ; chacun est classe (subdivision "
        "pedagogique, enrichissement, programme perime, atome obsolete)."
    ),
    "MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY": (
        "champs dont le nom promet le texte du Bulletin officiel sans qu'aucun "
        "producteur ne l'ait verifie. Le champ `libelle_bo` du referentiel "
        "interne n'est verbatim que dans la moitie des cas : il est deprecie "
        "au profit de `libelle_interne`, et le texte officiel exact vit dans "
        "l'inventaire sous `official_wording`."
    ),
    "OFFICIAL_REQUIRED_MISSING": (
        "attendus obligatoires dont AUCUN objet du manuel ne porte la trace. "
        "A distinguer de OFFICIAL_REQUIRED_UNMAPPED, qui ne dit que l'absence "
        "de rattachement etabli entre le referentiel interne et le BO."
    ),
    "OFFICIAL_REQUIRED_INSTITUTIONAL": (
        "exigences que le manuel ne peut pas certifier a lui seul -- « Un "
        "quart au moins de l'horaire total est reserve aux projets » releve de "
        "l'etablissement. Le manuel peut les outiller, pas les garantir."
    ),
    "OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH": (
        "attendus dont le libelle officiel ne porte aucun mot distinctif "
        "exploitable : la recherche par contenu ne peut ni conclure a la "
        "presence ni conclure a l'absence."
    ),
    "AUTOMATISM_NOT_REINVESTED": (
        "automatismes que le manuel travaille sans les repartir : le programme "
        "exclut qu'ils fassent l'objet d'un chapitre specifique et demande "
        "qu'ils soient entretenus sur l'annee. Aucun n'est absent du manuel."
    ),
    "OFFICIAL_ITEMS_CLAIMED_BY_SEVERAL_THEMES": (
        "attendus revendiques par plusieurs themes internes. Le chiffre brut "
        "ne dit pas si c'est une faute : il faut regarder qui ENSEIGNE "
        "l'attendu et qui le reinvestit. Voir "
        "audit/MULTIPLE_ASSIGNMENT_RESOLUTION.json."
    ),
    "UNJUSTIFIED_MULTIPLE_ASSIGNMENT": (
        "parmi eux, ceux qu'aucun contenu ne justifie : un theme qui se "
        "declare sans rien avoir derriere, ou un attendu pratique sans jamais "
        "etre enseigne."
    ),
    "FUTURE_PROGRAM_CONTAMINATION": (
        "objets du manuel qui reprennent un attendu d'un programme ne "
        "regissant pas cette edition, sur des notions absentes du programme "
        "en vigueur."
    ),
    "OBJECTS_CITING_AN_UNKNOWN_CAPACITY": (
        "objets qui se reclament d'une capacite absente de tout referentiel. "
        "L'objet parait rattache et ne l'est pas : personne ne s'en apercoit."
    ),
    "UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS": (
        "objets sans attendu ET sans statut : ni prerequis, ni enrichissement "
        "assume, ni entrainement a l'epreuve. Un manuel a le droit de depasser "
        "le programme ; il n'a pas le droit de le faire sans le dire."
    ),
    "ADDED_2026_TRULY_MISSING": (
        "attendus ajoutes par la reforme qu'il faudrait ecrire. La dette de "
        "contenu ne se deduit pas du differentiel : un attendu ajoute au "
        "programme peut etre traite depuis des annees."
    ),
}


def build() -> dict[str, object]:
    metriques = canonical_metrics()
    return {
        "artifact_type": "programme_dashboard",
        "schema_version": 1,
        "generated_by": "scripts/build_programme_dashboard.py",
        "note": (
            "Aucun compteur n'est saisi ici : chacun est lu dans l'artefact "
            "qui le produit, et cite son chemin."
        ),
        "metrics": {
            m.name: {
                "value": m.value,
                "artifact": m.artifact,
                "pointer": list(m.pointer),
                **({"reading": LECTURES[m.name]} if m.name in LECTURES else {}),
            }
            for m in metriques.values()
        },
    }


def render_md(charge: dict[str, object]) -> str:
    lignes = [
        "# Couverture programme — tableau de bord",
        "",
        "Fichier genere par `scripts/build_programme_dashboard.py`.",
        "Ne pas editer : chaque valeur est relue dans l'artefact qui la produit.",
        "",
        "| Compteur | Valeur | Artefact |",
        "|---|---|---|",
    ]
    metrics = charge["metrics"]
    assert isinstance(metrics, dict)
    for nom, detail in metrics.items():
        chemin = " / ".join(detail["pointer"])
        lignes.append(
            f"| `{nom}` | {detail['value']} | `{detail['artifact']}` :: {chemin} |"
        )
    lignes += ["", "## Comment lire ces compteurs", ""]
    for nom, detail in metrics.items():
        if "reading" in detail:
            lignes.append(f"- **`{nom}`** — {detail['reading']}")
    lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    charge = build()
    texte_json = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    texte_md = render_md(charge)
    if args.check:
        divergents = [
            str(chemin.relative_to(ROOT))
            for chemin, attendu in ((OUT_JSON, texte_json), (OUT_MD, texte_md))
            if not chemin.exists() or chemin.read_text(encoding="utf-8") != attendu
        ]
        if divergents:
            print("DIVERGENT :", *divergents, sep="\n  ")
            return 1
        print("Tableau de bord conforme aux artefacts canoniques.")
        return 0
    OUT_JSON.write_text(texte_json, encoding="utf-8")
    OUT_MD.write_text(texte_md, encoding="utf-8")
    print(texte_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
