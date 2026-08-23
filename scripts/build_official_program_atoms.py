#!/usr/bin/env python3
"""Build the autonomous official-program atom registry for 2026-2027.

The six coverage matrices were extracted directly from official programme
texts.  This registry copies only their regulatory atoms.  Rows that record
internal wrong-year or unsupported claims remain audit findings and are never
rehabilitated as official atoms.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
JSON_TARGET = AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
MD_TARGET = AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.md"
AUTHORITY_PATH = AUDIT / "OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"
MATRIX_PATHS = {
    manual: AUDIT / f"PROGRAM_COVERAGE_MATRIX_{manual}.json"
    for manual in ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
}
EXCLUDED_INTERNAL_STATES = {"WRONG_YEAR", "UNSUPPORTED_CLAIM"}
TYPE_MAP = {
    "MANDATORY_EXPECTED_CAPACITY": "MANDATORY_CAPACITY",
    "MANDATORY_ALGORITHM_OR_PROCEDURE": "MANDATORY_ALGORITHM",
    "OTHER_OFFICIAL": "OTHER_EXPLICIT",
}


def _digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _anchor(section: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", section.casefold()).strip("-")
    return f"section:{slug}"


def _authority_by_manual() -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(AUTHORITY_PATH.read_text(encoding="utf-8"))
    result: dict[str, dict[str, Any]] = {}
    for key, authority in payload["programme_d_enseignement"].items():
        manual = "TSPE" if key == "TSPE_2026_2027" else key
        result[manual] = authority
    return result


def build_registry() -> dict[str, Any]:
    authorities = _authority_by_manual()
    atoms: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    for manual, path in MATRIX_PATHS.items():
        rows = json.loads(path.read_text(encoding="utf-8"))
        authority = authorities[manual]
        for row in rows:
            state = row["coverage_status"]
            if state in EXCLUDED_INTERNAL_STATES:
                excluded.append(
                    {
                        "manual": manual,
                        "source_matrix_row_id": row["row_id"],
                        "reason": state,
                    }
                )
                continue
            atoms.append(
                {
                    "atom_id": row["row_id"].replace("MATRIX", "ATOM"),
                    "manual": manual,
                    "authority_NOR": row["NOR"],
                    "official_section": row["official_section"],
                    "official_page_or_anchor": _anchor(row["official_section"]),
                    "short_official_wording_or_paraphrase": row[
                        "official_wording_or_short_paraphrase"
                    ],
                    "type": TYPE_MAP.get(row["obligation_type"], row["obligation_type"]),
                    "mandatory": "YES" if row["mandatory"] else "NO",
                    "explicit_limitation": row.get("explicit_limitation")
                    or (
                        row["official_wording_or_short_paraphrase"]
                        if row["obligation_type"] == "EXPLICIT_LIMITATION"
                        else None
                    ),
                    "effective_year": authority["effective_from"],
                    "applicable_school_year": "2026-2027",
                    "official_url": authority["authority_url"],
                    "official_document_digest": authority["local_archival_digest"],
                    "source_matrix_path": str(path.relative_to(ROOT)),
                    "source_matrix_row_id": row["row_id"],
                    "source_coverage_status": state,
                }
            )

    by_manual = Counter(atom["manual"] for atom in atoms)
    mandatory_by_manual = Counter(
        atom["manual"] for atom in atoms if atom["mandatory"] == "YES"
    )
    source_paths = [AUTHORITY_PATH, *MATRIX_PATHS.values()]
    return {
        "schema_version": 1,
        "artifact_name": "OFFICIAL_PROGRAM_ATOMS_2026_2027",
        "namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "applicable_school_year": "2026-2027",
        "source_digest": _digest(source_paths),
        "methodology": {
            "source": "six direct-from-official-text coverage matrices",
            "internal_capacities_are_authority": False,
            "excluded_internal_states": sorted(EXCLUDED_INTERNAL_STATES),
            "coverage_is_quality": False,
        },
        "summary": {
            "total_atoms": len(atoms),
            "mandatory_atoms": sum(atom["mandatory"] == "YES" for atom in atoms),
            "by_manual": dict(sorted(by_manual.items())),
            "mandatory_by_manual": dict(sorted(mandatory_by_manual.items())),
            "excluded_internal_findings": len(excluded),
        },
        "excluded_internal_findings": excluded,
        "atoms": atoms,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# OFFICIAL PROGRAM ATOMS 2026-2027",
        "",
        "Namespace: `PROGRAMME_D_ENSEIGNEMENT`.",
        "",
        "Ce registre agrège uniquement les unités réglementaires extraites des textes officiels. Les capacités internes interviennent ultérieurement dans le mapping et ne sont jamais une autorité programme.",
        "",
        f"- Atoms officiels: {summary['total_atoms']}",
        f"- Atoms obligatoires: {summary['mandatory_atoms']}",
        f"- Findings internes exclus: {summary['excluded_internal_findings']}",
        "",
        "## Par manuel",
        "",
    ]
    for manual, count in summary["by_manual"].items():
        mandatory = summary["mandatory_by_manual"].get(manual, 0)
        lines.append(f"- `{manual}`: {count} atoms, dont {mandatory} obligatoires")
    lines.extend(
        [
            "",
            "## Traçabilité",
            "",
            "Chaque ligne complète (`atom_id`, NOR, section/ancre, formulation courte, type, caractère obligatoire, année d'effet, URL et digest officiel) se trouve dans `audit/OFFICIAL_PROGRAM_ATOMS_2026_2027.json`.",
            "",
            "Les lignes `WRONG_YEAR` et `UNSUPPORTED_CLAIM` des matrices restent des findings d'audit séparés et ne figurent jamais parmi les atoms officiels.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_registry()
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
        print(f"official program atoms current: {payload['summary']['total_atoms']}")
        return 0
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
