#!/usr/bin/env python3
"""Gate « une extension ne credite pas le programme obligatoire » (1SPE).

Un contenu declare OPTIONAL_EXTENSION — un « Vers la Terminale » — ne peut
jamais fermer a lui seul la couverture d'un atome obligatoire du programme de
Premiere : l'eleve ne le doit pas, donc il ne prouve rien.

Le gate croise la couverture officielle (`audit/OFFICIAL_PROGRAM_COVERAGE_*`
et `audit/official_program_coverage/<manuel>.json`) avec le statut declare de
chaque objet qui la credite. Le statut d'extension est lu la ou il est
declare, jamais devine :

* la META de l'objet (`programme_alignment`) ;
* les decisions humaines `audit/HUMAN_DECISION_*.json` dont le
  `programme_scope` est OPTIONAL_EXTENSION.

Metrique bloquante : MANDATORY_COVERAGE_FROM_EXTENSION_ONLY.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, object_meta, relative  # noqa: E402

MANUAL = "1SPE"
JSON_TARGET = ROOT / "audit/1SPE_MANDATORY_COVERAGE_EXTENSION_INDEPENDENCE.json"
MD_TARGET = ROOT / "audit/1SPE_MANDATORY_COVERAGE_EXTENSION_INDEPENDENCE.md"
COVERAGE_PER_MANUAL = ROOT / "audit/official_program_coverage" / f"{MANUAL}.json"
COVERAGE_AGGREGATE = ROOT / "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
DECISION_GLOB = "HUMAN_DECISION_*.json"
OPTIONAL_ALIGNMENT = "OPTIONAL_EXTENSION"
SOURCE_FIELD_SUFFIX = "_sources"

ALIGNMENT_EXTENSION = "DECLARED_OPTIONAL_EXTENSION"
ALIGNMENT_ORDINARY = "NO_EXTENSION_DECLARATION"
ALIGNMENT_MISSING = "CREDITED_SOURCE_MISSING"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def coverage_rows() -> list[dict[str, Any]]:
    """Mandatory rows for the manual, cross-checked against the aggregate."""

    per_manual = _load(COVERAGE_PER_MANUAL)
    if per_manual.get("manual") != MANUAL:
        raise RuntimeError(f"couverture inattendue: {relative(COVERAGE_PER_MANUAL)}")
    rows = [row for row in per_manual["rows"] if row.get("mandatory") == "YES"]

    aggregate = _load(COVERAGE_AGGREGATE)
    aggregate_ids = {
        row["atom_id"]
        for row in aggregate["rows"]
        if row.get("manual") == MANUAL and row.get("mandatory") == "YES"
    }
    declared = aggregate["summary"]["by_manual"][MANUAL]["mandatory_atoms"]
    if {row["atom_id"] for row in rows} != aggregate_ids or len(rows) != declared:
        raise RuntimeError(
            "les deux artefacts de couverture officielle ne decrivent pas le "
            "meme ensemble d'atomes obligatoires"
        )
    return rows


def declared_extension_sources() -> dict[str, str]:
    """Objects whose optional-extension status is declared somewhere."""

    declared: dict[str, str] = {}
    for path in sorted((ROOT / "audit").glob(DECISION_GLOB)):
        payload = _load(path)
        if not isinstance(payload, dict):
            continue
        if payload.get("programme_scope") != OPTIONAL_ALIGNMENT:
            continue
        for entry in payload.get("objects", []) or []:
            source = entry.get("source_path")
            if isinstance(source, str) and source:
                declared[source] = relative(path)
    return declared


def alignment_reader(
    decisions: dict[str, str] | None = None,
) -> Callable[[str], tuple[str, str | None]]:
    """Return a reader giving the declared alignment of a credited source."""

    ledger = declared_extension_sources() if decisions is None else decisions

    def read(source: str) -> tuple[str, str | None]:
        path_part = source.split("#", 1)[0]
        if path_part in ledger:
            return ALIGNMENT_EXTENSION, ledger[path_part]
        path = ROOT / path_part
        if not path.is_file():
            return ALIGNMENT_MISSING, None
        if path.suffix != ".tex":
            return ALIGNMENT_ORDINARY, None
        meta = object_meta(path.read_text(encoding="utf-8"))
        if meta.get("programme_alignment") == OPTIONAL_ALIGNMENT:
            return ALIGNMENT_EXTENSION, f"{path_part}#META.programme_alignment"
        return ALIGNMENT_ORDINARY, None

    return read


def credited_sources(row: dict[str, Any]) -> list[tuple[str, str]]:
    """Every (field, source) pair this coverage row uses as evidence."""

    pairs: list[tuple[str, str]] = []
    for field, value in sorted(row.items()):
        if not field.endswith(SOURCE_FIELD_SUFFIX) or not isinstance(value, list):
            continue
        for source in value:
            if isinstance(source, str) and source:
                pairs.append((field, source))
    return pairs


def evaluate(
    rows: list[dict[str, Any]],
    read_alignment: Callable[[str], tuple[str, str | None]],
) -> dict[str, Any]:
    """Classify each mandatory atom by the alignment of what credits it."""

    atoms: list[dict[str, Any]] = []
    for row in rows:
        credits = []
        for field, source in credited_sources(row):
            alignment, declaration = read_alignment(source)
            credits.append(
                {
                    "field": field,
                    "source": source,
                    "alignment": alignment,
                    "declared_by": declaration,
                }
            )
        extension = [c for c in credits if c["alignment"] == ALIGNMENT_EXTENSION]
        ordinary = [c for c in credits if c["alignment"] == ALIGNMENT_ORDINARY]
        missing = [c for c in credits if c["alignment"] == ALIGNMENT_MISSING]
        if not credits:
            verdict = "NO_CREDITING_SOURCE"
        elif not ordinary and extension:
            verdict = "CREDITED_BY_EXTENSION_ONLY"
        elif extension:
            verdict = "CREDITED_BY_BOTH"
        else:
            verdict = "CREDITED_WITHOUT_EXTENSION"
        atoms.append(
            {
                "atom_id": row["atom_id"],
                "obligation_type": row.get("obligation_type"),
                "chapter": row.get("chapter"),
                "contract_capacity": row.get("contract_capacity"),
                "credit_count": len(credits),
                "extension_credit_count": len(extension),
                "missing_credit_count": len(missing),
                "verdict": verdict,
                "credits": credits,
            }
        )
    atoms.sort(key=lambda atom: atom["atom_id"])
    return {
        "atoms": atoms,
        "extension_only": [
            atom for atom in atoms if atom["verdict"] == "CREDITED_BY_EXTENSION_ONLY"
        ],
    }


def build_payload() -> dict[str, Any]:
    rows = coverage_rows()
    decisions = declared_extension_sources()
    result = evaluate(rows, alignment_reader(decisions))
    atoms = result["atoms"]
    counts: dict[str, int] = {}
    for atom in atoms:
        counts[atom["verdict"]] = counts.get(atom["verdict"], 0) + 1
    missing = sorted(
        {
            credit["source"]
            for atom in atoms
            for credit in atom["credits"]
            if credit["alignment"] == ALIGNMENT_MISSING
        }
    )
    return {
        "schema_version": 1,
        "artifact_name": "1SPE_MANDATORY_COVERAGE_EXTENSION_INDEPENDENCE",
        "generated_by": (
            "scripts/build_1spe_mandatory_coverage_extension_independence.py"
        ),
        "manual": MANUAL,
        "scope": (
            "chaque atome obligatoire du programme officiel du manuel, croise "
            "avec le statut declare des objets qui le creditent"
        ),
        "inputs": {
            "coverage_per_manual": relative(COVERAGE_PER_MANUAL),
            "coverage_aggregate": relative(COVERAGE_AGGREGATE),
            "extension_decision_ledgers": sorted(set(decisions.values())),
            "declared_extension_sources": len(decisions),
        },
        "summary": {
            "MANDATORY_ATOMS": len(atoms),
            "MANDATORY_ATOMS_BY_VERDICT": dict(sorted(counts.items())),
            "MANDATORY_COVERAGE_FROM_EXTENSION_ONLY": len(result["extension_only"]),
            "MANDATORY_ATOMS_WITH_ANY_EXTENSION_CREDIT": sum(
                1 for atom in atoms if atom["extension_credit_count"]
            ),
            "CREDITED_SOURCES_MISSING_ON_DISK": len(missing),
            "GATE": "PASS" if not result["extension_only"] else "FAIL",
        },
        "extension_only_atoms": result["extension_only"],
        "credited_sources_missing_on_disk": missing,
        "atoms": atoms,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gate — une extension optionnelle ne credite pas le programme obligatoire",
        "",
        f"Manuel `{payload['manual']}`. Genere par `{payload['generated_by']}`.",
        "",
        "| METRIC_NAME | VALEUR |",
        "| --- | --- |",
        f"| MANDATORY_ATOMS | {summary['MANDATORY_ATOMS']} |",
        "| MANDATORY_COVERAGE_FROM_EXTENSION_ONLY | "
        f"{summary['MANDATORY_COVERAGE_FROM_EXTENSION_ONLY']} |",
        "| MANDATORY_ATOMS_WITH_ANY_EXTENSION_CREDIT | "
        f"{summary['MANDATORY_ATOMS_WITH_ANY_EXTENSION_CREDIT']} |",
        "| CREDITED_SOURCES_MISSING_ON_DISK | "
        f"{summary['CREDITED_SOURCES_MISSING_ON_DISK']} |",
        f"| GATE | {summary['GATE']} |",
        "",
        "## Verdict par atome",
        "",
        "| VERDICT | ATOMES |",
        "| --- | --- |",
    ]
    for verdict, count in summary["MANDATORY_ATOMS_BY_VERDICT"].items():
        lines.append(f"| {verdict} | {count} |")
    lines.extend(
        [
            "",
            "`NO_CREDITING_SOURCE` est une dette de contenu deja enregistree "
            "par la couverture officielle ; ce gate ne la traite pas, il "
            "interdit seulement qu'une extension la referme.",
            "",
            "## Entrees",
            "",
            f"- couverture par manuel : `{payload['inputs']['coverage_per_manual']}`",
            f"- couverture agregee : `{payload['inputs']['coverage_aggregate']}`",
            "- objets declares en extension : "
            f"{payload['inputs']['declared_extension_sources']} via "
            + (
                ", ".join(
                    f"`{path}`"
                    for path in payload["inputs"]["extension_decision_ledgers"]
                )
                or "aucun ledger de decision"
            )
            + " et les META `programme_alignment` des sources creditees",
            "",
        ]
    )
    if payload["extension_only_atoms"]:
        lines.extend(["## Atomes credites par extension seule", ""])
        for atom in payload["extension_only_atoms"]:
            lines.append(f"- `{atom['atom_id']}` ({atom['chapter']})")
        lines.append("")
    else:
        lines.extend(
            [
                "Aucun atome obligatoire n'est couvert uniquement par des "
                "objets d'extension optionnelle.",
                "",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_payload()
    expected = {JSON_TARGET: render_json(payload), MD_TARGET: render_markdown(payload)}
    if args.check:
        stale = [
            path
            for path, content in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        for path in stale:
            print(f"STALE_OR_MISSING: {relative(path)}")
        if stale:
            return 1
        count = payload["summary"]["MANDATORY_COVERAGE_FROM_EXTENSION_ONLY"]
        print(f"MANDATORY_COVERAGE_FROM_EXTENSION_ONLY={count}")
        return 0 if count == 0 else 1
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {relative(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
