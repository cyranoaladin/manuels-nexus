#!/usr/bin/env python3
"""LEGACY — conservé pour le pilote s01 ; le kit pdflatex est canonique
pour les nouvelles séquences (voir docs/latex_systems_decision.md).

Render a sequence directory into two chartered PDFs (student + teacher).

Usage:
    python scripts/render_sequence.py premiere/sequences/s01_representation_donnees

Requires: pandoc, xelatex (texlive-xetex).

Charter colours: #102A43 (dark blue), #1A75BC (accent blue), #F4B400 (gold).
Fonts: Merriweather for headings, Lato for body, Fira Code for code blocks.
Falls back to DejaVu Serif / Lato / DejaVu Sans Mono if charter fonts are
not installed.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --- Configuration -----------------------------------------------------------

# Charter colours
DARK_BLUE = "102A43"
ACCENT_BLUE = "1A75BC"
GOLD = "F4B400"

# Font detection: prefer charter fonts, fall back to system fonts
def _font_available(name: str) -> bool:
    result = subprocess.run(
        ["fc-list", f":family={name}"],
        capture_output=True, text=True,
    )
    return bool(result.stdout.strip())

HEADING_FONT = "Merriweather" if _font_available("Merriweather") else "DejaVu Serif"
BODY_FONT = "Lato" if _font_available("Lato") else "DejaVu Sans"
MONO_FONT = "Fira Code" if _font_available("Fira Code") else "DejaVu Sans Mono"

# Documents for student version (no corrections, no teacher material)
STUDENT_DOCS = [
    "cours_eleve.md",
    "trace_ecrite.md",
    "td.md",
    "tp.md",
    "fiche_methode.md",
    "aides_progressives.md",
    "evaluation.md",
]

# Documents for teacher version (everything)
TEACHER_DOCS = [
    "cours_eleve.md",
    "trace_ecrite.md",
    "td.md",
    "tp.md",
    "fiche_methode.md",
    "aides_progressives.md",
    "evaluation.md",
    "corrige.md",
    "corrige_professeur.md",
    "guide_professeur.md",
    "bareme.md",
    "grille_competences.md",
]

# LaTeX header template for XeLaTeX with charter styling
HEADER_TEMPLATE = r"""
\usepackage{{fontspec}}
\setmainfont{{{body_font}}}
\setsansfont{{{body_font}}}
\setmonofont{{{mono_font}}}
\usepackage{{xcolor}}
\definecolor{{nsi-dark}}{{HTML}}{{{dark}}}
\definecolor{{nsi-accent}}{{HTML}}{{{accent}}}
\definecolor{{nsi-gold}}{{HTML}}{{{gold}}}
\usepackage{{sectsty}}
\allsectionsfont{{\fontspec{{{heading_font}}}\color{{nsi-dark}}}}
\usepackage{{fancyhdr}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\fontspec{{{heading_font}}}\small\color{{nsi-accent}}NSI Première — Tunisie 2026-2027}}
\fancyhead[R]{{\small\thepage}}
\fancyfoot[C]{{\footnotesize\color{{nsi-dark}}Prototype pédagogique — ne pas diffuser}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\usepackage{{hyperref}}
\hypersetup{{colorlinks=true,linkcolor=nsi-accent,urlcolor=nsi-accent}}
"""


def strip_yaml_frontmatter(text: str) -> str:
    """Remove YAML frontmatter delimited by --- from markdown text."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end < 0:
        return text
    return text[end + 4:].lstrip("\n")


def build_combined_md(seq_dir: Path, doc_list: list[str]) -> str:
    """Concatenate markdown files, stripping frontmatter, with page breaks."""
    parts: list[str] = []
    for doc_name in doc_list:
        doc_path = seq_dir / doc_name
        if not doc_path.exists():
            print(f"WARNING: {doc_name} not found, skipping")
            continue
        content = doc_path.read_text(encoding="utf-8", errors="replace")
        content = strip_yaml_frontmatter(content)
        parts.append(content)
    return "\n\n\\newpage\n\n".join(parts)


def render_pdf(combined_md: str, output_path: Path, title: str) -> None:
    """Render combined markdown to PDF via pandoc + xelatex."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as md_file:
        md_file.write(combined_md)
        md_path = Path(md_file.name)

    header_content = HEADER_TEMPLATE.format(
        body_font=BODY_FONT,
        heading_font=HEADING_FONT,
        mono_font=MONO_FONT,
        dark=DARK_BLUE,
        accent=ACCENT_BLUE,
        gold=GOLD,
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".tex", delete=False, encoding="utf-8"
    ) as hdr_file:
        hdr_file.write(header_content)
        hdr_path = Path(hdr_file.name)

    cmd = [
        "pandoc",
        str(md_path),
        "-o", str(output_path),
        "--pdf-engine=xelatex",
        f"--include-in-header={hdr_path}",
        f"--metadata=title:{title}",
        "--variable=geometry:margin=2.5cm",
        "--variable=fontsize:11pt",
        "--highlight-style=tango",
        "--table-of-contents",
        "--toc-depth=2",
    ]

    print(f"Rendering {output_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    md_path.unlink(missing_ok=True)
    hdr_path.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"ERROR rendering {output_path.name}:")
        print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        raise SystemExit(1)

    size_kb = output_path.stat().st_size / 1024
    print(f"  -> {output_path} ({size_kb:.0f} KB)")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/render_sequence.py <sequence_directory>")
        raise SystemExit(1)

    seq_dir = Path(sys.argv[1])
    if not seq_dir.is_dir():
        print(f"ERROR: {seq_dir} is not a directory")
        raise SystemExit(1)

    # Check dependencies
    for tool in ["pandoc", "xelatex"]:
        if not shutil.which(tool):
            print(f"ERROR: {tool} not found. Install pandoc and texlive-xetex.")
            raise SystemExit(1)

    dist_dir = seq_dir / "dist"

    print(f"Using fonts: headings={HEADING_FONT}, body={BODY_FONT}, code={MONO_FONT}")
    print()

    # Student version
    student_md = build_combined_md(seq_dir, STUDENT_DOCS)
    render_pdf(
        student_md,
        dist_dir / "version_eleve.pdf",
        "S01 — Représenter des données (version élève)",
    )

    # Teacher version
    teacher_md = build_combined_md(seq_dir, TEACHER_DOCS)
    render_pdf(
        teacher_md,
        dist_dir / "version_prof.pdf",
        "S01 — Représenter des données (version professeur)",
    )

    # Verification: check student PDF does not contain correction keywords
    print()
    print("Verification:")
    student_path = dist_dir / "version_eleve.pdf"
    teacher_path = dist_dir / "version_prof.pdf"

    if student_path.exists() and teacher_path.exists():
        print(f"  version_eleve.pdf: {student_path.stat().st_size / 1024:.0f} KB")
        print(f"  version_prof.pdf:  {teacher_path.stat().st_size / 1024:.0f} KB")

        # Quick text extraction to verify no correction in student version
        check = subprocess.run(
            ["pandoc", str(dist_dir / "version_eleve.pdf"), "-t", "plain"],
            capture_output=True, text=True,
        )
        # If pandoc can't read PDF, just skip the check
        if check.returncode == 0:
            text = check.stdout.lower()
            if "corrigé professeur" in text:
                print("  WARNING: student PDF may contain teacher corrections!")
            else:
                print("  Student PDF does not contain teacher corrections. OK")
        else:
            # Verify by doc list: no corrige files in student docs
            for doc in STUDENT_DOCS:
                if "corrige" in doc or "professeur" in doc:
                    print(f"  WARNING: {doc} should not be in student version!")
                    raise SystemExit(1)
            print("  Student doc list verified: no correction documents included. OK")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
