#!/usr/bin/env python3
"""Detect line padding and repeated generated prose in ready supports."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES

SUPPORTS_ROOT = ROOT / "03_progressions" / "supports"
OBJECTIVE_RE = re.compile(r"^##\s+Objectif\s+(O\d+).*?(?=^##\s+Objectif\s+O\d+|^##\s+|\Z)", re.M | re.S)
SENTENCE_RE = re.compile(r"[^.!?\n]{35,}[.!?]")
STRUCTURAL_PREFIXES = (
    "#",
    "- objectif o",
    "- capacité",
    "- reconnaître une consigne",
    "- distinguer donnée",
    "- rédiger une justification",
    "- contrôler une réponse",
    "- critère local",
    "- critère de sortie",
    "- trace attendue",
    "- question flash",
    "- espace de réponse",
    "- livrable vérifiable",
    "- exemple d’exécution",
    "- exemple minimal",
    "- test nominal",
    "- test limite",
    "- test invalide",
    "- socle",
    "- standard",
    "- expert",
    "- contrôle",
    "- résultat",
    "- exercice n : n point",
    "- exercice n : reprendre question",
    "- méthode exigée",
    "- mini-production",
    "- contrainte de contrôle",
    "- production attendue",
    "- la capacité officielle",
    "- la méthode contient",
    "- le cas limite",
    "- la correction explique",
)


@dataclass
class PaddingResult:
    errors: list[str] = field(default_factory=list)


def normalize(text: str) -> str:
    text = re.sub(r"`[^`]+`", "`code`", text.lower())
    text = re.sub(r"\b\d+\b", "n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def is_structural_line(line: str) -> bool:
    lowered = normalize(line)
    return any(lowered.startswith(prefix) for prefix in STRUCTURAL_PREFIXES) or lowered == "» puis reprendre la procédure correcte."


def useful_lines(text: str) -> list[str]:
    text = strip_frontmatter(text)
    return [line.strip() for line in text.splitlines() if line.strip()]


def analyze_text(name: str, text: str) -> list[str]:
    errors: list[str] = []
    if "## Consolidation de fin de cours" in text:
        errors.append(f"{name}: section de consolidation artificielle")

    objective_blocks = [match.group(0) for match in OBJECTIVE_RE.finditer(text)]
    if len(objective_blocks) >= 2:
        close = 0
        total = 0
        for index, left in enumerate(objective_blocks):
            for right in objective_blocks[index + 1:]:
                total += 1
                if similarity(left, right) >= 0.82:
                    close += 1
        if total and close / total >= 0.50:
            errors.append(f"{name}: objectifs O1-O4 presque identiques")

    lines = useful_lines(text)
    normalized_lines = [
        normalize(line)
        for line in lines
        if len(line) > 45 and not is_structural_line(line)
    ]
    counts = Counter(normalized_lines)
    for line, count in counts.items():
        if count >= 3:
            errors.append(f"{name}: paragraphe répété {count} fois -> {line[:80]}")
            break

    if len(lines) >= 180:
        activity_count = len(re.findall(r"\b(Exercice|Question|Exemple corrigé|Activité corrective|Test)\b", text))
        if activity_count < 15:
            errors.append(f"{name}: longueur élevée sans activités, exemples ou corrections suffisants")
    return errors


def support_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for prefix in FIRST_BATCH_PREFIXES:
        files.extend(sorted(root.rglob(f"{prefix}_*.md")))
    return files


def analyze_padding(root: Path = SUPPORTS_ROOT) -> PaddingResult:
    result = PaddingResult()
    sentence_locations: dict[str, set[str]] = defaultdict(set)
    for path in support_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        result.errors.extend(analyze_text(path.name, text))
        for sentence in SENTENCE_RE.findall(strip_frontmatter(text)):
            normalized = normalize(sentence)
            if len(normalized) > 35 and not is_structural_line(normalized):
                sentence_locations[normalized].add(str(path.relative_to(root)))

    for sentence, locations in sentence_locations.items():
        prefixes = {Path(location).name[:3] for location in locations}
        if len(locations) > 5 and len(prefixes) > 3:
            result.errors.append(
                f"phrase répétée dans plus de 5 supports ({len(locations)}) -> {sentence[:90]}"
            )
    return result


def main() -> int:
    result = analyze_padding()
    if result.errors:
        print("check_no_line_padding: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_no_line_padding: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
