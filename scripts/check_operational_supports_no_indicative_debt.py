#!/usr/bin/env python3
"""Reject operational supports that are formally present but pedagogically hollow.

The gate checks semantic structure instead of demanding a fixed vocabulary or a
line-count target.  It remains fail-closed: titles without content, empty linked
resources and evaluations without real questions are rejected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter, strip_frontmatter
from scripts._operational_links import operational_resource_links, resolve_reference
from scripts.check_linked_evaluation_quality import analyze_one_evaluation, is_substantive_linked_resource

# TP remain subject to a non-negotiable depth floor.  The semantic profiles below
# replace brittle wording checks for TD/evaluations, not this operational safeguard.
MIN_LINES = {
    "td": 80,
    "evaluation": 55,
    "tp": 80,
    "cours": 100,
    "trace": 45,
}

SECTION_HEADING = re.compile(r"^(#{1,4})\s+(.+)$", re.M)
EXERCISE_HEADING = re.compile(r"^#{2,4}\s+Exercice\s+\d+\b", re.M | re.I)
EXERCISE_TITLE = re.compile(r"^#{2,4}\s+Exercice\s+\d+\b.*$", re.M | re.I)
OBJECTIVE_HEADING = re.compile(
    r"\b(objectifs?(?:\s+de\s+s[ée]ance|\s+op[ée]rationnels?)?|capacit[ée]s?\s+"
    r"(?:[ée]valu[ée]es|travaill[ée]es))\b",
    re.I,
)
CORRECTION_HEADING = re.compile(r"\b(corrig[ée]|rep[èe]res?\s+de\s+correction|r[ée]ponse\s+attendue)\b", re.I)
DIFFERENTIATION_HEADING = re.compile(
    r"\b(diff[ée]renciation|aides?\s+(gradu[ée]es|progressives)|version\s+am[ée]nag[ée]e|"
    r"[ée]tapes?\s+guid[ée]es|espaces?\s+de\s+r[ée]ponse|aide\s+[123])\b",
    re.I,
)
ERROR_OR_BOUNDARY_HEADING = re.compile(r"\b(erreurs?\s+fr[ée]quentes?|cas\s+limites?|pi[èe]ges?)\b", re.I)
RESOURCE_FIELDS = {
    "barème": ("bareme", "barème"),
    "corrigé": ("corrige", "corrigé"),
    "remédiation": ("remediation", "remédiation"),
    "trace": ("trace",),
    "version aménagée": ("version_amenagee", "version aménagée"),
    "fiche": ("fiche", "support"),
}


@dataclass
class OperationalDebtResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def linked_operational_supports(root: Path = ROOT) -> tuple[list[Path], list[str]]:
    supports: dict[str, Path] = {}
    errors: list[str] = []
    for resource in operational_resource_links(root):
        if resource.resolution.ambiguous:
            candidates = ", ".join(path.as_posix() for path in resource.resolution.candidates)
            errors.append(f"{resource.link.file}: support opérationnel ambigu -> {candidates}")
            continue
        if resource.path and resource.path.suffix == ".md":
            supports[resource.path.as_posix()] = resource.path
    return [supports[key] for key in sorted(supports)], errors


def infer_kind(path: Path, metadata: dict[str, object]) -> str:
    kind = str(metadata.get("document_type") or "").strip().lower()
    if kind:
        return kind
    name = path.name.lower()
    if "_td_" in name:
        return "td"
    if "_evaluation_" in name:
        return "evaluation"
    if "_tp_" in name:
        return "tp"
    return "support"


def section_contents(body: str, heading_pattern: re.Pattern[str]) -> list[str]:
    """Return non-empty section bodies whose title matches ``heading_pattern``."""
    headings = list(SECTION_HEADING.finditer(body))
    contents: list[str] = []
    for index, heading in enumerate(headings):
        if not heading_pattern.search(heading.group(2)):
            continue
        level = len(heading.group(1))
        end = len(body)
        for following in headings[index + 1:]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        contents.append(body[heading.end():end].strip())
    return contents


def has_substantive_section(body: str, heading_pattern: re.Pattern[str], *, min_words: int = 5) -> bool:
    return any(len(re.findall(r"\w+", content)) >= min_words for content in section_contents(body, heading_pattern))


def has_tiered_tasks(body: str) -> bool:
    """Accept explicit socle/standard/approfondissement levels when attached to tasks."""
    headings = EXERCISE_TITLE.findall(body)
    lower = "\n".join(headings).lower()
    return all(level in lower for level in ("socle", "standard", "approfondissement"))


def declared_reference(metadata: dict[str, object], fields: tuple[str, ...]) -> str | None:
    for field_name in fields:
        value = metadata.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def resolve_declared_resource(root: Path, support: Path, reference: str) -> Path | None:
    local = support.parent / reference
    if local.exists():
        return local
    return resolve_reference(root, reference).path


def validate_declared_resources(root: Path, support: Path, metadata: dict[str, object], rel: Path) -> list[str]:
    """Fail closed for every declared linked resource, while leaving optional links optional."""
    errors: list[str] = []
    for resource_type, fields in RESOURCE_FIELDS.items():
        reference = declared_reference(metadata, fields)
        if reference is None:
            continue
        resource = resolve_declared_resource(root, support, reference)
        if resource is None:
            errors.append(f"{rel}: {resource_type} lié absent -> {reference}")
        elif not is_substantive_linked_resource(resource):
            errors.append(f"{rel}: {resource_type} lié trop pauvre -> {reference}")
    return errors


def has_declared_capacity(metadata: dict[str, object]) -> bool:
    official = metadata.get("official_program")
    return isinstance(official, dict) and isinstance(official.get("capacities"), list) and bool(official["capacities"])


def analyze_td(body: str, metadata: dict[str, object], rel: Path) -> list[str]:
    errors: list[str] = []
    objective_ok = has_substantive_section(body, OBJECTIVE_HEADING) or has_declared_capacity(metadata)
    if not objective_ok:
        errors.append(f"{rel}: objectif ou capacité disciplinaire substantielle absent")
    exercises = len(EXERCISE_HEADING.findall(body))
    if exercises < 4:
        errors.append(f"{rel}: au moins 4 tâches numérotées attendues, trouvé {exercises}")
    if not has_substantive_section(body, CORRECTION_HEADING, min_words=10):
        errors.append(f"{rel}: correction ou repères de correction substantiels absents")
    if not has_substantive_section(body, DIFFERENTIATION_HEADING) and not has_tiered_tasks(body):
        errors.append(f"{rel}: différenciation ou aides graduées substantielles absentes")
    if not has_substantive_section(body, ERROR_OR_BOUNDARY_HEADING, min_words=4):
        errors.append(f"{rel}: cas limite, piège ou erreur fréquente absent")
    return errors


def analyze_evaluation(root: Path, support: Path, rel: Path) -> list[str]:
    """Delegate question and linked-resource checks to the specialised semantic gate."""
    return analyze_one_evaluation(support, root)


def analyze_tp(body: str, rel: Path) -> list[str]:
    """Keep the TP depth floor while requiring its operational structure."""
    errors: list[str] = []
    useful_lines = [line for line in body.splitlines() if line.strip()]
    minimum = MIN_LINES["tp"]
    if len(useful_lines) < minimum:
        errors.append(f"{rel}: profondeur TP insuffisante ({len(useful_lines)} lignes utiles, minimum {minimum})")
    required_sections = {
        "objectif": OBJECTIVE_HEADING,
        # A TP can phrase the student task as a consigne, a requested piece of
        # work, a staged procedure or an entry activity; each remains an actual
        # instruction section and must contain content.
        "consignes": re.compile(
            r"\b(consignes?|travail\s+demand[ée]|[ée]tapes?\s+de\s+r[ée]alisation|"
            r"d[ée]roul[ée]\s+en\s+classe|activit[ée]\s+d['’]entr[ée]e)\b",
            re.I,
        ),
        # Tests can be explicitly named or embedded in a validation protocol.
        "tests": re.compile(r"\b(tests?|protocole\s+de\s+validation|validation\s+op[ée]rationnelle)\b", re.I),
        # An expected trace or an explicit validation protocol is a verifiable
        # deliverable; a bare heading without content remains rejected.
        "livrable": re.compile(
            r"\b(livrable|trace\s+attendue|validation\s+op[ée]rationnelle|protocole\s+de\s+validation)\b",
            re.I,
        ),
        "critères de réussite": re.compile(r"\bcrit[èe]res?\s+de\s+r[ée]ussite\b", re.I),
    }
    for label, pattern in required_sections.items():
        if not has_substantive_section(body, pattern):
            errors.append(f"{rel}: section TP substantielle absente -> {label}")
    return errors


def analyze_operational_supports_no_indicative_debt(
    root: Path = ROOT,
    files: list[Path] | None = None,
) -> OperationalDebtResult:
    result = OperationalDebtResult()
    if files is None:
        supports, link_errors = linked_operational_supports(root)
        result.errors.extend(link_errors)
    else:
        supports = files
    for path in supports:
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        body = strip_frontmatter(text)
        metadata = read_frontmatter(path)
        kind = infer_kind(path, metadata)
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        if not text.lstrip().startswith("---"):
            result.errors.append(f"{rel}: frontmatter absent")
        if "\n# " not in "\n" + text:
            result.errors.append(f"{rel}: titre niveau 1 absent")
        if "\n## " not in text:
            result.errors.append(f"{rel}: sections niveau 2 absentes")
        result.errors.extend(validate_declared_resources(root, path, metadata, rel))
        if kind == "td":
            result.errors.extend(analyze_td(body, metadata, rel))
        elif kind == "evaluation":
            result.errors.extend(analyze_evaluation(root, path, rel))
        elif kind == "tp":
            result.errors.extend(analyze_tp(body, rel))
        elif len(re.findall(r"\w+", body)) < 40:
            result.errors.append(f"{rel}: support trop pauvre")
    return result


def main() -> int:
    result = analyze_operational_supports_no_indicative_debt()
    if result.errors:
        print("check_operational_supports_no_indicative_debt: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_operational_supports_no_indicative_debt: PASS ({result.checked_files} supports)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
