#!/usr/bin/env python3
"""La capacite d'un objet se DERIVE de son contenu, jamais d'une rotation.

Le remplissage attribuait les codes en tournant : `C6, C7, C8, C9, C1, C2...`
a partir du sixieme fichier. Un exercice de convexite devenait ainsi
`TEXP-ARI-C3` -- « tests de divisibilite, primalite, chiffrement » -- sans que
rien dans son enonce ne l'y rattache.

Ce gate rend cette mecanique impossible, par deux voies independantes.

STRUCTURELLE, et automatique sur toute la collection. Si la suite des codes
declares par les exercices d'un chapitre est PERIODIQUE sur l'ordre du
contrat, l'attribution ne vient pas du contenu : elle vient d'un compteur.
Aucune signature n'est requise pour le voir.

SEMANTIQUE, et declaree. `capacity_signatures.py` dit, capacite par capacite,
quels objets mathematiques doivent apparaitre. Une capacite sans signature
n'est pas declaree alignee : elle est declaree NON VERIFIEE, et le registre
le dit plutot que de la compter comme un succes.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import capacity_signatures as signatures  # noqa: E402

CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)
JSON_TARGET = ROOT / "audit/CAPACITY_CONTENT_ALIGNMENT.json"
MD_TARGET = ROOT / "audit/CAPACITY_CONTENT_ALIGNMENT.md"
GENERATED_BY = "scripts/build_capacity_content_alignment.py"

ALIGNED = "ALIGNED"
MISALIGNED = "CAPACITY_CONTENT_MISALIGNMENT"
UNVERIFIED = "NO_SIGNATURE_DECLARED"
STATES = (ALIGNED, MISALIGNED, UNVERIFIED)

#: En dessous de cette longueur, une suite de codes ne prouve aucune rotation :
#: deux exercices qui se suivent sur C1 puis C2 sont une progression normale.
MIN_CYCLE_EVIDENCE = 12


def read_meta(text: str) -> dict[str, Any]:
    if "META:" not in text:
        return {}
    try:
        return json.loads(text.split("META:", 1)[1].splitlines()[0].strip())
    except json.JSONDecodeError:
        return {}


def body_of(text: str) -> str:
    """Ce que l'eleve lit ET ce que la machine verifie.

    Le bloc oracle fait partie de la preuve : un exercice d'arithmetique dont
    l'oracle appelle `math.gcd` le montre aussi surement que son enonce.
    """

    return "\n".join(
        ligne for ligne in text.splitlines() if not ligne.lstrip().startswith("% META:")
    )


def detect_round_robin(codes: list[str], contract_order: list[str]) -> dict[str, Any]:
    """La suite des codes est-elle engendree par un compteur ?

    On cherche la plus longue queue periodique. Une periode egale au nombre de
    capacites, sur une queue assez longue, ne s'explique pas par le contenu.
    """

    simples = [c for c in codes if c]
    for depart in range(len(simples)):
        queue = simples[depart:]
        if len(queue) < MIN_CYCLE_EVIDENCE:
            break
        # UNE ROTATION EST UN BALAYAGE DU CONTRAT. On exige donc que la
        # periode soit exactement le nombre de capacites, et qu'il y en ait au
        # moins trois : dans un chapitre a deux capacites, alterner C1 et C2
        # est une progression deliberee, pas un compteur -- la periode
        # minimale possible ne prouve rien.
        periodes = [len(contract_order)] if len(contract_order) >= 3 else []
        for periode in periodes:
            if len(queue) < 2 * periode:
                continue
            if not all(
                queue[i] == queue[i - periode] for i in range(periode, len(queue))
            ):
                continue
            # ET chaque tour doit VISITER TOUTE la table : une queue constante
            # (`C3, C3, C3...`) est periodique pour n'importe quelle periode,
            # et c'est une serie deliberee sur une capacite, pas un compteur.
            tour = queue[:periode]
            if sorted(tour) == sorted(contract_order):
                return {
                    "detected": True,
                    "period": periode,
                    "from_index": depart,
                    "run_length": len(queue),
                }
    return {"detected": False, "period": None, "from_index": None, "run_length": 0}


def evaluate_signature(body: str, signature: dict[str, list]) -> dict[str, Any]:
    manquants: list[list[str]] = []
    for groupe in signature.get("required", []):
        if not any(re.search(motif, body, re.I) for motif in groupe):
            manquants.append(groupe)
    interdits = [
        motif
        for motif in signature.get("forbidden", [])
        if re.search(motif, body, re.I)
    ]
    return {
        "missing_required_groups": manquants,
        "forbidden_markers_found": interdits,
        "aligned": not manquants and not interdits,
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    objets: list[dict[str, Any]] = []
    chapitres: dict[str, dict[str, Any]] = {}

    for corpus in CORPORA:
        if not corpus.is_dir():
            continue
        for chapitre_dir in sorted(corpus.iterdir()):
            contrat = chapitre_dir / "contrat.yaml"
            if not contrat.is_file():
                continue
            chapitre = chapitre_dir.name
            declare = yaml.safe_load(contrat.read_text(encoding="utf-8")) or {}
            ordre = [c["code"] for c in declare.get("capacites", [])]
            suite: list[str] = []
            exercices = chapitre_dir / "exercices"
            if exercices.is_dir():
                for chemin in sorted(exercices.glob("*.tex")):
                    texte = chemin.read_text(encoding="utf-8", errors="replace")
                    meta = read_meta(texte)
                    codes = meta.get("capacites_codes") or []
                    suite.append(codes[0] if len(codes) == 1 else "")
                    corps = body_of(texte)
                    for code in codes:
                        signature = signatures.signature_for(chapitre, code)
                        if signature is None:
                            etat, detail = UNVERIFIED, None
                        else:
                            detail = evaluate_signature(corps, signature)
                            etat = ALIGNED if detail["aligned"] else MISALIGNED
                        objets.append({
                            "object_id": meta.get("id"),
                            "path": str(chemin.relative_to(root)),
                            "chapter": chapitre,
                            "capacity": code,
                            "state": etat,
                            "evidence": detail,
                        })
            rotation = detect_round_robin(suite, ordre)
            chapitres[chapitre] = {
                "contract_capacities": ordre,
                "exercise_count": len(suite),
                "round_robin": rotation,
            }

    par_etat = collections.Counter(o["state"] for o in objets)
    rotations = [ch for ch, info in chapitres.items() if info["round_robin"]["detected"]]
    summary = {etat: par_etat.get(etat, 0) for etat in STATES}
    summary.update({
        "CAPACITY_ASSIGNMENTS_EXAMINED": len(objets),
        "CAPACITY_CONTENT_MISALIGNMENT": par_etat.get(MISALIGNED, 0),
        "ROUND_ROBIN_CAPACITY_ASSIGNMENT": len(rotations),
        "CHAPTERS_WITH_DECLARED_SIGNATURES": len(signatures.declared_chapters()),
        "STATES_SUM_EQUALS_TOTAL": sum(par_etat.values()) == len(objets),
        "APPROVES_NOTHING": True,
    })

    return {
        "artifact_type": "capacity_content_alignment",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "states": list(STATES),
        "signature_table": "scripts/capacity_signatures.py",
        "rule": (
            "une capacite se derive du contenu : une suite periodique de codes "
            "vient d'un compteur, et une signature non satisfaite n'est pas "
            "rachetee par la declaration"
        ),
        "summary": summary,
        "round_robin_chapters": sorted(rotations),
        "chapters": chapitres,
        "assignments": objets,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Alignement capacite / contenu",
        "",
        payload["rule"].capitalize() + ".",
        "",
        f"- `CAPACITY_CONTENT_MISALIGNMENT` : `{s['CAPACITY_CONTENT_MISALIGNMENT']}`",
        f"- `ROUND_ROBIN_CAPACITY_ASSIGNMENT` : `{s['ROUND_ROBIN_CAPACITY_ASSIGNMENT']}`",
        f"- attributions examinees : `{s['CAPACITY_ASSIGNMENTS_EXAMINED']}`",
        f"- non verifiees faute de signature : `{s[UNVERIFIED]}`",
        "",
    ]
    if payload["round_robin_chapters"]:
        lignes += ["## Chapitres a attribution periodique", ""]
        for chapitre in payload["round_robin_chapters"]:
            info = payload["chapters"][chapitre]["round_robin"]
            lignes.append(
                f"- `{chapitre}` : periode {info['period']} sur "
                f"{info['run_length']} exercices"
            )
        lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build(ROOT)
    rendus = {
        JSON_TARGET: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MD_TARGET: render_markdown(payload),
    }
    if args.check:
        ecarts = [
            str(p.relative_to(ROOT))
            for p, c in rendus.items()
            if not p.is_file() or p.read_text(encoding="utf-8") != c
        ]
        for e in ecarts:
            print(f"diff: {e}")
        return 1 if ecarts else 0
    for chemin, contenu in rendus.items():
        chemin.write_text(contenu, encoding="utf-8")
        print(f"wrote {chemin.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
