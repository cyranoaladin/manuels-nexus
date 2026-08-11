#!/usr/bin/env python3
"""Validate pilot QCM JSON schema and pedagogical fields."""

from __future__ import annotations

from typing import List
import json

from scripts._qa_common import ROOT, TARGET_SEQUENCES, load_program_entries, print_result


def main() -> None:
    program = load_program_entries()
    errors: List[str] = []

    for seq in TARGET_SEQUENCES.values():
        path = seq / "qcm.json"
        rel = path.relative_to(ROOT) if path.exists() else path
        if not path.exists():
            errors.append(f"{rel}: fichier absent")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{rel}: JSON invalide ({exc})")
            continue

        metadata = payload.get("metadata")
        questions = payload.get("questions")
        if not isinstance(metadata, dict):
            errors.append(f"{rel}: metadata absent")
        if not isinstance(questions, list) or len(questions) < 8:
            errors.append(f"{rel}: au moins 8 questions attendues")
            continue

        seen_difficulties = set()
        for index, question in enumerate(questions, 1):
            prefix = f"{rel}: question {index}"
            for key in ["id", "question", "propositions", "bonne_reponse", "difficulte", "capacite_officielle", "erreur_ciblee"]:
                if key not in question:
                    errors.append(f"{prefix}: champ manquant -> {key}")
            propositions = question.get("propositions")
            if not isinstance(propositions, list) or len(propositions) < 3:
                errors.append(f"{prefix}: au moins 3 propositions attendues")
            explanations = question.get("explications")
            if not isinstance(explanations, dict) or not propositions or len(explanations) < len(propositions):
                errors.append(f"{prefix}: explication attendue pour chaque proposition")
            capacity = question.get("capacite_officielle")
            if capacity not in program:
                errors.append(f"{prefix}: capacité inconnue -> {capacity}")
            if question.get("difficulte"):
                seen_difficulties.add(str(question["difficulte"]))

        if not {"socle", "standard", "expert"}.issubset(seen_difficulties):
            errors.append(f"{rel}: difficultés socle, standard et expert attendues")

    print_result("check_qcm_schema", errors)


if __name__ == "__main__":
    main()
