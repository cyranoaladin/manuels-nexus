#!/usr/bin/env python3
"""Audit paper TP contracts and report paper/executable TP balance."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter, sequence_id_from_path, strip_frontmatter


@dataclass
class PaperTPResult:
    errors: list[str] = field(default_factory=list)
    paper_count: int = 0
    executable_count: int = 0
    preferable_executable: list[str] = field(default_factory=list)


def is_paper_tp(path: Path, text: str) -> bool:
    metadata = read_frontmatter(path)
    return (
        str(metadata.get("document_type", "")).lower() == "tp_papier"
        or str(metadata.get("tp_mode", "")).lower() == "papier"
        or "TP papier" in text
    )


def has_python_assets(path: Path) -> bool:
    sequence = sequence_id_from_path(path)
    code_dir = path.parent / "code"
    return code_dir.exists() and any(code_dir.glob(f"{sequence}_*.py"))


def sibling_exists(path: Path, token: str) -> bool:
    sequence = sequence_id_from_path(path)
    return any(path.parent.glob(f"{sequence}_*{token}*.md"))


def paper_tp_errors(text: str, rel: str) -> list[str]:
    body = strip_frontmatter(text)
    lowered = body.lower()
    errors: list[str] = []
    if not re.search(r"tp papier|aucune ressource python|non exécutable|non executable|trace écrite|trace ecrite", lowered):
        errors.append(f"{rel}: justification du mode papier absente")
    if not re.search(r"table de trace|trace|pseudo-code|pseudocode|alignement|étape|etape", lowered):
        errors.append(f"{rel}: table de trace ou activité papier vérifiable absente")
    if "corrigé question par question" not in lowered and not re.search(r"###\s+Corrigé question\s+\d+", body, re.I):
        errors.append(f"{rel}: corrigé question par question absent")
    if "barème" not in lowered and "bareme" not in lowered:
        errors.append(f"{rel}: barème associé absent")
    if not re.search(r"version aménagée|version amenagee|aménagement|amenagement|aide", lowered):
        errors.append(f"{rel}: version aménagée ou aménagement non mentionné")
    if not re.search(r"livrable|à rendre|a rendre|production attendue|trace écrite", lowered):
        errors.append(f"{rel}: livrable classe non explicite")
    return errors


def analyze_paper_tp_justification(root: Path = ROOT) -> PaperTPResult:
    result = PaperTPResult()
    for path in sorted((root / "03_progressions" / "supports").rglob("*.md")):
        if "_tp_" not in path.name.lower() and "_TP_" not in path.name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        if is_paper_tp(path, text):
            result.paper_count += 1
            errors = paper_tp_errors(text, rel)
            if sibling_exists(path, "version_amenagee"):
                errors = [error for error in errors if "version aménagée" not in error]
            result.errors.extend(errors)
            if has_python_assets(path):
                result.errors.append(f"{rel}: TP papier avec assets Python existants, statut à clarifier")
            if re.search(r"SQL|csv|table|algorithme|fonction", text, re.I) and "aucune ressource Python" in text:
                result.preferable_executable.append(rel)
        else:
            result.executable_count += 1
    return result


def main() -> int:
    result = analyze_paper_tp_justification()
    total = result.paper_count + result.executable_count
    ratio = (result.paper_count / total * 100) if total else 0.0
    print(f"TP papier : {result.paper_count}")
    print(f"TP exécutables : {result.executable_count}")
    print(f"Ratio papier/exécutable : {ratio:.1f}% papier")
    if result.preferable_executable:
        print("Séquences où un TP exécutable serait préférable :")
        for item in result.preferable_executable[:80]:
            print(f"- {item}")
    if result.errors:
        print("check_paper_tp_justification: KO")
        for error in result.errors[:200]:
            print(f"- {error}")
        return 1
    print("check_paper_tp_justification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
