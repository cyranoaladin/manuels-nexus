#!/usr/bin/env python3
"""Gate « niveau Terminale etiquete » sur les sources publiees du manuel 1SPE.

Question posee : chaque occurrence PUBLIEE d'un niveau etranger au manuel
(pour 1SPE : « Terminale ») est-elle a l'interieur d'une extension optionnelle
explicitement declaree, ou d'une phrase qui exclut explicitement le contenu du
chapitre ?

Tout est derive, rien n'est code en dur :

* la surface publiee vient de l'assembleur canonique (`collect_chapter`) ;
* le niveau etranger vient de `assemble_manuel.MANUAL_LEVEL_LABELS` : le
  manuel declare son propre niveau, les autres manuels declarent le leur ;
* le vocabulaire des etiquettes d'extension vient des `extension_label` que
  les META des sources publiees declarent elles-memes ;
* les macros conteneur d'extension optionnelle sont resolues dans la charte :
  une macro `\\newcommand{\\X}[1]{\\begin{env}#1\\end{env}}` dont la chaine
  d'alias d'environnements atteint la boite « aller plus loin » (hors
  parcours) est un conteneur d'extension declare.

Aucune liste blanche, aucun identifiant d'objet, aucun chemin d'objet.

Metrique bloquante : UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import (  # noqa: E402
    ROOT,
    comment_mask,
    foreign_level_labels,
    line_of,
    object_meta,
    published_union,
    read_meta,
    relative,
    sha256_of,
)

MANUAL = "1SPE"
JSON_TARGET = ROOT / "audit/1SPE_TERMINALE_EXTENSION_LABELING_GATE.json"
MD_TARGET = ROOT / "audit/1SPE_TERMINALE_EXTENSION_LABELING_GATE.md"
CHARTER_ROOT = ROOT / "gabarits"
#: Nom que la charte donne elle-meme a sa boite hors parcours (« aller plus
#: loin »). C'est le seul ancrage de vocabulaire de ce gate cote LaTeX.
OUT_OF_TRACK_BOX_MARKER = "plusloin"

MECHANISM_META = "META_PROGRAMME_ALIGNMENT"
MECHANISM_MACRO = "CHARTER_OUT_OF_TRACK_MACRO"
MECHANISM_LABEL = "INLINE_DECLARED_EXTENSION_LABEL"
CLASS_DEFERRAL = "EXPLICIT_LEVEL_DEFERRAL_PARENTHETICAL"
CLASS_UNLABELED = "UNLABELED_WRONG_LEVEL_CONTENT"

_MACRO_DEF = re.compile(
    r"\\newcommand\{\\([A-Za-z]+)\}\[1\]\{\\begin\{([A-Za-z]+)\}#1\\end\{\2\}\}"
)
_ENV_ALIAS = re.compile(
    r"\\(?:new|renew)environment\{([A-Za-z]+)\}\{\\begin\{([A-Za-z]+)\}\}"
    r"\{\\end\{\2\}\}"
)
_TEXTBF = re.compile(r"\\textbf\{")
_OPTIONAL_ALIGNMENT = "OPTIONAL_EXTENSION"


# ---------------------------------------------------------------------------
# Vocabulaire derive
# ---------------------------------------------------------------------------
def optional_extension_macros(charter_root: Path = CHARTER_ROOT) -> frozenset[str]:
    """Macros de la charte qui ouvrent une boite hors parcours."""

    macros: dict[str, str] = {}
    alias: dict[str, set[str]] = {}
    for path in sorted(charter_root.rglob("*")):
        if path.suffix not in {".cls", ".sty"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in _MACRO_DEF.finditer(text):
            macros[match.group(1)] = match.group(2)
        for match in _ENV_ALIAS.finditer(text):
            alias.setdefault(match.group(1), set()).add(match.group(2))

    def reachable(environment: str) -> set[str]:
        seen: set[str] = set()
        stack = [environment]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(alias.get(current, ()))
        return seen

    return frozenset(
        name
        for name, environment in macros.items()
        if any(
            OUT_OF_TRACK_BOX_MARKER in candidate.lower()
            for candidate in reachable(environment)
        )
    )


def wrong_level_pattern(manual: str = MANUAL) -> re.Pattern[str]:
    """Regex des noms de niveau qui n'appartiennent pas a `manual`."""

    words: set[str] = set()
    for label in foreign_level_labels(manual):
        head = re.split(r"[\s—-]+", label.strip())[0]
        if head:
            words.add(head)
    if not words:
        raise RuntimeError("aucun niveau etranger derive de l'assembleur")
    alternation = "|".join(re.escape(word) for word in sorted(words))
    return re.compile(rf"\b(?:{alternation})\b", re.IGNORECASE)


