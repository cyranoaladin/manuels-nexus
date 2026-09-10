#!/usr/bin/env python3
"""Ce que la reforme de 2026 exige vraiment du manuel de premiere.

Le differentiel dit ce que le programme a change. Il ne dit pas ce que le
manuel doit ecrire : un attendu « ajoute en 2026 » peut deja etre traite depuis
des annees, parce que le manuel allait au-dela de l'ancien programme ou parce
que la reforme a officialise une pratique repandue. Deduire la dette de contenu
du seul differentiel surestimerait le travail restant.

Deux audits symetriques, et le second compte autant que le premier :

  ajoutes en 2026   le manuel les traite-t-il deja, ou faut-il les ecrire ?
  retires en 2026   subsistent-ils dans le manuel, et sous quel statut ?

Un contenu retire du programme n'a pas a disparaitre du manuel : il peut rester
comme approfondissement. Ce qui est interdit, c'est qu'il continue d'etre
presente comme exigible -- l'eleve travaillerait pour une epreuve qui ne le lui
demandera pas.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_official_to_manual_coverage import _sans_accents, racine, termes_distinctifs
from manual_objects import charger_contrats, charger_objets, charger_transversaux

ROOT = Path(__file__).resolve().parents[1]
DIFF = ROOT / "audit" / "1SPE_PROGRAMME_DIFF_2019_2026.json"
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
OUT = ROOT / "audit" / "1SPE_REFORM_TRANSITION_AUDIT.json"

#: Part des termes DISTINCTIFS qu'un objet doit contenir pour qu'on tienne
#: l'attendu retire pour encore present. Volontairement elevee : ce qui est
#: cherche est la survivance d'un contenu precis. Un seuil bas sur les mots
#: ordinaires faisait ressortir « Utiliser un arbre pondere ou un tableau pour
#: calculer une probabilite » dans un cours de derivation, sur les seuls mots
#: « utiliser », « tableau » et « calculer ».
SEUIL_SURVIVANCE = 0.7
#: Part des termes distinctifs d'un attendu retire qu'un attendu de 2026 doit
#: reprendre pour qu'on tienne la notion pour toujours au programme, et minimum
#: absolu. La part compte autant que le nombre : deux mots communs suffisaient
#: a rapprocher « Fonctions cosinus et sinus. Parite, periodicite. Courbes
#: representatives. » d'un attendu sur les variations, alors que l'etude de ces
#: fonctions quitte reellement le programme de premiere.
#:
#: Le differentiel est un outil forensique : quand son appariement echoue,
#: c'est le texte de 2026 qui fait autorite, pas le verdict du diff.
PART_PARTAGEE_POUR_SURVIVRE = 0.5
TERMES_PARTAGES_MINIMUM = 2
#: Au-dela de ce nombre d'attendus de 2026 qui le portent, un radical est
#: trop repandu pour temoigner de la survivance d'une notion precise.
FREQUENCE_MAXIMALE_POUR_ETRE_SPECIFIQUE = 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    diff = json.loads(DIFF.read_text(encoding="utf-8"))
    couverture = json.loads(COVERAGE.read_text(encoding="utf-8"))
    par_id = {r["official_id"]: r for r in couverture["rows"]}

    ajoutes: list[dict[str, Any]] = []
    for verdict in diff["verdicts"]:
        if verdict["verdict"] != "ADDED_2026" or not verdict.get("mandatory"):
            continue
        ligne = par_id.get(verdict["official_id_2026"])
        statut = ligne["coverage_status"] if ligne else "MISSING"
        atomes = ligne["internal_atoms"] if ligne else []
        if statut == "MISSING":
            classement = "TRULY_MISSING"
            motif = "aucun objet du manuel ne porte cet attendu ajoute en 2026"
        elif statut in ("COMPLETE", "PARTIAL") and not atomes:
            classement = "ALREADY_PRESENT_WITHOUT_OFFICIAL_MAPPING"
            motif = (
                "le manuel le traite deja, sans qu'aucune capacite interne ne "
                "le declare : c'est le suivi qui manquait, pas le contenu"
            )
        elif statut in ("COMPLETE", "PARTIAL"):
            classement = "NEWLY_ADDED_AND_ALREADY_FIXED"
            motif = "traite et rattache a une capacite interne"
        else:
            classement = "UNDECIDED"
            motif = f"statut de couverture {statut}"
        ajoutes.append({
            "official_id": verdict["official_id_2026"],
            "official_wording": verdict["official_wording"],
            "official_normativity": ligne["official_normativity"] if ligne else None,
            "coverage_status": statut,
            "present_in_internal_reference": bool(atomes),
            "objects_by_role": ligne["objects_by_role"] if ligne else {},
            "classification": classement,
            "reason": motif,
        })

    # Les retires : subsistent-ils, et comment sont-ils presentes ?
    contrats = charger_contrats()
    objets = [
        o
        for o in charger_objets(contrats) + charger_transversaux()
        if o.manual == "1SPE"
    ]
    textes: dict[str, str] = {}
    couverture_2026 = [
        r for r in couverture["rows"] if r["manual"] == "1SPE"
    ]
    # Combien d'attendus de 2026 portent chaque radical ? Un radical present
    # partout ne distingue rien.
    frequence_2026: Counter[str] = Counter()
    for r in couverture_2026:
        minuscule = _sans_accents(r["official_wording"]).lower()
        for t in termes_distinctifs(r["official_wording"]):
            if racine(t) in minuscule:
                frequence_2026[racine(t)] += 1
    retires: list[dict[str, Any]] = []
    for verdict in diff["verdicts"]:
        if verdict["verdict"] != "REMOVED_2026" or not verdict.get("mandatory"):
            continue
        libelle = verdict["official_wording"]

        # Le programme de 2026 dit-il encore la meme chose autrement ? La
        # question n'est pas de retrouver la phrase : la reforme deplace des
        # notions d'une rubrique a l'autre. Les probabilites conditionnelles
        # quittent les contenus de premiere et deviennent un automatisme -- le
        # manuel qui les enseigne ne travaille donc pas hors programme. Ce qui
        # est cherche ici est le partage de termes DISTINCTIFS avec un attendu
        # de 2026, quelle qu'en soit la rubrique.
        termes = termes_distinctifs(libelle)
        parents_2026 = [
            (len(termes & termes_distinctifs(r["official_wording"])), r)
            for r in couverture_2026
        ]
        partage, jumeau = max(parents_2026, key=lambda t: t[0], default=(0, None))
        assez_partage = (
            jumeau is not None
            and partage >= TERMES_PARTAGES_MINIMUM
            and termes
            and partage / len(termes) >= PART_PARTAGEE_POUR_SURVIVRE
        )
        if assez_partage and jumeau is not None:
            retires.append({
                "official_id_2019": verdict["official_id_2019"],
                "official_wording": libelle,
                "still_in_programme_as": jumeau["official_id"],
                "still_in_programme_wording": jumeau["official_wording"],
                "still_in_programme_normativity": jumeau["official_normativity"],
                "shared_terms": sorted(
                    termes & termes_distinctifs(jumeau["official_wording"])
                ),
                "surviving_objects": [],
                "surviving_in_course_or_assessment": [],
                "classification": "STILL_IN_PROGRAMME_SHARED_WORDING",
                "evidence_strength": "SHARED_DISTINCTIVE_WORDING",
                "reason": (
                    "un attendu du programme de 2026 porte les memes notions, "
                    f"sous la rubrique « {jumeau['official_heading'] or 'implicite'} » : "
                    "le manuel qui les traite ne travaille pas hors annee"
                ),
            })
            continue

        # Second filet : la NOTION est-elle encore nommee dans le programme
        # de 2026, quelle qu'en soit la rubrique ? Le recouvrement de mots ne
        # suffit pas quand le BO reformule court. « Distinguer P(A n B), PA(B),
        # PB(A) » est litteralement un automatisme de 2026, mais son libelle
        # est trop bref pour partager assez de mots avec la phrase de 2019.
        # Le terme retenu doit etre SPECIFIQUE au programme de 2026, pas
        # seulement present : « courbes representatives » se retrouve dans une
        # dizaine d'attendus et ne prouve rien, alors que « cosinus » n'est
        # porte que par quelques-uns. Un mot trop repandu rapprocherait
        # n'importe quel attendu retire de n'importe quel attendu conserve.
        # Ordre fixe : `termes` est un ensemble, et l'iteration d'un ensemble
        # de chaines varie d'un processus a l'autre. L'artefact cesserait
        # d'etre reproductible.
        specifiques = [
            t for t in sorted(termes)
            if 1 <= frequence_2026.get(racine(t), 0) <= FREQUENCE_MAXIMALE_POUR_ETRE_SPECIFIQUE
        ]
        porteurs = [
            r for r in couverture_2026
            if any(
                racine(t) in _sans_accents(r["official_wording"]).lower()
                for t in specifiques
            )
        ]
        if porteurs:
            obligatoires_porteurs = [r for r in porteurs if r["mandatory"]]
            cible = (obligatoires_porteurs or porteurs)[0]
            retires.append({
                "official_id_2019": verdict["official_id_2019"],
                "official_wording": libelle,
                "still_in_programme_as": cible["official_id"],
                "still_in_programme_wording": cible["official_wording"],
                "still_in_programme_normativity": cible["official_normativity"],
                "still_in_programme_is_mandatory": bool(obligatoires_porteurs),
                "matched_on_terms": specifiques,
                "surviving_objects": [],
                "surviving_in_course_or_assessment": [],
                # Preuve faible, et dite comme telle : savoir qu'un mot du
                # libelle retire figure encore au programme ne dit pas que la
                # NOTION y figure encore. « Cosinus » et « sinus » restent au
                # programme de 2026, mais l'etude des fonctions cosinus et
                # sinus -- parite, periodicite, courbes -- en sort. Aucun
                # rapprochement lexical ne tranche cela : il y faut une
                # lecture.
                "classification": (
                    "NOTION_STILL_NAMED_IN_PROGRAMME_REQUIRES_REVIEW"
                    if obligatoires_porteurs
                    else "ENRICHMENT_NOT_REQUIRED_FOR_PROGRAMME"
                ),
                "evidence_strength": "WEAK_LEXICAL",
                "reason": (
                    "un terme specifique de cet attendu reste nomme par le "
                    f"programme de 2026 sous la rubrique "
                    f"« {cible['official_heading'] or 'implicite'} ». Cela ne "
                    "prouve pas que la notion elle-meme y reste : a verifier."
                    + (
                        ""
                        if obligatoires_porteurs
                        else " Le porteur trouve n'est pas obligatoire."
                    )
                ),
            })
            continue

        exigence = max(2, round(len(termes) * SEUIL_SURVIVANCE)) if termes else 0
        survivants: list[Any] = []
        if termes and exigence <= len(termes):
            for objet in objets:
                texte = textes.get(objet.path)
                if texte is None:
                    texte = _sans_accents(
                        (ROOT / objet.path).read_text(
                            encoding="utf-8", errors="replace"
                        )
                    ).lower()
                    textes[objet.path] = texte
                if sum(1 for t in termes if racine(t) in texte) >= exigence:
                    survivants.append(objet)
        # Un contenu retire n'est fautif que s'il est presente comme exigible :
        # dans un cours ou une evaluation, l'eleve le travaillera comme un
        # attendu alors que le programme ne le demande plus.
        exigibles = [
            o for o in survivants
            if o.role in ("PRIMARY_TEACHING", "ASSESSMENT")
        ]
        if not survivants:
            classement = "REMOVED_AND_ABSENT"
            motif = "le contenu retire ne subsiste pas dans le manuel"
        elif exigibles:
            classement = "STILL_PRESENTED_AS_REQUIRED"
            motif = (
                "subsiste dans un cours ou une evaluation : l'eleve le "
                "travaillera comme un attendu alors que le programme ne le "
                "demande plus"
            )
        else:
            classement = "ENRICHMENT_NOT_REQUIRED_FOR_PROGRAMME"
            motif = (
                "subsiste hors du cours et de l'evaluation : il peut rester "
                "comme approfondissement sans compter dans la couverture"
            )
        retires.append({
            "official_id_2019": verdict["official_id_2019"],
            "official_wording": libelle,
            "still_in_programme_as": None,
            "surviving_objects": sorted(o.object_id for o in survivants),
            "surviving_in_course_or_assessment": sorted(
                o.object_id for o in exigibles
            ),
            "classification": classement,
            "reason": motif,
        })

    compte_a = Counter(x["classification"] for x in ajoutes)
    compte_r = Counter(x["classification"] for x in retires)
    charge = {
        "artifact_type": "reform_transition_audit",
        "schema_version": 1,
        "generated_by": "scripts/build_1spe_reform_transition_audit.py",
        "manual": "1SPE",
        "from_authority": diff["from_authority"],
        "to_authority": diff["to_authority"],
        "summary": {
            "ADDED_2026_MANDATORY": len(ajoutes),
            "ADDED_TRULY_MISSING": compte_a.get("TRULY_MISSING", 0),
            "ADDED_ALREADY_PRESENT_WITHOUT_OFFICIAL_MAPPING": compte_a.get(
                "ALREADY_PRESENT_WITHOUT_OFFICIAL_MAPPING", 0
            ),
            "ADDED_ALREADY_FIXED": compte_a.get("NEWLY_ADDED_AND_ALREADY_FIXED", 0),
            "REMOVED_2026_MANDATORY": len(retires),
            "REMOVED_2019_CONTENT_STILL_PRESENTED_AS_REQUIRED": compte_r.get(
                "STILL_PRESENTED_AS_REQUIRED", 0
            ),
            "REMOVED_KEPT_AS_ENRICHMENT": compte_r.get(
                "ENRICHMENT_NOT_REQUIRED_FOR_PROGRAMME", 0
            ),
            "REMOVED_AND_ABSENT": compte_r.get("REMOVED_AND_ABSENT", 0),
            "REMOVED_BUT_STILL_IN_PROGRAMME": compte_r.get(
                "STILL_IN_PROGRAMME_SHARED_WORDING", 0
            ),
            "REMOVED_2019_CONTENT_REQUIRING_EDITORIAL_REVIEW": compte_r.get(
                "NOTION_STILL_NAMED_IN_PROGRAMME_REQUIRES_REVIEW", 0
            ),
        },
        "added_2026": ajoutes,
        "removed_2026": retires,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Audit de transition conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    print("--- ajoutes en 2026 ---")
    for cle, valeur in sorted(compte_a.items()):
        print(f"  {valeur:3d}  {cle}")
    print("--- retires en 2026 ---")
    for cle, valeur in sorted(compte_r.items()):
        print(f"  {valeur:3d}  {cle}")
    print()
    for cle, valeur in charge["summary"].items():
        print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
