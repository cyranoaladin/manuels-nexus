#!/usr/bin/env python3
"""Render one canonical support unit into student/teacher HTML and lightweight PDFs."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from scripts._qa_common import ROOT, strip_frontmatter


CHARTER = "CHARTE_NSI_CORPUS_NEEDS_REVIEW"
TEACHER_TOKENS = ("corrige", "corrigé", "bareme", "barème", "professeur")
TEACHER_SECTION_PATTERNS = (
    re.compile(r"\brep[èe]res?\s+(?:enseignant|professeur)\b", re.I),
    re.compile(r"\bpour\s+l[’']?(?:enseignant|professeur)\b", re.I),
    re.compile(r"\bnotes?\s+(?:enseignant|professeur)\b", re.I),
    re.compile(r"\bindications?\s+(?:enseignant|professeur)\b", re.I),
    re.compile(r"\b[àa]\s+masquer\s+dans\s+la\s+projection\s+[ée]l[èe]ve\b", re.I),
    re.compile(r"\bcorrection\b|\bcorrig[ée]s?\b", re.I),
    re.compile(r"\bbar[èe]me\s+correcteur\b", re.I),
    re.compile(r"\bsolutions?\b", re.I),
    re.compile(r"\br[ée]ponses?\s+attendues?\b", re.I),
    re.compile(r"\b[ée]l[ée]ments?\s+de\s+correction\b", re.I),
    re.compile(r"\br[ée]ponses?\s+rapides?\b", re.I),
    re.compile(r"\br[ée]ponses?\s+de\s+r[ée]f[ée]rence\b", re.I),
    re.compile(r"\br[ée]sultats?\s+attendus?\b", re.I),
)
INLINE_TEACHER_RESOURCE = re.compile(
    r"\b(?:corrig[ée]\s+(?:professeur|distribu[ée])|corrige_professeur|"
    r"bar[èe]me\s+correcteur|r[ée]ponses?\s+attendues?|"
    r"[ée]l[ée]ments?\s+de\s+correction)\b",
    re.I,
)
DIRECT_STUDENT_ANSWER = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:r[ée]sultat\s+(?:final|de\s+r[ée]f[ée]rence)|"
    r"r[ée]ponse\s+attendue|livrable\s+pr[ée]rempli)\s*:\s*"
    r"(?!(?:à\s+(?:d[ée]terminer|compl[ée]ter)|v[ée]rifier|[ée]crire|produire|justifier)\b).+",
)


def level_for(unit: str) -> str:
    return "premiere" if unit.startswith("P") else "terminale"


def support_dir(unit: str) -> Path:
    return ROOT / "03_progressions" / "supports" / level_for(unit) / unit


def markdown_files(unit: str, teacher: bool) -> list[Path]:
    base = support_dir(unit)
    files = sorted(base.glob(f"{unit}_*.md"))
    selected: list[Path] = []
    for path in files:
        lower = path.name.lower()
        is_teacher = any(token in lower for token in TEACHER_TOKENS)
        if teacher or not is_teacher:
            selected.append(path)
    return selected


def md_to_html(text: str) -> str:
    lines: list[str] = []
    in_list = False
    for raw in strip_frontmatter(text).splitlines():
        line = raw.rstrip()
        if not line:
            if in_list:
                lines.append("</ul>")
                in_list = False
            continue
        if line.startswith("#"):
            if in_list:
                lines.append("</ul>")
                in_list = False
            level = min(len(line) - len(line.lstrip("#")), 4)
            title = html.escape(line.lstrip("#").strip())
            lines.append(f"<h{level}>{title}</h{level}>")
        elif line.startswith("- "):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            lines.append(f"<li>{html.escape(line[2:].strip())}</li>")
        else:
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        lines.append("</ul>")
    return "\n".join(lines)


def is_teacher_section_title(title: str) -> bool:
    """Identify an explicitly teacher-only Markdown heading.

    This deliberately evaluates headings only: a student scenario may legitimately
    say that a teacher wants a result, without exposing a correction resource.
    """
    return any(pattern.search(title) for pattern in TEACHER_SECTION_PATTERNS)


def strip_teacher_sections(markdown: str) -> str:
    lines = strip_frontmatter(markdown).splitlines()
    kept: list[str] = []
    skip = False
    skip_level = 0
    for line in lines:
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            if skip and level <= skip_level:
                skip = False
            if is_teacher_section_title(title):
                skip = True
                skip_level = level
                continue
        if not skip:
            if INLINE_TEACHER_RESOURCE.search(line):
                continue
            if DIRECT_STUDENT_ANSWER.match(line):
                continue
            kept.append(line)
    return "\n".join(kept)


def build_html(unit: str, teacher: bool) -> str:
    role = "prof" if teacher else "élève"
    body: list[str] = [
        "<!doctype html>",
        "<html lang=\"fr\"><meta charset=\"utf-8\">",
        f"<title>{unit} - version {html.escape(role)}</title>",
        "<style>body{font-family:Arial,sans-serif;margin:2rem;line-height:1.45}"
        "header{border-bottom:4px solid #1A75BC;margin-bottom:1rem}"
        "h1,h2,h3{color:#102A43}.marker{color:#1A75BC;font-weight:bold}</style>",
        f"<header><p class=\"marker\">{CHARTER}</p><h1>{unit} - version {html.escape(role)}</h1>"
        "<p>Prototype pédagogique - statut needs_review</p></header>",
    ]
    for path in markdown_files(unit, teacher):
        body.append(f"<section data-source=\"{path.relative_to(ROOT).as_posix()}\">")
        markdown = path.read_text(encoding="utf-8", errors="replace")
        if not teacher:
            markdown = strip_teacher_sections(markdown)
        body.append(md_to_html(markdown))
        body.append("</section>")
    body.append("</html>")
    return "\n".join(body)


def minimal_pdf(path: Path, title: str, text: str) -> None:
    """Write a small valid-enough PDF with one text stream for audit artifacts."""
    safe = re.sub(r"[^A-Za-z0-9 _.,:;()/=-]", " ", f"{title}\n{CHARTER}\n{text[:1200]}")
    stream = "BT /F1 10 Tf 50 780 Td " + " Tj 0 -14 Td ".join(
        f"({line[:90].replace('(', '[').replace(')', ']')})" for line in safe.splitlines()[:45]
    ) + " ET"
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(stream.encode('latin-1', errors='ignore'))} >> stream\n{stream}\nendstream endobj\n",
    ]
    output = ["%PDF-1.4\n"]
    offsets = [0]
    for obj in objects:
        offsets.append(sum(len(part.encode("latin-1", errors="ignore")) for part in output))
        output.append(obj)
    xref_offset = sum(len(part.encode("latin-1", errors="ignore")) for part in output)
    output.append(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.append(f"{offset:010d} 00000 n \n")
    output.append(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n")
    path.write_bytes("".join(output).encode("latin-1", errors="ignore"))


def render(unit: str, output_root: Path) -> Path:
    base = support_dir(unit)
    if not base.is_dir():
        raise SystemExit(f"unité introuvable : {unit}")
    out = output_root / unit
    out.mkdir(parents=True, exist_ok=True)
    for teacher, suffix in [(False, "eleve"), (True, "prof")]:
        html_text = build_html(unit, teacher)
        html_path = out / f"{unit}_{suffix}.html"
        pdf_path = out / f"{unit}_{suffix}.pdf"
        html_path.write_text(html_text, encoding="utf-8")
        minimal_pdf(pdf_path, f"{unit} version {suffix}", html_text)
    print(f"render_unit: {unit} -> {out}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT / "dist" / "rendered_units")
    args = parser.parse_args()
    render(args.unit, args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
