#!/usr/bin/env python3
"""Check that QCM producers and consumers use the `explications` contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QCM_PATHS = [
    ROOT / "02_modeles_documents/modele_qcm.json",
    ROOT / "premiere/sequences/s01_representation_donnees/qcm.json",
    ROOT / "terminale/sequences/s01_structures_donnees_interfaces_implementations/qcm.json",
]
CONSUMER_SCRIPTS = [
    ROOT / "scripts/check_metadata.py",
    ROOT / "scripts/check_qcm_schema.py",
    ROOT / "scripts/check_teacher_corrections_alignment.py",
]
FORBIDDEN_SCRIPT_PATTERNS = [
    re.compile(r"\.get\(['\"]explication['\"]\)"),
    re.compile(r"\[['\"]explication['\"]\]"),
    re.compile(r"['\"]explication['\"]\s+in\s+"),
]


def check_qcm_file(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{rel}: JSON invalide ({exc})"]

    questions = payload.get("questions")
    if not isinstance(questions, list) or not questions:
        return [f"{rel}: questions absentes"]

    for index, question in enumerate(questions, 1):
        if not isinstance(question, dict):
            errors.append(f"{rel}: question {index} non objet")
            continue
        if "explication" in question:
            errors.append(f"{rel}: question {index} utilise l'ancien champ explication")
        explanations = question.get("explications")
        propositions = question.get("propositions")
        if not isinstance(explanations, dict) or not explanations:
            errors.append(f"{rel}: question {index} champ explications absent ou vide")
        if isinstance(propositions, list) and isinstance(explanations, dict):
            missing = [item for item in propositions if item not in explanations]
            if missing:
                errors.append(f"{rel}: question {index} explications manquantes pour {missing}")
    return errors


def check_consumer(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(ROOT)
    errors: list[str] = []
    if "explications" not in text:
        errors.append(f"{rel}: ne référence pas le champ explications")
    for pattern in FORBIDDEN_SCRIPT_PATTERNS:
        if pattern.search(text):
            errors.append(f"{rel}: référence l'ancien champ explication")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in QCM_PATHS:
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: fichier absent")
            continue
        errors.extend(check_qcm_file(path))
    for path in CONSUMER_SCRIPTS:
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: script absent")
            continue
        errors.extend(check_consumer(path))

    if errors:
        print("check_qcm_contract_consistency: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_qcm_contract_consistency: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
