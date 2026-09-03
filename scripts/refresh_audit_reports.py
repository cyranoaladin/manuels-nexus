#!/usr/bin/env python3
"""Ajoute la traçabilité aux artefacts d'audit, sans toucher à ce qui ne lui appartient pas.

Ce script ajoutait aussi `schema_version = "2.0.0"` — une CHAÎNE — à
`audit/BUILD_MANIFEST.json` et `audit/CHAPTER_READINESS.json`, dont les schémas
déclarent un ENTIER (2 et 1). `scripts/inventory_collection.py` refusait alors
de lire ses propres entrées, et deux chantiers s'arrêtaient. Le champ
`schema_version` appartient au producteur de chaque artefact ; ce script ne le
touche plus, ni aucun autre champ métier.

Il n'avait par ailleurs aucun analyseur d'arguments : `--help` l'EXÉCUTAIT, et
réécrivait donc les deux fichiers au moment même où l'on cherchait à savoir ce
qu'il faisait. Il en a désormais un, et un `--check` qui ne touche à rien.

Ce qu'il ajoute, et rien d'autre : `git_sha`, `generated_at`, `generator`.
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TARGETS = (
    "audit/CHAPTER_READINESS.json",
    "audit/BUILD_MANIFEST.json",
)

# La traçabilité que ce script ajoute. Tout le reste appartient au producteur
# de l'artefact, `schema_version` en premier lieu.
TRACEABILITY_FIELDS = ("git_sha", "generated_at", "generator")
NEVER_TOUCH = ("schema_version", "artifact_type", "generated_by")


class RefreshError(RuntimeError):
    """Une garantie manque : mieux vaut ne rien écrire."""


def git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RefreshError(f"git rev-parse a échoué : {result.stderr.strip()}")
    return result.stdout.strip()


def refresh(path: Path, sha: str, moment: str, *, write: bool) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact": str(path.relative_to(ROOT)), "state": "ABSENT"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RefreshError(f"{path} illisible : {error}") from error
    if not isinstance(payload, dict):
        return {"artifact": str(path.relative_to(ROOT)), "state": "NOT_AN_OBJECT"}

    before = {name: payload.get(name) for name in NEVER_TOUCH}
    payload["git_sha"] = sha
    payload["generated_at"] = moment
    payload["generator"] = "scripts/refresh_audit_reports.py"
    after = {name: payload.get(name) for name in NEVER_TOUCH}
    if before != after:  # pragma: no cover - garde-fou, jamais atteint
        raise RefreshError(f"{path} : un champ du producteur allait être écrasé")

    if write:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return {
        "artifact": str(path.relative_to(ROOT)),
        "state": "WRITTEN" if write else "WOULD_WRITE",
        "schema_version_left_untouched": payload.get("schema_version"),
        "fields_added": list(TRACEABILITY_FIELDS),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="dire ce qui serait écrit, sans rien écrire",
    )
    arguments = parser.parse_args(argv)

    try:
        sha = git_sha()
        moment = datetime.datetime.now(datetime.timezone.utc).isoformat()
        rows = [
            refresh(ROOT / target, sha, moment, write=not arguments.check)
            for target in TARGETS
        ]
    except RefreshError as error:
        print(f"REFRESH-AUDIT-REPORTS-ERROR: {error}", file=sys.stderr)
        return 2

    for row in rows:
        print(
            f"{row['artifact']} : {row['state']}"
            + (
                f" (schema_version={row['schema_version_left_untouched']} inchangé)"
                if "schema_version_left_untouched" in row
                else ""
            )
        )
    print(f"HEAD {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
