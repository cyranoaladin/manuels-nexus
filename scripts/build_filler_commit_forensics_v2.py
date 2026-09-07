#!/usr/bin/env python3
"""Forensique du commit `533d1919`, rejouee avec la normalisation corrigee.

La conclusion precedente -- « 1196 objets de contenu inedit » -- etait fausse
pour la population contaminee, et pour une raison mecanique : le corps
compare portait encore l'identifiant de l'objet, si bien que quatorze copies
rigoureusement identiques passaient pour quatorze creations originales. Elle
comparait de plus les corps crees UNIQUEMENT a ceux qui existaient avant le
commit : une banque recopiee quinze fois a l'interieur du meme commit ne
pouvait pas etre reconnue.

Ce producteur reprend l'analyse complete et SUPERSEDE formellement l'ancien
rapport, qui reste dans l'historique.

SIX CLASSES, ET AUCUN INCONNU :

`PREEXISTING_AUTHENTIC_CONTENT`  l'objet portait deja un contenu substantiel
                                avant le commit, et en porte encore apres.
`FILLER_COPY`                   le corps est la copie d'un autre corps, soit
                                anterieur au commit, soit cree par lui.
`GENUINE_NEW_AUTHORING`         cree par le commit, corps unique, aucune
                                copie ni avant ni pendant.
`FORMAT_ONLY`                   meme texte lu par l'eleve, habillage different.
`METADATA_ONLY`                 seule l'identite declaree change.
`UNKNOWN`                       interdit : la classification doit etre totale.

UN ORIGINAL SE PROUVE. Quand un corps apparait N fois parmi les fichiers
crees par ce commit et nulle part avant, rien ne designe lequel des N serait
l'original : aucun ne peut donc revendiquer `GENUINE_NEW_AUTHORING`. Les N
sont des copies, et le groupe est publie comme
`WITHIN_COMMIT_GROUP_WITHOUT_ESTABLISHED_ORIGINAL`.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_TARGET = ROOT / "audit/FILLER_COMMIT_FORENSICS_V2.json"
MD_TARGET = ROOT / "audit/FILLER_COMMIT_FORENSICS_V2.md"
GENERATED_BY = "scripts/build_filler_commit_forensics_v2.py"
SUPERSEDES = "audit/FILLER_COMMIT_FORENSICS.json"

FILLER_COMMIT = "533d19198eb7810699a41a7b5275744691420859"
PEDAGOGICAL = re.compile(r"(^|/)chapitres/[^/]+/[^/]+/.*\.tex$")
MIN_BODY_CHARS = 80

MACRO = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?")
BRACES = re.compile(r"[{}]")
WS = re.compile(r"\s+")

PREEXISTING = "PREEXISTING_AUTHENTIC_CONTENT"
COPY = "FILLER_COPY"
NEW = "GENUINE_NEW_AUTHORING"
FORMAT = "FORMAT_ONLY"
METADATA = "METADATA_ONLY"
UNKNOWN = "UNKNOWN"
CLASSES = (PREEXISTING, COPY, NEW, FORMAT, METADATA, UNKNOWN)

_LEDGER = None


def identity_rule():
    global _LEDGER
    if _LEDGER is None:
        spec = importlib.util.spec_from_file_location(
            "filler_identity", ROOT / "scripts/build_p0_content_clone_ledger.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["filler_identity"] = module
        spec.loader.exec_module(module)
        _LEDGER = module
    return _LEDGER


def _git(args: list[str], root: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _payload(text: str) -> str:
    """Le texte que l'eleve lit, debarrasse de l'habillage de charte."""

    stripped = "\n".join(
        line for line in text.splitlines()[1:] if not line.lstrip().startswith("%")
    )
    stripped = MACRO.sub(" ", stripped)
    stripped = BRACES.sub(" ", stripped)
    return WS.sub(" ", stripped).strip()


def _blobs(root: Path, revision: str) -> dict[str, str]:
    """Chemin -> contenu, pour tous les objets pedagogiques d'une revision.

    Une seule invocation de `git cat-file --batch` : lire quatre mille blobs
    un par un prenait des minutes.
    """

    entrees: list[tuple[str, str]] = []
    for line in _git(
        ["ls-tree", "-r", revision, "--", "NSI", "Mathematiques"], root
    ).splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) < 4 or parts[1] != "blob":
            continue
        chemin = parts[3].strip()
        if PEDAGOGICAL.search(chemin):
            entrees.append((chemin, parts[2]))
    if not entrees:
        return {}
    # `git cat-file --batch` annonce une taille en OCTETS : lire son flux en
    # texte decale le curseur des le premier accent, et l'entete suivante est
    # alors lue au milieu d'un JSON. On reste donc en octets, et on decode
    # blob par blob.
    completed = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=root,
        input=("\n".join(sha for _, sha in entrees) + "\n").encode("utf-8"),
        capture_output=True,
        check=False,
    )
    contenus: dict[str, str] = {}
    flux = completed.stdout
    position = 0
    for chemin, _sha in entrees:
        fin_entete = flux.find(b"\n", position)
        if fin_entete < 0:
            break
        entete = flux[position:fin_entete].split()
        if len(entete) < 3:
            position = fin_entete + 1
            continue
        taille = int(entete[2])
        debut = fin_entete + 1
        contenus[chemin] = flux[debut : debut + taille].decode("utf-8", "replace")
        position = debut + taille + 1
    return contenus


def build(root: Path = ROOT) -> dict[str, Any]:
    ledger = identity_rule()
    normalise = ledger.pedagogical_body

    avant = _blobs(root, f"{FILLER_COMMIT}^")
    apres = _blobs(root, FILLER_COMMIT)

    # Index des corps ANTERIEURS au commit : une creation qui les reproduit
    # est une copie, et on sait de quoi.
    corps_avant: dict[str, str] = {}
    for chemin, contenu in sorted(avant.items()):
        corps = normalise(contenu)
        if len(corps) >= MIN_BODY_CHARS:
            corps_avant.setdefault(_digest(corps), chemin)

    status = _git(
        ["diff", "--name-status", f"{FILLER_COMMIT}^", FILLER_COMMIT], root
    )
    touches: list[tuple[str, str]] = []
    for line in status.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        code, chemin = parts[0], parts[-1]
        if PEDAGOGICAL.search(chemin):
            touches.append((code, chemin))

    # Corps CREES par ce commit, groupes : un corps cree N fois n'a pas
    # d'original demontrable parmi les N.
    crees: dict[str, list[str]] = collections.defaultdict(list)
    for code, chemin in touches:
        if not code.startswith("A"):
            continue
        corps = normalise(apres.get(chemin, ""))
        if len(corps) >= MIN_BODY_CHARS:
            crees[_digest(corps)].append(chemin)

    records: list[dict[str, Any]] = []
    for code, chemin in sorted(touches):
        contenu_apres = apres.get(chemin, "")
        contenu_avant = "" if code.startswith("A") else avant.get(chemin, "")
        corps_apres = normalise(contenu_apres)
        corps_ancien = normalise(contenu_avant) if contenu_avant else ""
        empreinte = _digest(corps_apres)

        if code.startswith("D"):
            verdict, pourquoi = PREEXISTING, "objet supprime par le commit"
        elif code.startswith("A"):
            if len(corps_apres) < MIN_BODY_CHARS:
                verdict, pourquoi = FORMAT, "objet cree vide ou quasi vide"
            elif empreinte in corps_avant:
                verdict = COPY
                pourquoi = f"copie de {corps_avant[empreinte]}, anterieur au commit"
            elif len(crees[empreinte]) > 1:
                verdict = COPY
                pourquoi = (
                    f"corps cree {len(crees[empreinte])} fois par ce commit : "
                    "aucun des exemplaires n'est demontrablement l'original"
                )
            else:
                verdict, pourquoi = NEW, "objet cree, corps unique avant et pendant"
        elif corps_ancien == corps_apres:
            verdict, pourquoi = METADATA, "seule l'identite declaree change"
        elif _payload(contenu_avant) == _payload(contenu_apres):
            verdict, pourquoi = FORMAT, "meme texte lu par l'eleve, charte differente"
        elif empreinte in corps_avant and corps_avant[empreinte] != chemin:
            verdict = COPY
            pourquoi = (
                f"corps remplace par une copie de {corps_avant[empreinte]}"
            )
        elif len(corps_ancien) >= MIN_BODY_CHARS:
            verdict = PREEXISTING
            pourquoi = "objet deja substantiel avant le commit, et modifie"
        else:
            verdict, pourquoi = NEW, "objet quasi vide avant, contenu ajoute"

        records.append({
            "path": chemin,
            "change": code,
            "verdict": verdict,
            "why": pourquoi,
            "body_digest": empreinte,
            "before_chars": len(corps_ancien),
            "after_chars": len(corps_apres),
        })

    return _assemble(records, crees, corps_avant)


def _assemble(
    records: list[dict[str, Any]],
    crees: dict[str, list[str]],
    corps_avant: dict[str, str],
) -> dict[str, Any]:
    par_verdict = collections.Counter(r["verdict"] for r in records)
    sans_original = {
        empreinte: chemins
        for empreinte, chemins in sorted(crees.items())
        if len(chemins) > 1 and empreinte not in corps_avant
    }
    copies_de_source_anterieure = sum(
        1 for r in records if r["verdict"] == COPY and "anterieur au commit" in r["why"]
    )
    summary = {
        classe: par_verdict.get(classe, 0) for classe in CLASSES
    }
    summary.update({
        "PEDAGOGICAL_MUTATIONS": len(records),
        "CLASSES_SUM_EQUALS_TOTAL": sum(par_verdict.values()) == len(records),
        "FILLER_COPIES_OF_A_PREEXISTING_BODY": copies_de_source_anterieure,
        "FILLER_COPIES_CREATED_WITHIN_THE_COMMIT": (
            par_verdict.get(COPY, 0) - copies_de_source_anterieure
        ),
        "WITHIN_COMMIT_GROUPS_WITHOUT_ESTABLISHED_ORIGINAL": len(sans_original),
    })
    return {
        "artifact_type": "filler_commit_forensics_v2",
        "schema_version": 2,
        "generated_by": GENERATED_BY,
        "commit": FILLER_COMMIT,
        "supersedes": SUPERSEDES,
        "supersede_reason": (
            "l'analyse precedente comparait des corps portant encore "
            "l'identifiant de l'objet, et ne confrontait les creations qu'aux "
            "corps ANTERIEURS au commit : une banque recopiee quinze fois a "
            "l'interieur du meme commit passait pour quinze creations "
            "originales"
        ),
        "classes": list(CLASSES),
        "approves_nothing": True,
        "summary": summary,
        "within_commit_groups_without_established_original": [
            {"body_digest": empreinte, "paths": chemins}
            for empreinte, chemins in sorted(sans_original.items())
        ],
        "records": records,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Forensique de `533d1919`, normalisation corrigee",
        "",
        f"Supersede `{payload['supersedes']}`.",
        "",
        payload["supersede_reason"].capitalize() + ".",
        "",
        "## Classification",
        "",
        "| classe | objets |",
        "| --- | --- |",
    ]
    for classe in payload["classes"]:
        lignes.append(f"| `{classe}` | {s[classe]} |")
    lignes += [
        "",
        f"- mutations pedagogiques : `{s['PEDAGOGICAL_MUTATIONS']}`",
        f"- copies d'un corps anterieur : `{s['FILLER_COPIES_OF_A_PREEXISTING_BODY']}`",
        f"- copies creees dans le commit : `{s['FILLER_COPIES_CREATED_WITHIN_THE_COMMIT']}`",
        f"- groupes sans original demontrable : "
        f"`{s['WITHIN_COMMIT_GROUPS_WITHOUT_ESTABLISHED_ORIGINAL']}`",
        "",
    ]
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
        for ecart in ecarts:
            print(f"diff: {ecart}")
        return 1 if ecarts else 0
    for chemin, contenu in rendus.items():
        chemin.write_text(contenu, encoding="utf-8")
        print(f"wrote {chemin.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
