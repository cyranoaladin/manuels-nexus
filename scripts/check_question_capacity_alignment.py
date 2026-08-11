#!/usr/bin/env python3
"""Check that evaluation questions use capacities matching their task."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


P05_EVALUATION = ROOT / "03_progressions" / "supports" / "premiere" / "P05" / "P05_evaluation_tables_csv.md"


@dataclass
class QuestionCapacityResult:
    errors: list[str] = field(default_factory=list)
    questions_checked: int = 0


def split_question_blocks(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^### Question\s+(\d+)\b.*$", text, re.M))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            next_section = re.search(r"^##\s+", text[match.end():], re.M)
            end = match.end() + next_section.start() if next_section else len(text)
        blocks[match.group(1)] = text[start:end]
    return blocks


def expected_capacity_for_p05(question_number: str, block: str) -> str:
    lowered = block.lower()
    if question_number == "1":
        return "P-TABLE-01"
    if any(keyword in lowered for keyword in ["filtr", "tri", "recherche", "conversion", "erreur", "valueerror"]):
        return "P-TABLE-02"
    return "P-TABLE-01"


def capacities_in_block(block: str) -> list[str]:
    return re.findall(r"P-[A-Z]+-\d{2}", block)


def analyze_question_capacity_alignment(root: Path = ROOT) -> QuestionCapacityResult:
    result = QuestionCapacityResult()
    path = root / P05_EVALUATION.relative_to(ROOT)
    if not path.exists():
        result.errors.append(f"{path.relative_to(root).as_posix()}: fichier P05 évaluation absent")
        return result
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = split_question_blocks(text)
    expected_by_number = {"1": "P-TABLE-01", "2": "P-TABLE-02", "3": "P-TABLE-02", "4": "P-TABLE-02"}
    for number, expected in expected_by_number.items():
        block = blocks.get(number)
        if not block:
            result.errors.append(f"P05 Question {number}: bloc question absent")
            continue
        result.questions_checked += 1
        actual = capacities_in_block(block)
        semantic_expected = expected_capacity_for_p05(number, block)
        expected = "P-TABLE-02" if semantic_expected == "P-TABLE-02" else expected
        if expected not in actual:
            result.errors.append(
                f"P05 Question {number}: capacité attendue {expected}, capacités trouvées {actual or 'aucune'}"
            )
        if number != "1" and "P-TABLE-01" in actual and expected == "P-TABLE-02":
            result.errors.append(f"P05 Question {number}: filtrage/conversion/tri ne doit pas rester P-TABLE-01")
    return result


def main() -> int:
    result = analyze_question_capacity_alignment()
    if result.errors:
        print("check_question_capacity_alignment: KO")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print(f"check_question_capacity_alignment: PASS ({result.questions_checked} questions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
