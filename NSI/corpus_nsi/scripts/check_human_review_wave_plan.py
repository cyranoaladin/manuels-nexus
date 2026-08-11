#!/usr/bin/env python3
"""Check the first human-review wave plan without validating resources."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, load_pilot_scope


PLAN = "human_review_wave_1_plan.md"


@dataclass
class HumanReviewWavePlanResult:
    errors: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    priority_hits: set[str] = field(default_factory=set)


def extract_resources(text: str) -> list[str]:
    candidates = re.findall(r"`([^`]+\.(?:md|py|yml|json))`", text)
    return [candidate for candidate in candidates if candidate.startswith("03_progressions/")]


def analyze_human_review_wave_plan(root: Path = ROOT) -> HumanReviewWavePlanResult:
    result = HumanReviewWavePlanResult()
    priority_prefixes = load_pilot_scope(root).get("human_review_wave_priority_prefixes", [])
    if not priority_prefixes:
        result.errors.append("pilot_scope.yml: human_review_wave_priority_prefixes absent")
    path = root / PLAN
    if not path.exists():
        result.errors.append(f"{PLAN} absent")
        return result
    text = path.read_text(encoding="utf-8", errors="replace")
    result.resources = extract_resources(text)
    if len(result.resources) != 20:
        result.errors.append(f"20 ressources prioritaires attendues, trouvé {len(result.resources)}")
    for resource in result.resources:
        if not (root / resource).exists():
            result.errors.append(f"{resource}: ressource absente")
        prefix_match = re.search(r"/([PT]\d{2})[_/]", "/" + resource)
        if prefix_match and prefix_match.group(1) in priority_prefixes:
            result.priority_hits.add(prefix_match.group(1))
    for prefix in priority_prefixes:
        if prefix not in result.priority_hits:
            result.errors.append(f"priorité {prefix} absente de la vague 1")
    if re.search(r"\b(validated|published|covered)\b", text, re.I):
        result.errors.append("validation anticipée interdite dans le plan de revue")
    if re.search(r"reviewer\s*:\s*\S|date\s*:\s*\d{4}-\d{2}-\d{2}", text, re.I):
        result.errors.append("reviewer/date ne doivent pas être renseignés avant revue réelle")
    return result


def main() -> int:
    result = analyze_human_review_wave_plan()
    print(f"Ressources vague 1 : {len(result.resources)}")
    print(f"Priorités couvertes : {', '.join(sorted(result.priority_hits))}")
    if result.errors:
        print("check_human_review_wave_plan: KO")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print("check_human_review_wave_plan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
