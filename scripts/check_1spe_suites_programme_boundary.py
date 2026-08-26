#!/usr/bin/env python3
"""Check all 1SPE-SUITES TeX sources for rendered Terminale-only reasoning."""

from __future__ import annotations

import re
from bisect import bisect_right
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"
CANONICAL_P0_RELATIVE_PATHS = (
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-026.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-026.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-027.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-031.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-031.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-037.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-038.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-038.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-040.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-040.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-042.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-042.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-043.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-043.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-044.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-046.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-048.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-048.tex"),
    Path("Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-049.tex"),
)
CANONICAL_P0_PATHS = tuple(ROOT / path for path in CANONICAL_P0_RELATIVE_PATHS)

LOG_TOKEN = (
    r"(?:(?<!O\()\\(?:log|ln)(?![A-Za-z])|\blogarithm(?:e|ique)?s?\b)"
)
SOLVING_CONTEXT = (
    r"(?:résoud\w*|résolution|appliqu\w*|utilis\w*|calcul\w*|détermin\w*|"
    r"rang|inéquation|équation|deux membres|division|passage)"
)

FORMAL_IMPLICATION_PATTERNS = (
    re.compile(
        r"(?:(?:croissante|décroissante|monotone).{0,180}"
        r"(?:majorée|minorée|bornée)|(?:majorée|minorée|bornée).{0,180}"
        r"(?:croissante|décroissante|monotone))"
        r".{0,100}(?:donc|ainsi|par conséquent).{0,100}"
        r"(?:converg\w*|admet une limite)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bune suite.{0,40}"
        r"(?:(?:croissante|décroissante|monotone).{0,80}"
        r"(?:majorée|minorée|bornée)|(?:majorée|minorée|bornée).{0,80}"
        r"(?:croissante|décroissante|monotone))"
        r".{0,80}(?:converg\w*|admet une limite)",
        re.IGNORECASE,
    ),
    re.compile(r"théorème.{0,100}(?:convergence|converg\w*)", re.IGNORECASE),
)

SEQUENCE_SUBJECT = (
    r"(?:la suite|elle|\$[^$]+\$|[A-Za-z][A-Za-z0-9]*_\{?n\}?)"
)
FORMAL_DIRECT_ASSERTION_PATTERNS = (
    re.compile(
        rf"{SEQUENCE_SUBJECT}\s+(?:"
        r"(?:semble\s+)?converg\w*(?:\s+vers)?|"
        r"est\s+converg\w*(?:\s+vers)?|"
        r"(?:semble\s+)?tend\w*\s+vers)\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"{SEQUENCE_SUBJECT}\s+(?:semble\s+)?"
        r"admet\s+(?:une limite|pour limite)\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"la limite de\s+{SEQUENCE_SUBJECT}\s+est\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"{SEQUENCE_SUBJECT}\s+(?:semble\s+)?a pour limite\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"{SEQUENCE_SUBJECT}\s+(?:possède|a)\s+une limite\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"(?:on\s+prouve|on\s+démontre|on\s+établit)\s+que\s+"
        rf"{SEQUENCE_SUBJECT}\s+se rapproche\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"(?:on\s+)?(?:prouve|démontre|établit)\s+"
        rf"(?:la\s+)?convergence\s+de\s+{SEQUENCE_SUBJECT}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\$[A-Za-z][A-Za-z0-9]*_\{?n\}?\s*"
        r"\\(?:to|longrightarrow)\s*[^$]+\$",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:on en déduit|on obtient).{0,80}\bla limite\s+(?:est|vaut)\b",
        re.IGNORECASE,
    ),
)

