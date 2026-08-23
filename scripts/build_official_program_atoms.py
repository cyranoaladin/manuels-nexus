#!/usr/bin/env python3
"""Build the direct-source official-programme atom registry for 2026-2027."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
JSON_TARGET = AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
MD_TARGET = AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.md"
AUTHORITY_PATH = AUDIT / "OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"
SEGMENTS_PATH = AUDIT / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
DEFINITIONS_ROOT = AUDIT / "official_atom_definitions"
MANUAL_ORDER = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
DEFINITION_PATHS = {
    manual: DEFINITIONS_ROOT / f"{manual}.json" for manual in MANUAL_ORDER
}


def _digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item.relative_to(ROOT))):
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _authority_by_manual() -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(AUTHORITY_PATH.read_text(encoding="utf-8"))
    result: dict[str, dict[str, Any]] = {}
    for key, authority in payload["programme_d_enseignement"].items():
        manual = "TSPE" if key == "TSPE_2026_2027" else key
        result[manual] = authority
    if set(result) != set(MANUAL_ORDER):
        raise ValueError(f"unexpected authorities: {sorted(result)}")
    return result


def build_registry() -> dict[str, Any]:
    authorities = _authority_by_manual()
    source_payload = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
    source_segments = {
        segment["segment_id"]: segment for segment in source_payload["segments"]
    }
    atoms: list[dict[str, Any]] = []
    classified_non_atoms: list[dict[str, Any]] = []

    for manual in MANUAL_ORDER:
        path = DEFINITION_PATHS[manual]
        definition = json.loads(path.read_text(encoding="utf-8"))
        authority = authorities[manual]
        if definition["manual"] != manual:
            raise ValueError(f"manual mismatch in {path.relative_to(ROOT)}")
        if definition["authority_NOR"] != authority["official_ref"]:
            raise ValueError(f"authority mismatch in {path.relative_to(ROOT)}")

        for item in definition["atoms"]:
            segment_ids = item["source_segment_ids"]
            segments = [source_segments[segment_id] for segment_id in segment_ids]
            if any(segment["manual"] != manual for segment in segments):
                raise ValueError(f"cross-manual source in {item['atom_id']}")
            atoms.append(
                {
                    "atom_id": item["atom_id"],
                    "manual": manual,
                    "authority_NOR": authority["official_ref"],
                    "official_section": item["official_section"],
                    "official_page_or_anchor": item["official_anchor"],
                    "short_official_wording_or_paraphrase": item[
                        "short_official_wording_or_paraphrase"
                    ],
                    "type": item["obligation_type"],
                    "mandatory": item["mandatory_for_coverage"],
                    "mandatory_justification": item["mandatory_justification"],
                    "explicit_limitation": (
                        item["short_official_wording_or_paraphrase"]
                        if item["obligation_type"] == "EXPLICIT_LIMITATION"
                        else None
                    ),
                    "effective_year": authority["effective_from"],
                    "applicable_school_year": "2026-2027",
                    "official_url": authority["authority_url"],
                    "official_document_digest": authority["local_archival_digest"],
                    "source_definition_path": str(path.relative_to(ROOT)),
                    "source_segment_ids": segment_ids,
                    "coverage_status": "UNMAPPED",
                }
            )

        for item in definition["classified_non_atoms"]:
            segment = source_segments[item["source_segment_id"]]
            if segment["manual"] != manual:
                raise ValueError(f"cross-manual non-atom in {path.relative_to(ROOT)}")
            classified_non_atoms.append(
                {
                    "manual": manual,
                    "source_segment_id": item["source_segment_id"],
                    "classification": item["classification"],
                    "mandatory_for_coverage": item["mandatory_for_coverage"],
                    "justification": item["justification"],
                    "source_definition_path": str(path.relative_to(ROOT)),
                }
            )

    identifiers = [atom["atom_id"] for atom in atoms]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate direct-source atom identifiers")

    by_manual = Counter(atom["manual"] for atom in atoms)
    mandatory_by_manual = Counter(
        atom["manual"] for atom in atoms if atom["mandatory"] == "YES"
    )
    source_paths = [
        AUTHORITY_PATH,
        SEGMENTS_PATH,
        *(DEFINITION_PATHS[manual] for manual in MANUAL_ORDER),
    ]
    return {
        "schema_version": 2,
        "artifact_name": "OFFICIAL_PROGRAM_ATOMS_2026_2027",
        "namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "applicable_school_year": "2026-2027",
        "source_digest": _digest(source_paths),
        "methodology": {
            "source": "six reviewed per-authority definitions derived directly from official source segments",
            "official_source_segments_are_authority": True,
            "internal_capacities_are_authority": False,
            "coverage_matrices_are_authority": False,
            "fuzzy_matches_are_proof": False,
            "coverage_is_quality": False,
        },
        "summary": {
            "total_atoms": len(atoms),
            "mandatory_atoms": sum(atom["mandatory"] == "YES" for atom in atoms),
            "by_manual": dict(sorted(by_manual.items())),
            "mandatory_by_manual": dict(sorted(mandatory_by_manual.items())),
            "classified_non_atoms": len(classified_non_atoms),
            "wrong_year_atoms": 0,
            "duplicate_atoms": 0,
        },
        "classified_non_atoms": classified_non_atoms,
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
        "Ce registre est reconstruit depuis les segments des six textes officiels. Les matrices de couverture et les capacités internes ne sont pas des autorités.",
        "",
        f"- Atoms officiels: {summary['total_atoms']}",
        f"- Atoms obligatoires pour la couverture: {summary['mandatory_atoms']}",
        f"- Segments officiellement classés non-atoms: {summary['classified_non_atoms']}",
        f"- Doublons: {summary['duplicate_atoms']}",
        f"- Wrong year: {summary['wrong_year_atoms']}",
        "",
        "## Par manuel",
        "",
    ]
    for manual in MANUAL_ORDER:
        count = summary["by_manual"].get(manual, 0)
        mandatory = summary["mandatory_by_manual"].get(manual, 0)
        lines.append(f"- `{manual}`: {count} atoms, dont {mandatory} obligatoires")
    lines.extend(
        [
            "",
            "## Statut de couverture",
            "",
            "Les atoms sont initialisés à `UNMAPPED`. Aucun `FULL` n'est dérivé de la seule existence d'un chemin.",
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
