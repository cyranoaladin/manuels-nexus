#!/usr/bin/env python3
"""Toutes les alertes des journaux LaTeX 1SPE, classées, et aucune non classée.

Un registre antérieur -- `LATEX_LAYOUT_WARNING_LEDGER` -- fige l'observation
d'une construction passée : vingt-cinq lignes Overfull/Underfull, et quatre
familles nommées mais renvoyées à un triage séparé, dont
`PDF_BACKEND_POP_EMPTY_COLOR_PAGE_STACK` à 943 et 3 008 occurrences. Ce
triage-là est fait ; ce module le remplace par une lecture VIVANTE des deux
journaux réellement produits, sans aucune ligne recopiée.

La règle est simple : toute ligne d'alerte du journal appartient à une famille
déclarée, et le compte de chaque famille doit être zéro. Une famille inconnue
est bloquante par construction -- elle ne peut pas être « petite », « bénigne »
ou « hors périmètre », puisqu'elle n'a pas encore été regardée.

`Info` n'est pas une alerte : microtype signale des caractères absents d'une
fonte pour ses seuls réglages de protrusion, et le moteur le dit lui-même en
`Info`. Ces lignes sont comptées et publiées, jamais confondues avec une
alerte.

Métrique bloquante : `LATEX_WARNINGS`, `UNCLASSIFIED_WARNING_LINES`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402


def _relative(path: Path) -> str:
    """Chemin lisible, y compris pour un journal fabriqué hors du dépôt."""

    try:
        return relative(path)
    except ValueError:
        return str(path)

JSON_TARGET = ROOT / "audit/1SPE_LATEX_LOG_WARNING_GATE.json"
MD_TARGET = ROOT / "audit/1SPE_LATEX_LOG_WARNING_GATE.md"
GENERATED_BY = "scripts/build_1spe_latex_log_warning_gate.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")

# Toute ligne qui ouvre une alerte, quelle qu'en soit la source : le noyau, une
# classe, un module, un paquet, le moteur de sortie, ou le casseur de lignes.
WARNING_LINE = re.compile(
    r"^(?:"
    r"(?P<latex>LaTeX(?:3)? Warning)"
    r"|(?:Class|Package|Module) (?P<origin>[\w@.-]+) Warning"
    r"|warning +\((?P<backend>[\w ]+)\): *(?P<backend_message>.*?) *$"
    r"|(?P<box>Overfull|Underfull) \\(?P<box_kind>[hv])box"
    r")"
)
INFO_LINE = re.compile(r"^(?:Class|Package|Module) ([\w@.-]+) Info\b")

# La partition, refermée : chaque famille dit ce qu'elle était, et pourquoi
# elle ne peut plus revenir sans qu'on le sache.
FAMILIES: dict[str, dict[str, str]] = {
    "PDF_BACKEND_POP_EMPTY_COLOR_PAGE_STACK": {
        "cause": (
            "`\\color` pousse sa couleur sur-le-champ et confie la dépile à "
            "`\\aftergroup` : composée dans la boîte capturée d'une note de "
            "marge, la poussée partait dans le Form XObject tandis que la "
            "dépile restait sur la page. Une alerte par note."
        ),
        "resolution": (
            "La couleur se referme DANS la boîte, par le groupe que le noyau "
            "LaTeX fournit pour cela (`\\color@begingroup`/`\\color@endgroup`)."
        ),
        "closed_by": "gabarits/common/nexus-margin-rail.tex",
    },
    "REQUESTED_NAME_DIFFERS_FROM_PROVIDED_NAME": {
        "cause": (
            "Les gabarits sont chargés par leur chemin ; le noyau comparait ce "
            "chemin au nom nu déclaré par `\\ProvidesPackage`."
        ),
        "resolution": (
            "Chaque gabarit se déclare sous `\\@currpath\\@currname`, c'est-à-"
            "dire sous le nom par lequel on l'a effectivement demandé, en "
            "gardant son nom de fichier dans la description."
        ),
        "closed_by": "gabarits/**/nexus-*.{cls,sty}",
    },
    "SCRLAYER_FOOTHEIGHT_TOO_LOW": {
        "cause": (
            "Le folio est une pastille circulaire dont le diamètre suit le "
            "nombre de chiffres. Mesuré sur la page 1, `\\footheight` devenait "
            "trop court à la page 10, puis à la page 100."
        ),
        "resolution": (
            "`\\footheight` est mesuré une fois sur la pastille la plus haute "
            "que le manuel puisse porter, celle de trois chiffres, support de "
            "ligne compris -- la hauteur exacte que scrlayer réclamait."
        ),
        "closed_by": "gabarits/common/nexus-manuel.cls",
    },
    "TYPEAREA_DIV_NOT_DEFINED_FOR_FONTSIZE": {
        "cause": (
            "typearea ne tabule aucun DIV pour un corps de 9,5 pt : il "
            "cherchait le sien en vain, le signalait, puis retombait sur "
            "`DIV=calc`."
        ),
        "resolution": (
            "`DIV=6` est écrit -- exactement ce que ce calcul donne. Les "
            "longueurs de page sont inchangées au sp près."
        ),
        "closed_by": "gabarits/common/nexus-manuel.cls",
    },
    "UNDERFULL_HBOX": {
        "cause": (
            "Un système de deux équations était composé en ligne dans un item "
            "de liste : la ligne de texte qui le précédait s'étirait pour le "
            "laisser passer à la ligne suivante."
        ),
        "resolution": (
            "Le système est composé hors texte, ce qu'il était déjà "
            "typographiquement."
        ),
        "closed_by": (
            "Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/"
            "cours/13_C4_positions_relatives.tex"
        ),
    },
    "OVERFULL_HBOX": {
        "cause": "Débordement horizontal d'une boîte composée.",
        "resolution": "Aucun débordement dans la construction observée.",
        "closed_by": "—",
    },
}


class WarningGateError(RuntimeError):
    """Une preuve manque : le verdict ne peut pas être rendu."""


def _reject(message: str) -> None:
    raise WarningGateError(message)


def classify(line: str, match: re.Match[str]) -> str:
    """La famille d'une ligne d'alerte, lue sur la ligne elle-même."""

    if match.group("backend") is not None:
        message = match.group("backend_message") or ""
        if "pop empty color page stack" in message:
            return "PDF_BACKEND_POP_EMPTY_COLOR_PAGE_STACK"
        return "UNKNOWN"
    if match.group("box") is not None:
        return f"{match.group('box').upper()}_HBOX"
    if match.group("latex") is not None:
        if "You have requested" in line:
            return "REQUESTED_NAME_DIFFERS_FROM_PROVIDED_NAME"
        return "UNKNOWN"
    origin = match.group("origin")
    if origin == "scrlayer-scrpage" and "footheight" in line:
        return "SCRLAYER_FOOTHEIGHT_TOO_LOW"
    if origin == "typearea" and "DIV for" in line:
        return "TYPEAREA_DIV_NOT_DEFINED_FOR_FONTSIZE"
    return "UNKNOWN"


def read_log(variant: str) -> dict[str, Any]:
    log = BUILD / f"MANUEL_1SPE_{variant}.log"
    if not log.is_file():
        _reject(f"journal absent : {_relative(log)}")
    text = log.read_text(encoding="utf-8", errors="replace")

    counts: dict[str, int] = {name: 0 for name in FAMILIES}
    unknown: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = WARNING_LINE.match(line)
        if match is None:
            continue
        family = classify(line, match)
        if family == "UNKNOWN":
            unknown.append({"log_line": number, "text": line.strip()[:200]})
            continue
        counts[family] += 1

    informations = sum(1 for line in text.splitlines() if INFO_LINE.match(line))
    return {
        "variant": variant,
        "log_path": _relative(log),
        "log_lines": text.count("\n") + 1,
        "by_family": counts,
        "unclassified": unknown[:20],
        "LATEX_WARNINGS": sum(counts.values()) + len(unknown),
        "UNCLASSIFIED_WARNING_LINES": len(unknown),
        "INFORMATION_LINES_NOT_WARNINGS": informations,
    }


def build() -> dict[str, Any]:
    variants = [read_log(variant) for variant in VARIANTS]
    families = {
        name: {
            **detail,
            "occurrences": sum(row["by_family"][name] for row in variants),
        }
        for name, detail in FAMILIES.items()
    }
    return {
        "artifact_type": "1spe_latex_log_warning_gate",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "rule": (
            "Toute ligne d'alerte appartient à une famille déclarée, et chaque "
            "famille vaut zéro. Une famille inconnue est bloquante : elle n'a "
            "pas encore été regardée."
        ),
        "an_info_line_is_not_a_warning": (
            "microtype signale en `Info` les caractères absents d'une fonte "
            "pour ses seuls réglages de protrusion. Ces lignes sont comptées "
            "et publiées, jamais comptées comme alertes."
        ),
        "supersedes": {
            "artifact": "audit/LATEX_LAYOUT_WARNING_LEDGER.json",
            "why": (
                "Ce registre fige une construction passée et renvoyait quatre "
                "familles à un triage séparé. Le triage est fait ; la lecture "
                "est désormais vivante et exhaustive."
            ),
        },
        "families": families,
        "variants": variants,
        "summary": {
            "LATEX_WARNINGS": sum(row["LATEX_WARNINGS"] for row in variants),
            "UNCLASSIFIED_WARNING_LINES": sum(
                row["UNCLASSIFIED_WARNING_LINES"] for row in variants
            ),
            "DECLARED_FAMILIES": len(FAMILIES),
            "INFORMATION_LINES_NOT_WARNINGS": sum(
                row["INFORMATION_LINES_NOT_WARNINGS"] for row in variants
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Alertes des journaux LaTeX — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['rule']}",
        "",
        f"> {payload['an_info_line_is_not_a_warning']}",
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
        "## Familles",
        "",
        "| Famille | Occurrences | Cause | Fermée par |",
        "|---|---:|---|---|",
    ]
    for name, detail in payload["families"].items():
        lines.append(
            f"| `{name}` | {detail['occurrences']} | {detail['cause']} "
            f"| `{detail['closed_by']}` |"
        )
    for row in payload["variants"]:
        lines += [
            "",
            f"## Variante `{row['variant']}`",
            "",
            f"`{row['log_path']}` — {row['log_lines']} lignes, "
            f"{row['INFORMATION_LINES_NOT_WARNINGS']} lignes d'information.",
            "",
            "| Famille | Occurrences |",
            "|---|---:|",
        ]
        for name, value in row["by_family"].items():
            lines.append(f"| `{name}` | {value} |")
        if row["unclassified"]:
            lines += ["", "### Non classées", ""]
            for entry in row["unclassified"]:
                lines.append(f"- ligne {entry['log_line']} : `{entry['text']}`")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except WarningGateError as error:
        print(f"1SPE-LATEX-LOG-WARNING-GATE-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {_relative(JSON_TARGET)} et {_relative(MD_TARGET)}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    for row in payload["variants"]:
        for entry in row["unclassified"]:
            print(
                f"UNCLASSIFIED {row['variant']}:{entry['log_line']} {entry['text']}",
                file=sys.stderr,
            )
    summary = payload["summary"]
    return 1 if summary["LATEX_WARNINGS"] or summary["UNCLASSIFIED_WARNING_LINES"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