FORBIDDEN_PATTERNS = {
    "LOGARITHM_SOLVING_METHOD": (
        re.compile(rf"{SOLVING_CONTEXT}.{{0,180}}{LOG_TOKEN}", re.IGNORECASE),
        re.compile(rf"{LOG_TOKEN}.{{0,180}}{SOLVING_CONTEXT}", re.IGNORECASE),
    ),
    "FORMAL_CONVERGENCE_THEOREM": (
        *FORMAL_IMPLICATION_PATTERNS,
        *FORMAL_DIRECT_ASSERTION_PATTERNS,
    ),
    "FORMAL_LIMIT_NOTATION": (
        re.compile(r"\\lim(?![A-Za-z])|\\operatorname\s*\{\s*lim\s*\}", re.IGNORECASE),
    ),
    "FORMAL_PASSAGE_TO_LIMIT": (
        re.compile(
            r"(?:en passant|passons|passage).{0,80}à la limite",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:en faisant tendre|on fait tendre).{0,80}vers",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:on\s+)?(?:prend|prendre|prenons)\s+la limite\s+"
            r"(?:dans|des deux membres|de chaque membre)\b",
            re.IGNORECASE,
        ),
    ),
    "LATER_THEORY_SCOPE": (
        re.compile(
            r"étudi\w*.{0,80}propriétés\s*\([^)]*"
            r"\bconvergence\b[^)]*\blimite\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:relève|réserv\w*)\s+(?:de|des)\s+classes préparatoires",
            re.IGNORECASE,
        ),
    ),
}

INLINE_FORMATTING_PATTERN = re.compile(
    r"\\(?:textbf|textit|emph)\s*\{([^{}]*)\}",
)

DIRECT_CONJECTURE_PREFIX = re.compile(
    r"(?:on|(?:un|une|l['’])\s+[\w-]+)\s+conjecture\s+que\s*$"
    r"|conjecturer\s+que\s*$",
    re.IGNORECASE,
)
EXPLICIT_NEGATION_PREFIX = re.compile(
    r"\bn['’][\w-]+\s+(?:aucun|ni)\b[^.!?;:]{0,120}$",
    re.IGNORECASE,
)


def _is_directly_conjectural(source: str, match: re.Match[str]) -> bool:
    if re.search(r"\bsemble\b", match.group(), re.IGNORECASE):
        return True
    return DIRECT_CONJECTURE_PREFIX.search(source[: match.start()]) is not None


def _is_explicitly_negated(source: str, match: re.Match[str]) -> bool:
    return EXPLICIT_NEGATION_PREFIX.search(source[: match.start()]) is not None


def _strip_comment(line: str) -> str:
    for index, character in enumerate(line):
        if character != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index]
    return line


def strip_non_rendered_comments(source: str) -> str:
    """Remove LaTeX comments while preserving escaped percentage signs."""

    return "\n".join(_strip_comment(line) for line in source.splitlines())


def normalize_inline_formatting(source: str) -> str:
    """Unwrap simple inline emphasis without changing rendered wording."""

    normalized = source
    while True:
        updated, replacements = INLINE_FORMATTING_PATTERN.subn(r"\1", normalized)
        if replacements == 0:
            return normalized
        normalized = updated


def scan_text(source: str, *, path: str = "<memory>") -> list[dict[str, object]]:
    """Return deterministic programme-boundary findings for rendered text."""

    findings: list[dict[str, object]] = []
    rendered = normalize_inline_formatting(strip_non_rendered_comments(source))
    fragments: list[str] = []
    fragment_lines: list[int] = []
    for line_number, line in enumerate(rendered.splitlines(), start=1):
        normalized = " ".join(line.split())
        if normalized:
            fragments.append(normalized)
            fragment_lines.append(line_number)

    starts: list[int] = []
    offset = 0
    for fragment in fragments:
        starts.append(offset)
        offset += len(fragment) + 1
    normalized_source = " ".join(fragments)
    seen_spans: dict[str, list[tuple[int, int]]] = {}
    for code, patterns in FORBIDDEN_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(normalized_source):
                if (
                    code == "FORMAL_CONVERGENCE_THEOREM"
                    and match.group().casefold().startswith("théorème")
                    and _is_explicitly_negated(normalized_source, match)
                ):
                    continue
                if (
                    code == "FORMAL_CONVERGENCE_THEOREM"
                    and pattern in FORMAL_DIRECT_ASSERTION_PATTERNS
                    and _is_directly_conjectural(normalized_source, match)
                ):
                    continue
                start, end = match.span()
                if any(
                    start < previous_end and previous_start < end
                    for previous_start, previous_end in seen_spans.get(code, [])
                ):
                    continue
                seen_spans.setdefault(code, []).append((start, end))
                fragment_index = max(0, bisect_right(starts, match.start()) - 1)
                line_number = fragment_lines[fragment_index]
                excerpt_start = max(0, match.start() - 60)
                excerpt_end = min(len(normalized_source), match.end() + 60)
                findings.append(
                    {
                        "path": path,
                        "line": line_number,
                        "code": code,
                        "excerpt": normalized_source[excerpt_start:excerpt_end][:240],
                    }
                )
    return sorted(
        findings,
        key=lambda finding: (
            str(finding["path"]),
            int(finding["line"]),
            str(finding["code"]),
        ),
    )


