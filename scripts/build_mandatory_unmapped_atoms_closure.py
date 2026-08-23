#!/usr/bin/env python3
"""Build the deterministic closure ledger for mandatory structural gaps."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "audit" / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
JSON_TARGET = ROOT / "audit" / "MANDATORY_UNMAPPED_ATOMS_CLOSURE.json"
MD_TARGET = ROOT / "audit" / "MANDATORY_UNMAPPED_ATOMS_CLOSURE.md"


def _digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def build_payload() -> dict[str, Any]:
    coverage = json.loads(SOURCE.read_text(encoding="utf-8"))
    structural = [
        row
        for row in coverage["rows"]
        if row["coverage_status"] == "STRUCTURALLY_MAPPED"
    ]
    closures = []
    for row in structural:
        gap_type = row.get("gap_type")
        reason = row.get("gap_reason") or row.get("reason")
        if not gap_type or not reason:
            raise ValueError(f"explicit gap classification required: {row['atom_id']}")
        closures.append(
            {
                "atom_id": row["atom_id"],
                "NOR": row["NOR"],
                "official_section": row["official_section"],
                "official_wording": row["official_wording_or_short_paraphrase"],
                "manual": row["manual"],
                "why_unmapped": reason,
                "existing_related_content": row["evidence_paths"],
                "gap_type": gap_type,
                "correct_action": reason,
                "mapped_chapter": row["chapter"],
                "contract_capacity": row["contract_capacity"],
                "closure_status": "STRUCTURALLY_MAPPED",
                "remaining_content_state": {
                    "programme": row["programme_state"],
                    "scientific": row["scientific_state"],
                    "pedagogical": row["pedagogical_state"],
                    "assessment_alignment": row["assessment_alignment_state"],
                },
                "full_claim": False,
            }
        )
    by_gap = Counter(row["gap_type"] for row in closures)
    by_manual = Counter(row["manual"] for row in closures)
    return {
        "schema_version": 2,
        "artifact_type": "mandatory_unmapped_atoms_closure",
        "source_registry": str(SOURCE.relative_to(ROOT)),
        "source_digest": _digest(SOURCE),
        "methodology": {
            "structural_mapping_is_not_full": True,
            "content_debt_is_preserved": True,
            "legacy_333_denominator_is_authoritative": False,
            "current_direct_official_denominator": coverage["summary"][
                "mandatory_atoms"
            ],
        },
        "summary": {
            "mandatory_atoms": coverage["summary"]["mandatory_atoms"],
            "mandatory_mapped": coverage["summary"]["mapped_mandatory_atoms"],
            "mandatory_unmapped_remaining": coverage["summary"][
                "unmapped_mandatory_atoms"
            ],
            "structural_closures": len(closures),
            "by_gap_type": dict(sorted(by_gap.items())),
            "by_manual": dict(sorted(by_manual.items())),
            "unknown": 0,
            "full": coverage["summary"]["full_atoms"],
        },
        "closures": closures,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Fermeture des atoms obligatoires non mappés",
        "",
        f"- Atoms obligatoires mappés : {summary['mandatory_mapped']}/{summary['mandatory_atoms']}",
        f"- Non mappés restants : {summary['mandatory_unmapped_remaining']}",
        f"- Fermetures structurelles documentées : {summary['structural_closures']}",
        f"- FULL : {summary['full']}",
        f"- UNKNOWN : {summary['unknown']}",
        "",
        "Une fermeture structurelle prouve le rattachement atom → unité éditoriale → capacité contractuelle. Elle ne prouve ni la suffisance du contenu, ni la validation scientifique ou pédagogique.",
        "",
        "## Par manuel",
        "",
    ]
    for manual, count in summary["by_manual"].items():
        lines.append(f"- `{manual}` : {count}")
    lines.extend(["", "## Par type de gap conservé", ""])
    for gap_type, count in summary["by_gap_type"].items():
        lines.append(f"- `{gap_type}` : {count}")
    lines.append("")
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
            "mandatory mapping closure current: "
            f"{payload['summary']['mandatory_mapped']}/"
            f"{payload['summary']['mandatory_atoms']}"
        )
        return 0
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
