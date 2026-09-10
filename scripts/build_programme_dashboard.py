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
    "INTERNAL_ATOMS_PROPOSED": (
        "rapprochements mesures, publies avec leurs concurrents ; ils ne "
        "valent pas couverture."
    ),
    "AUTOMATISMS_1SPE_OFFICIAL": (
        "automatismes que le programme de 2026 enonce ; leur presence dans le "
        "manuel se juge ailleurs, sur les objets eux-memes."
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
