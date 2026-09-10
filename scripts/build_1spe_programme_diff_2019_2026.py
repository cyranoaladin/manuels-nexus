#!/usr/bin/env python3
"""Ce que la reforme de 2026 change au programme de premiere.

Le manuel de premiere a ete ecrit sous le programme de 2019 puis repris sous
celui du 26 fevrier 2026. Dire « le chapitre couvre le programme » sans dire
DE QUEL programme on parle laisse passer les deux erreurs symetriques : un
attendu retire en 2026 qu'on continue d'enseigner et de compter comme
couverture, et un attendu ajoute en 2026 que personne ne cherche parce qu'il
n'existait pas dans la version d'avant.

Ce differentiel compare les deux inventaires officiels item par item et range
chaque attendu dans l'une des cinq situations : UNCHANGED, MOVED,
REFORMULATED_2026, ADDED_2026, REMOVED_2026.

Une reformulation n'est jamais affirmee sans preuve : les deux libelles et la
mesure de leur proximite sont publies avec elle, et le rapprochement reste
soumis a lecture humaine. Ce qui est certain -- l'identite mot pour mot, et
l'absence de tout correspondant -- est distingue de ce qui est propose.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_official_programme_binding import forme_typographique, jetons, proximite

ROOT = Path(__file__).resolve().parents[1]
ANCIEN = ROOT / "audit" / "official" / "1SPE_MENE1901632A.json"
NOUVEAU = ROOT / "audit" / "official" / "1SPE_MENE2602917A.json"
OUT = ROOT / "audit" / "1SPE_PROGRAMME_DIFF_2019_2026.json"

#: En deca, deux libelles ne parlent pas du meme attendu et les rapprocher
#: masquerait un ajout ou une suppression sous une pretendue reformulation.
SEUIL_REFORMULATION = 0.42


def emplacement(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        item["official_section"] or "",
        item["official_subsection"] or "",
        item["official_rubric"] or "",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    ancien = json.loads(ANCIEN.read_text(encoding="utf-8"))
    nouveau = json.loads(NOUVEAU.read_text(encoding="utf-8"))

    # L'appariement se fait sur le libelle seul, pas sur le couple
    # libelle+nature : quand le BO reclasse un attendu qu'il enonce dans les
    # memes termes, c'est un changement de nature, pas une suppression suivie
    # d'un ajout. Les compter comme deux mouvements distincts gonflerait des
    # deux cotes et cacherait ce qui a reellement change.
    par_cle_2019: dict[str, list[dict[str, Any]]] = {}
    for item in ancien["items"]:
        par_cle_2019.setdefault(
            forme_typographique(item["official_wording"]), []
        ).append(item)

    verdicts: list[dict[str, Any]] = []
    restants_2019 = {id(i): i for i in ancien["items"]}
    apparies_2026: set[str] = set()

    # 1. Identites mot pour mot : le seul rapprochement qui ne demande aucun
    #    jugement. Selon que l'emplacement bouge ou non, c'est MOVED ou
    #    UNCHANGED -- un attendu deplace reste du au manuel, mais pas au meme
    #    chapitre, et le confondre avec un inchange masque une reorganisation.
    for item in nouveau["items"]:
        cle = forme_typographique(item["official_wording"])
        candidats = [c for c in par_cle_2019.get(cle, []) if id(c) in restants_2019]
        if not candidats:
            continue
        jumeau = candidats[0]
        del restants_2019[id(jumeau)]
        apparies_2026.add(item["official_id"])
        bouge = emplacement(item) != emplacement(jumeau)
        reclasse = item["kind"] != jumeau["kind"]
        verdicts.append({
            "verdict": (
                "RECLASSIFIED_2026" if reclasse
                else "MOVED" if bouge
                else "UNCHANGED"
            ),
            "kind": item["kind"],
            "kind_2019": jumeau["kind"],
            "official_id_2026": item["official_id"],
            "official_wording": item["official_wording"],
            "location_2019": list(emplacement(jumeau)),
            "location_2026": list(emplacement(item)),
            "evidence": "libelle identique au caractere pres",
            "review_status": "ESTABLISHED",
        })

    # 2. Reformulations : rapprochement mesure, publie avec sa mesure, et
    #    soumis a lecture humaine. Un appariement est retenu au plus une fois,
    #    faute de quoi un meme attendu de 2019 servirait d'antecedent a
    #    plusieurs attendus de 2026 et masquerait autant d'ajouts reels.
    paires: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
    for item in nouveau["items"]:
        if item["official_id"] in apparies_2026:
            continue
        for ancien_item in restants_2019.values():
            # Le rapprochement ne se limite pas aux attendus de meme nature.
            # La reforme deplace justement des capacites vers les automatismes
            # -- « Calculer des probabilites conditionnelles lorsque les
            # evenements sont presentes sous forme de tableau croise » est une
            # capacite attendue en 2019 et un automatisme en 2026, a une
            # rectification orthographique pres. Exiger la meme nature la
            # faisait ressortir comme retiree d'un cote et ajoutee de l'autre.
            note = proximite(
                jetons(item["official_wording"]),
                jetons(ancien_item["official_wording"]),
            )
            if note >= SEUIL_REFORMULATION:
                paires.append((note, item, ancien_item))
    paires.sort(key=lambda t: (-t[0], t[1]["official_id"]))
    pris_2019: set[int] = set()
    for note, item, ancien_item in paires:
        if item["official_id"] in apparies_2026 or id(ancien_item) in pris_2019:
            continue
        apparies_2026.add(item["official_id"])
        pris_2019.add(id(ancien_item))
        #: Au-dela de ce seuil, le libelle est le meme a la ponctuation ou a
        #: l'orthographe pres : ce qui a change est la nature de l'attendu, pas
        #: sa formulation.
        quasi_identique = note >= 0.85
        verdicts.append({
            "verdict": (
                "RECLASSIFIED_2026"
                if quasi_identique and ancien_item["kind"] != item["kind"]
                else "REFORMULATED_2026"
            ),
            "kind": item["kind"],
            "kind_2019": ancien_item["kind"],
            "official_id_2026": item["official_id"],
            "official_wording": item["official_wording"],
            "wording_2019": ancien_item["official_wording"],
            "location_2019": list(emplacement(ancien_item)),
            "location_2026": list(emplacement(item)),
            "similarity": round(note, 3),
            "evidence": "rapprochement mesure sur les mots pleins",
            "review_status": "PROPOSED_REQUIRES_HUMAN_CONFIRMATION",
        })
    for identifiant in pris_2019:
        restants_2019.pop(identifiant, None)

    for item in nouveau["items"]:
        if item["official_id"] in apparies_2026:
            continue
        verdicts.append({
            "verdict": "ADDED_2026",
            "kind": item["kind"],
            "official_id_2026": item["official_id"],
            "official_wording": item["official_wording"],
            "location_2026": list(emplacement(item)),
            "mandatory": item["mandatory"],
            "evidence": "aucun correspondant dans le programme de 2019",
            "review_status": "ESTABLISHED",
        })
    for ancien_item in restants_2019.values():
        verdicts.append({
            "verdict": "REMOVED_2026",
            "kind": ancien_item["kind"],
            "official_id_2019": ancien_item["official_id"],
            "official_wording": ancien_item["official_wording"],
            "location_2019": list(emplacement(ancien_item)),
            "mandatory": ancien_item["mandatory"],
            "evidence": "aucun correspondant dans le programme de 2026",
            "review_status": "ESTABLISHED",
        })

    compte: dict[str, int] = {}
    for v in verdicts:
        compte[v["verdict"]] = compte.get(v["verdict"], 0) + 1
    ajoutes_obligatoires = [
        v for v in verdicts if v["verdict"] == "ADDED_2026" and v.get("mandatory")
    ]
    retires_obligatoires = [
        v for v in verdicts if v["verdict"] == "REMOVED_2026" and v.get("mandatory")
    ]

    # Un attendu qui change de nature ne change pas seulement d'etiquette : une
    # capacite attendue devenue automatisme ne se travaille plus au meme
    # endroit ni au meme moment de l'annee, et ne s'evalue plus de la meme
    # facon. C'est le mouvement le plus facile a manquer, parce que le libelle,
    # lui, n'a presque pas bouge.
    nature_changee = [
        v for v in verdicts
        if v.get("kind_2019") and v["kind_2019"] != v["kind"]
    ]
    automatismes_2026 = [v for v in verdicts if v["kind"] == "AUTOMATISM"]
    automatismes_herites = [
        v for v in automatismes_2026 if v.get("kind_2019") not in (None, "AUTOMATISM")
    ]

    charge = {
        "artifact_type": "programme_diff",
        "schema_version": 1,
        "generated_by": "scripts/build_1spe_programme_diff_2019_2026.py",
        "manual": "1SPE",
        "from_authority": ancien["authority_ref"],
        "from_effective": ancien["effective_from"],
        "to_authority": nouveau["authority_ref"],
        "to_effective": nouveau["effective_from"],
        "verdicts_are_established_or_proposed": {
            "ESTABLISHED": "identite mot pour mot, ou absence de tout correspondant",
            "PROPOSED_REQUIRES_HUMAN_CONFIRMATION": "reformulation rapprochee par mesure",
        },
        "summary": {
            "items_2019": len(ancien["items"]),
            "items_2026": len(nouveau["items"]),
            "counts": dict(sorted(compte.items())),
            "ADDED_2026_MANDATORY": len(ajoutes_obligatoires),
            "REMOVED_2026_MANDATORY": len(retires_obligatoires),
            "reformulations_awaiting_review": compte.get("REFORMULATED_2026", 0),
            "KIND_CHANGED_BETWEEN_EDITIONS": len(nature_changee),
            "AUTOMATISMS_2026": len(automatismes_2026),
            "AUTOMATISMS_2026_INHERITED_FROM_A_2019_CAPACITY": len(automatismes_herites),
            "AUTOMATISMS_2026_WITHOUT_ANY_2019_ANTECEDENT": sum(
                1 for v in automatismes_2026 if v["verdict"] == "ADDED_2026"
            ),
        },
        "kind_changed_between_editions": nature_changee,
        "verdicts": verdicts,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Differentiel conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")

    print(f"1SPE : {ancien['authority_ref']} ({ancien['effective_from']})"
          f"  ->  {nouveau['authority_ref']} ({nouveau['effective_from']})")
    for verdict, n in sorted(compte.items()):
        print(f"   {n:4d}  {verdict}")
    print(f"\najoutes obligatoires        : {len(ajoutes_obligatoires)}")
    print(f"retires obligatoires        : {len(retires_obligatoires)}")
    print(f"attendus changeant de nature: {len(nature_changee)}")
    print(f"automatismes 2026           : {len(automatismes_2026)}"
          f"  dont {len(automatismes_herites)} herites d'une capacite de 2019")
    return 0


if __name__ == "__main__":
    sys.exit(main())
