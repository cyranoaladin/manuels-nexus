#!/usr/bin/env python3
"""Matrice d'execution des tests : quelles commandes sont supportees, et leur resultat.

Le depot expose plusieurs points d'entree pytest qui ne collectent pas le meme
perimetre et ne s'executent pas depuis le meme repertoire. Une commande lancee
depuis la mauvaise racine peut echouer massivement sans qu'aucun test ne soit
faux : les suites NSI resolvent leurs manifestes relativement a NSI/.

Cette matrice nomme chaque commande, son statut de support, et le resultat
observe sur le SHA courant. Les resultats ne sont jamais devines : ils sont lus
dans des captures reelles passees en entree.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SUMMARY_RE = re.compile(
    r"(?:(?P<failed>\d+) failed)?[,\s]*(?P<passed>\d+) passed"
    r"(?:[,\s]*(?P<warnings>\d+) warnings?)?(?:[,\s]*(?P<errors>\d+) errors?)?"
)
EXIT_RE = re.compile(r"^EXIT=(\d+)$", re.MULTILINE)


def parse_capture(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    tail = text[-4000:]
    result: dict[str, Any] = {
        "capture": path.name,
        "capture_sha256": "sha256:"
        + __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "warnings": 0,
    }
    for match in SUMMARY_RE.finditer(tail):
        if match.group("passed"):
            result["passed"] = int(match.group("passed"))
            result["failed"] = int(match.group("failed") or 0)
            result["warnings"] = int(match.group("warnings") or 0)
            result["errors"] = int(match.group("errors") or 0)
    errors = re.search(r"(\d+) errors? in ", tail)
    if errors:
        result["errors"] = int(errors.group(1))
    exit_code = EXIT_RE.search(text)
    if exit_code:
        result["exit_code"] = int(exit_code.group(1))
    result["failed_tests"] = sorted(
        {line.split(" ", 1)[1].strip() for line in text.splitlines() if line.startswith("FAILED ")}
    )
    return result


def _timings(directory: Path) -> dict[str, dict[str, Any]]:
    """Horodatage et code de sortie reels, non masques par une pipeline."""

    path = directory / "results.tsv"
    if not path.is_file():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) == 5:
            rows[parts[0]] = {
                "cwd_absolute": parts[1],
                "start": parts[2],
                "end": parts[3],
                "exit_code": int(parts[4]),
            }
    return rows


def build_report(captures: dict[str, Path], directory: Path) -> dict[str, Any]:
    timings = _timings(directory)
    commands = [
        {
            "id": "nsi_canonical",
            "command": "python -m pytest tests/ -q",
            "cwd": "NSI",
            "scope": "suites NSI",
            "declared_in": [".github/workflows/ci-nsi.yml", "NSI/Makefile"],
            "support_status": "SUPPORTED_CI",
            "capture": "nsi_canonical.log",
        },
        {
            "id": "maths_ci",
            "command": "python -m pytest tests/test_meta_schemas.py -q",
            "cwd": "Mathematiques/manuel-maths",
            "scope": "schemas META du manuel de mathematiques",
            "declared_in": [".github/workflows/ci-mathematiques.yml"],
            "support_status": "SUPPORTED_CI",
            "capture": "maths_ci.log",
        },
        {
            "id": "maths_full",
            "command": "python -m pytest tests/ -q",
            "cwd": "Mathematiques/manuel-maths",
            "scope": "suites du manuel de mathematiques",
            "declared_in": ["Mathematiques/manuel-maths/Makefile"],
            "support_status": "SUPPORTED_CANONICAL",
            "capture": "maths_full.log",
        },
        {
            "id": "root_audit_tests",
            "command": "python -m pytest tests/ -q",
            "cwd": ".",
            "scope": "suites d'audit de la racine",
            "declared_in": ["usage courant"],
            "support_status": "SUPPORTED_CANONICAL",
            "capture": "root_audit_tests.log",
        },
        {
            "id": "root_umbrella",
            "command": "python -m pytest --import-mode=importlib --cov=scripts",
            "cwd": ".",
            "scope": "les trois testpaths de pyproject.toml",
            "declared_in": [".github/workflows/ci-audit-collection.yml", "pyproject.toml"],
            "support_status": "SUPPORTED_CI",
            "capture": "root_umbrella.log",
        },
    ]
    rows = []
    for entry in commands:
        path = captures.get(entry["capture"])
        observed = parse_capture(path) if path and path.is_file() else None
        if observed is not None:
            observed.update(timings.get(entry["id"], {}))
            observed["timeout"] = observed.get("exit_code") == 124
        row = {**entry, "observed": observed}
        if observed is not None:
            row["green"] = observed["failed"] == 0 and observed["errors"] == 0
        else:
            row["green"] = None
        rows.append(row)

    supported = [row for row in rows if row["support_status"].startswith("SUPPORTED")]
    return {
        "artifact_type": "test_execution_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_test_execution_matrix.py",
        "source_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip(),
        "results_are_read_from_real_captures": True,
        "commands": rows,
        "supported_command_count": len(supported),
        "supported_commands_green": sum(1 for row in supported if row["green"]),
        "ambiguous_entrypoints": [],
        "final_requirement": "toute commande supportee ou CI : failed = 0 et errors = 0",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", required=True, help="repertoire des captures")
    parser.add_argument("--out", help="ecrire le rapport JSON")
    args = parser.parse_args(argv)

    directory = Path(args.captures)
    captures = {path.name: path for path in directory.glob("*.log")}
    report = build_report(captures, directory)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(
            f"{report['supported_commands_green']}/{report['supported_command_count']} "
            "commandes supportees vertes"
        )
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
