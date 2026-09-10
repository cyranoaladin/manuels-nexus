#!/usr/bin/env python3
"""Aucune couche aval ne doit pouvoir rendre obligatoire ce que le BO ne l'est pas.

C'est le risque propre a toute chaine d'atomisation : le texte officiel place un
enonce sous une rubrique qui ne l'impose pas, puis la mecanique le decoupe, le
renomme, le compte -- et il ressort exigible. Personne n'a menti ; le niveau
d'obligation a simplement ete cree par le traitement.

Le controle refait le chemin en sens inverse. Pour chaque attendu publie, il
recalcule la portee que lui donne SA rubrique dans le texte, et exige que
l'obligation publiee en decoule. Un attendu obligatoire dont la rubrique
d'origine ne l'est pas est un niveau d'obligation fabrique.

Il publie aussi ce que la revue a change : le nombre d'obligations avant et
apres, et la liste des attendus dont la portee a bouge, avec leur
justification. Le nombre n'est jamais l'autorite -- l'autorite est la chaine
BO, rubrique, portee, atome -- mais il doit rester tracable.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import programme_normativity as pn

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"
OUT = ROOT / "audit" / "NORMATIVITY_PROVENANCE_GATE.json"
RELATIF = "audit/OFFICIAL_PROGRAMME_INVENTORY.json"


def _items(charge: dict[str, Any]) -> list[dict[str, Any]]:
    trouves = []
    for entree in charge["documents"]:
        chemin = ROOT / entree["inventory_path"]
        if chemin.is_file():
            trouves.extend(json.loads(chemin.read_text(encoding="utf-8"))["items"])
    return trouves


def _items_du_commit(reference: str) -> dict[str, dict[str, Any]]:
    """Etat publie au dernier commit, pour mesurer ce que la revue a change."""
    try:
        index = json.loads(
            subprocess.run(
                ["git", "show", f"{reference}:{RELATIF}"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )
    except subprocess.CalledProcessError:
        return {}
    trouves: dict[str, dict[str, Any]] = {}
    for entree in index["documents"]:
        try:
            charge = json.loads(
                subprocess.run(
                    ["git", "show", f"{reference}:{entree['inventory_path']}"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout
            )
        except subprocess.CalledProcessError:
            continue
        for item in charge["items"]:
            trouves[item["official_id"]] = item
    return trouves


def portee_de_la_source(item: dict[str, Any]) -> pn.Portee:
    """Portee que la rubrique du texte officiel donne a cet attendu."""
    if item["official_section"] == "Préambule":
        sous = item["official_subsection"] or ""
        if sous.isupper():
            return pn.for_preamble_passage(sous)
        return pn.PROJECT_REQUIREMENT
    if item.get("rubric_is_implicit_in_source"):
        # Le BO n'a ouvert aucune rubrique : la portee vient de la partie, ou
        # du rang commun des listes d'attendus non intitulees.
        return pn.for_section(item["official_section"]) or pn.DEFAULT
    return pn.resolve(item["official_section"], item["official_heading"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--baseline", default="HEAD")
    args = parser.parse_args(argv)

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    items = _items(index)
    avant = _items_du_commit(args.baseline)

    fabriques: list[dict[str, Any]] = []
    incoherents: list[dict[str, Any]] = []
    for item in items:
        source = portee_de_la_source(item)
        if item["mandatory"] and not source.mandatory:
            fabriques.append({
                "official_id": item["official_id"],
                "official_wording": item["official_wording"],
                "official_heading": item["official_heading"],
                "published_normativity": item["official_normativity"],
                "source_normativity": source.normativity,
                "reason": (
                    "publie comme obligatoire alors que la rubrique dont il "
                    "vient ne l'est pas"
                ),
            })
        if item["official_normativity"] != source.normativity:
            incoherents.append({
                "official_id": item["official_id"],
                "published": item["official_normativity"],
                "recomputed": source.normativity,
            })

    changements: list[dict[str, Any]] = []
    for item in items:
        ancien = avant.get(item["official_id"])
        if ancien is None or ancien["mandatory"] == item["mandatory"]:
            continue
        changements.append({
            "official_id": item["official_id"],
            "official_wording": item["official_wording"],
            "official_heading": item["official_heading"],
            "mandatory_before": ancien["mandatory"],
            "mandatory_after": item["mandatory"],
            "normativity_before": ancien.get("official_normativity"),
            "normativity_after": item["official_normativity"],
            "justification": item["normativity_basis"],
        })

    applicables = {
        e["authority_ref"] for e in index["documents"] if e["applies_to_edition"]
    }
    obligatoires_apres = sum(
        1 for i in items if i["mandatory"] and i["authority_ref"] in applicables
    )
    obligatoires_avant = sum(
        1 for i in avant.values()
        if i["mandatory"] and i["authority_ref"] in applicables
    )

    charge = {
        "artifact_type": "normativity_provenance_gate",
        "schema_version": 1,
        "generated_by": "scripts/check_normativity_provenance.py",
        "rule": (
            "Un attendu ne peut etre obligatoire que si la rubrique du texte "
            "officiel dont il vient l'est. Le nombre n'est jamais l'autorite ; "
            "l'autorite est la chaine BO, rubrique, portee, atome."
        ),
        "baseline": args.baseline,
        "summary": {
            "NORMATIVITY_CREATED_BY_ATOMIZATION": len(fabriques),
            "NORMATIVITY_INCONSISTENT_WITH_SOURCE": len(incoherents),
            "MANDATORY_COUNT_BEFORE": obligatoires_avant,
            "MANDATORY_COUNT_AFTER": obligatoires_apres,
            "CHANGED_NORMATIVITY_ITEMS": len(changements),
            "NORMATIVITY_PROVENANCE_GATE": (
                "PASS" if not fabriques and not incoherents else "FAIL"
            ),
        },
        "created_by_atomization": fabriques,
        "inconsistent_with_source": incoherents,
        "changed_normativity_items": sorted(
            changements, key=lambda c: c["official_id"]
        ),
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists():
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        publie = json.loads(OUT.read_text(encoding="utf-8"))
        # La comparaison porte sur le verdict, non sur l'artefact entier : la
        # baseline avance a chaque commit, et le fichier changerait sans qu'un
        # seul attendu ait bouge.
        if publie["summary"]["NORMATIVITY_CREATED_BY_ATOMIZATION"] != len(fabriques):
            print("DIVERGENT : le verdict publie ne correspond plus")
            return 1
        print("Provenance de normativite conforme.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    resume = charge["summary"]
    assert isinstance(resume, dict)
    for cle, valeur in resume.items():
        print(f"{cle} = {valeur}")
    for c in changements[:6]:
        print(f"  [{c['official_heading']}] {c['official_wording'][:56]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
