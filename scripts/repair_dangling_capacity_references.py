#!/usr/bin/env python3
"""Repare les capacites citees par des objets mais absentes de tout referentiel.

Le defaut est invisible a la lecture : la metadonnee est bien remplie, elle
designe simplement quelque chose qui n'existe pas. L'objet parait rattache au
programme et ne l'est pas ; aucun controle ne s'en apercoit, et la couverture
qu'il devait prouver reste sans preuve.

Quatre familles, quatre reparations differentes -- et surtout, aucune creation
d'atome destinee a faire tomber un compteur :

  LOCAL_CODE_IN_WRONG_FIELD   « C1 » est un code de chapitre, pas un
                              identifiant d'atome. Il est deplace dans le champ
                              qui lui revient, ou le contrat sait le resoudre.
  TYPO_OR_ALIAS               « 1NSI-ALGO-DICHO-GLOUTON-KNN-C1 » est un
                              identifiant forge en collant le nom du chapitre au
                              code local. L'objet porte deja le code : la
                              reference inventee est retiree.
  MISSING_REFERENTIAL_ENTRY   le contrat declare une capacite que le
                              referentiel n'a jamais recue. Elle existe
                              pourtant, elle est enseignee, et le BO la porte :
                              l'entree manquante est creee.
  PREAMBLE_REFERENCE          « BO-PREAMBULE-... » designe le preambule du
                              programme, dans son espace de noms propre. Rien
                              a reparer ici : c'est l'inventaire officiel qui
                              devait porter ces passages, et il les porte
                              desormais.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_objects import META, fichiers_suivis

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "DANGLING_CAPACITY_REPAIRS.json"

CODE_LOCAL = re.compile(r"^C\d+$")

REFERENTIELS = (
    ROOT / "Mathematiques" / "manuel-maths" / "referentiel",
    ROOT / "NSI" / "referentiel",
)


def atomes_connus() -> set[str]:
    """Identifiants reellement definis par les referentiels.

    Ce controle est la garde de tout le script. Un identifiant qui RESSEMBLE a
    un alias forge -- nom du chapitre suivi du code -- peut parfaitement etre
    l'identifiant canonique d'une capacite : « 1SPE-DERIVATION-GLOBAL-C1 » en
    est un. Ne se fier qu'a la forme reviendrait a effacer le rattachement de
    centaines d'objets parfaitement declares.
    """
    connus: set[str] = set()
    for dossier in REFERENTIELS:
        for chemin in sorted(dossier.glob("capacites_*.json")):
            charge = json.loads(chemin.read_text(encoding="utf-8"))
            connus.update(c["id"] for c in charge.get("capacites", []))
    return connus

#: Capacites que des contrats declarent et que le referentiel n'a jamais
#: recues. Chacune est enseignee par son chapitre et repond a un attendu du
#: programme : l'entree est creee avec le libelle du contrat, jamais invente.
ENTREES_MANQUANTES: tuple[dict[str, str], ...] = (
    {
        "referentiel": "Mathematiques/manuel-maths/referentiel/capacites_TCOMPL_TEMPS-ATTENTE.json",
        "id": "TCOMPL-ATT-C7",
        "libelle": (
            "Définir la loi uniforme sur [0,1] puis sur [a,b], déterminer sa "
            "densité et sa fonction de répartition."
        ),
        "contenu": "Lois uniformes discrètes et continues sur [0,1].",
        "contrat": "Mathematiques/manuel-maths/chapitres/TCOMPL-TEMPS-ATTENTE/contrat.yaml",
    },
    {
        "referentiel": "Mathematiques/manuel-maths/referentiel/capacites_TCOMPL_ECHANTILLONNAGE.json",
        "id": "TCOMPL-ECH-C7",
        "libelle": "Définir la loi uniforme sur {1,2,…,n} et calculer son espérance.",
        "contenu": "Lois uniformes discrètes et continues sur [0,1].",
        "contrat": "Mathematiques/manuel-maths/chapitres/TCOMPL-ECHANTILLONNAGE/contrat.yaml",
    },
    {
        "referentiel": "Mathematiques/manuel-maths/referentiel/capacites_TCOMPL_MODELES-EVOLUTION.json",
        "id": "TCOMPL-ME-C6",
        "libelle": (
            "Mobiliser la notion intuitive de limite finie ou infinie d'une "
            "suite et les opérations sur les limites."
        ),
        "contenu": "Limites de suites.",
        "contrat": "Mathematiques/manuel-maths/chapitres/TCOMPL-MODELES-EVOLUTION/contrat.yaml",
    },
)


def _reecrire_meta(chemin: Path, meta: dict[str, Any]) -> None:
    texte = chemin.read_text(encoding="utf-8")
    trouve = META.search(texte)
    assert trouve is not None
    rendu = "% META: " + json.dumps(meta, ensure_ascii=False)
    chemin.write_text(
        texte[: trouve.start()] + rendu + texte[trouve.end() :], encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    connus = atomes_connus()
    reparations: list[dict[str, Any]] = []
    a_ecrire: list[tuple[Path, dict[str, Any]]] = []

    for chemin in fichiers_suivis(".tex"):
        texte = chemin.read_text(encoding="utf-8", errors="replace")
        trouve = META.search(texte)
        if not trouve:
            continue
        try:
            meta = json.loads(trouve.group(1))
        except json.JSONDecodeError:
            continue
        citees = list(meta.get("capacites") or [])
        if not citees:
            continue
        codes_locaux = [c for c in citees if CODE_LOCAL.match(c)]
        # Un alias n'est retire que s'il ne designe AUCUNE capacite existante
        # et que le code local correspondant est deja porte par l'objet : la
        # reference inventee est alors redondante, et fausse.
        codes_portes = set(meta.get("capacites_codes") or [])
        alias = [
            c for c in citees
            if not CODE_LOCAL.match(c)
            and c not in connus
            and c.startswith(str(meta.get("chapitre", "")) + "-")
            and c.rsplit("-", 1)[-1] in codes_portes
        ]
        if not codes_locaux and not alias:
            continue
        restantes = [c for c in citees if c not in codes_locaux and c not in alias]
        nouveaux_codes = sorted(
            {*(meta.get("capacites_codes") or []), *codes_locaux},
            key=lambda c: (len(c), c),
        )
        neuf = dict(meta)
        if restantes:
            neuf["capacites"] = restantes
        else:
            neuf.pop("capacites", None)
        if nouveaux_codes:
            neuf["capacites_codes"] = nouveaux_codes
        a_ecrire.append((chemin, neuf))
        if codes_locaux:
            reparations.append({
                "object_id": meta.get("id"),
                "path": str(chemin.relative_to(ROOT)),
                "classification": "LOCAL_CODE_IN_WRONG_FIELD",
                "moved": codes_locaux,
                "reason": (
                    "codes de chapitre ecrits dans le champ reserve aux "
                    "identifiants d'atome ; deplaces vers `capacites_codes`, "
                    "que le contrat sait resoudre"
                ),
            })
        if alias:
            reparations.append({
                "object_id": meta.get("id"),
                "path": str(chemin.relative_to(ROOT)),
                "classification": "TYPO_OR_ALIAS",
                "removed": alias,
                "reason": (
                    "identifiant forge en collant le nom du chapitre au code "
                    "local ; l'objet porte deja ce code, la reference inventee "
                    "est retiree"
                ),
            })

    entrees: list[dict[str, Any]] = []
    for entree in ENTREES_MANQUANTES:
        chemin = ROOT / entree["referentiel"]
        charge = json.loads(chemin.read_text(encoding="utf-8"))
        deja = {c["id"] for c in charge["capacites"]}
        entrees.append({
            "capacity_id": entree["id"],
            "referential": entree["referentiel"],
            "declared_by": entree["contrat"],
            "classification": "MISSING_REFERENTIAL_ENTRY",
            "already_present": entree["id"] in deja,
            "reason": (
                "le contrat de chapitre declare cette capacite depuis "
                "l'origine ; le referentiel ne l'avait jamais recue"
            ),
        })
        if entree["id"] in deja or args.check:
            continue
        charge["capacites"].append({
            "id": entree["id"],
            "libelle_bo": entree["libelle"],
            "libelle_interne": entree["libelle"],
            "libelle_bo_is_verbatim": False,
            "contenu_bo": entree["contenu"],
            "libelle_eleve": "",
            "demonstration_exigible": False,
        })
        chemin.write_text(
            json.dumps(charge, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    if not args.check:
        for chemin, meta in a_ecrire:
            _reecrire_meta(chemin, meta)

    charge_sortie = {
        "artifact_type": "dangling_capacity_repairs",
        "schema_version": 1,
        "generated_by": "scripts/repair_dangling_capacity_references.py",
        "summary": {
            "OBJECTS_REPAIRED": len({r["object_id"] for r in reparations}),
            "LOCAL_CODE_IN_WRONG_FIELD": sum(
                1 for r in reparations if r["classification"] == "LOCAL_CODE_IN_WRONG_FIELD"
            ),
            "TYPO_OR_ALIAS": sum(
                1 for r in reparations if r["classification"] == "TYPO_OR_ALIAS"
            ),
            "MISSING_REFERENTIAL_ENTRIES_CREATED": len(entrees),
        },
        "object_repairs": sorted(reparations, key=lambda r: r["object_id"] or ""),
        "referential_entries": entrees,
    }
    texte = json.dumps(charge_sortie, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        restant = [r for r in reparations]
        if restant or any(not e["already_present"] for e in entrees):
            print("REPARATIONS EN ATTENTE :", len(restant))
            return 1
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Aucune reference pendante en attente.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    resume = charge_sortie["summary"]
    assert isinstance(resume, dict)
    for cle, valeur in resume.items():
        print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