def scan_paths(paths: Iterable[Path]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in sorted((Path(item) for item in paths), key=lambda item: str(item)):
        try:
            relative = str(path.resolve().relative_to(ROOT.resolve()))
        except ValueError:
            relative = str(path)
        if not path.is_file():
            findings.append(
                {
                    "path": relative,
                    "line": 0,
                    "code": "SOURCE_MISSING",
                    "excerpt": "canonical pilot source is missing",
                }
            )
            continue
        findings.extend(scan_text(path.read_text(encoding="utf-8"), path=relative))
    return sorted(
        findings,
        key=lambda finding: (
            str(finding["path"]),
            int(finding["line"]),
            str(finding["code"]),
        ),
    )


def validated_canonical_p0_paths() -> tuple[Path, ...]:
    expected = tuple((ROOT / path).resolve() for path in CANONICAL_P0_RELATIVE_PATHS)
    actual = tuple(Path(path).resolve() for path in CANONICAL_P0_PATHS)
    if actual != expected:
        raise ValueError("canonical P0 scope mismatch")
    return tuple(Path(path) for path in CANONICAL_P0_PATHS)


def scan_canonical_p0_scope() -> list[dict[str, object]]:
    return scan_paths(validated_canonical_p0_paths())


def canonical_chapter_tex_paths() -> tuple[Path, ...]:
    if not CHAPTER.is_dir():
        raise ValueError(f"canonical chapter directory is missing: {CHAPTER}")
    paths = tuple(sorted(CHAPTER.rglob("*.tex"), key=lambda path: str(path)))
    if not paths:
        raise ValueError(f"canonical chapter has no TeX sources: {CHAPTER}")
    return paths


def _complete_chapter_scan_paths(
    p0_paths: Iterable[Path], chapter_paths: Iterable[Path]
) -> tuple[Path, ...]:
    chapter = tuple(Path(path) for path in chapter_paths)
    observed = {path.resolve() for path in chapter}
    missing_p0 = tuple(
        Path(path) for path in p0_paths if Path(path).resolve() not in observed
    )
    return (*chapter, *missing_p0)


def scan_canonical_chapter_scope() -> list[dict[str, object]]:
    p0_paths = validated_canonical_p0_paths()
    chapter_paths = canonical_chapter_tex_paths()
    return scan_paths(_complete_chapter_scan_paths(p0_paths, chapter_paths))


def main() -> int:
    p0_paths = validated_canonical_p0_paths()
    chapter_paths = canonical_chapter_tex_paths()
    findings = scan_paths(_complete_chapter_scan_paths(p0_paths, chapter_paths))
    if findings:
        for finding in findings:
            print(
                f"{finding['code']}: {finding['path']}:{finding['line']}: "
                f"{finding['excerpt']}"
            )
        print(f"FAIL: {len(findings)} rendered programme-boundary finding(s)")
        return 1
    print(
        "PASS: 1SPE-SUITES programme boundary clean "
        f"({len(p0_paths)} P0 files; {len(chapter_paths)} chapter TeX files)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
