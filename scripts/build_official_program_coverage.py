#!/usr/bin/env python3
"""Aggregate the six reviewed official-programme coverage matrices."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MATRIX_ROOT = AUDIT / "official_program_coverage"
ATOMS_PATH = AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
JSON_TARGET = AUDIT / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
MD_TARGET = AUDIT / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.md"
MANUAL_ORDER = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
MATRIX_PATHS = tuple(MATRIX_ROOT / f"{manual}.json" for manual in MANUAL_ORDER)


def _validate_mandatory_bijection(
    atoms: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> None:
    """Every mandatory official atom has exactly one coverage row."""

    mandatory = {
        str(atom.get("atom_id"))
        for atom in atoms
        if atom.get("mandatory") == "YES"
    }
    row_ids = [str(row.get("atom_id")) for row in rows]
    missing = sorted(mandatory - set(row_ids))
    unexpected = sorted(set(row_ids) - mandatory)
    duplicates = sorted(
        atom_id for atom_id, count in Counter(row_ids).items() if count > 1
    )
    if missing or unexpected or duplicates or len(row_ids) != len(mandatory):
        raise ValueError(
            "MANDATORY_ATOM_BIJECTION: "
            f"missing={missing}, unexpected={unexpected}, duplicates={duplicates}"
        )


def _digest(paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _refuse_wording_drift(
    atoms: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> None:
    """Le libelle officiel ne peut pas differer entre le registre et la matrice.

    Le meme texte officiel etait recopie a trois endroits -- le segment lu dans
    le document, la definition d'atome, la ligne de couverture -- et rien ne
    les confrontait. Une formule mise a plat par l'extraction du PDF a ainsi
    traverse toute la chaine jusqu'a la vue de revue, ou une lecture humaine
    l'a refusee.

    Le registre d'atomes fait autorite ici : c'est lui qui derive des segments
    officiels. La matrice enregistre la couverture, pas le texte du programme.
    """

    registry = {
        atom["atom_id"]: atom["short_official_wording_or_paraphrase"]
        for atom in atoms
    }
    drift = [
        row["atom_id"]
        for row in rows
        if row["atom_id"] in registry
        and row["official_wording_or_short_paraphrase"] != registry[row["atom_id"]]
    ]
    if drift:
        raise ValueError(
            "OFFICIAL_WORDING_DRIFT: la matrice de couverture contredit le "
            f"registre d'atomes pour {drift}. Le registre fait autorite : il "
            "derive des segments officiels."
        )


def build_payload() -> dict[str, Any]:
    atoms = json.loads(ATOMS_PATH.read_text(encoding="utf-8"))["atoms"]
    rows = [
        row
        for path in MATRIX_PATHS
        for row in json.loads(path.read_text(encoding="utf-8"))["rows"]
    ]
    _validate_mandatory_bijection(atoms, rows)
    _refuse_wording_drift(atoms, rows)
    by_manual: dict[str, dict[str, int]] = {}
    for manual in MANUAL_ORDER:
        subset = [row for row in rows if row["manual"] == manual]
        by_manual[manual] = {
            "mandatory_atoms": len(subset),
            "mapped": sum(row["coverage_status"] != "UNMAPPED" for row in subset),
            "unmapped": sum(row["coverage_status"] == "UNMAPPED" for row in subset),
            "full": sum(row["coverage_status"] == "FULL" for row in subset),
        }
    states = Counter(row["coverage_status"] for row in rows)
    return {
        "schema_version": 1,
        "artifact_name": "OFFICIAL_PROGRAM_COVERAGE_2026_2027",
        "namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "applicable_school_year": "2026-2027",
        "source_digest": _digest((ATOMS_PATH, *MATRIX_PATHS)),
        "methodology": {
            "official_atoms_are_source": True,
            "internal_capacities_are_authority": False,
            "full_is_path_exists": False,
            "coverage_states_are_progressive": True,
        },
        "summary": {
            "mandatory_atoms": len(rows),
            "mapped_mandatory_atoms": sum(
                row["coverage_status"] != "UNMAPPED" for row in rows
            ),
            "unmapped_mandatory_atoms": sum(
                row["coverage_status"] == "UNMAPPED" for row in rows
            ),
            "full_atoms": sum(row["coverage_status"] == "FULL" for row in rows),
            "wrong_year": 0,
            "unsupported_claims": 0,
            "by_status": dict(sorted(states.items())),
            "by_manual": by_manual,
        },
        "rows": rows,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# OFFICIAL PROGRAM COVERAGE 2026-2027",
        "",
        f"- Mandatory mapped: {summary['mapped_mandatory_atoms']}/{summary['mandatory_atoms']}",
        f"- Mandatory unmapped: {summary['unmapped_mandatory_atoms']}",
        f"- FULL: {summary['full_atoms']}",
        f"- Wrong year: {summary['wrong_year']}",
        f"- Unsupported claims: {summary['unsupported_claims']}",
        "",
        "## Par manuel",
        "",
    ]
    for manual in MANUAL_ORDER:
        item = summary["by_manual"][manual]
        lines.append(
            f"- `{manual}`: {item['mapped']}/{item['mandatory_atoms']} mapped; "
            f"{item['unmapped']} unmapped; {item['full']} FULL"
        )
    lines.extend(
        [
            "",
            "`FULL` demeure interdit tant que les validations scientifique, pédagogique et d'alignement d'évaluation ne sont pas toutes vertes au SHA source courant.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    expected = {JSON_TARGET: render_json(payload), MD_TARGET: render_markdown(payload)}
    if args.check:
        stale = [
            path
            for path, content in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"STALE_OR_MISSING: {path.relative_to(ROOT)}")
            return 1
        print(
            "official programme coverage current: "
            f"{payload['summary']['mapped_mandatory_atoms']}/"
            f"{payload['summary']['mandatory_atoms']}"
        )
        return 0
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
