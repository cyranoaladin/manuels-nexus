#!/usr/bin/env python3
"""Controle de la definition canonique d'une suite geometrique.

Decision humaine du 2026-08-27 : sous la definition canonique

    u_{n+1} = q u_n  pour tout n,

une suite geometrique PEUT comporter un terme nul (q = 0, ou terme initial nul).
Le quotient u_{n+1}/u_n n'est qu'une caracterisation conditionnelle, valable
lorsque les termes sont non nuls ; ce n'est pas la definition generale.

Deux erreurs sont donc recherchees dans le corpus :

ZERO_TERM_MISCONCEPTION
    affirmer qu'une suite geometrique ne peut pas avoir de terme nul ;

QUOTIENT_AS_GENERAL_DEFINITION
    presenter la constance de u_{n+1}/u_n comme LA definition, sans reserve
    sur la non-nullite des termes.

Le controle peut lire l'arbre de travail ou n'importe quel commit (--sha).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATH_CHAPTERS = "Mathematiques/manuel-maths/chapitres"

#: « une suite geometrique ne peut pas avoir de terme nul » et variantes.
ZERO_TERM_RE = re.compile(
    r"suite\s+g[ée]om[ée]trique[^.\n]{0,80}?"
    r"(?:ne\s+peut\s+pas\s+(?:avoir|comporter)|n'a\s+jamais|ne\s+comporte\s+jamais)"
    r"[^.\n]{0,40}?terme\s+nul",
    re.IGNORECASE,
)
#: « c'est la definition » / « definition : ... quotient ... constant ».
QUOTIENT_DEFINITION_RE = re.compile(
    r"(?:c'est\s+la\s+d[ée]finition[^.\n]{0,80}?g[ée]om[ée]trique"
    r"|d[ée]finition\s*:[^.\n]{0,120}?quotient[^.\n]{0,60}?constant"
    r"|est\s+g[ée]om[ée]trique\s+si\s+(?:et\s+seulement\s+si\s+)?le\s+quotient)",
    re.IGNORECASE,
)
#: Une reserve explicite desamorce le second motif.
SAFEGUARD_RE = re.compile(
    r"caract[ée]risation|non\s+nuls?|non\s+nulle|strictement\s+positifs?"
    r"|pas\s+la\s+d[ée]finition\s+g[ée]n[ée]rale|d[ée]finition\s+s[ûu]re",
    re.IGNORECASE,
)


@dataclass
class Finding:
    defect_class: str
    chapter_id: str
    path: str
    line: int
    excerpt: str


def _tracked(sha: str | None, prefix: str) -> list[str]:
    if sha:
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", sha, "--", prefix],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    else:
        listing = subprocess.run(
            ["git", "ls-files", "--", prefix],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    return [line for line in listing.splitlines() if line.endswith((".tex", ".json"))]


def _content(sha: str | None, path: str) -> str:
    if sha:
        return subprocess.run(
            ["git", "show", f"{sha}:{path}"], cwd=ROOT, capture_output=True, text=True
        ).stdout
    return (ROOT / path).read_text(encoding="utf-8")


def scan(sha: str | None = None, chapter: str | None = None) -> list[Finding]:
    prefix = f"{MATH_CHAPTERS}/{chapter}" if chapter else MATH_CHAPTERS
    findings: list[Finding] = []
    for path in _tracked(sha, prefix):
        text = _content(sha, path)
        chapter_id = path.split("/chapitres/", 1)[1].split("/", 1)[0]
        for number, line in enumerate(text.splitlines(), start=1):
            if ZERO_TERM_RE.search(line):
                findings.append(
                    Finding("ZERO_TERM_MISCONCEPTION", chapter_id, path, number, line.strip()[:220])
                )
            if QUOTIENT_DEFINITION_RE.search(line) and not SAFEGUARD_RE.search(line):
                findings.append(
                    Finding(
                        "QUOTIENT_AS_GENERAL_DEFINITION",
                        chapter_id, path, number, line.strip()[:220],
                    )
                )
    return findings


def build_report(sha: str | None, chapter: str | None) -> dict:
    findings = scan(sha, chapter)
    counts = {
        "ZERO_TERM_MISCONCEPTION": sum(
            1 for item in findings if item.defect_class == "ZERO_TERM_MISCONCEPTION"
        ),
        "QUOTIENT_AS_GENERAL_DEFINITION": sum(
            1 for item in findings if item.defect_class == "QUOTIENT_AS_GENERAL_DEFINITION"
        ),
    }
    return {
        "artifact_type": "geometric_sequence_definition_audit",
        "schema_version": 1,
        "generated_by": "scripts/audit_geometric_sequence_definition.py",
        "canonical_definition": "u_{n+1} = q u_n pour tout n",
        "zero_term_is_possible": True,
        "quotient_is_a_conditional_characterisation": True,
        "source_sha": sha or "WORKING_TREE",
        "scope_chapter": chapter or "ALL_MATH_CHAPTERS",
        "counts": counts,
        "findings": [asdict(item) for item in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", help="commit a inspecter (defaut : arbre de travail)")
    parser.add_argument("--chapter", help="limiter a un chapitre")
    parser.add_argument("--out", help="ecrire le rapport JSON")
    args = parser.parse_args(argv)

    report = build_report(args.sha, args.chapter)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"{args.sha or 'WORKING_TREE'} : {report['counts']}")
    else:
        sys.stdout.write(payload)
    return 1 if any(report["counts"].values()) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
