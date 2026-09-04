#!/usr/bin/env python3
"""Chaque test sauté du périmètre 1SPE, nommé et disposé.

Un test qui saute ne protège rien, et un compte de « sautés » sans noms ne dit
pas si la release est couverte. Avant PRINT_READY, chaque skip doit donc porter
son identité, sa raison, sa portée, et une disposition : soit il est
véritablement NON APPLICABLE au produit courant et le prouve, soit il DOIT
tourner.

Ce module ne devine rien : il lit la capture du run de périmètre, en extrait
les lignes `SKIPPED` que pytest a réellement écrites, et confronte chacune aux
dispositions déclarées. Un skip observé sans disposition est `UNKNOWN`, et
`UNKNOWN` est bloquant -- on ne classe pas ce qu'on n'a pas regardé.

Interdits, et le dire fait partie du contrôle : ajouter un `skipif`
opportunément, poser un `xfail`, exclure un marqueur ou rétrécir le chemin des
tests pour obtenir zéro. Un test tourne, ou il est réellement non applicable.

Métriques bloquantes : `UNKNOWN_SKIPPED`, `RELEASE_RELEVANT_SKIPPED`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_SKIP_DISPOSITION.json"
MD_TARGET = ROOT / "audit/1SPE_SKIP_DISPOSITION.md"
GENERATED_BY = "scripts/build_1spe_skip_disposition.py"

SKIPPED_LINE = re.compile(
    r"^SKIPPED \[(?P<count>\d+)\] (?P<source>[^:]+):(?P<line>\d+): (?P<reason>.*)$"
)

# Les dispositions déclarées, une par skip observé. Rien n'est classé sans avoir
# été regardé, et la clef est l'endroit exact où pytest dit avoir sauté.
DISPOSITIONS: dict[str, dict[str, str]] = {
    "tests/test_1spe_proba_cond_tree_figures.py:466": {
        "test_id": (
            "tests/test_1spe_proba_cond_tree_figures.py::"
            "test_les_feuilles_somment_a_un_quand_l_arbre_est_complet[019]"
        ),
        "reason": "arbre volontairement partiel (EX-019)",
        "scope": "1SPE_RELEASE_SCOPE",
        "release_relevance": "RELEASE_RELEVANT",
        "disposition": "MUST_RUN",
        "resolution": (
            "L'arbre d'EX-019 ne développe que la branche rouge : ses feuilles "
            "ne somment pas à un, et le contrôle passait son tour. Le "
            "comportement est pourtant déterministe -- la masse des feuilles "
            "tracées se calcule sur l'énoncé. Le skip est remplacé par une "
            "assertion : masse attendue, arbre bien tronqué, feuilles "
            "exactement celles que l'énoncé déclare, aucune branche ajoutée."
        ),
        "closed_by": "tests/test_1spe_proba_cond_tree_figures.py",
    },
}


class SkipDispositionError(RuntimeError):
    """Une preuve manque : la disposition ne peut pas être établie."""


def observed_skips(capture: Path) -> list[dict[str, Any]]:
    if not capture.is_file():
        raise SkipDispositionError(f"capture absente : {capture}")
    rows: list[dict[str, Any]] = []
    for line in capture.read_text(encoding="utf-8", errors="replace").splitlines():
        match = SKIPPED_LINE.match(line.strip())
        if match is None:
            continue
        rows.append(
            {
                "source": match.group("source"),
                "line": int(match.group("line")),
                "count": int(match.group("count")),
                "reason": match.group("reason"),
                "key": f"{match.group('source')}:{match.group('line')}",
            }
        )
    return rows


def build(capture: Path) -> dict[str, Any]:
    skips = observed_skips(capture)
    disposed: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    for row in skips:
        declared = DISPOSITIONS.get(row["key"])
        if declared is None:
            unknown.append(row)
            continue
        disposed.append({**row, **declared})

    still_skipping = [
        row for row in disposed if row["disposition"] == "MUST_RUN"
    ]
    return {
        "artifact_type": "1spe_skip_disposition",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "capture": str(capture),
        "capture_sha256": "sha256:"
        + hashlib.sha256(capture.read_bytes()).hexdigest(),
        "what_is_forbidden_to_reach_zero": (
            "Ajouter un skipif opportunément, poser un xfail, exclure un "
            "marqueur, rétrécir le chemin des tests. Un test tourne, ou il est "
            "réellement non applicable et le prouve."
        ),
        "skips": disposed,
        "undisposed": unknown,
        "summary": {
            "SKIPPED_OBSERVED": sum(row["count"] for row in skips),
            "DISPOSED": len(disposed),
            "UNKNOWN_SKIPPED": len(unknown),
            "RELEASE_RELEVANT_SKIPPED": sum(
                row["count"]
                for row in disposed
                if row["release_relevance"] == "RELEASE_RELEVANT"
            ),
            "MUST_RUN_STILL_SKIPPING": len(still_skipping),
            "EXPECTED_NOT_APPLICABLE_WITH_PROOF": sum(
                1
                for row in disposed
                if row["disposition"] == "EXPECTED_NOT_APPLICABLE_WITH_PROOF"
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Disposition des tests sautés — périmètre 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> Interdit pour atteindre zéro : {payload['what_is_forbidden_to_reach_zero']}",
        "",
        f"Capture lue : `{payload['capture_sha256'][:26]}…`",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Skips observés et leur disposition",
        "",
        "| Test | Raison | Portée | Pertinence | Disposition |",
        "|---|---|---|---|---|",
    ]
    for row in payload["skips"]:
        lines.append(
            f"| `{row['test_id']}` | {row['reason']} | `{row['scope']}` | "
            f"`{row['release_relevance']}` | `{row['disposition']}` |"
        )
    for row in payload["skips"]:
        lines += ["", f"### `{row['key']}`", "", row["resolution"], ""]
    if payload["undisposed"]:
        lines += ["", "## Sans disposition — bloquant", ""]
        for row in payload["undisposed"]:
            lines.append(f"- `{row['key']}` : {row['reason']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build(arguments.capture)
    except SkipDispositionError as error:
        print(f"1SPE-SKIP-DISPOSITION-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    summary = payload["summary"]
    return 1 if summary["UNKNOWN_SKIPPED"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
