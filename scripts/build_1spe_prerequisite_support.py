#!/usr/bin/env python3
"""Le socle suppose acquis est-il reactive, ou seulement suppose ?

Le programme de premiere s'appuie sur des automatismes construits avant lui :
« A la liste ci-dessous s'ajoute la liste des automatismes travailles en classe
de seconde, qui doivent etre entretenus en classe de premiere. » Un manuel qui
suppose ce socle sans jamais le remettre en place laisse l'eleve sans recours :
il ne saura pas ce qui lui manque, et le manuel ne le lui apprendra pas.

Il ne s'agit pas d'integrer le manuel de seconde. Il s'agit de verifier que
chaque prerequis DECLARE par un chapitre trouve, dans ce chapitre, de quoi se
diagnostiquer et se reprendre : un QCM d'entree qui revele le manque, une fiche
de remediation qui y repond.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_official_to_manual_coverage import _sans_accents, racine, termes_distinctifs
from manual_objects import charger_contrats, charger_objets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "1SPE_PREREQUISITE_SUPPORT.json"
#: Un prerequis est tenu pour repris si un objet de reprise en contient assez
#: de termes distinctifs.
TERMES_REQUIS = 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    contrats = charger_contrats()
    objets = charger_objets(contrats)
    par_chapitre: dict[str, list[Any]] = {}
    for objet in objets:
        par_chapitre.setdefault(objet.chapter, []).append(objet)

    textes: dict[str, str] = {}
    lignes: list[dict[str, Any]] = []
    for chemin in sorted(
        (ROOT / "Mathematiques" / "manuel-maths" / "chapitres").glob("1SPE-*/contrat.yaml")
    ):
        charge = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
        chapitre = charge.get("chapitre", chemin.parent.name)
        objets_du_chapitre = par_chapitre.get(chapitre, [])
        for prerequis in charge.get("prerequis") or []:
            libelle = prerequis.get("libelle", "")
            termes = termes_distinctifs(libelle)
            exigence = min(len(termes), TERMES_REQUIS) if termes else 0
            code = prerequis.get("code")
            # Lien declare : l'objet nomme le prerequis qu'il remet en place.
            # C'est une preuve structurelle, bien meilleure qu'un rapprochement
            # de mots -- une fiche intitulee « Calcul litteral » repond a un
            # prerequis nomme « Calcul litteral : mise en equation, resolution »
            # sans en reprendre les termes.
            declarees = [
                o.object_id for o in objets_du_chapitre
                if code and code in o.prerequis_testes
            ]
            reprises: list[str] = list(declarees)
            diagnostics: list[str] = []
            for objet in objets_du_chapitre:
                if objet.object_id in declarees:
                    continue
                if objet.role not in ("REMEDIATION", "ASSESSMENT"):
                    continue
                texte = textes.get(objet.path)
                if texte is None:
                    texte = _sans_accents(
                        (ROOT / objet.path).read_text(encoding="utf-8", errors="replace")
                    ).lower()
                    textes[objet.path] = texte
                if exigence and sum(1 for t in termes if racine(t) in texte) >= exigence:
                    (
                        diagnostics if objet.role == "ASSESSMENT" else reprises
                    ).append(objet.object_id)
            if declarees and diagnostics:
                statut = "DIAGNOSED_AND_REMEDIATED"
                motif = (
                    "une fiche declare remettre ce prerequis en place, et un "
                    "diagnostic en revele le manque"
                )
            elif declarees:
                statut = "REMEDIATED_ONLY"
                motif = (
                    "une fiche declare remettre ce prerequis en place ; rien "
                    "ne signale le manque a l'eleve en amont"
                )
            elif reprises and diagnostics:
                statut = "DIAGNOSED_AND_REMEDIATED"
                motif = "un diagnostic le revele, une reprise y repond"
            elif reprises:
                statut = "REMEDIATED_ONLY"
                motif = "une reprise existe, mais rien ne signale le manque a l'eleve"
            elif diagnostics:
                statut = "DIAGNOSED_ONLY"
                motif = "le manque est revele, mais le manuel n'y repond pas"
            else:
                statut = "ASSUMED_WITHOUT_SUPPORT"
                motif = (
                    "prerequis suppose acquis, sans diagnostic ni reprise dans "
                    "le chapitre qui s'en sert"
                )
            lignes.append({
                "chapter": chapitre,
                "declared_by_object": declarees,
                "prerequisite_code": prerequis.get("code"),
                "prerequisite_label": libelle,
                "origin": prerequis.get("chapitre_origine"),
                "diagnostic_evidence": sorted(diagnostics),
                "remediation_evidence": sorted(reprises),
                "status": statut,
                "reason": motif,
            })

    compte = Counter(x["status"] for x in lignes)
    charge_sortie = {
        "artifact_type": "prerequisite_support",
        "schema_version": 1,
        "generated_by": "scripts/build_1spe_prerequisite_support.py",
        "manual": "1SPE",
        "basis": (
            "« A la liste ci-dessous s'ajoute la liste des automatismes "
            "travailles en classe de seconde, qui doivent etre entretenus en "
            "classe de premiere. »"
        ),
        "summary": {
            "PREREQUISITES_DECLARED": len(lignes),
            "PREREQUISITES_DIAGNOSED_AND_REMEDIATED": compte.get(
                "DIAGNOSED_AND_REMEDIATED", 0
            ),
            "PREREQUISITES_ASSUMED_WITHOUT_SUPPORT": compte.get(
                "ASSUMED_WITHOUT_SUPPORT", 0
            ),
            "status_counts": dict(sorted(compte.items())),
        },
        "prerequisites": lignes,
    }
    texte = json.dumps(charge_sortie, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Matrice des prerequis conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    for cle, valeur in sorted(compte.items()):
        print(f"  {valeur:3d}  {cle}")
    print()
    resume = charge_sortie["summary"]
    assert isinstance(resume, dict)
    for cle, valeur in resume.items():
        if not isinstance(valeur, dict):
            print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
