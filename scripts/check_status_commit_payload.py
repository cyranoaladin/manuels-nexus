#!/usr/bin/env python3
"""Garde : un commit `[STATUS]` ne transporte aucune charge pédagogique.

Le bloc `\\remarque{}` ajouté à `TNSI-PROJET-ANNUEL.tex` est arrivé dans le
commit `[STATUS] apply digest-bound publication maturity transitions`. Un
commit de statut n'a le droit de toucher qu'à la ligne `% META:` ; toute autre
ligne modifiée dans un objet canonique est une mutation pédagogique
clandestine.

Sortie non nulle == `STATUS_ONLY_COMMIT_PEDAGOGICAL_PAYLOAD_CHANGE = FAIL`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_PREFIXES = ("[STATUS]", "[MATURITY]")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def body_of(rev: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True
    )
    if result.returncode != 0:
        return None
    lines = result.stdout.decode("utf-8", "replace").splitlines()
    if lines and lines[0].startswith("% META:"):
        return "\n".join(lines[1:])
    return "\n".join(lines)


def offending_objects(commit: str) -> list[str]:
    """Objets dont le corps change dans un commit de statut."""
    parent = _git("rev-parse", f"{commit}^").strip()
    changed = _git("diff", "--name-only", parent, commit).split()
    offenders = []
    for path in changed:
        if not path.endswith(".tex"):
            continue
        before = body_of(parent, path)
        after = body_of(commit, path)
        if before is None or after is None:
            continue
        if before != after:
            offenders.append(path)
    return offenders


def scan(revision_range: str) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    log = _git("log", "--format=%H%x00%s", revision_range).strip()
    if not log:
        return findings
    for line in log.splitlines():
        commit, subject = line.split("\x00", 1)
        if not subject.startswith(STATUS_PREFIXES):
            continue
        offenders = offending_objects(commit)
        if offenders:
            findings[f"{commit[:12]} {subject}"] = offenders
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "revision_range",
        nargs="?",
        default="origin/main..HEAD",
        help="plage de révisions à inspecter (défaut : origin/main..HEAD)",
    )
    args = parser.parse_args()

    findings = scan(args.revision_range)
    if not findings:
        print("STATUS_ONLY_COMMIT_PEDAGOGICAL_PAYLOAD_CHANGE = PASS")
        return 0

    print("STATUS_ONLY_COMMIT_PEDAGOGICAL_PAYLOAD_CHANGE = FAIL")
    for commit, paths in findings.items():
        print(f"  {commit}")
        for path in paths:
            print(f"    corps modifié : {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
