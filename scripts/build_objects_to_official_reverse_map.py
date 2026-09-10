#!/usr/bin/env python3
"""Le sens inverse : chaque objet du manuel releve-t-il du programme ?

La matrice de couverture regarde le programme et cherche ce qui le prouve. Elle
ne dit rien de ce que le manuel contient EN PLUS. Un manuel peut couvrir tout
le programme et consacrer un tiers de sa progression a des contenus hors annee
ou hors sujet : l'eleve travaillerait beaucoup pour une epreuve qui ne le lui
demandera pas.

Ce n'est pas un proces fait a l'enrichissement. Un manuel a le droit -- et
souvent l'interet -- de depasser le programme, de rappeler un prerequis, ou
d'entrainer au format de l'epreuve. Ce qui n'est pas acceptable, c'est qu'un
objet n'ait AUCUN statut : ni attendu, ni prerequis, ni enrichissement assume,
ni entrainement. C'est ce residu que compte
`UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS`.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_official_to_manual_coverage import (
    _sans_accents,
    _slug_preambule,
    racine,
    termes_distinctifs,
)
from manual_objects import charger_contrats, charger_objets, charger_transversaux

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
OUT = ROOT / "audit" / "OBJECTS_TO_OFFICIAL_REVERSE_MAP.json"

#: Types d'objets qui entrainent au format de l'epreuve plutot qu'a une notion.
ENTRAINEMENT_EPREUVE = {"banque_ecrite", "banque_pratique"}
#: Types d'objets qui reprennent un acquis anterieur pour le remettre en place.
REPRISE = {"remediation", "amenagee", "coup_de_pouce"}
#: Termes qu'un objet doit partager avec un attendu d'un programme non
#: applicable pour qu'on le soupconne de travailler hors annee.
TERMES_HORS_ANNEE = 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    liaison = json.loads(BINDING.read_text(encoding="utf-8"))
    couverture = json.loads(COVERAGE.read_text(encoding="utf-8"))
    contrats = charger_contrats()
    objets = charger_objets(contrats) + charger_transversaux()

    obligatoire_par_id = {
        r["official_id"]: r["mandatory"] for r in couverture["rows"]
    }
    parents_par_atome: dict[str, list[str]] = defaultdict(list)
    for lien in liaison["bindings"]:
        if lien["binding_method"] in ("ANCHOR", "VERBATIM", "CONTEXT", "DISPOSED"):
            for oid in lien.get("official_ids") or [lien["official_id"]]:
                parents_par_atome[lien["atom_id"]].append(oid)

    # Les objets deja retenus comme preuve par la matrice de couverture : un
    # objet qui prouve un attendu obligatoire releve du programme, meme s'il ne
    # declare aucune capacite.
    atomes_en_attente = {
        lien["atom_id"]
        for lien in liaison["bindings"]
        if lien["review_status"] == "AMBIGUOUS_REQUIRES_HUMAN"
    }
    prouve_un_attendu: dict[str, set[str]] = defaultdict(set)
    # Un objet retenu comme preuve d'un attendu NON obligatoire n'est pas non
    # plus sans justification : le programme nomme cet attendu, il ne l'impose
    # pas. C'est le cas de la page d'algorithmes de l'exponentielle, qui met en
    # oeuvre les deux « Exemples d'algorithme » du BO. La distinction est
    # conservee : elle decide du classement, elle ne se perd pas.
    prouve_un_attendu_facultatif: dict[str, set[str]] = defaultdict(set)
    for ligne in couverture["rows"]:
        cible = (
            prouve_un_attendu if ligne["mandatory"] else prouve_un_attendu_facultatif
        )
        for role in ligne["objects_by_role"]:
            for oid in ligne["objects_by_role"][role]:
                cible[oid].add(ligne["official_id"])

    hors_edition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entree in index["documents"]:
        if entree["applies_to_edition"]:
            continue
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        hors_edition[entree["manual"]].extend(charge["items"])

    # Un attendu d'un programme non applicable ne temoigne du hors-annee que
    # s'il est ETRANGER au programme en vigueur. Les programmes de 2019 et de
    # 2026 se recouvrent largement : sans ce filtre, presque tout objet de
    # premiere partageait trois mots avec un attendu de 2019 et se retrouvait
    # declare hors annee.
    applicables: dict[str, str] = defaultdict(str)
    for ligne in couverture["rows"]:
        applicables[ligne["manual"]] += " " + _sans_accents(
            ligne["official_wording"]
        ).lower()
    temoins_hors_annee: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for manuel, items in hors_edition.items():
        courant = applicables.get(manuel, "")
        for item in items:
            termes = termes_distinctifs(item["official_wording"])
            if len(termes) < TERMES_HORS_ANNEE:
                continue
            if any(racine(t) not in courant for t in termes):
                # Au moins un terme de cet attendu ne figure nulle part dans le
                # programme applicable : il porte donc quelque chose que ce
                # programme ne demande pas.
                temoins_hors_annee[manuel].append(item)

    # Un objet peut citer une capacite qui n'existe nulle part. C'est une
    # reference pendante : personne ne s'en apercoit, l'objet parait rattache,
    # et il ne l'est pas. Trois causes se melangent ici -- un code local ecrit
    # dans le champ reserve aux identifiants d'atome, un identifiant d'atome
    # jamais cree, et des competences du preambule qui n'ont pas d'entree dans
    # les referentiels.
    atomes_connus = {lien["atom_id"] for lien in liaison["bindings"]}
    # « BO-PREAMBULE-... » n'est pas une capacite disciplinaire : c'est une
    # reference au preambule du programme, dans son espace de noms propre. Elle
    # est connue des lors que l'inventaire officiel porte la partie qu'elle
    # designe -- ce qui evite a la fois d'inventer une fausse capacite et de
    # compter une reference legitime parmi les fantomes.
    parties_de_preambule = {
        (ligne["manual"], _slug_preambule(ligne["official_subsection"] or ""))
        for ligne in couverture["rows"]
        if ligne["official_section"] == "Préambule"
    }
    references_pendantes: dict[str, list[str]] = defaultdict(list)
    for objet in objets:
        for atome in objet.atoms:
            if atome in atomes_connus:
                continue
            if atome.startswith("BO-PREAMBULE-") and (
                objet.manual,
                atome.removeprefix("BO-PREAMBULE-"),
            ) in parties_de_preambule:
                continue
            references_pendantes[atome].append(objet.object_id)

    lignes: list[dict[str, Any]] = []
    textes: dict[str, str] = {}
    for objet in objets:
        parents_declares = sorted(
            {oid for a in objet.atoms for oid in parents_par_atome.get(a, [])}
            | prouve_un_attendu.get(objet.object_id, set())
        )
        facultatifs_prouves = sorted(
            prouve_un_attendu_facultatif.get(objet.object_id, set())
            - set(parents_declares)
        )
        parents = sorted(set(parents_declares) | set(facultatifs_prouves))
        obligatoires = [p for p in parents if obligatoire_par_id.get(p)]
        if obligatoires:
            classement = "IN_PROGRAMME"
            motif = f"sert {len(obligatoires)} attendu(s) obligatoire(s)"
        elif objet.kind in ENTRAINEMENT_EPREUVE:
            classement = "EXAM_TRAINING"
            motif = "objet de banque, destine au format de l'epreuve"
        elif parents_declares:
            classement = "LEGITIMATE_ENRICHMENT"
            motif = (
                "rattache au programme, mais a des attendus que le texte ne "
                "rend pas obligatoires"
            )
        elif any(a.startswith("BO-PREAMBULE-") for a in objet.atoms):
            # L'objet cite une competence du preambule que l'inventaire ne
            # porte pas : seule la partie prescriptive « Demarche de projet » y
            # a ete versee. Ce n'est pas un objet sans justification -- il dit
            # d'ou il vient --, c'est l'inventaire qui s'arrete avant.
            classement = "CITES_A_PREAMBLE_COMPETENCE_NOT_INVENTORIED"
            motif = (
                "se reclame d'une competence du preambule du programme, hors "
                "du perimetre actuel de l'inventaire officiel"
            )
        elif objet.programme_alignment == "OPTIONAL_EXTENSION":
            # L'objet declare lui-meme qu'il sort du programme de l'annee.
            classement = "LEGITIMATE_ENRICHMENT"
            motif = (
                "l'objet s'annonce comme extension hors programme"
                + (f" : « {objet.extension_label} »" if objet.extension_label else "")
            )
        elif objet.atoms and any(
            a in atomes_en_attente for a in objet.atoms
        ):
            # L'objet declare une capacite, mais le parent officiel de cette
            # capacite attend encore un arbitrage. Le ranger parmi les
            # hors-sujet reprocherait au manuel un travail inachevé du
            # rattachement, pas un defaut de contenu.
            classement = "AWAITING_BINDING_ARBITRATION"
            motif = (
                "sert une capacite interne dont le parent officiel n'est pas "
                "encore etabli"
            )
        elif objet.kind in REPRISE:
            classement = "PREREQUISITE"
            motif = (
                "objet de remediation ou de reprise : il remet en place un "
                "acquis anterieur plutot que d'enseigner un attendu"
            )
        else:
            # Dernier examen : l'objet parle-t-il d'un programme qui ne regit
            # pas cette edition ? C'est la seule hypothese qui reste avant de
            # le declarer sans statut.
            texte = textes.get(objet.path)
            if texte is None:
                texte = _sans_accents(
                    (ROOT / objet.path).read_text(encoding="utf-8", errors="replace")
                ).lower()
                textes[objet.path] = texte
            hors = None
            for item in temoins_hors_annee.get(objet.manual, []):
                termes = termes_distinctifs(item["official_wording"])
                etrangers = [
                    t for t in termes
                    if racine(t) not in applicables.get(objet.manual, "")
                ]
                # L'objet doit reprendre les termes ETRANGERS au programme en
                # vigueur, pas seulement ceux que les deux editions partagent.
                if etrangers and all(racine(t) in texte for t in etrangers) and sum(
                    1 for t in termes if racine(t) in texte
                ) >= TERMES_HORS_ANNEE:
                    hors = item
                    break
            if hors is not None:
                classement = "WRONG_YEAR"
                motif = (
                    "reprend un attendu d'un programme qui ne regit pas cette "
                    f"edition ({hors['authority_ref']})"
                )
            elif facultatifs_prouves:
                # La matrice de couverture le cite deja comme preuve d'un
                # attendu officiel que le texte ne rend pas obligatoire. Le
                # declarer « sans justification » contredirait l'artefact qui
                # le nomme. Le controle du hors-annee passe avant : un objet
                # qui traite un programme perime ne se rachete pas en croisant
                # au passage un exemple facultatif du programme en vigueur.
                classement = "LEGITIMATE_ENRICHMENT"
                motif = (
                    "met en oeuvre un attendu officiel non obligatoire "
                    f"({len(facultatifs_prouves)}), sans porter d'attendu exigible"
                )
            elif objet.kind in ("cours", "transversal"):
                classement = "OFF_TOPIC"
                motif = (
                    "objet d'enseignement sans attendu obligatoire ni statut "
                    "d'enrichissement : rien ne dit pourquoi il est la"
                )
            else:
                classement = "OFF_TOPIC"
                motif = "aucun attendu, aucun statut : objet sans justification"
        lignes.append({
            "object_id": objet.object_id,
            "manual": objet.manual,
            "chapter": objet.chapter,
            "kind": objet.kind,
            "role": objet.role,
            "path": objet.path,
            "official_parents": parents,
            "mandatory_parents": obligatoires,
            "classification": classement,
            "reason": motif,
        })

    compte = Counter(x["classification"] for x in lignes)
    sans_statut = [x for x in lignes if x["classification"] == "OFF_TOPIC"]
    charge = {
        "artifact_type": "objects_to_official_reverse_map",
        "schema_version": 1,
        "generated_by": "scripts/build_objects_to_official_reverse_map.py",
        "question": (
            "Chaque objet du manuel releve-t-il du programme, d'un prerequis, "
            "d'un enrichissement assume ou de l'entrainement a l'epreuve ?"
        ),
        "classifications": {
            "IN_PROGRAMME": "sert au moins un attendu obligatoire",
            "LEGITIMATE_ENRICHMENT": (
                "rattache a des attendus non obligatoires, ou declare par "
                "l'objet lui-meme comme extension hors programme"
            ),
            "PREREQUISITE": "remet en place un acquis anterieur",
            "EXAM_TRAINING": "entraine au format de l'epreuve",
            "WRONG_YEAR": "reprend un programme qui ne regit pas cette edition",
            "AWAITING_BINDING_ARBITRATION": (
                "sert une capacite dont le parent officiel attend un arbitrage"
            ),
            "CITES_A_PREAMBLE_COMPETENCE_NOT_INVENTORIED": (
                "se reclame d'une competence du preambule que l'inventaire "
                "officiel ne porte pas encore"
            ),
            "OFF_TOPIC": "sans attendu et sans statut : a examiner",
        },
        "summary": {
            "objects": len(lignes),
            "UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS": len(sans_statut),
            "OBJECTS_CITING_AN_UNKNOWN_CAPACITY": len(
                {o for objs in references_pendantes.values() for o in objs}
            ),
            "UNKNOWN_CAPACITIES_CITED": len(references_pendantes),
            "WRONG_YEAR_OBJECTS": compte.get("WRONG_YEAR", 0),
            "OBJECTS_AWAITING_BINDING_ARBITRATION": compte.get(
                "AWAITING_BINDING_ARBITRATION", 0
            ),
            "classification_counts": dict(sorted(compte.items())),
            "by_manual": {
                manuel: dict(
                    sorted(
                        Counter(
                            x["classification"] for x in lignes if x["manual"] == manuel
                        ).items()
                    )
                )
                for manuel in sorted({x["manual"] for x in lignes})
            },
        },
        "dangling_capacity_references": {
            atome: sorted(objs)
            for atome, objs in sorted(references_pendantes.items())
        },
        "objects": lignes,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Cartographie inverse conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    for cle, valeur in sorted(compte.items()):
        print(f"  {valeur:5d}  {cle}")
    print()
    print(f"UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS = {len(sans_statut)}")
    print(f"WRONG_YEAR_OBJECTS = {compte.get('WRONG_YEAR', 0)}")
    print(f"UNKNOWN_CAPACITIES_CITED = {len(references_pendantes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
