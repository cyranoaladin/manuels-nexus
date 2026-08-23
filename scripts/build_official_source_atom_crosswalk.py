#!/usr/bin/env python3
"""Build the reviewed official-source-segment to official-atom crosswalk."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
SEGMENTS_PATH = AUDIT / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
ATOMS_PATH = AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
JSON_TARGET = AUDIT / "OFFICIAL_SOURCE_ATOM_CROSSWALK_2026_2027.json"
MD_TARGET = AUDIT / "OFFICIAL_SOURCE_ATOM_CROSSWALK_2026_2027.md"


def _digest(paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def build_payload() -> dict[str, Any]:
    sources = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
    registry = json.loads(ATOMS_PATH.read_text(encoding="utf-8"))
    atoms_by_segment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for atom in registry["atoms"]:
        for segment_id in atom["source_segment_ids"]:
            atoms_by_segment[segment_id].append(atom)
    non_atoms = {
        item["source_segment_id"]: item for item in registry["classified_non_atoms"]
    }

    rows: list[dict[str, Any]] = []
    unclassified: list[str] = []
    unparsed_mandatory: list[str] = []
    duplicate_atoms: list[str] = []
    wrong_year: list[str] = []
    mandatory_atom_ids = {
        atom["atom_id"] for atom in registry["atoms"] if atom["mandatory"] == "YES"
    }
    mapped_mandatory_ids: set[str] = set()

    for segment in sources["segments"]:
        segment_id = segment["segment_id"]
        atoms = atoms_by_segment.get(segment_id, [])
        non_atom = non_atoms.get(segment_id)
        if atoms and non_atom:
            duplicate_atoms.append(segment_id)
        if len(atoms) > 1:
            duplicate_atoms.append(segment_id)
        if atoms:
            disposition = "OFFICIAL_ATOM"
            atom_ids = [atom["atom_id"] for atom in atoms]
            mapped_mandatory_ids.update(
                atom["atom_id"] for atom in atoms if atom["mandatory"] == "YES"
            )
            if any(
                atom["manual"] != segment["manual"]
                or atom["authority_NOR"] != segment["authority_NOR"]
                or atom["applicable_school_year"] != "2026-2027"
                for atom in atoms
            ):
                wrong_year.extend(atom_ids)
        elif non_atom:
            disposition = "CLASSIFIED_NON_ATOM"
            atom_ids = []
        else:
            disposition = "UNCLASSIFIED"
            atom_ids = []
            unclassified.append(segment_id)
        if segment["mandatory"] == "YES" and not atoms:
            unparsed_mandatory.append(segment_id)
        rows.append(
            {
                "segment_id": segment_id,
                "manual": segment["manual"],
                "source_anchor": segment["source_anchor"],
                "classification": segment["classification"],
                "mandatory": segment["mandatory"],
                "disposition": disposition,
                "atom_ids": atom_ids,
                "justification": non_atom["justification"] if non_atom else None,
            }
        )

    ambiguous_atoms = [
        atom["atom_id"]
        for atom in registry["atoms"]
        if not atom["source_segment_ids"]
    ]
    summary = {
        "status": "PASS",
        "official_authorities": len(sources["source_documents"]),
        "source_segments": len(rows),
        "official_atoms": len(registry["atoms"]),
        "mandatory_atoms": len(mandatory_atom_ids),
        "mapped_mandatory_atoms": len(mapped_mandatory_ids),
        "classified_non_atoms": len(non_atoms),
        "unparsed_mandatory_segments": len(unparsed_mandatory),
        "unclassified_source_segments": len(unclassified),
        "duplicate_atoms": len(set(duplicate_atoms)),
        "ambiguous_atoms": len(ambiguous_atoms),
        "wrong_year_atoms": len(set(wrong_year)),
    }
    if any(
        summary[key]
        for key in (
            "unparsed_mandatory_segments",
            "unclassified_source_segments",
            "duplicate_atoms",
            "ambiguous_atoms",
            "wrong_year_atoms",
        )
    ) or summary["mandatory_atoms"] != summary["mapped_mandatory_atoms"]:
        summary["status"] = "RED"
    return {
        "schema_version": 1,
        "artifact_name": "OFFICIAL_SOURCE_ATOM_CROSSWALK_2026_2027",
        "namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "applicable_school_year": "2026-2027",
        "source_digest": _digest((SEGMENTS_PATH, ATOMS_PATH)),
        "methodology": {
            "official_source_segments_are_source": True,
            "internal_capacities_are_source": False,
            "fuzzy_matches_are_proof": False,
            "mapping": "exact reviewed source_segment_ids from per-authority atom definitions",
        },
        "summary": summary,
        "findings": {
            "unparsed_mandatory_segment_ids": unparsed_mandatory,
            "unclassified_source_segment_ids": unclassified,
            "duplicate_source_segment_ids": sorted(set(duplicate_atoms)),
            "ambiguous_atom_ids": ambiguous_atoms,
            "wrong_year_atom_ids": sorted(set(wrong_year)),
        },
        "rows": rows,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# OFFICIAL SOURCE ↔ ATOM CROSSWALK 2026-2027",
        "",
        f"Status: **{summary['status']}**.",
        "",
        f"- Authorities: {summary['official_authorities']}/6",
        f"- Source segments: {summary['source_segments']}",
        f"- Official atoms: {summary['official_atoms']}",
        f"- Mandatory atoms mapped: {summary['mapped_mandatory_atoms']}/{summary['mandatory_atoms']}",
        f"- Classified non-atoms: {summary['classified_non_atoms']}",
        f"- Unparsed mandatory segments: {summary['unparsed_mandatory_segments']}",
        f"- Unclassified source segments: {summary['unclassified_source_segments']}",
        f"- Duplicate atoms: {summary['duplicate_atoms']}",
        f"- Ambiguous atoms: {summary['ambiguous_atoms']}",
        f"- Wrong year: {summary['wrong_year_atoms']}",
        "",
        "Le détail ligne par ligne est conservé dans le compagnon JSON. Les rapprochements flous ne constituent jamais une preuve.",
        "",
    ]
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
            "official source/atom crosswalk current: "
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