def declared_extension_labels(manual: str = MANUAL) -> tuple[str, ...]:
    """Etiquettes d'extension declarees par les META des sources publiees."""

    labels: set[str] = set()
    for path in published_union(manual):
        meta = read_meta(path)
        label = meta.get("extension_label")
        if isinstance(label, str) and label.strip():
            labels.add(label.strip())
    return tuple(sorted(labels))


# ---------------------------------------------------------------------------
# Portees d'extension declarees dans un fichier
# ---------------------------------------------------------------------------
def _matching_brace(text: str, open_index: int) -> int | None:
    depth = 0
    index = open_index
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _next_group_end(text: str, start: int) -> int | None:
    """End offset of the first top-level TeX group at or after `start`."""

    index = start
    while index < len(text):
        char = text[index]
        if char in " \t\r\n":
            index += 1
            continue
        if char == "%":
            newline = text.find("\n", index)
            if newline == -1:
                return None
            index = newline + 1
            continue
        if char != "\\":
            return None
        macro = re.match(r"\\([A-Za-z]+)\s*", text[index:])
        if macro is None:
            return None
        name = macro.group(1)
        after = index + macro.end()
        if name == "end":
            brace = text.find("{", index)
            if brace == -1:
                return None
            closing = _matching_brace(text, brace)
            if closing is None:
                return None
            index = closing
            continue
        if name == "begin":
            brace = text.find("{", index)
            if brace == -1:
                return None
            closing = _matching_brace(text, brace)
            if closing is None:
                return None
            environment = text[brace + 1 : closing - 1]
            end_marker = f"\\end{{{environment}}}"
            stop = text.find(end_marker, closing)
            if stop == -1:
                return None
            return stop + len(end_marker)
        if after < len(text) and text[after] == "[":
            option = text.find("]", after)
            if option == -1:
                return None
            after = option + 1
        if after < len(text) and text[after] == "{":
            closing = _matching_brace(text, after)
            if closing is None:
                return None
            return closing
        return None
    return None


def macro_spans(text: str, macros: frozenset[str]) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for name in sorted(macros):
        for match in re.finditer(rf"\\{re.escape(name)}\s*\{{", text):
            end = _matching_brace(text, match.end() - 1)
            if end is None:
                continue
            spans.append(
                {
                    "start": match.start(),
                    "end": end,
                    "mechanism": MECHANISM_MACRO,
                    "declaration": f"\\{name}",
                }
            )
    return spans


def label_spans(text: str, labels: tuple[str, ...]) -> list[dict[str, Any]]:
    """Spans opened by an inline `\\textbf{<etiquette declaree>...}` marker."""

    spans: list[dict[str, Any]] = []
    if not labels:
        return spans
    for match in _TEXTBF.finditer(text):
        closing = _matching_brace(text, match.end() - 1)
        if closing is None:
            continue
        content = text[match.end() : closing - 1].strip()
        declared = next(
            (label for label in labels if content.startswith(label)), None
        )
        if declared is None:
            continue
        tail = text[closing:]
        skip = re.match(r"\s*\\end\{[A-Za-z*]+\}", tail)
        after = closing + (skip.end() if skip else 0)
        scoped_end = _next_group_end(text, after)
        spans.append(
            {
                "start": match.start(),
                "end": scoped_end if scoped_end is not None else closing,
                "mechanism": MECHANISM_LABEL,
                "declaration": declared,
                "scope_resolved": scoped_end is not None,
            }
        )
    return spans


