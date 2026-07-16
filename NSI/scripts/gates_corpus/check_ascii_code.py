#!/usr/bin/env python3
"""Gate : le code du corpus n'emploie pas de ponctuation typographique.

Seuls les environnements ``python``, ``console`` et ``codereference``, ainsi
que ``\\lstinline``, sont controles. La typographie française du prose reste
hors perimetre.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCAN_PATHS = (ROOT / "chapitres", ROOT / "gabarits" / "specimen.tex")
FORBIDDEN_CHARACTERS = ("‘", "’", "“", "”", "«", "»", "—")
FORBIDDEN_SET = frozenset(FORBIDDEN_CHARACTERS)

ENVIRONMENT_BEGIN_RE = re.compile(
    r"\\begin\{(?P<context>python|console|codereference)\}", re.IGNORECASE
)


@dataclass(frozen=True)
class AsciiViolation:
    context: str
    character: str
    line: int
    column: int


def _position(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    previous_newline = text.rfind("\n", 0, offset)
    return line, offset - previous_newline


def _balanced_brace_end(text: str, start: int) -> int | None:
    """Retourne l'indice apres une argument TeX equilibre ou ``None``."""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 1
    cursor = start + 1
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] == "{":
            depth += 1
        elif text[cursor] == "}":
            depth -= 1
            if depth == 0:
                return cursor + 1
        cursor += 1
    return None


def _parse_lstinline_at(text: str, start: int) -> tuple[int, int, int] | None:
    """Retourne corps/debut suivant pour un ``\\lstinline`` reel a ``start``."""
    command = r"\lstinline"
    if not text.startswith(command, start):
        return None
    cursor = start + len(command)
    if cursor < len(text) and text[cursor].isalpha():
        return None
    while cursor < len(text) and text[cursor] in " \t":
        cursor += 1
    if cursor < len(text) and text[cursor] == "[":
        option_end = text.find("]", cursor + 1)
        if option_end == -1:
            return None
        cursor = option_end + 1
    while cursor < len(text) and text[cursor] in " \t":
        cursor += 1
    if cursor >= len(text):
        return None
    if text[cursor] == "{":
        end = _balanced_brace_end(text, cursor)
        if end is None:
            return None
        return cursor + 1, end - 1, end
    delimiter = text[cursor]
    if delimiter.isspace() or delimiter.isalpha() or delimiter in "{}":
        return None
    body_start = cursor + 1
    cursor = body_start
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] == delimiter:
            return body_start, cursor, cursor + 1
        cursor += 1
    return None


def _parse_environment_at(text: str, start: int) -> tuple[str, int, int, int] | None:
    """Retourne contexte/corps/suivant pour un environnement de code reel."""
    match = ENVIRONMENT_BEGIN_RE.match(text, start)
    if match is None:
        return None
    context = match.group("context").lower()
    body_start = match.end()
    if context == "codereference" and body_start < len(text) and text[body_start] == "{":
        title_end = _balanced_brace_end(text, body_start)
        if title_end is None:
            return None
        body_start = title_end
    end_re = re.compile(rf"\\end\{{{re.escape(context)}\}}", re.IGNORECASE)
    end_match = end_re.search(text, body_start)
    if end_match is None:
        return None
    return context, body_start, end_match.start(), end_match.end()


def _find_in_span(text: str, start: int, end: int, context: str) -> list[AsciiViolation]:
    violations: list[AsciiViolation] = []
    for offset in range(start, end):
        character = text[offset]
        if character not in FORBIDDEN_SET:
            continue
        line, column = _position(text, offset)
        violations.append(AsciiViolation(context, character, line, column))
    return violations


def _is_comment_start(text: str, index: int) -> bool:
    """Indique si ``%`` introduit un commentaire LaTeX a cette position."""
    if text[index] != "%":
        return False
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 0


def find_violations(text: str) -> list[AsciiViolation]:
    """Liste la ponctuation interdite dans les seuls contextes de code."""
    violations: list[AsciiViolation] = []
    cursor = 0
    while cursor < len(text):
        if text[cursor] == "%" and _is_comment_start(text, cursor):
            line_end = text.find("\n", cursor)
            cursor = len(text) if line_end == -1 else line_end + 1
            continue
        inline = _parse_lstinline_at(text, cursor)
        if inline is not None:
            body_start, body_end, cursor = inline
            violations.extend(_find_in_span(text, body_start, body_end, "lstinline"))
            continue
        environment = _parse_environment_at(text, cursor)
        if environment is not None:
            context, body_start, body_end, cursor = environment
            violations.extend(_find_in_span(text, body_start, body_end, context))
            continue
        cursor += 1
    return sorted(violations, key=lambda hit: (hit.line, hit.column, hit.context))


def iter_tex_sources() -> list[Path]:
    """Retourne le corpus et le specimen imposes par la charte."""
    sources: list[Path] = []
    chapters = SCAN_PATHS[0]
    if chapters.exists():
        sources.extend(sorted(chapters.rglob("*.tex")))
    specimen = SCAN_PATHS[1]
    if specimen.exists():
        sources.append(specimen)
    return sources


def main() -> int:
    errors: list[str] = []
    checked = 0
    for path in iter_tex_sources():
        checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for hit in find_violations(text):
            errors.append(
                f"  {path.relative_to(ROOT)}:{hit.line}:{hit.column}: "
                f"{hit.context} contient U+{ord(hit.character):04X} ({hit.character!r})"
            )

    if errors:
        print("ROUGE -- ponctuation typographique detectee dans le code :")
        for error in errors:
            print(error)
        return 1

    print(f"VERT -- code ASCII verifie dans {checked} fichiers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
