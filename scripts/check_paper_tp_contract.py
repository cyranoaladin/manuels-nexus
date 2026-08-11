#!/usr/bin/env python3
"""Validate explicit contracts for paper TP resources."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter


@dataclass
class PaperTPResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


REQUIRED_TEXT = [
    "TP papier",
    "Barème associé",
    "Corrigé question par question",
    "aucune ressource Python",
]


def candidate_files(root: Path) -> list[Path]:
    base = root / "03_progressions" / "supports"
    if not base.exists():
        return []
    files: list[Path] = []
    for path in sorted(base.rglob("*.md")):
        metadata = read_frontmatter(path)
        document_type = str(metadata.get("document_type", ""))
        if str(metadata.get("tp_mode", "")).lower() == "papier" or document_type == "tp_papier":
            files.append(path)
    return sorted(files)


def analyze_paper_tp_contract(root: Path = ROOT) -> PaperTPResult:
    result = PaperTPResult()
    for path in candidate_files(root):
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        metadata = read_frontmatter(path)
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        document_type = str(metadata.get("document_type", ""))
        tp_mode = str(metadata.get("tp_mode", "")).lower()
        if document_type not in {"trace", "tp_papier", "tp"}:
            result.errors.append(f"{rel}: document_type incompatible avec TP papier -> {document_type}")
        if document_type != "tp_papier" and tp_mode != "papier":
            result.errors.append(f"{rel}: tp_mode: papier ou document_type: tp_papier requis")
        for token in REQUIRED_TEXT:
            if token not in text:
                result.errors.append(f"{rel}: élément obligatoire de TP papier absent -> {token}")
        match = re.match(r"([PT]\d{2})_", path.name)
        sequence = match.group(1) if match else str(metadata.get("sequence_id", ""))
        if sequence:
            if f"{sequence}_TD_" not in text:
                result.errors.append(f"{rel}: lien TD de la séquence absent")
            if f"{sequence}_evaluation_" not in text:
                result.errors.append(f"{rel}: lien évaluation de la séquence absent")
        if sequence == "T18" and not re.search(r"table (du )?mauvais caract", text, flags=re.I):
            result.errors.append(f"{rel}: table de trace disciplinaire absente")
        code_dir = path.parent / "code"
        if code_dir.exists() and any(code_dir.glob("*boyer_moore*.py")):
            result.errors.append(f"{rel}: TP papier déclaré mais assets Python Boyer-Moore présents")
    return result


def main() -> int:
    result = analyze_paper_tp_contract()
    if result.errors:
        print("check_paper_tp_contract: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_paper_tp_contract: PASS ({result.checked_files} TP papier)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
