#!/usr/bin/env python3
"""Reject scaffold language in student-facing supports."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import unicodedata

from scripts._qa_common import ROOT, read_frontmatter


@dataclass
class StudentScaffoldResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


FORBIDDEN_PHRASES = [
    "réponse structurée en donnée, méthode, résultat et contrôle",
    "un pair peut vérifier",
    "comparer la réponse avec la donnée de départ",
    "créer une nouvelle donnée de test",
    "résultat indicatif",
    "conclusion compatible",
]

TEACHER_OR_INTERNAL_MARKERS = {
    "guide",
    "professeur",
    "corrige",
    "corrigé",
    "bareme",
    "barème",
    "contract",
    "contrat",
    "modele",
    "modèle",
}

SKIPPED_DOCUMENT_TYPES = {
    "guide_professeur",
    "corrige",
    "bareme",
    "contract",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value).strip()


def is_student_facing(path: Path) -> bool:
    name = normalize(path.name)
    if any(marker in name for marker in TEACHER_OR_INTERNAL_MARKERS):
        return False
    metadata = read_frontmatter(path)
    document_type = normalize(str(metadata.get("document_type") or ""))
    if document_type in SKIPPED_DOCUMENT_TYPES:
        return False
    return True


def target_files(root: Path = ROOT) -> list[Path]:
    bases = [
        root / "03_progressions" / "supports",
        root / "03_progressions" / "fiches_cours",
        root / "premiere" / "sequences",
        root / "terminale" / "sequences",
    ]
    files: list[Path] = []
    for base in bases:
        if base.exists():
            files.extend(path for path in sorted(base.rglob("*.md")) if is_student_facing(path))
    return files


def analyze_student_supports_no_scaffold_language(root: Path = ROOT, files: list[Path] | None = None) -> StudentScaffoldResult:
    result = StudentScaffoldResult()
    paths = files if files is not None else target_files(root)
    normalized_forbidden = [(phrase, normalize(phrase)) for phrase in FORBIDDEN_PHRASES]
    for path in paths:
        result.checked_files += 1
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            normalized_line = normalize(line)
            for phrase, normalized_phrase in normalized_forbidden:
                if normalized_phrase in normalized_line:
                    result.errors.append(f"{rel}:{lineno}: langage gabarit interdit -> {phrase}")
    return result


def main() -> int:
    result = analyze_student_supports_no_scaffold_language()
    if result.errors:
        print("check_student_supports_no_scaffold_language: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_student_supports_no_scaffold_language: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
