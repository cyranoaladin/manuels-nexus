#!/usr/bin/env python3
"""Check quality of evaluation supports linked to course sheets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Mapping

from scripts._qa_common import ROOT, read_frontmatter, strip_frontmatter
from scripts._operational_links import ReferenceResolution, operational_resource_links, resolve_reference

REQUIRED_FRONTMATTER = ["title", "level", "sequence_id", "document_type", "status", "official_program"]
QUESTION_HEADING = re.compile(r"^#{2,3}\s+Question\s+\d+\b.*$", flags=re.M | re.I)
SCORED_QUESTION_HEADING = re.compile(r"^#{1,4}\s+(?:Bar[èe]me\s+)?Question\s+\d+\b.*$", flags=re.M | re.I)
ANY_SECTION_HEADING = re.compile(r"^#{1,3}\s+.+$", flags=re.M)
MATERIAL_POLICIES = (
    re.compile(r"mat[ée]riel\s*(autorisé)?\s*:\s*\S+", re.I),
    re.compile(r"documents?\s*(et\s+.*machine)?\s*:\s*non autoris[ée]s?", re.I),
    re.compile(r"documents?\s+interdits?", re.I),
    re.compile(r"machine\s+interdite", re.I),
    re.compile(r"sans\s+documents?", re.I),
    re.compile(r"aucun\s+document", re.I),
)
INSTRUCTION_VERBS = re.compile(
    r"\b(associer|calculer|classer|compl[ée]ter|comparer|construire|corriger|d[ée]boguer|"
    r"d[ée]crire|d[ée]finir|d[ée]terminer|donner|[ée]crire|expliquer|identifier|"
    r"indiquer|justifier|lire|produire|programmer|r[ée]aliser|tracer)\b",
    re.I,
)
TASK_FAMILIES = {
    "lecture/analyse": re.compile(r"\b(lire|associer|d[ée]crire|d[ée]finir|identifier|analyser)\b", re.I),
    "trace/calcul": re.compile(r"\b(calculer|compl[ée]ter|table|trace)\b", re.I),
    "production": re.compile(r"\b([ée]crire|produire|construire|programmer|r[ée]aliser)\b", re.I),
    "justification": re.compile(r"\b(justifier|expliquer|prouver)\b", re.I),
    "d[ée]bogage": re.compile(r"\b(corriger|d[ée]boguer|erreur)\b", re.I),
}
LINKED_RESOURCE_FIELDS = {
    "barème": ("bareme", "barème"),
    "corrigé": ("corrige", "corrigé"),
    "remédiation": ("remediation", "remédiation"),
    "fiche liée": ("fiche", "fiche_liee", "fiche liée"),
}


@dataclass
class LinkedEvaluationQualityResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def target_evaluation_files(root: Path = ROOT) -> list[Path]:
    return sorted(resolution.path for resolution in expected_evaluation_files(root).values() if resolution.path is not None)


def expected_evaluation_files(root: Path = ROOT) -> dict[str, ReferenceResolution]:
    expected: dict[str, ReferenceResolution] = {}
    for resource in operational_resource_links(root, {"évaluation", "evaluation"}):
        expected[resource.link.file] = resolve_reference(root, resource.link.file)
    return expected


def count_question_headings(text: str) -> int:
    """Count only level-2 or level-3 question headings in an evaluation body."""
    return len(QUESTION_HEADING.findall(text))


def count_scored_question_headings(text: str) -> int:
    """Count question-by-question entries in a linked barème or corrigé."""
    return len(SCORED_QUESTION_HEADING.findall(text))


def question_blocks(text: str) -> list[str]:
    """Return the content belonging to each recognised question heading."""
    headings = list(QUESTION_HEADING.finditer(text))
    blocks: list[str] = []
    for index, heading in enumerate(headings):
        next_heading = ANY_SECTION_HEADING.search(text, heading.end())
        end = next_heading.start() if next_heading else len(text)
        blocks.append(text[heading.end():end].strip())
    return blocks


def has_material_policy(text: str) -> bool:
    """Accept clear authorisation or prohibition statements, never a missing policy."""
    return any(pattern.search(text) for pattern in MATERIAL_POLICIES)


def has_real_question_instructions(blocks: list[str]) -> bool:
    """Reject headings that are not followed by an actionable student instruction."""
    return bool(blocks) and all(
        len(re.findall(r"\w+", block)) >= 6 and INSTRUCTION_VERBS.search(block)
        for block in blocks
    )


def task_family_count(blocks: list[str]) -> int:
    combined = "\n".join(blocks)
    return sum(bool(pattern.search(combined)) for pattern in TASK_FAMILIES.values())


def linked_reference_path(root: Path, evaluation: Path, reference: str) -> Path | None:
    """Resolve a frontmatter resource relative to the evaluation before basename lookup."""
    local = evaluation.parent / reference
    if local.exists():
        return local
    resolved = resolve_reference(root, reference)
    return resolved.path


def is_substantive_linked_resource(path: Path) -> bool:
    """A linked support must contain structured, non-trivial content."""
    body = strip_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    headings = re.findall(r"^#{1,4}\s+\S+", body, flags=re.M)
    words = re.findall(r"\w+", body)
    return len(words) >= 20 and len(headings) >= 2


def metadata_reference(metadata: Mapping[str, object], field_names: tuple[str, ...]) -> str | None:
    for field_name in field_names:
        value = metadata.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def uses_linked_resource_frontmatter(metadata: Mapping[str, object]) -> bool:
    return any(metadata_reference(metadata, fields) is not None for fields in LINKED_RESOURCE_FIELDS.values())


def check_linked_resources(
    root: Path,
    evaluation: Path,
    metadata: Mapping[str, object],
    questions: int,
    rel: Path,
) -> list[str]:
    """Validate declared resources instead of requiring teacher markers in a student subject."""
    errors: list[str] = []
    for resource_type, field_names in LINKED_RESOURCE_FIELDS.items():
        reference = metadata_reference(metadata, field_names)
        required = resource_type in {"barème", "corrigé"}
        if reference is None:
            if required:
                errors.append(f"{rel}: référence frontmatter absente -> {resource_type}")
            continue
        linked = linked_reference_path(root, evaluation, reference)
        if linked is None:
            errors.append(f"{rel}: {resource_type} lié absent -> {reference}")
            continue
        if not is_substantive_linked_resource(linked):
            errors.append(f"{rel}: {resource_type} lié trop pauvre -> {reference}")
            continue
        if resource_type in {"barème", "corrigé"}:
            linked_text = strip_frontmatter(linked.read_text(encoding="utf-8", errors="replace"))
            if count_scored_question_headings(linked_text) < questions:
                errors.append(f"{rel}: {resource_type} lié incomplet question par question")
    return errors


def analyze_one_evaluation(path: Path, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_frontmatter(text)
    metadata = read_frontmatter(path)
    rel = path.relative_to(root) if path.is_relative_to(root) else path
    missing_fm = [key for key in REQUIRED_FRONTMATTER if key not in metadata]
    if missing_fm:
        errors.append(f"{rel}: frontmatter incomplet -> {', '.join(missing_fm)}")
    if metadata.get("document_type") != "evaluation":
        errors.append(f"{rel}: document_type attendu evaluation")
    if metadata.get("status") != "needs_review":
        errors.append(f"{rel}: status attendu needs_review")
    official = metadata.get("official_program")
    capacities = official.get("capacities") if isinstance(official, dict) else None
    if not isinstance(capacities, list) or not capacities:
        errors.append(f"{rel}: capacités officielles absentes")

    questions = count_question_headings(body)
    if questions < 4 or questions > 6:
        errors.append(f"{rel}: 4 à 6 questions attendues, trouvé {questions}")
    structured_links = uses_linked_resource_frontmatter(metadata)
    blocks = question_blocks(body)
    if structured_links and not has_real_question_instructions(blocks):
        errors.append(f"{rel}: consignes de questions insuffisantes ou purement déclaratives")
    if structured_links and task_family_count(blocks) < 3:
        errors.append(f"{rel}: variété de tâches insuffisante")
    lower = body.lower()
    if "durée" not in lower and "duree" not in lower:
        errors.append(f"{rel}: durée absente")
    if not has_material_policy(body):
        errors.append(f"{rel}: politique de matériel absente ou ambiguë")
    if (
        "capacités évaluées" not in lower
        and "capacites evaluees" not in lower
        and "capacité évaluée" not in lower
        and "capacite evaluee" not in lower
        and "capacites" not in lower
    ):
        errors.append(f"{rel}: capacités évaluées absentes")
    if structured_links:
        if "critère" not in lower and "critere" not in lower:
            errors.append(f"{rel}: critères observables absents")
        if "erreur fréquente" not in lower and "erreur frequente" not in lower and "cas limite" not in lower:
            errors.append(f"{rel}: cas limite ou erreur fréquente absent")
        errors.extend(check_linked_resources(root, path, metadata, questions, rel))
    else:
        marker_groups = {
            "critères de réussite": ["critères de réussite", "criteres de reussite"],
            "corrigé": ["corrigé", "corrige"],
            "erreurs fréquentes": ["erreurs fréquentes", "erreurs frequentes"],
            "remédiation": ["remédiation", "remediation"],
            "fiche liée": ["fiche liée", "fiche liee", "fiche de cours liée", "fiche de cours liee"],
        }
        for marker, alternatives in marker_groups.items():
            if not any(alternative in lower for alternative in alternatives):
                errors.append(f"{rel}: exigence évaluation manquante -> {marker}")
    if "aménagement" not in lower and "amenagement" not in lower and "version aménagée" not in lower:
        errors.append(f"{rel}: aménagement ou version aménagée absent")
    return errors


def analyze_linked_evaluation_quality(root: Path = ROOT, files: list[Path] | None = None) -> LinkedEvaluationQualityResult:
    result = LinkedEvaluationQualityResult()
    if files is not None:
        paths = {path.as_posix(): path for path in files}
    else:
        expected = expected_evaluation_files(root)
        paths = {reference: resolution.path for reference, resolution in expected.items() if resolution.path is not None}
        for reference, resolution in expected.items():
            if resolution.ambiguous:
                candidates = ", ".join(path.as_posix() for path in resolution.candidates)
                result.errors.append(f"{reference}: support évaluation ambigu -> {candidates}")
            elif resolution.absent:
                result.errors.append(f"{reference}: support évaluation absent")
    for path in paths.values():
        result.checked_files += 1
        result.errors.extend(analyze_one_evaluation(path, root))
    return result


def main() -> int:
    result = analyze_linked_evaluation_quality()
    if result.errors:
        print("check_linked_evaluation_quality: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_linked_evaluation_quality: PASS ({result.checked_files} évaluations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