def _parenthetical_deferral(text: str, offset: int, pattern: re.Pattern[str]) -> str | None:
    """Return the parenthetical that defers the notion to another level.

    Une phrase qui exclut le contenu du chapitre a ici une forme structurelle
    close : le nom de niveau apparait dans une parenthese qui se TERMINE par
    l'attribution de niveau (`... en Terminale`, `programme de Terminale`).
    Rien de mathematique ne peut donc suivre le nom de niveau a l'interieur de
    la parenthese : l'occurrence n'est pas du contenu, c'est un renvoi.
    """

    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    line = text[line_start : line_end if line_end != -1 else len(text)]
    local = offset - line_start
    open_index = line.rfind("(", 0, local)
    if open_index == -1:
        return None
    close_index = line.find(")", local)
    if close_index == -1:
        return None
    inner = line[open_index + 1 : close_index]
    if "(" in inner or ")" in inner:
        return None
    attribution = re.compile(
        rf"(?:^|\s)(?:en|au|aux|du|de|des|hors|pour)\s+"
        rf"(?:la\s+|le\s+|les\s+)?"
        rf"(?:classe\s+de\s+|programme\s+de\s+|niveau\s+de\s+|cours\s+de\s+)?"
        rf"(?:{pattern.pattern})\s*[.!?]?$",
        re.IGNORECASE,
    )
    return inner.strip() if attribution.search(inner) else None


# ---------------------------------------------------------------------------
# Classement des occurrences
# ---------------------------------------------------------------------------
def classify_text(
    relative_path: str,
    text: str,
    *,
    labels: tuple[str, ...],
    macros: frozenset[str],
    pattern: re.Pattern[str],
) -> list[dict[str, Any]]:
    """Classify every published foreign-level occurrence found in `text`."""

    meta = object_meta(text)
    mask = comment_mask(text)
    spans = macro_spans(text, macros) + label_spans(text, labels)
    object_declared = (
        meta.get("programme_alignment") == _OPTIONAL_ALIGNMENT
        and isinstance(meta.get("extension_label"), str)
        and bool(meta["extension_label"].strip())
    )

    rows: list[dict[str, Any]] = []
    for match in pattern.finditer(text):
        if mask[match.start()]:
            continue  # commentaire LaTeX : jamais compose, donc jamais publie
        row: dict[str, Any] = {
            "source_path": relative_path,
            "line": line_of(text, match.start()),
            "token": match.group(0),
        }
        if object_declared:
            row["classification"] = MECHANISM_META
            row["declaration"] = meta["extension_label"].strip()
            row["scope"] = "OBJECT"
        else:
            enclosing = [
                span
                for span in spans
                if span["start"] <= match.start() < span["end"]
            ]
            if enclosing:
                span = min(enclosing, key=lambda item: item["end"] - item["start"])
                row["classification"] = span["mechanism"]
                row["declaration"] = span["declaration"]
                row["scope"] = "BLOCK"
                row["scope_lines"] = [
                    line_of(text, span["start"]),
                    line_of(text, span["end"] - 1),
                ]
            else:
                deferral = _parenthetical_deferral(text, match.start(), pattern)
                if deferral is not None:
                    row["classification"] = CLASS_DEFERRAL
                    row["declaration"] = deferral
                    row["scope"] = "SENTENCE"
                else:
                    row["classification"] = CLASS_UNLABELED
                    row["declaration"] = None
                    row["scope"] = None
        rows.append(row)
    return rows


