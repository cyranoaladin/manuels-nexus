#!/usr/bin/env python3
"""Check disciplinary substance of evaluations linked to operational sheets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import unicodedata

from scripts._qa_common import ROOT, strip_frontmatter
from scripts.check_linked_evaluation_quality import target_evaluation_files
from scripts.check_linked_td_substance import correction_has_substance as td_correction_has_substance

VAGUE_ANSWERS = [
    "solution explicite attendue",
    "réponse explicite attendue",
    "reponse explicite attendue",
    "résultat indicatif",
    "resultat indicatif",
    "la réponse doit montrer",
    "la reponse doit montrer",
    "production vérifiable",
    "production verifiable",
]

CONCRETE_PATTERNS = [
    r"\bSELECT\b.*\bFROM\b",
    r"\bINSERT\b|\bUPDATE\b|\bDELETE\b",
    r"\bTTL\b|\bACK\b|\bIP\b|\bTCP\b|\bHTTPS\b|\bRIP\b|\bOSPF\b",
    r"\broute\b|\bpaquet\b|\bpasserelle\b|\bcertificat\b|\bclé\b|\bcle\b",
    r"\breturn\b|\bfor\b|\bwhile\b|\bif\b|\bdef\b",
    r"\bpseudo-code\b|\bpseudocode\b",
    r"\brécurrence\b|\brecurrence\b|\bétat\b|\betat\b|\bmémoïsation\b|\bmemoisation\b|\btabulation\b",
    r"\btrace\b|\btableau\b|\binvariant\b|\bcomplexité\b|\bcomplexite\b",
    r"\b\d+\b",
    r"`[^`]+`",
    r"\"[^\"]+\"",
    r"\bTrue\b|\bFalse\b|\bNone\b",
    r"\baffiché\b|\baffiche\b|\bretourné\b|\bretourne\b",
    r"\|.*\|",
    r"```",
]


@dataclass
class EvaluationSubstanceResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"`[^`]+`", "`code`", value)
    value = re.sub(r"\b\d+(?:[.,]\d+)?\b", "n", value)
    value = re.sub(r"[^a-z0-9_]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def has_concrete_evidence(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.I | re.S) for pattern in CONCRETE_PATTERNS)


def correction_has_substance(path: Path, question: str, correction: str) -> bool:
    return td_correction_has_substance(path, question, f"{question}\n{correction}")


def numbered_blocks(body: str, title: str) -> dict[int, str]:
    pattern = re.compile(
        rf"^###\s+{re.escape(title)}\s+(\d+)\b(.*?)(?=^###\s+{re.escape(title)}\s+\d+\b|^##\s+|\Z)",
        flags=re.M | re.S | re.I,
    )
    return {int(match.group(1)): match.group(2).strip() for match in pattern.finditer(body)}


def bareme_entries(body: str) -> dict[int, str]:
    entries: dict[int, str] = {}
    for match in re.finditer(r"(?:Question|Q)\s*(\d+)\s*:\s*(.+)", body, flags=re.I):
        entries[int(match.group(1))] = match.group(2).strip()
    return entries


def bareme_is_repetitive(baremes: dict[int, str]) -> bool:
    if len(baremes) < 4:
        return False
    normalized = {normalize(value) for value in baremes.values() if value}
    generic = {
        "n point methode n point resultat",
        "n points methode n points resultat",
        "n point méthode n point résultat",
    }
    if len(normalized) <= 1:
        only = next(iter(normalized), "")
        return only in generic
    return all(value in generic for value in normalized)


def analyze_one_evaluation(path: Path, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_frontmatter(text)
    rel = path.relative_to(root) if path.is_relative_to(root) else path
    normalized = normalize(body)
    has_vague_answer = False

    for phrase in VAGUE_ANSWERS:
        if normalize(phrase) in normalized:
            has_vague_answer = True
            errors.append(f"{rel}: réponse attendue vague ou non vérifiable -> {phrase}")

    questions = numbered_blocks(body, "Question")
    corrections = numbered_blocks(body, "Corrigé question")
    baremes = bareme_entries(body)

    if questions and not corrections:
        errors.append(f"{rel}: section Corrigé question explicite absente")

    if questions:
        for number, question in questions.items():
            if number not in baremes:
                errors.append(f"{rel}: barème absent pour question {number}")
            correction = corrections.get(number, "")
            if not correction:
                errors.append(f"{rel}: corrigé absent pour question {number}")
            elif not correction_has_substance(path, question, correction):
                errors.append(f"{rel}: corrigé question {number} sans preuve disciplinaire suffisante")

    normalized_baremes = {normalize(value) for value in baremes.values() if value}
    if bareme_is_repetitive(baremes) or (has_vague_answer and len(baremes) >= 4 and len(normalized_baremes) <= 1):
        errors.append(f"{rel}: barème trop répétitif, éléments observables non différenciés")

    lower = body.lower()
    if "sql" in path.name.lower() and ("select" not in lower or ("résultat" not in lower and "resultat" not in lower and "|" not in body)):
        errors.append(f"{rel}: évaluation SQL sans requête et résultat attendus")
    if any(token in path.name.lower() for token in ["programmation_dynamique", "tri", "dichotomie", "boyer", "diviser", "calculabilite"]):
        if not has_concrete_evidence(body) and not any(token in lower for token in ["pseudo-code", "trace", "tableau", "récurrence", "recurrence", "complexité", "complexite"]):
            errors.append(f"{rel}: évaluation algorithmique sans trace, pseudo-code, relation ou complexité attendue")
    if any(token in path.name.lower() for token in ["reseaux", "protocoles", "routage", "chiffrement", "https"]):
        if not any(token in lower for token in ["ttl", "ip", "ack", "route", "paquet", "https", "certificat"]):
            errors.append(f"{rel}: évaluation réseau/sécurité sans champ, paquet, route ou décision attendue")
    return errors


def analyze_linked_evaluation_substance(root: Path = ROOT, files: list[Path] | None = None) -> EvaluationSubstanceResult:
    result = EvaluationSubstanceResult()
    paths = files if files is not None else target_evaluation_files(root)
    for path in paths:
        result.checked_files += 1
        result.errors.extend(analyze_one_evaluation(path, root))
    return result


def main() -> int:
    result = analyze_linked_evaluation_substance()
    if result.errors:
        print("check_linked_evaluation_substance: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_linked_evaluation_substance: PASS ({result.checked_files} évaluations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
