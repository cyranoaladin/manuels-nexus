#!/usr/bin/env python3
"""Check teacher corrections align with TD, evaluation and QCM question counts."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = [
    ROOT / "premiere/sequences/s01_representation_donnees",
    ROOT / "terminale/sequences/s01_structures_donnees_interfaces_implementations",
]
REQUIRED_TERMS = ["Justification", "Barème", "Variante acceptable", "Erreurs fréquentes", "Remédiation", "Capacité officielle"]


def md_question_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = len(re.findall(r"^#{2,4}\s+(?:Exercice|Question|Activité)\s+\d+", text, flags=re.M))
    numbered = len(re.findall(r"^\s*\d+\.\s+", text, flags=re.M))
    return max(headings, numbered)


def corrected_count(text: str) -> int:
    return len(re.findall(r"^##\s+(?:Question|Exercice)\s+\d+", text, flags=re.M))


def qcm_count(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    questions = payload.get("questions", [])
    return len(questions) if isinstance(questions, list) else 0


def qcm_explanations(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    total = 0
    for item in payload.get("questions", []):
        explanations = item.get("explications") if isinstance(item, dict) else None
        if isinstance(explanations, dict) and explanations:
            total += 1
    return total


def main() -> int:
    errors: list[str] = []
    for seq in SEQUENCES:
        corrige = (seq / "corrige_professeur.md").read_text(encoding="utf-8", errors="replace")
        eval_corrige = (seq / "evaluation_corrigee.md").read_text(encoding="utf-8", errors="replace")
        td_count = md_question_count(seq / "td.md")
        evaluation_count = md_question_count(seq / "evaluation.md")
        qcm_total = qcm_count(seq / "qcm.json")
        if corrected_count(corrige) < max(1, min(td_count, 8)):
            errors.append(f"{seq.relative_to(ROOT)}: corrige_professeur has fewer corrections than TD requirement")
        if corrected_count(eval_corrige) < max(1, min(evaluation_count, 8)):
            errors.append(f"{seq.relative_to(ROOT)}: evaluation_corrigee has fewer corrections than evaluation requirement")
        if qcm_explanations(seq / "qcm.json") != qcm_total:
            errors.append(f"{seq.relative_to(ROOT)}: not every QCM question has explanation")
        for label, text in [("corrige_professeur", corrige), ("evaluation_corrigee", eval_corrige)]:
            for term in REQUIRED_TERMS:
                if term not in text:
                    errors.append(f"{seq.relative_to(ROOT)}: {label} missing {term}")
            if not re.search(r"[PT]-[A-Z]+(?:-[A-Z]+)*-[0-9]{2}[A-Z]?", text):
                errors.append(f"{seq.relative_to(ROOT)}: {label} has no atomic capacity id")
    if errors:
        print("check_teacher_corrections_alignment: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_teacher_corrections_alignment: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
