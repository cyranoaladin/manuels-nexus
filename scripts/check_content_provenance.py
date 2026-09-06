#!/usr/bin/env python3
"""Garde contre le remplissage synthetique d'objets pedagogiques.

Le commit `533d1919`, annonce comme une mise a jour de charte LaTeX, a introduit
986 objets pedagogiques en recopiant quelques corps canoniques. Rien ne l'a
arrete : ni son intitule, ni son ampleur, ni le fait que les copies creditaient
des capacites qu'elles ne traitaient pas.

Cette garde inspecte la nature des changements, pas seulement leur nombre. Un
commit d'infrastructure qui ajoute massivement du contenu pedagogique doit
declarer d'ou vient ce contenu.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

#: Prefixes qui n'annoncent pas un apport de contenu pedagogique.
NON_CONTENT_PREFIXES = (
    "[LATEX]", "[CI]", "[DOCS]", "[TESTS]", "[AUDIT]", "[REFACTOR]",
    "[BUILD]", "[STYLE]", "[CHORE]", "[GATE-INTEGRITY]",
)
#: Au-dela, un apport de contenu cesse d'etre une retouche.
MASS_OBJECT_THRESHOLD = 20
CONTENT_PATH = re.compile(r"(^|/)chapitres/[^/]+/(exercices|corriges|cours|methodes|remediation|evaluations|qcm)/")
MIN_BODY_CHARS = 80


def _git(args: list[str], root: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout


def _body(text: str) -> str:
    return "\n".join(line for line in text.splitlines()[1:] if line.strip())


def _digest(text: str) -> str:
    return hashlib.sha256(_body(text).encode()).hexdigest()


def inspect(root: Path, base: str, head: str) -> dict[str, Any]:
    subject = _git(["log", "-1", "--format=%s", head], root).strip()
    status = _git(["diff", "--name-status", base, head], root).splitlines()

    added: list[str] = []
    modified: list[str] = []
    for line in status:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        code, path = parts[0], parts[-1]
        if not CONTENT_PATH.search(path) or not path.endswith(".tex"):
            continue
        if code.startswith("A"):
            added.append(path)
        elif code.startswith("M"):
            modified.append(path)

    # Corps presents AVANT le changement : une nouveaute qui les reproduit est
    # une copie, pas un apport.
    before: dict[str, str] = {}
    for line in _git(["ls-tree", "-r", base, "--", "NSI", "Mathematiques"], root).splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) < 4 or parts[1] != "blob" or not parts[3].strip().endswith(".tex"):
            continue
        path = parts[3].strip()
        if not CONTENT_PATH.search(path):
            continue
        content = _git(["cat-file", "-p", parts[2]], root)
        if len(_body(content)) >= MIN_BODY_CHARS:
            before.setdefault(_digest(content), path)

    duplicated: list[dict[str, Any]] = []
    added_bodies: dict[str, str] = {}
    for path in added:
        content = _git(["show", f"{head}:{path}"], root)
        body = _body(content)
        if len(body) < MIN_BODY_CHARS:
            continue
        digest = _digest(content)
        if digest in before:
            duplicated.append({
                "added": path,
                "duplicates": before[digest],
                "why": "objet ajoute dont le corps existait deja",
            })
        elif digest in added_bodies:
            duplicated.append({
                "added": path,
                "duplicates": added_bodies[digest],
                "why": "deux objets ajoutes dans le meme changement portent le meme corps",
            })
        else:
            added_bodies[digest] = path

    findings: list[dict[str, Any]] = []
    if duplicated:
        findings.append({
            "code": "SYNTHETIC_FILLER_CONTAMINATION",
            "count": len(duplicated),
            "why": "des objets sont ajoutes en recopiant le corps d'objets existants",
        })

    touched = len(added) + len(modified)
    non_content = subject.startswith(NON_CONTENT_PREFIXES)
    if non_content and touched >= MASS_OBJECT_THRESHOLD:
        findings.append({
            "code": "MASS_CONTENT_MUTATION_REQUIRES_EXPLICIT_CONTENT_PROVENANCE",
            "count": touched,
            "subject": subject,
            "why": (
                "un changement annonce comme non-contenu modifie massivement des "
                "objets pedagogiques : la provenance du contenu doit etre declaree"
            ),
        })

    return {
        "artifact_type": "content_provenance_check",
        "base": base,
        "head": head,
        "subject": subject,
        "added_objects": len(added),
        "modified_objects": len(modified),
        "duplicated_objects": duplicated[:200],
        "duplicated_count": len(duplicated),
        "findings": findings,
        "passed": not findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base", default="HEAD^")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = inspect(args.root, args.base, args.head)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{report['base']}..{report['head']} : {report['subject'][:70]}")
        print(f"  objets ajoutes {report['added_objects']}, modifies {report['modified_objects']}")
        print(f"  objets dupliques : {report['duplicated_count']}")
        for finding in report["findings"]:
            print(f"  ROUGE {finding['code']} ({finding['count']})")
        print("  PASS" if report["passed"] else "  FAIL")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
