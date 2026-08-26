#!/usr/bin/env python3
"""Registre des avertissements de dependances et de l'etat d'epinglage.

Objectif contractuel : avant FINAL_SOURCE_SHA, les dependances Python doivent
etre bornees et reproductibles. Ce registre etablit, sans rien modifier :

* pour chaque dependance epinglee, l'ecart entre la version epinglee et la
  version reellement installee dans l'environnement courant ;
* pour chaque declaration non bornee, la portee du risque ;
* pour chaque avertissement observe pendant la suite de tests, son proprietaire
  (amont ou projet), son impact et sa resolution.

Les avertissements ne sont jamais devines : ils sont lus dans une capture reelle
de sortie pytest passee en entree (--pytest-output).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_REQUIREMENTS = ROOT / "requirements-ci-audit.txt"
UNBOUNDED_REQUIREMENTS = (ROOT / "NSI" / "requirements.txt",)
WORKFLOWS = ROOT / ".github" / "workflows"

#: `<frozen importlib._bootstrap>:488: DeprecationWarning: ...` doit etre lu
#: aussi bien qu'un chemin de fichier ordinaire.
WARNING_LINE_RE = re.compile(
    r"^\s*(?P<location><[^>]+>|[^\s:]+):(?P<line>\d+):?\s*"
    r"(?P<category>\w*Warning):\s*(?P<message>.+)$"
)
SUMMARY_RE = re.compile(r"(?P<count>\d+) warnings?", re.IGNORECASE)

#: Proprietaire d'un avertissement : le projet ne peut corriger que les siens.
PROJECT_PREFIXES = ("scripts/", "tests/", "Mathematiques/", "NSI/", "audit/")


def pinned_requirements() -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in PINNED_REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        name, separator, version = stripped.partition("==")
        if separator:
            pins[name.strip()] = version.strip()
    return pins


def unbounded_requirements() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in UNBOUNDED_REQUIREMENTS:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "==" in stripped:
                continue
            entries.append(
                {
                    "declaration_file": path.relative_to(ROOT).as_posix(),
                    "requirement": stripped,
                    "bound": "lower_only" if ">=" in stripped else "none",
                }
            )
    return entries


def installed_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def pin_drift() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, pinned in sorted(pinned_requirements().items()):
        installed = installed_version(name)
        if installed == pinned:
            state = "MATCH"
        elif installed is None:
            state = "ABSENT"
        else:
            state = "DRIFT"
        rows.append(
            {
                "package": name,
                "pinned": pinned,
                "installed_here": installed,
                "state": state,
            }
        )
    return rows


def workflow_install_policy() -> list[dict[str, object]]:
    policies: list[dict[str, object]] = []
    if not WORKFLOWS.is_dir():
        return policies
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        policies.append(
            {
                "workflow": path.relative_to(ROOT).as_posix(),
                "installs_pinned_requirements": "requirements-ci-audit.txt" in text,
                "uses_no_deps": "--no-deps" in text,
                "runs_pip_check": "pip check" in text,
                "uses_hashes": "--require-hashes" in text,
            }
        )
    return policies


def _owner(location: str) -> str:
    return "project" if location.startswith(PROJECT_PREFIXES) else "upstream"


def parse_pytest_warnings(path: Path) -> list[dict[str, str]]:
    """Lit les avertissements reellement observes dans une capture pytest."""

    warnings: list[dict[str, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    in_summary = False
    for line in text.splitlines():
        if "warnings summary" in line.lower():
            in_summary = True
            continue
        if in_summary and line.startswith("=") and "warnings summary" not in line.lower():
            in_summary = False
        match = WARNING_LINE_RE.match(line)
        if not match:
            continue
        location = match.group("location")
        warnings.append(
            {
                "location": location,
                "line": match.group("line"),
                "category": match.group("category"),
                "message": match.group("message").strip()[:400],
                "owner": _owner(location),
                "phase": "summary" if in_summary else "post_summary",
            }
        )
    unique: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for warning in warnings:
        unique.setdefault(
            (
                warning["location"],
                warning["line"],
                warning["category"],
                warning["message"],
            ),
            warning,
        )
    return list(unique.values())


def build_ledger(pytest_output: Path | None) -> dict:
    drift = pin_drift()
    warnings = parse_pytest_warnings(pytest_output) if pytest_output else []
    return {
        "artifact_type": "dependency_warning_and_pinning_ledger",
        "schema_version": 1,
        "generated_by": "scripts/build_dependency_warning_ledger.py",
        "read_only": True,
        "python_version_here": sys.version.split()[0],
        "pinning": {
            "pinned_requirements_file": PINNED_REQUIREMENTS.relative_to(ROOT).as_posix(),
            "pinned_package_count": len(drift),
            "match_count": sum(1 for row in drift if row["state"] == "MATCH"),
            "drift_count": sum(1 for row in drift if row["state"] == "DRIFT"),
            "absent_count": sum(1 for row in drift if row["state"] == "ABSENT"),
            "packages": drift,
        },
        "unbounded_declarations": unbounded_requirements(),
        "workflow_install_policy": workflow_install_policy(),
        "pytest_warnings": {
            # Le chemin absolu de la capture n'est pas semantique : seul son
            # empreinte prouve de quelle execution proviennent ces lignes.
            "source_capture_sha256": (
                "sha256:"
                + hashlib.sha256(pytest_output.read_bytes()).hexdigest()
                if pytest_output
                else None
            ),
            "source_capture_name": pytest_output.name if pytest_output else None,
            "count": len(warnings),
            "project_owned": sum(1 for w in warnings if w["owner"] == "project"),
            "upstream_owned": sum(1 for w in warnings if w["owner"] == "upstream"),
            "warnings": warnings,
        },
        "final_reproducibility_requirements": [
            "un fichier de contraintes reproductible couvrant l'environnement de test local et la CI",
            "pip check vert dans l'environnement effectivement utilise",
            "la CI et le poste de developpement resolvant le meme ensemble de versions",
            "chaque avertissement soit corrige, soit trace comme dette amont assumee",
        ],
        "closure_planned_before": "FINAL_SOURCE_SHA",
        "changes_nothing_now": (
            "aucune version n'est modifiee pendant la wave de contenu, conformement "
            "a la decision de gouvernance"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pytest-output", help="capture texte d'une execution reelle de pytest"
    )
    parser.add_argument("--out", help="ecrire le registre JSON dans ce fichier")
    args = parser.parse_args(argv)

    ledger = build_ledger(Path(args.pytest_output) if args.pytest_output else None)
    payload = json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        pinning = ledger["pinning"]
        print(
            f"{pinning['pinned_package_count']} epingles, "
            f"{pinning['drift_count']} derives, {pinning['absent_count']} absents, "
            f"{ledger['pytest_warnings']['count']} avertissements"
        )
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
