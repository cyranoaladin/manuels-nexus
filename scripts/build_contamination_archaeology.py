#!/usr/bin/env python3
"""Chercher le contenu authentique AVANT d'en ecrire un nouveau.

Neuf cents objets sont contamines. Ecrire neuf cents remplacements sans avoir
d'abord fouille l'historique reviendrait a jeter du travail authentique qui
dort peut-etre dans un blob. Ce producteur ouvre toutes les versions connues
de chaque objet contamine et dit, pour chacun, ce que l'historique contient.

QUATRE ETATS, ET RIEN D'AUTRE :

`AUTHENTIC_CONTENT_RECOVERED`      une version anterieure au remplissage porte
                                   un corps substantiel different du clone.
`AUTHENTIC_ALTERNATIVE_FOUND_LATER` une version POSTERIEURE porte un tel corps.
`EMPTY_BEFORE_FILLER`              l'objet existait, vide ou quasi vide.
`NO_AUTHENTIC_CONTENT_FOUND`       aucune version n'a jamais porte autre chose.

Le dernier etat est le plus important a dire honnetement : il signifie que ce
fichier n'a JAMAIS contenu de pedagogie, et donc qu'il n'y a rien a restaurer.
Ce n'est pas un slot a remplir -- c'est un objet qui n'aurait pas du naitre.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "audit/CROSS_MANUAL_CONTAMINATION_MATRIX.json"
JSON_TARGET = ROOT / "audit/CONTAMINATION_ARCHAEOLOGY.json"
MD_TARGET = ROOT / "audit/CONTAMINATION_ARCHAEOLOGY.md"
GENERATED_BY = "scripts/build_contamination_archaeology.py"

FILLER_COMMIT = "533d19198eb7810699a41a7b5275744691420859"
MIN_BODY_CHARS = 80
CHAPTER_IN_PATH = re.compile(r"(?:^|/)chapitres/([^/]+)/")


def _chapter_of(path: str) -> str | None:
    found = CHAPTER_IN_PATH.search(path)
    return found.group(1) if found else None

RECOVERED = "AUTHENTIC_CONTENT_RECOVERED"
LATER = "AUTHENTIC_ALTERNATIVE_FOUND_LATER"
EMPTY = "EMPTY_BEFORE_FILLER"
NONE_FOUND = "NO_AUTHENTIC_CONTENT_FOUND"
STATES = (RECOVERED, LATER, EMPTY, NONE_FOUND)

_LEDGER = None


def identity_rule():
    global _LEDGER
    if _LEDGER is None:
        spec = importlib.util.spec_from_file_location(
            "arch_identity", ROOT / "scripts/build_p0_content_clone_ledger.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["arch_identity"] = module
        spec.loader.exec_module(module)
        _LEDGER = module
    return _LEDGER


def _git_text(args: list[str], root: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout


def history_index(root: Path) -> dict[str, list[tuple[str, str]]]:
    """Chemin -> [(commit, blob)], toutes branches, du plus recent au plus ancien."""

    sortie = _git_text(
        [
            "log", "--all", "--raw", "--no-renames", "--format=%x00%H",
            "--", "Mathematiques/manuel-maths/chapitres", "NSI/chapitres",
        ],
        root,
    )
    index: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    commit = ""
    for ligne in sortie.split("\n"):
        if ligne.startswith("\x00"):
            commit = ligne[1:].strip()
            continue
        if not ligne.startswith(":"):
            continue
        # :100644 100644 <avant> <apres> M\tchemin
        entete, _, chemin = ligne.partition("\t")
        champs = entete.split()
        if len(champs) < 5 or not chemin:
            continue
        blob = champs[3]
        if set(blob) == {"0"}:
            continue
        index[chemin.strip()].append((commit, blob))
    return index


def read_blobs(root: Path, blobs: list[str]) -> dict[str, str]:
    """Lire beaucoup de blobs en une passe, en OCTETS.

    `git cat-file --batch` annonce une taille en octets : lire son flux en
    texte decale le curseur des le premier accent.
    """

    uniques = sorted(set(blobs))
    if not uniques:
        return {}
    completed = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=root,
        input=("\n".join(uniques) + "\n").encode("utf-8"),
        capture_output=True,
        check=False,
    )
    contenus: dict[str, str] = {}
    flux = completed.stdout
    position = 0
    for sha in uniques:
        fin = flux.find(b"\n", position)
        if fin < 0:
            break
        entete = flux[position:fin].split()
        if len(entete) < 3:
            position = fin + 1
            continue
        taille = int(entete[2])
        debut = fin + 1
        contenus[sha] = flux[debut : debut + taille].decode("utf-8", "replace")
        position = debut + taille + 1
    return contenus


def build(root: Path = ROOT) -> dict[str, Any]:
    ledger = identity_rule()
    normalise = ledger.pedagogical_body

    matrice = json.loads(MATRIX.read_text(encoding="utf-8"))
    contamines = [r for r in matrice["rows"] if not r["IS_CANONICAL_SOURCE"]]
    index = history_index(root)

    ordre = {
        sha: rang
        for rang, sha in enumerate(
            _git_text(["rev-list", "--all", "--reverse", "--topo-order"], root).split()
        )
    }
    rang_remplissage = ordre.get(FILLER_COMMIT, 1 << 30)

    # UN CORPS QUI A VECU DANS DEUX CHAPITRES N'EST PAS UN CONTENU AUTHENTIQUE
    # A RESTAURER. Sans ce garde, la version deposee par le remplissage
    # lui-meme passerait pour un contenu retrouve. On lit donc TOUT
    # l'historique des chapitres -- trente-six mille blobs, une seule passe --
    # et on retient, pour chaque corps, les chapitres ou il a vecu.
    tous_blobs = [blob for versions in index.values() for _, blob in versions]
    contenus = read_blobs(root, tous_blobs)
    chapitres_par_corps: dict[str, set[str]] = collections.defaultdict(set)
    for chemin, versions in index.items():
        chapitre = _chapter_of(chemin)
        if not chapitre:
            continue
        for _commit, blob in versions:
            corps = normalise(contenus.get(blob, ""))
            if len(corps) >= MIN_BODY_CHARS:
                chapitres_par_corps[ledger.digest(corps)].add(chapitre)

    enregistrements: list[dict[str, Any]] = []
    for row in sorted(contamines, key=lambda r: r["OBJECT_PATH"]):
        chemin = row["OBJECT_PATH"]
        courant = ledger.digest(normalise((root / chemin).read_text(
            encoding="utf-8", errors="replace"
        ))) if (root / chemin).is_file() else None

        versions = []
        for commit, blob in index.get(chemin, []):
            texte = contenus.get(blob, "")
            corps = normalise(texte)
            versions.append({
                "commit": commit,
                "blob": blob,
                "rank": ordre.get(commit, 1 << 30),
                "digest": ledger.digest(corps),
                "chars": len(corps),
                "substantive": len(corps) >= MIN_BODY_CHARS,
            })
        versions.sort(key=lambda v: v["rank"])

        # Authentique = substantiel, different du clone actuel, et n'ayant
        # jamais vecu dans un autre chapitre.
        differentes = [
            v
            for v in versions
            if v["substantive"]
            and v["digest"] != courant
            and chapitres_par_corps.get(v["digest"], set()) <= {row["TARGET_CHAPTER"]}
        ]
        avant = [v for v in differentes if v["rank"] < rang_remplissage]
        apres = [v for v in differentes if v["rank"] > rang_remplissage]

        if avant:
            etat, preuve = RECOVERED, avant[-1]
        elif apres:
            etat, preuve = LATER, apres[-1]
        elif any(v["rank"] < rang_remplissage and not v["substantive"] for v in versions):
            etat, preuve = EMPTY, None
        else:
            etat, preuve = NONE_FOUND, None

        enregistrements.append({
            "object_id": row["OBJECT_ID"],
            "path": chemin,
            "manual": row["TARGET_MANUAL"],
            "chapter": row["TARGET_CHAPTER"],
            "object_type": row["OBJECT_TYPE"],
            "group_id": row["GROUP_ID"],
            "state": etat,
            "known_versions": len(versions),
            "evidence": (
                {
                    "commit": preuve["commit"],
                    "blob": preuve["blob"],
                    "body_chars": preuve["chars"],
                }
                if preuve
                else None
            ),
        })

    par_etat = collections.Counter(r["state"] for r in enregistrements)
    par_chapitre: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for r in enregistrements:
        par_chapitre[r["chapter"]][r["state"]] += 1

    summary = {etat: par_etat.get(etat, 0) for etat in STATES}
    summary.update({
        "OBJECTS_CONTAMINATED_BY_533d1919": len(enregistrements),
        "STATES_SUM_EQUALS_TOTAL": sum(par_etat.values()) == len(enregistrements),
        "APPROVES_NOTHING": True,
    })

    return {
        "artifact_type": "contamination_archaeology",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "filler_commit": FILLER_COMMIT,
        "states": list(STATES),
        "rule": (
            "une version est authentique si son corps normalise est "
            "substantiel et differe du corps clone actuel ; l'historique est "
            "lu sur toutes les branches"
        ),
        "summary": summary,
        "per_chapter": {
            ch: dict(sorted(compte.items())) for ch, compte in sorted(par_chapitre.items())
        },
        "records": enregistrements,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Archeologie de la contamination",
        "",
        payload["rule"].capitalize() + ".",
        "",
        "| etat | objets |",
        "| --- | --- |",
    ]
    for etat in payload["states"]:
        lignes.append(f"| `{etat}` | {s[etat]} |")
    lignes += ["", "## Par chapitre", "", "| chapitre | " + " | ".join(payload["states"]) + " |",
               "| --- |" + " --- |" * len(payload["states"])]
    for chapitre, compte in payload["per_chapter"].items():
        cellules = " | ".join(str(compte.get(e, 0)) for e in payload["states"])
        lignes.append(f"| {chapitre} | {cellules} |")
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
