#!/usr/bin/env python3
"""Deux metriques QCM distinctes, jamais le seul nombre 108.

Des points de controle anterieurs parlaient de "108 renvois TSPE casses" tandis
que la mesure courante donne "108 distracteurs sans diagnostic OU sans renvoi".
Le meme nombre designait deux notions differentes. Cet artefact les separe
definitivement, chacune avec son ensemble exact, son digest et sa distribution :

* TSPE_BROKEN_REMEDIATION_REFERENCES
    un renvoi EST present mais ne resout vers aucune cible existante ;
* GLOBAL_DISTRACTORS_MISSING_DIAGNOSTIC_OR_REFERENCE
    un distracteur incorrect n'a pas de diagnostic, ou pas de renvoi, ou ni
    l'un ni l'autre -- le OU est ensuite decompose.

Lecture seule sur les sources ; aucune baseline touchee.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import yaml

try:
    from scripts.capacity_identity import CapacityIdentityResolver
except ModuleNotFoundError:  # exécution directe depuis scripts/
    from capacity_identity import CapacityIdentityResolver  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
NSI_CHAPTERS = ROOT / "NSI" / "chapitres"
OUTPUT_JSON = ROOT / "audit" / "QCM_REFERENCE_DEBT_METRICS.json"
OUTPUT_MD = ROOT / "audit" / "QCM_REFERENCE_DEBT_METRICS.md"

#: Un renvoi commence par sa cible : C<n> une capacite du cours, M<n> une fiche
#: methode, R<n> ou RE-C<n> un objet de remediation. Le reste est un guide de
#: lecture ("etape 2", "propriete 3") et ne designe pas d'objet.
LEAD = re.compile(r"^\s*(?:cours\s+)?(RE-C|[CMR])\s*(\d+)", re.IGNORECASE)


def set_digest(values: Iterable[str]) -> str:
    payload = json.dumps(sorted(values), separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _chapter_targets(
    chapter: str,
    *,
    resolver: CapacityIdentityResolver | None = None,
) -> dict[str, set[str]]:
    candidates = (CHAPTERS / chapter, NSI_CHAPTERS / chapter)
    root = next((candidate for candidate in candidates if candidate.is_dir()), candidates[0])
    resolver = resolver or CapacityIdentityResolver.from_corpora(
        (CHAPTERS, NSI_CHAPTERS)
    )
    methods: set[str] = set()
    directory = root / "methodes"
    if directory.is_dir():
        for path in sorted(directory.glob("*.tex")):
            methods |= {
                match.group(1)
                for match in re.finditer(
                    r"\\begin\{fichemethode\}\{(M\d+)\}",
                    path.read_text(encoding="utf-8"),
                )
            }
    capacities = {
        identity.local_code for identity in resolver.capacities_of(chapter)
    }
    remediation: set[str] = set()
    directory = root / "remediation"
    if directory.is_dir():
        for path in sorted(directory.glob("*.tex")):
            match = re.search(r"-(?:RE|FR)-(C?\d+)", path.stem)
            if match:
                remediation.add(match.group(1))
    return {"M": methods, "C": capacities, "R": remediation}


def _resolves(kind: str, number: str, targets: dict[str, set[str]]) -> bool:
    kind = kind.upper()
    if kind == "M":
        return f"M{number}" in targets["M"]
    if kind == "C":
        return f"C{number}" in targets["C"]
    return number in targets["R"] or f"C{number}" in targets["R"]


def build_metrics() -> dict[str, Any]:
    broken: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    unparsed: list[dict[str, Any]] = []
    analysed_references = 0
    distractors = 0
    chapters_with_options = 0
    chapter_roots = (CHAPTERS, NSI_CHAPTERS)
    resolver = CapacityIdentityResolver.from_corpora(chapter_roots)
    qcm_paths = sorted(
        path for root in chapter_roots for path in root.glob("*/qcm/*-QCM.json")
    )
    counts = Counter(path.parent.parent.name for path in qcm_paths)
    duplicates = sorted(chapter for chapter, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError("MULTIPLE_QCM_SOURCES: " + ", ".join(duplicates))

    for path in qcm_paths:
        chapter = path.parents[1].name
        targets = _chapter_targets(chapter, resolver=resolver)
        document = json.loads(path.read_text(encoding="utf-8"))
        has_options = False
        for question in document.get("questions", []):
            options = question.get("options")
            if not options:
                continue
            has_options = True
            correct = question.get("correcte")
            diagnostics = question.get("diagnostics") or {}
            for letter in options:
                if letter == correct:
                    continue
                distractors += 1
                identifier = f"{chapter}/{question['id']}/{letter}"
                diagnostic = diagnostics.get(letter)
                erreur = bool(
                    isinstance(diagnostic, dict)
                    and str(diagnostic.get("erreur", "")).strip()
                )
                reference = ""
                if isinstance(diagnostic, dict):
                    reference = str(diagnostic.get("renvoi", "")).strip()
                if not erreur or not reference:
                    missing.append(
                        {
                            "id": identifier,
                            "chapter": chapter,
                            "question": question["id"],
                            "option": letter,
                            "has_diagnostic": erreur,
                            "has_reference": bool(reference),
                        }
                    )
                    continue
                analysed_references += 1
                match = LEAD.match(reference)
                if match is None:
                    unparsed.append({"id": identifier, "reference": reference})
                    continue
                kind = match.group(1)
                kind = "R" if kind.upper().startswith("RE-C") else kind
                if not _resolves(kind, match.group(2), targets):
                    broken.append(
                        {
                            "id": identifier,
                            "chapter": chapter,
                            "reference": reference,
                            "target_kind": kind.upper(),
                        }
                    )
        if has_options:
            chapters_with_options += 1

    tspe_broken = [row for row in broken if row["chapter"].startswith("TSPE")]
    diagnostic_only = [row for row in missing if row["has_reference"] and not row["has_diagnostic"]]
    reference_only = [row for row in missing if row["has_diagnostic"] and not row["has_reference"]]
    both = [row for row in missing if not row["has_diagnostic"] and not row["has_reference"]]

    def described(name: str, rows: list[dict[str, Any]], note: str) -> dict[str, Any]:
        identifiers = [row["id"] for row in rows]
        return {
            "metric": name,
            "count": len(rows),
            "ids": sorted(identifiers),
            "set_digest": set_digest(identifiers),
            "by_manual": dict(
                sorted(Counter(row["id"].split("-")[0] for row in rows).items())
            ),
            "by_chapter": dict(
                sorted(Counter(row["id"].split("/")[0] for row in rows).items())
            ),
            "note": note,
        }

    return {
        "artifact_type": "qcm_reference_debt_metrics",
        "schema_version": 1,
        "generated_by": "scripts/build_qcm_reference_debt_metrics.py",
        "modifies_nothing": True,
        "inventory": {
            "qcm_files": len(qcm_paths),
            "chapters_with_options": chapters_with_options,
            "distractors": distractors,
            "references_analysed": analysed_references,
        },
        "contract": {
            "diagnostic_required": True,
            "reference_required": True,
            "authority": (
                "tout distracteur incorrect exige une erreur documentee ET un "
                "renvoi de remediation"
            ),
            "objective": {
                "REQUIRED_DISTRACTOR_DIAGNOSTIC_MISSING": 0,
                "REQUIRED_REMEDIATION_REFERENCE_MISSING": 0,
            },
        },
        "metrics": [
            described(
                "TSPE_BROKEN_REMEDIATION_REFERENCES",
                tspe_broken,
                "renvoi PRESENT mais ne resolvant vers aucune cible existante, "
                "restreint au manuel TSPE",
            ),
            described(
                "GLOBAL_BROKEN_REMEDIATION_REFERENCES",
                broken,
                "meme regle, tous manuels",
            ),
            described(
                "GLOBAL_DISTRACTORS_MISSING_DIAGNOSTIC_OR_REFERENCE",
                missing,
                "distracteur incorrect sans diagnostic, sans renvoi, ou sans "
                "les deux ; c'est le OU a decomposer",
            ),
            described(
                "MISSING_DIAGNOSTIC_ONLY",
                diagnostic_only,
                "renvoi present, diagnostic absent",
            ),
            described(
                "MISSING_REFERENCE_ONLY",
                reference_only,
                "diagnostic present, renvoi absent",
            ),
            described("MISSING_BOTH", both, "ni diagnostic ni renvoi"),
            described(
                "REQUIRED_DISTRACTOR_DIAGNOSTIC_MISSING",
                diagnostic_only + both,
                "dette obligatoire de diagnostic ; objectif contractuel 0",
            ),
            described(
                "REQUIRED_REMEDIATION_REFERENCE_MISSING",
                reference_only + both,
                "dette obligatoire de renvoi ; objectif contractuel 0",
            ),
        ],
        "unparsed_references": sorted(unparsed, key=lambda row: row["id"]),
        "disambiguation": {
            "collided_number": 108,
            "same_set": set_digest(row["id"] for row in tspe_broken)
            == set_digest(row["id"] for row in missing),
            "statement": (
                "les deux metriques sont distinctes et ne doivent plus jamais "
                "etre designees par le seul nombre 108 : l'une compte des "
                "renvois presents mais non resolus, l'autre des distracteurs "
                "dont le renvoi ou le diagnostic manque"
            ),
        },
        "invariants": {
            "three_way_split_is_exact": len(diagnostic_only)
            + len(reference_only)
            + len(both)
            == len(missing),
            "unparsed_is_zero": not unparsed,
        },
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# QCM — deux dettes de renvoi, jamais un seul « 108 »",
        "",
        payload["disambiguation"]["statement"].capitalize() + ".",
        "",
        "| Métrique | Cardinal | Digest |",
        "|---|---:|---|",
    ]
    for metric in payload["metrics"]:
        lines.append(
            f"| `{metric['metric']}` | {metric['count']} | `{metric['set_digest'][:23]}…` |"
        )
    lines += [
        "",
        "## Décomposition du OU",
        "",
        "Le `OU` de la métrique globale se décompose en trois classes disjointes ;",
        "la dette contractuellement obligatoire est nommée séparément, avec un",
        "objectif de zéro pour chacune.",
        "",
        "## Distribution",
        "",
    ]
    for metric in payload["metrics"]:
        if metric["count"] and metric["by_chapter"]:
            lines.append(f"- `{metric['metric']}` : " + ", ".join(
                f"{chapter} {count}" for chapter, count in metric["by_chapter"].items()
            ))
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_metrics()
    rendered_json = render_json(payload)
    rendered_md = render_md(payload)
    if args.check:
        if not OUTPUT_JSON.is_file() or OUTPUT_JSON.read_text(encoding="utf-8") != rendered_json:
            raise SystemExit("STALE: audit/QCM_REFERENCE_DEBT_METRICS.json")
        if not OUTPUT_MD.is_file() or OUTPUT_MD.read_text(encoding="utf-8") != rendered_md:
            raise SystemExit("STALE: audit/QCM_REFERENCE_DEBT_METRICS.md")
        print("current: audit/QCM_REFERENCE_DEBT_METRICS.json")
        return 0
    OUTPUT_JSON.write_text(rendered_json, encoding="utf-8")
    OUTPUT_MD.write_text(rendered_md, encoding="utf-8")
    counts = {metric["metric"]: metric["count"] for metric in payload["metrics"]}
    print(json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
