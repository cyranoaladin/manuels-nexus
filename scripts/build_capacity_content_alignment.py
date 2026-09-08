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

import capacity_evidence_reviews as evidence_reviews  # noqa: E402
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
NOT_EVIDENCED = "NOT_EVIDENCED_BY_SIGNATURE"
UNVERIFIED = "NO_SIGNATURE_DECLARED"
STATES = (ALIGNED, MISALIGNED, NOT_EVIDENCED, UNVERIFIED)

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
                # UN COUP DE POUCE N'EST PAS UN ENONCE. C'est une phrase
                # d'aide attachee a un exercice, qui declare les memes
                # capacites que lui mais n'en porte qu'un fragment : lui
                # demander de satisfaire seul la signature reviendrait a
                # exiger d'une note de bas de page qu'elle tienne le livre.
                # Son corps est donc joint a celui de l'exercice dont il
                # derive, et c'est l'ensemble qui est evalue.
                aides: dict[str, list[str]] = collections.defaultdict(list)
                for chemin in sorted(exercices.glob("*.tex")):
                    texte = chemin.read_text(encoding="utf-8", errors="replace")
                    if "\\coupDePouce" not in texte:
                        continue
                    parent = (read_meta(texte).get("exercice_ref")
                              or (read_meta(texte).get("id") or "").rsplit("-CDP", 1)[0])
                    aides[parent].append(body_of(texte))
                for chemin in sorted(exercices.glob("*.tex")):
                    texte = chemin.read_text(encoding="utf-8", errors="replace")
                    meta = read_meta(texte)
                    codes = meta.get("capacites_codes") or []
                    suite.append(codes[0] if len(codes) == 1 else "")
                    corps = body_of(texte)
                    if "\\coupDePouce" in texte:
                        parent = (meta.get("exercice_ref")
                                  or (meta.get("id") or "").rsplit("-CDP", 1)[0])
                        source = exercices / f"{parent}.tex"
                        if source.is_file():
                            corps = body_of(
                                source.read_text(encoding="utf-8", errors="replace")
                            ) + "\n" + corps
                    elif aides.get(meta.get("id")):
                        corps = corps + "\n" + "\n".join(aides[meta["id"]])
                    for code in codes:
                        signature = signatures.signature_for(chapitre, code)
                        if signature is None:
                            etat, detail = UNVERIFIED, None
                        else:
                            detail = evaluate_signature(corps, signature)
                            # UN MARQUEUR INTERDIT EST UNE PREUVE ; UN MARQUEUR
                            # REQUIS ABSENT N'EN EST PAS UNE. Le premier montre
                            # que le corps parle d'un autre domaine -- c'est le
                            # desalignement. Le second dit seulement que la
                            # signature n'a pas vu ce qu'elle cherchait : un
                            # enonce peut demander une derivee en ecrivant
                            # `f'(x)` sans jamais employer le mot. Compter cela
                            # comme un desalignement ferait crier au loup, et
                            # le gate finirait desarme a force de faux cris.
                            if detail["forbidden_markers_found"]:
                                etat = MISALIGNED
                            elif detail["missing_required_groups"]:
                                etat = NOT_EVIDENCED
                            else:
                                etat = ALIGNED
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

    # LA PREUVE DE CONTENU L'EMPORTE SUR LA FORME DE LA SUITE. La regle
    # structurelle existe parce qu'aucune preuve de contenu n'etait
    # disponible : une suite periodique trahissait alors un compteur. Quand
    # chaque attribution du chapitre est corroboree par sa signature, la
    # periodicite s'explique autrement -- un chapitre equilibre, ou chaque
    # capacite recoit le meme nombre d'exercices, produit naturellement une
    # suite periodique. On publie donc les deux : le motif observe, et le
    # soupcon qui subsiste apres corroboration.
    par_chapitre: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for objet in objets:
        par_chapitre[objet["chapter"]][objet["state"]] += 1
    for chapitre, info in chapitres.items():
        compte = par_chapitre.get(chapitre, collections.Counter())
        corrobore = (
            compte.get(ALIGNED, 0) > 0
            and compte.get(MISALIGNED, 0) == 0
            and compte.get(NOT_EVIDENCED, 0) == 0
            and compte.get(UNVERIFIED, 0) == 0
        )
        info["content_corroborated"] = corrobore
        info["round_robin_unexplained"] = (
            info["round_robin"]["detected"] and not corrobore
        )

    motifs = [ch for ch, info in chapitres.items() if info["round_robin"]["detected"]]
    rotations = [ch for ch, info in chapitres.items() if info["round_robin_unexplained"]]
    summary = {etat: par_etat.get(etat, 0) for etat in STATES}
    # LES REVUES SEMANTIQUES SONT PUBLIEES AVEC LEUR VERDICT. Une attribution
    # que la signature n'attestait pas a ete LUE : le registre porte ce qu'on
    # a lu, pourquoi la signature ne le voyait pas, et ce qu'on en a fait.
    revues = evidence_reviews.by_object()
    sans_preuve = par_etat.get(NOT_EVIDENCED, 0)
    # QUATRE CLASSES DE PREUVE, DISJOINTES, DONT L'UNION EST LE TOTAL.
    #
    # `PROVEN_BY_STRUCTURE` ne prouve PAS que le contenu sert la capacite : il
    # prouve que le code declare existe au contrat du chapitre et s'y resout
    # sans ambiguite. C'est une preuve d'IDENTITE, pas d'adequation. La
    # confondre avec une preuve de contenu serait exactement le raccourci qui
    # a laisse passer neuf cents exercices d'analyse sous des capacites
    # d'arithmetique : eux aussi declaraient des codes valides.
    #
    # `PROVEN_BY_SEMANTIC_REVIEW` est la preuve de contenu : la signature
    # declaree pour cette capacite est satisfaite par le corps de l'objet.
    #
    # `UNPROVEN_BY_CONTENT` compte donc ce qui n'a QUE la preuve structurelle.
    # Il ne tombera a zero que par l'ecriture des signatures manquantes,
    # jamais par un changement de nom.
    structurel = len(objets) - par_etat.get(ALIGNED, 0)
    summary.update({
        "CAPACITY_ASSIGNMENTS_TOTAL": len(objets),
        "PROVEN_BY_SEMANTIC_REVIEW": par_etat.get(ALIGNED, 0),
        "PROVEN_BY_STRUCTURE_ONLY": structurel,
        "UNPROVEN_BY_CONTENT": structurel,
        "PROOF_CLASSES_PARTITION_EXACT": (
            par_etat.get(ALIGNED, 0) + structurel == len(objets)
        ),
        "CAPACITY_ASSIGNMENTS_SEMANTICALLY_PROVEN": par_etat.get(ALIGNED, 0),
        "CAPACITY_ASSIGNMENTS_WITHOUT_EVIDENCE": sans_preuve,
        "SEMANTIC_REVIEWS_RECORDED": len(evidence_reviews.REVIEWS),
        "SEMANTIC_REVIEW_VERDICTS": dict(sorted(
            collections.Counter(r["verdict"] for r in evidence_reviews.REVIEWS).items()
        )),
        "CAPACITY_ASSIGNMENTS_EXAMINED": len(objets),
        "CAPACITY_CONTENT_MISALIGNMENT": par_etat.get(MISALIGNED, 0),
        "ROUND_ROBIN_CAPACITY_ASSIGNMENT": len(rotations),
        "ROUND_ROBIN_PATTERN_CHAPTERS": len(motifs),
        "ROUND_ROBIN_EXPLAINED_BY_CONTENT": len(motifs) - len(rotations),
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
        "semantic_reviews": evidence_reviews.REVIEWS,
        "semantic_review_table": "scripts/capacity_evidence_reviews.py",
        "round_robin_chapters": sorted(rotations),
        "round_robin_pattern_chapters": sorted(motifs),
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
        f"- non attestees par leur signature : `{s[NOT_EVIDENCED]}`",
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
