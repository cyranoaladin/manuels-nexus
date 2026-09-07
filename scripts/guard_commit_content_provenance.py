#!/usr/bin/env python3
"""Un commit doit dire ce qu'il touche, et le diff a le dernier mot.

`533d1919` s'annoncait « [LATEX] update mode_emploi.tex to v6 charte and
11-step Nexus loop ». Il a cree deux mille six cent soixante-dix-sept copies
d'objets pedagogiques dans quinze chapitres qu'il ne nomme pas. Aucune revue
lisant le message n'avait de raison d'ouvrir ce diff.

Ce garde ne juge JAMAIS sur le message. Le message fournit seulement le
PERIMETRE DECLARE : les chapitres qu'il nomme. Le verdict vient du diff.

Deux findings, tous deux binaires -- aucun seuil, donc rien a assouplir :

`MASS_CONTENT_MUTATION`
    le commit modifie le payload pedagogique de chapitres que son message ne
    nomme pas. Dire ce qu'on touche est le minimum ; un commit de chapitre le
    fait naturellement.

`CROSS_MANUAL_CLONE_CONTAMINATION`
    le commit cree un objet dont le corps normalise existe deja dans un AUTRE
    chapitre. C'est la contamination elle-meme, prise a la source.

Un commit d'infrastructure qui doit legitimement toucher au contenu le
declare par une ligne `EXPLICIT_CONTENT_CHANGE_PROVENANCE:` dans son message,
qui nomme la raison. Le garde l'accepte alors, et la trace reste.
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
PEDAGOGICAL = re.compile(r"(^|/)chapitres/([^/]+)/[^/]+/.*\.tex$")
PROVENANCE_TRAILER = "EXPLICIT_CONTENT_CHANGE_PROVENANCE:"
MIN_BODY_CHARS = 80

MASS = "MASS_CONTENT_MUTATION"
CONTAMINATION = "CROSS_MANUAL_CLONE_CONTAMINATION"

_LEDGER = None


def identity_rule():
    global _LEDGER
    if _LEDGER is None:
        spec = importlib.util.spec_from_file_location(
            "guard_identity", ROOT / "scripts/build_p0_content_clone_ledger.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["guard_identity"] = module
        spec.loader.exec_module(module)
        _LEDGER = module
    return _LEDGER


def _git(args: list[str], root: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout


def chapter_of(path: str) -> str | None:
    found = PEDAGOGICAL.search(path)
    return found.group(2) if found else None


def declared_scope(message: str) -> set[str]:
    """Les chapitres que le message NOMME, et rien d'autre.

    Un identifiant de chapitre est reconnu tel qu'il apparait dans les
    chemins : `TCOMPL-INFERENCE-BAYESIENNE`, `1SPE-TRIGONOMETRIE`. Le message
    ne sert qu'a cela : il ne peut jamais innocenter un diff.
    """

    return set(re.findall(r"\b(?:1|T)(?:SPE|NSI|COMPL|EXP)[A-Z0-9-]*\b", message))


def has_explicit_provenance(message: str) -> bool:
    for line in message.splitlines():
        if line.strip().startswith(PROVENANCE_TRAILER):
            return bool(line.split(PROVENANCE_TRAILER, 1)[1].strip())
    return False


def inspect(root: Path, commit: str) -> dict[str, Any]:
    ledger = identity_rule()
    normalise = ledger.pedagogical_body
    message = _git(["log", "-1", "--format=%B", commit], root)
    nomme = declared_scope(message)

    touches: list[tuple[str, str]] = []
    for line in _git(["diff", "--name-status", f"{commit}^", commit], root).splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        if PEDAGOGICAL.search(parts[-1]):
            touches.append((parts[0], parts[-1]))

    # Corps normalises presents AVANT le commit, par chapitre.
    corps_avant: dict[str, list[str]] = collections.defaultdict(list)
    for line in _git(
        ["ls-tree", "-r", f"{commit}^", "--", "NSI", "Mathematiques"], root
    ).splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) < 4 or parts[1] != "blob":
            continue
        chemin = parts[3].strip()
        if not PEDAGOGICAL.search(chemin):
            continue
        contenu = _git(["cat-file", "-p", parts[2]], root)
        corps = normalise(contenu)
        if len(corps) >= MIN_BODY_CHARS:
            corps_avant[ledger.digest(corps)].append(chemin)

    payload_mutes: set[str] = set()
    contaminations: list[dict[str, str]] = []
    for code, chemin in touches:
        chapitre = chapter_of(chemin)
        if not chapitre:
            continue
        apres = "" if code.startswith("D") else _git(["show", f"{commit}:{chemin}"], root)
        avant = "" if code.startswith("A") else _git(["show", f"{commit}^:{chemin}"], root)
        corps_apres, corps_ancien = normalise(apres), normalise(avant)
        if corps_apres == corps_ancien:
            continue  # identite ou metadonnee seule : pas une mutation de payload
        payload_mutes.add(chapitre)
        if not code.startswith("A") or len(corps_apres) < MIN_BODY_CHARS:
            continue
        sources = corps_avant.get(ledger.digest(corps_apres), [])
        etrangeres = [s for s in sources if chapter_of(s) != chapitre]
        if etrangeres:
            contaminations.append({
                "path": chemin,
                "chapter": chapitre,
                "copied_from": sorted(etrangeres)[0],
                "source_chapter": chapter_of(sorted(etrangeres)[0]) or "",
            })

    non_declares = sorted(payload_mutes - nomme)
    findings: list[dict[str, Any]] = []
    if non_declares and not has_explicit_provenance(message):
        findings.append({
            "code": MASS,
            "blocking": True,
            "detail": (
                f"{len(non_declares)} chapitre(s) voient leur payload "
                "pedagogique modifie sans etre nommes par le message"
            ),
            "chapters": non_declares,
        })
    if contaminations:
        findings.append({
            "code": CONTAMINATION,
            "blocking": True,
            "detail": (
                f"{len(contaminations)} objet(s) crees en recopiant le corps "
                "d'un objet d'un AUTRE chapitre"
            ),
            "objects": contaminations[:50],
            "object_count": len(contaminations),
        })

    return {
        "commit": commit,
        "declared_scope": sorted(nomme),
        "pedagogical_objects_touched": len(touches),
        "chapters_with_payload_mutation": sorted(payload_mutes),
        "chapters_mutated_but_not_declared": non_declares,
        "explicit_content_change_provenance": has_explicit_provenance(message),
        "findings": findings,
        "verdict": "REFUSED" if findings else "ACCEPTED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("commit", nargs="?", default="HEAD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    rapport = inspect(ROOT, args.commit)
    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{rapport['commit'][:12]} : {rapport['verdict']}")
        for finding in rapport["findings"]:
            print(f"  - {finding['code']} : {finding['detail']}")
    return 0 if rapport["verdict"] == "ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