def build_payload() -> dict[str, Any]:
    macros = optional_extension_macros()
    labels = declared_extension_labels(MANUAL)
    pattern = wrong_level_pattern(MANUAL)
    files = published_union(MANUAL)

    rows: list[dict[str, Any]] = []
    evidence: list[Path] = []
    for path in files:
        found = classify_text(
            relative(path),
            path.read_text(encoding="utf-8"),
            labels=labels,
            macros=macros,
            pattern=pattern,
        )
        if found:
            evidence.append(path)
        rows.extend(found)
    rows.sort(key=lambda row: (row["source_path"], row["line"]))

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    unlabeled = [row for row in rows if row["classification"] == CLASS_UNLABELED]

    return {
        "schema_version": 1,
        "artifact_name": "1SPE_TERMINALE_EXTENSION_LABELING_GATE",
        "generated_by": "scripts/build_1spe_terminale_extension_labeling_gate.py",
        "manual": MANUAL,
        "scope": (
            "toutes les occurrences non commentees d'un niveau etranger dans "
            "les sources que l'assembleur publie pour au moins une variante"
        ),
        "derivation": {
            "published_surface": (
                "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
                "::collect_chapter"
            ),
            "foreign_level_labels": foreign_level_labels(MANUAL),
            "declared_extension_labels": list(labels),
            "charter_out_of_track_macros": sorted(f"\\{name}" for name in macros),
            "wrong_level_token_regex": pattern.pattern,
        },
        "published_source_count": len(files),
        "evidence_source_count": len(evidence),
        "evidence_source_digest": sha256_of(evidence),
        "summary": {
            "PUBLISHED_WRONG_LEVEL_OCCURRENCES": len(rows),
            "OCCURRENCES_BY_CLASSIFICATION": dict(sorted(counts.items())),
            "UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT": len(unlabeled),
            "GATE": "PASS" if not unlabeled else "FAIL",
        },
        "unlabeled_occurrences": unlabeled,
        "occurrences": rows,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    derivation = payload["derivation"]
    lines = [
        "# Gate — contenu de niveau Terminale etiquete (manuel 1SPE)",
        "",
        f"Genere par `{payload['generated_by']}`.",
        "",
        "| METRIC_NAME | VALEUR |",
        "| --- | --- |",
        "| PUBLISHED_WRONG_LEVEL_OCCURRENCES | "
        f"{summary['PUBLISHED_WRONG_LEVEL_OCCURRENCES']} |",
        "| UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT | "
        f"{summary['UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT']} |",
        f"| GATE | {summary['GATE']} |",
        "",
        "## Repartition",
        "",
        "| CLASSIFICATION | OCCURRENCES |",
        "| --- | --- |",
    ]
    for name, count in summary["OCCURRENCES_BY_CLASSIFICATION"].items():
        lines.append(f"| {name} | {count} |")
    lines.extend(
        [
            "",
            "## Derivation",
            "",
            f"- surface publiee : `{derivation['published_surface']}` "
            f"({payload['published_source_count']} fichiers)",
            f"- sources portant une occurrence : {payload['evidence_source_count']}",
            f"- empreinte de ces sources : `{payload['evidence_source_digest']}`",
            "- niveaux etrangers derives de l'assembleur : "
            + ", ".join(f"« {label} »" for label in derivation["foreign_level_labels"]),
            "- etiquettes d'extension derivees des META : "
            + ", ".join(f"« {label} »" for label in derivation["declared_extension_labels"]),
            "- macros hors parcours derivees de la charte : "
            + ", ".join(f"`{name}`" for name in derivation["charter_out_of_track_macros"]),
            "",
        ]
    )
    if payload["unlabeled_occurrences"]:
        lines.extend(["## Occurrences non etiquetees", ""])
        for row in payload["unlabeled_occurrences"]:
            lines.append(f"- `{row['source_path']}` ligne {row['line']}")
        lines.append("")
    else:
        lines.extend(
            [
                "Aucune occurrence publiee de niveau etranger hors extension "
                "optionnelle declaree ou hors renvoi de niveau explicite.",
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
        count = payload["summary"]["UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT"]
        print(f"UNLABELED_WRONG_LEVEL_TERMINALE_CONTENT={count}")
        return 0 if count == 0 else 1
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {relative(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
