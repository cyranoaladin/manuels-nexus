#!/usr/bin/env python3
"""Check that course documents are explanatory courses, not answer sheets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter, strip_frontmatter


COURSE_RE = re.compile(r"(^|_)cours_", re.I)
GENERIC_SECTION_ONLY_RE = re.compile(
    r"Objectifs spécifiques\s*#+\s*À savoir\s*#+\s*Méthodes\s*#+\s*Exemples corrigés\s*#+\s*Critères",
    re.I | re.S,
)


@dataclass
class CourseQualityResult:
    errors: list[str] = field(default_factory=list)
    files_checked: int = 0


def useful_word_count(text: str) -> int:
    body = strip_frontmatter(text)
    body = re.sub(r"^#+.*$", " ", body, flags=re.M)
    return len(re.findall(r"\b[\wÀ-ÿ]{3,}\b", body))


def count_heading_or_marker(text: str, pattern: str) -> int:
    return len(re.findall(pattern, strip_frontmatter(text), re.I))


def section_text(text: str, heading_pattern: str) -> str:
    body = strip_frontmatter(text)
    match = re.search(rf"^##\s+{heading_pattern}\s*$", body, flags=re.I | re.M)
    if not match:
        return ""
    next_heading = re.search(r"^##\s+", body[match.end() :], flags=re.M)
    end = match.end() + next_heading.start() if next_heading else len(body)
    return body[match.end() : end]


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÿ]{3,}\b", value))


DISCIPLINARY_TERMS_RE = re.compile(
    r"\b(?:algorithme|complexité|invariant|variable|fonction|assertion|test|table|clé|"
    r"dictionnaire|liste|tuple|csv|sql|select|join|graphe|sommet|arête|file|pile|"
    r"arbre|abr|routage|paquet|ttl|adresse|http|https|processus|mémoire|"
    r"récurrence|dynamique|boyer|moore|unicode|binaire|hexadécimal|dichotomie|"
    r"glouton|distance|voisin|calculabilité|arrêt|oral|projet|certificat|api)\b",
    re.I,
)


def introductory_block(text: str) -> str:
    body = strip_frontmatter(text)
    match = re.search(r"^##\s+Exemples corrigés", body, flags=re.I | re.M)
    return body[: match.start()] if match else body[:1600]


def course_quality_errors(text: str, rel: str) -> list[str]:
    errors: list[str] = []
    body = strip_frontmatter(text)
    intro = introductory_block(text)
    if useful_word_count(text) < 220:
        errors.append(f"{rel}: cours trop court pour être autonome")
    if GENERIC_SECTION_ONLY_RE.search(body) and useful_word_count(text) < 80:
        errors.append(f"{rel}: structure de fiche sans explication disciplinaire")
    if not re.search(r"Situation-problème|Situation-probleme|À savoir|A savoir|Définition|Definition", intro, re.I):
        errors.append(f"{rel}: introduction conceptuelle insuffisamment explicative")
    if word_count(intro) < 35:
        errors.append(f"{rel}: introduction conceptuelle trop courte")
    if count_heading_or_marker(text, r"Exemple corrigé\s+\d+|###\s+Exemple") < 3:
        errors.append(f"{rel}: moins de trois exemples gradués")
    if count_heading_or_marker(text, r"erreur fréquente|##\s+Erreurs fréquentes|-\s+[^.\n]*(?:confond|oublie|écrase|inverse|omet|mélange)") < 2:
        errors.append(f"{rel}: erreurs fréquentes spécifiques insuffisantes")
    if count_heading_or_marker(text, r"cas limite|vide|absent|invalide|doublon|exception|interblocage") < 2:
        errors.append(f"{rel}: cas limites spécifiques insuffisants")
    if not re.search(r"##\s+(?:Critères|À retenir|A retenir|Synthèse|Synthese)", body, re.I):
        errors.append(f"{rel}: synthèse finale ou critères de révision absents")
    if not re.search(r"[PT](?:-[A-Z]+)+-\d{2}[A-Z]?", text):
        errors.append(f"{rel}: capacité officielle non citée")
    has_knowledge = bool(re.search(r"À savoir|A savoir|Définitions?|Definitions?|formalisation|savoir\b", body, re.I))
    has_method = bool(re.search(r"Méthodes?|Methodes?|savoir-faire|Démarche attendue|Demarche attendue", body, re.I))
    if not has_knowledge or not has_method:
        errors.append(f"{rel}: distinction savoir / savoir-faire / méthode insuffisante")
    operational_re = r"\b(?:calculer|trier|filtrer|tester|vérifier|convertir|parcourir|chercher|joindre|simuler|implémenter|exécuter|expliquer|identifier|définir|comparer|isoler|associer|préparer|contrôler|appliquer|produire|corriger|reconstruire)\b"
    methods = section_text(text, r"Méthodes?|Methodes?") + "\n" + section_text(
        text, r"Savoir-faire et méthodes opérationnelles|Savoir-faire et methodes operationnelles"
    )
    method_hits = len(re.findall(operational_re, methods, re.I))
    body_hits = len(re.findall(operational_re, body, re.I))
    if method_hits < 2 and body_hits < 6:
        errors.append(f"{rel}: méthodes trop peu opérationnelles")
    if len(DISCIPLINARY_TERMS_RE.findall(body)) < 8:
        errors.append(f"{rel}: vocabulaire disciplinaire propre à la notion insuffisant")
    return errors


def candidate_courses(root: Path = ROOT) -> list[Path]:
    paths: list[Path] = []
    base = root / "03_progressions" / "supports"
    for path in sorted(base.rglob("*.md")):
        metadata = read_frontmatter(path)
        if str(metadata.get("document_type", "")).lower() == "cours" or COURSE_RE.search(path.name):
            paths.append(path)
    return paths


def analyze_course_explanatory_quality(root: Path = ROOT) -> CourseQualityResult:
    result = CourseQualityResult()
    for path in candidate_courses(root):
        result.files_checked += 1
        rel = path.relative_to(root).as_posix()
        result.errors.extend(course_quality_errors(path.read_text(encoding="utf-8", errors="replace"), rel))
    return result


def main() -> int:
    result = analyze_course_explanatory_quality()
    if result.errors:
        print("check_course_explanatory_quality: KO")
        for error in result.errors[:200]:
            print(f"- {error}")
        return 1
    print(f"check_course_explanatory_quality: PASS ({result.files_checked} cours)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
