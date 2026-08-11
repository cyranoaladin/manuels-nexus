#!/usr/bin/env python3
"""Reject first-batch supports that satisfy form checks without enough substance."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES, REQUIRED_KINDS, find_kind_file

GENERIC_PATTERNS = [
    "variante contrôlée",
    "réponse cohérente",
    "production vérifiable",
    "résultat attendu est",
    "donnée voisine",
    "exemple de référence ou une valeur cohérente",
]
OBJECTIVE_RE = re.compile(r"^##\s+Objectif\s+(O\d+).*?(?=^##\s+Objectif\s+O\d+|^##\s+|\Z)", re.M | re.S)
EXERCISE_RE = re.compile(r"^###\s+Exercice\s+(\d+).*?(?=^###\s+Exercice\s+\d+|^##\s+|\Z)", re.M | re.S)
CORRECTION_RE = re.compile(r"^###\s+Corrigé exercice\s+(\d+).*?(?=^###\s+Corrigé exercice\s+\d+|^##\s+|\Z)", re.M | re.S)
QUESTION_RE = re.compile(r"^###\s+Question\s+(\d+).*?(?=^###\s+Question\s+\d+|^##\s+|\Z)", re.M | re.S)
BAREME_RE = re.compile(r"^###\s+Barème question\s+(\d+).*?(?=^###\s+Barème question\s+\d+|^##\s+|\Z)", re.M | re.S)
ACTIVITY_RE = re.compile(r"Activité corrective\s+(EF\d+)\s*:\s*(.+)")
EXAMPLE_BLOCK_RE = re.compile(r"^###\s+Exemple corrigé\s+\d+.*?(?=^###\s+Exemple corrigé\s+\d+|^##\s+|\Z)", re.M | re.S)


@dataclass
class SubstanceResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def normalize(text: str) -> str:
    text = re.sub(r"`[^`]+`", "`code`", text.lower())
    text = re.sub(r"\b\d+\b", "N", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def pairwise_too_similar(blocks: list[str], threshold: float = 0.80) -> bool:
    if len(blocks) < 2:
        return False
    comparisons = 0
    too_close = 0
    for index, left in enumerate(blocks):
        for right in blocks[index + 1:]:
            comparisons += 1
            if similarity(left, right) >= threshold:
                too_close += 1
    return comparisons > 0 and too_close / comparisons > 0.50


def unique_blocks(blocks: list[str], threshold: float = 0.80) -> int:
    unique: list[str] = []
    for block in blocks:
        if not any(similarity(block, existing) >= threshold for existing in unique):
            unique.append(block)
    return len(unique)


def token_signature(text: str) -> set[str]:
    stopwords = {
        "appliquer",
        "methode",
        "méthode",
        "question",
        "point",
        "points",
        "identifier",
        "correctement",
        "donnee",
        "donnée",
        "puis",
        "avec",
        "pour",
        "vers",
        "que",
        "par",
        "une",
        "les",
        "des",
        "dans",
        "sur",
    }
    tokens = set(re.findall(r"[a-zA-ZÀ-ÿ0-9_]+", normalize(text)))
    return {token for token in tokens if len(token) > 2 and token not in stopwords}


def unique_token_blocks(blocks: list[str], threshold: float = 0.76) -> int:
    unique: list[set[str]] = []
    for block in blocks:
        signature = token_signature(block)
        if not signature:
            continue
        if not any(len(signature & existing) / len(signature | existing) >= threshold for existing in unique):
            unique.append(signature)
    return len(unique)


def extract_examples(text: str) -> list[str]:
    blocks = [match.group(0) for match in EXAMPLE_BLOCK_RE.finditer(text)]
    if blocks:
        return blocks
    examples: list[str] = []
    for line in text.splitlines():
        if "exemple" in line.lower() and ":" in line:
            examples.append(line.split(":", 1)[1].strip())
    return [item for item in examples if item]


def extract_example_titles(text: str) -> list[str]:
    return re.findall(r"^###\s+Exemple corrigé\s+\d+\s*-\s*(.+)$", text, flags=re.M)


def extract_data_prompts(blocks: list[str]) -> list[str]:
    prompts: list[str] = []
    for block in blocks:
        match = re.search(r"(?:Donnée|Énoncé|Énoncé disciplinaire|Question|Travail demandé)\s*:\s*(.+)", block)
        prompts.append(match.group(1).strip() if match else block)
    return prompts


def extract_bareme_targets(blocks: list[str]) -> list[str]:
    targets: list[str] = []
    for block in blocks:
        match = re.search(r"identifier correctement\s+(.+?)\s+et la donnée", block, flags=re.I)
        method = re.search(r"appliquer la méthode\s+«\s*(.+?)\s*»", block, flags=re.I)
        target = match.group(1).strip() if match else block
        if method:
            target = f"{target} | {method.group(1).strip()}"
        targets.append(target)
    return targets


def analyze_support(path: Path, kind: str) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()

    for pattern in GENERIC_PATTERNS:
        if pattern in lowered:
            errors.append(f"{path}: formulation générique -> {pattern}")

    objective_blocks = [match.group(0) for match in OBJECTIVE_RE.finditer(text)]
    if len(objective_blocks) >= 3 and pairwise_too_similar(objective_blocks):
        errors.append(f"{path}: objectifs trop répétitifs")

    if kind == "cours":
        examples = extract_examples(text)
        titles = extract_example_titles(text) or examples
        if len(examples) < 3 or unique_blocks(titles, threshold=0.84) < 3:
            errors.append(f"{path}: moins de 3 exemples vraiment différents")

    if kind == "td":
        exercises = [match.group(0) for match in EXERCISE_RE.finditer(text)]
        data_prompts = extract_data_prompts(exercises)
        objectives = set(re.findall(r"Objectif travaillé\s*:\s*(O\d+)", text))
        if len(exercises) < 8:
            errors.append(f"{path}: moins de 8 exercices")
        if len(objectives) < 4:
            errors.append(f"{path}: objectifs d'exercices insuffisamment variés")
        if len(exercises) >= 8 and unique_blocks(data_prompts, threshold=0.76) < 7:
            errors.append(f"{path}: exercices quasi identiques")

    if kind == "corrige":
        corrections = {int(match.group(1)): match.group(0) for match in CORRECTION_RE.finditer(text)}
        for number in range(1, 9):
            block = corrections.get(number, "")
            if not block:
                errors.append(f"{path}: corrigé exercice {number} absent")
            elif "méthode" not in block.lower() or "résultat" not in block.lower():
                errors.append(f"{path}: corrigé exercice {number} trop générique")

    if kind == "evaluation":
        questions = [match.group(0) for match in QUESTION_RE.finditer(text)]
        prompts = extract_data_prompts(questions)
        if len(questions) < 4:
            errors.append(f"{path}: moins de 4 questions d'évaluation")
        if len(questions) >= 4 and unique_blocks(prompts, threshold=0.84) < 4:
            errors.append(f"{path}: questions d'évaluation trop similaires")

    if kind == "bareme":
        rows = [match.group(0) for match in BAREME_RE.finditer(text)]
        targets = extract_bareme_targets(rows)
        if len(rows) < 4:
            errors.append(f"{path}: barème incomplet question par question")
        if len(rows) >= 4 and unique_token_blocks(targets, threshold=0.70) < 4:
            errors.append(f"{path}: barème question par question trop générique")

    if kind == "remediation":
        activities = [match.group(2).strip() for match in ACTIVITY_RE.finditer(text)]
        if len(activities) < 4:
            errors.append(f"{path}: remédiation sans activités EF1-EF4")
        if len(activities) >= 4 and unique_blocks(activities, threshold=0.78) < 4:
            errors.append(f"{path}: activités de remédiation trop proches")
    return errors


def analyze_substance(root: Path = ROOT, prefixes: list[str] | None = None) -> SubstanceResult:
    prefixes = prefixes or FIRST_BATCH_PREFIXES
    result = SubstanceResult()
    for prefix in prefixes:
        for kind in REQUIRED_KINDS:
            path = find_kind_file(root, prefix, kind)
            if path is None:
                result.errors.append(f"{prefix}: support {kind} absent")
                continue
            result.checked_files += 1
            result.errors.extend(analyze_support(path, kind))
    return result


def main() -> int:
    result = analyze_substance()
    if result.errors:
        print("check_support_substance: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_support_substance: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
