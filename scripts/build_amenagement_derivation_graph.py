#!/usr/bin/env python3
"""Graphe de derivation des versions amenagees.

  CANONICAL_OBJECT  ->  AMENAGEMENT_PROFILE  ->  AMENAGED_OBJECT

Chaque objet amenage doit dire de quel objet du chapitre il derive et quels
amenagements lui ont ete appliques. Sans cette chaine, rien ne distingue une
version amenagee d'un exercice plus facile ecrit a cote — et un exercice plus
facile n'est pas un amenagement, c'est une baisse d'exigence.

CE QUE LE PRODUCTEUR REFUSE.

`AMENAGED_WITHOUT_SOURCE`      aucun objet canonique declare, ou introuvable.
`AMENAGEMENT_MOVES_THE_TARGET` l'objet travaille une capacite absente de sa
                               source : l'amenagement a deplace la cible.
`AMENAGEMENT_DROPS_THE_TARGET` l'objet ne travaille aucune capacite de sa
                               source : il n'en derive plus.
`PROFILE_DECLARED_NOT_APPLIED` un profil est annonce sans laisser de marque
                               observable dans le texte. Une etiquette n'est
                               pas un amenagement.
`FRAGILE_TABULAR_MARKUP`       `\\lstinline{...}` colle a un `&` : la
                               compilation du livret casse.

Aucun de ces verdicts n'est negociable par declaration : ils sont tous
constates sur le fichier.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402
from amenagement_profiles import (  # noqa: E402
    FRAGILE_IN_TABULAR,
    PROFILES,
    observed_profiles,
)

OUTPUT_JSON = ROOT / "audit/AMENAGEMENT_DERIVATION_GRAPH.json"
OUTPUT_MD = ROOT / "audit/AMENAGEMENT_DERIVATION_GRAPH.md"

MANUAL_CHAPTERS = {
    "1NSI": ROOT / "NSI/chapitres",
    "TNSI": ROOT / "NSI/chapitres",
}

META = re.compile(r"^%\s*META:\s*(\{.*\})\s*$")


def read_meta(path: Path) -> dict[str, Any]:
    first = path.read_text(encoding="utf-8").split("\n", 1)[0]
    match = META.match(first.strip())
    if match is None:
        raise ValueError(f"META absente ou illisible: {path}")
    return json.loads(match.group(1))


def _chapter_objects(chapter_dir: Path) -> dict[str, dict[str, Any]]:
    """Tous les objets du chapitre, indexes par identifiant."""
    objects: dict[str, dict[str, Any]] = {}
    for path in sorted(chapter_dir.rglob("*.tex")):
        if "/amenagee/" in path.as_posix():
            continue
        try:
            meta = read_meta(path)
        except (ValueError, json.JSONDecodeError):
            continue
        identifier = meta.get("id")
        if isinstance(identifier, str):
            objects[identifier] = {"meta": meta, "path": path}
    return objects


def _contract_alias(chapter_dir: Path) -> dict[str, str]:
    """code local -> reference officielle, lu au contrat du chapitre.

    Comparer sans resoudre etait un defaut : un objet declarant
    `capacites_codes: ["C1"]` et sa source declarant `capacites:
    ["P-BASE-01"]` travaillent la MEME capacite, et la comparaison brute les
    disait differentes. C'est la faute que `capacity_identity` interdit —
    resoudre par egalite, jamais par apparence.
    """
    import yaml  # noqa: PLC0415

    contract = yaml.safe_load(
        (chapter_dir / "contrat.yaml").read_text(encoding="utf-8")
    ) or {}
    alias: dict[str, str] = {}
    for capacity in contract.get("capacites") or []:
        if not isinstance(capacity, dict):
            continue
        code = capacity.get("code")
        reference = capacity.get("ref_capacite")
        if isinstance(code, str) and isinstance(reference, str):
            alias[code] = reference
    return alias


def _capacity_codes(meta: dict[str, Any], alias: dict[str, str]) -> set[str]:
    """Capacites travaillees, exprimees en references officielles."""
    codes = set()
    for key in ("capacites_codes", "capacites"):
        value = meta.get(key)
        if isinstance(value, list):
            codes.update(str(v) for v in value if isinstance(v, str))
    return {alias.get(code, code) for code in codes}


def audit_object(
    path: Path,
    chapter_objects: dict[str, Any],
    alias: dict[str, str],
) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    meta = read_meta(path)
    findings: list[str] = []

    sources = meta.get("derive_de")
    sources = sources if isinstance(sources, list) else []
    resolved = [s for s in sources if s in chapter_objects]
    if not sources or len(resolved) != len(sources):
        findings.append("AMENAGED_WITHOUT_SOURCE")

    scoped = _capacity_codes(meta, alias)
    source_scoped = {
        code
        for identifier in resolved
        for code in _capacity_codes(chapter_objects[identifier]["meta"], alias)
    }
    if resolved:
        if not scoped & source_scoped:
            findings.append("AMENAGEMENT_DROPS_THE_TARGET")
        if scoped - source_scoped:
            findings.append("AMENAGEMENT_MOVES_THE_TARGET")

    declared = meta.get("profil_amenagement")
    declared = set(declared) if isinstance(declared, list) else set()
    unknown = sorted(declared - set(PROFILES))
    if not declared or unknown:
        findings.append("PROFILE_DECLARED_NOT_APPLIED")
    else:
        observed = observed_profiles(text)
        if declared - observed:
            findings.append("PROFILE_DECLARED_NOT_APPLIED")

    if FRAGILE_IN_TABULAR.search(text):
        findings.append("FRAGILE_TABULAR_MARKUP")

    return {
        "object_id": meta.get("id"),
        "path": path.relative_to(ROOT).as_posix(),
        "chapter": meta.get("chapitre"),
        "status": meta.get("status"),
        "CANONICAL_OBJECT": sources,
        "canonical_resolved": resolved,
        "AMENAGEMENT_PROFILE": sorted(declared),
        "profiles_observed": sorted(observed_profiles(text)),
        "capacity_codes": sorted(scoped),
        "source_capacity_codes": sorted(source_scoped),
        "findings": sorted(set(findings)),
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    chapters: list[dict[str, Any]] = []
    inputs: list[str] = []

    for manual, base in sorted(MANUAL_CHAPTERS.items()):
        for chapter_dir in sorted(base.iterdir()):
            if not chapter_dir.name.startswith(f"{manual}-"):
                continue
            if not (chapter_dir / "contrat.yaml").is_file():
                continue
            amenagee = chapter_dir / "amenagee"
            paths = sorted(amenagee.glob("*.tex")) if amenagee.is_dir() else []
            objects = _chapter_objects(chapter_dir)
            alias = _contract_alias(chapter_dir)
            rows = [audit_object(p, objects, alias) for p in paths]
            records.extend(rows)
            inputs.extend(p.relative_to(root).as_posix() for p in paths)
            chapters.append({
                "manual": manual,
                "chapter": chapter_dir.name,
                "amenaged_objects": len(rows),
                "covered": bool(rows),
                "findings": sorted({f for row in rows for f in row["findings"]}),
            })

    by_manual: dict[str, dict[str, int]] = {}
    for row in chapters:
        entry = by_manual.setdefault(
            row["manual"], {"chapters_total": 0, "chapters_covered": 0}
        )
        entry["chapters_total"] += 1
        entry["chapters_covered"] += int(row["covered"])

    counts: dict[str, int] = {}
    for row in records:
        for finding in row["findings"]:
            counts[finding] = counts.get(finding, 0) + 1

    summary = {
        "AMENAGED_OBJECTS": len(records),
        "CHAPTERS_COVERED": sum(v["chapters_covered"] for v in by_manual.values()),
        "CHAPTERS_TOTAL": sum(v["chapters_total"] for v in by_manual.values()),
        "AMENAGED_WITHOUT_SOURCE": counts.get("AMENAGED_WITHOUT_SOURCE", 0),
        "AMENAGEMENT_MOVES_THE_TARGET": counts.get("AMENAGEMENT_MOVES_THE_TARGET", 0),
        "AMENAGEMENT_DROPS_THE_TARGET": counts.get("AMENAGEMENT_DROPS_THE_TARGET", 0),
        "PROFILE_DECLARED_NOT_APPLIED": counts.get("PROFILE_DECLARED_NOT_APPLIED", 0),
        "FRAGILE_TABULAR_MARKUP": counts.get("FRAGILE_TABULAR_MARKUP", 0),
        "DERIVATION_DEFECTS": sum(counts.values()),
    }
    payload = {
        "artifact_type": "amenagement_derivation_graph",
        "schema_version": 1,
        "generated_by": "scripts/build_amenagement_derivation_graph.py",
        "approves_nothing": True,
        "summary": summary,
        "by_manual": by_manual,
        "profiles": {
            name: description for name, (description, _) in sorted(PROFILES.items())
        },
        "chapters": chapters,
        "records": records,
    }
    payload["freshness"] = freshness.stamp(inputs, root=root)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Dérivation des versions aménagées",
        "",
        "`CANONICAL_OBJECT` → `AMENAGEMENT_PROFILE` → `AMENAGED_OBJECT`",
        "",
        f"- Objets aménagés : `{s['AMENAGED_OBJECTS']}`",
        f"- Chapitres couverts : `{s['CHAPTERS_COVERED']}` / `{s['CHAPTERS_TOTAL']}`",
        f"- `AMENAGED_WITHOUT_SOURCE` : `{s['AMENAGED_WITHOUT_SOURCE']}`",
        f"- `AMENAGEMENT_MOVES_THE_TARGET` : `{s['AMENAGEMENT_MOVES_THE_TARGET']}`",
        f"- `AMENAGEMENT_DROPS_THE_TARGET` : `{s['AMENAGEMENT_DROPS_THE_TARGET']}`",
        f"- `PROFILE_DECLARED_NOT_APPLIED` : `{s['PROFILE_DECLARED_NOT_APPLIED']}`",
        f"- `FRAGILE_TABULAR_MARKUP` : `{s['FRAGILE_TABULAR_MARKUP']}`",
        "",
        "## Profils",
        "",
    ]
    for name, description in payload["profiles"].items():
        lines.append(f"- `{name}` — {description}")
    lines += ["", "| Objet | Chapitre | Dérive de | Profils | Défauts |", "|---|---|---|---|---|"]
    for row in payload["records"]:
        lines.append(
            f"| `{row['object_id']}` | `{row['chapter']}` | "
            f"{', '.join(f'`{s}`' for s in row['CANONICAL_OBJECT']) or '—'} | "
            f"{', '.join(row['AMENAGEMENT_PROFILE']) or '—'} | "
            f"{', '.join(row['findings']) or '—'} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT_JSON.is_file():
            print("AMENAGEMENT_DERIVATION_GRAPH check: MISSING")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("AMENAGEMENT_DERIVATION_GRAPH check: STALE")
            return 1
        print("AMENAGEMENT_DERIVATION_GRAPH check: OK")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
