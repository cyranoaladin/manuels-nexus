#!/usr/bin/env python3
"""Check disciplinary substance of TD supports linked to operational sheets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import unicodedata

from scripts._qa_common import ROOT, strip_frontmatter
from scripts.check_linked_td_quality import target_td_files

GENERIC_PHRASES = [
    "résultat indicatif",
    "resultat indicatif",
    "réponse explicite attendue",
    "reponse explicite attendue",
    "solution explicite attendue",
    "démarche : partir de la donnée fournie",
    "demarche : partir de la donnee fournie",
    "isoler les grandeurs utiles",
    "conclusion explicite",
    "réponse cohérente",
    "reponse coherente",
    "production vérifiable",
    "production verifiable",
]

CONCRETE_PATTERNS = [
    r"\bSELECT\b.*\bFROM\b",
    r"\bINSERT\b|\bUPDATE\b|\bDELETE\b",
    r"\bTTL\b|\bACK\b|\bIP\b|\bTCP\b|\bHTTPS\b|\bRIP\b|\bOSPF\b",
    r"\broute\b|\bpaquet\b|\bpasserelle\b|\bmasque\b",
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

VAGUE_CORRECTION_PATTERNS = [
    r"\br[eé]ponse acceptable\b",
    r"\bexplique correctement\b",
    r"\bconclut correctement\b",
    r"\bmeilleure valeur\b",
    r"\bsituation\b",
    r"\bd[ée]marche vue en cours\b",
]


@dataclass
class TDSubstanceResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"`[^`]+`", "`code`", value)
    value = re.sub(r"\b\d+\b", "n", value)
    value = re.sub(r"[^a-z0-9_]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def has_concrete_evidence(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.I | re.S) for pattern in CONCRETE_PATTERNS)


def meaningful_words(text: str) -> list[str]:
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"^\s*\|.*\|\s*$", " ", text, flags=re.M)
    normalized = normalize(text)
    return [word for word in normalized.split() if word not in {"le", "la", "les", "un", "une", "de", "du", "des", "est"}]


def has_markdown_table(text: str) -> bool:
    return bool(re.search(r"^\s*\|.+\|\s*$", text, flags=re.M))


def mostly_table_without_interpretation(text: str) -> bool:
    if not has_markdown_table(text):
        return False
    return len(meaningful_words(text)) < 10


def contains_vague_only_answer(text: str) -> bool:
    normalized = normalize(text)
    if any(normalize(phrase) in normalized for phrase in GENERIC_PHRASES):
        return True
    return any(re.search(pattern, text, flags=re.I) for pattern in VAGUE_CORRECTION_PATTERNS)


def domain_for(path: Path) -> str:
    name = path.name.lower()
    if "sql" in name:
        return "sql"
    if any(token in name for token in ["bases_relationnelles", "relationnelles", "bdd", "cles_contraintes", "clés_contraintes"]):
        return "database"
    if any(token in name for token in ["reseaux", "protocoles", "routage", "chiffrement", "https"]):
        return "network"
    if any(token in name for token in ["tris", "dichotomie", "glouton", "knn", "parcours", "programmation_dynamique", "boyer", "diviser", "calculabilite"]):
        return "algorithm"
    if any(token in name for token in ["bases", "conversions", "complement", "booleens", "flottants", "unicode"]):
        return "representation"
    return "general"


def correction_has_substance(path: Path, exercise: str, correction: str) -> bool:
    text = correction.strip()
    if not text:
        return False
    if contains_vague_only_answer(text):
        return False
    if mostly_table_without_interpretation(text):
        return False
    words = meaningful_words(text)
    if len(words) < 10:
        return False

    lower = text.lower()
    structured_markers = sum(
        any(token in lower for token in alternatives)
        for alternatives in [
            ["donnée utilisée", "donnee utilisee", "donnée", "donnee"],
            ["méthode", "methode"],
            ["résultat", "resultat", "réponse attendue", "reponse attendue"],
            ["contrôle", "controle", "vérification", "verification"],
            ["erreur traitée", "erreur traitee", "erreur fréquente", "erreur frequente"],
        ]
    )
    concrete_count = sum(
        bool(re.search(pattern, text, flags=re.I | re.S))
        for pattern in [
            r"\b\d+\b",
            r"`[^`]+`",
            r"\"[^\"]+\"",
            r"«[^»]+»",
            r"\b[PT]-[A-Z0-9-]+\b",
            r"->|=>",
            r"\bTrue\b|\bFalse\b",
            r"```",
        ]
    )
    if structured_markers >= 4 or (structured_markers >= 3 and concrete_count >= 1):
        return True

    domain = domain_for(path)
    if domain == "sql":
        has_query = bool(re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b", text, flags=re.I))
        has_result = any(token in lower for token in ["résultat", "resultat", "renvoie", "ligne", "lignes", "après", "apres", "avant", "table contient"])
        return has_query and has_result and len(words) >= 12
    if domain == "network":
        markers = sum(
            token in lower
            for token in ["ttl", "ip", "ack", "tcp", "https", "rip", "ospf", "paquet", "route", "passerelle", "protocole", "source", "destination", "port", "certificat"]
        )
        decisions = sum(
            token in lower
            for token in ["détruit", "detruit", "retransmet", "renvoie", "envoie", "route", "refuse", "accepte", "reçoit", "recoit", "passe par"]
        )
        return markers >= 2 and (decisions >= 1 or structured_markers >= 3)
    if domain == "database":
        markers = sum(
            token in lower
            for token in [
                "clé primaire",
                "cle primaire",
                "clé étrangère",
                "cle etrangere",
                "contrainte",
                "référence",
                "reference",
                "id_eleve",
                "id_note",
                "table",
                "ligne",
            ]
        )
        decisions = sum(
            token in lower
            for token in ["cohérente", "coherente", "invalide", "refusée", "refusee", "existe", "absent", "orpheline", "domaine"]
        )
        return markers >= 2 and decisions >= 1 and concrete_count >= 1
    if domain == "algorithm":
        markers = sum(
            token in lower
            for token in [
                "pseudo-code",
                "pseudocode",
                "trace",
                "tableau",
                "récurrence",
                "recurrence",
                "invariant",
                "complexité",
                "complexite",
                "état",
                "etat",
                "initialisation",
                "dp[",
                "o(",
            ]
        )
        return markers >= 2
    if domain == "representation":
        markers = sum(token in lower for token in ["base", "binaire", "décimal", "decimal", "hexadécimal", "hexadecimal", "bit", "octet", "unicode", "utf-8", "complément", "booleen", "booléen"])
        return markers >= 1 and (bool(re.search(r"\b\d+\b", text)) or "`" in text)

    has_result_word = any(token in lower for token in ["résultat", "resultat", "réponse attendue", "reponse attendue", "donc", "car"])
    return has_result_word and concrete_count >= 1 and len(words) >= 12


def split_numbered_blocks(body: str, title: str) -> dict[int, str]:
    pattern = re.compile(
        rf"^###\s+{re.escape(title)}\s+(\d+)\b(.*?)(?=^###\s+{re.escape(title)}\s+\d+\b|^##\s+|\Z)",
        flags=re.M | re.S | re.I,
    )
    return {int(match.group(1)): match.group(2).strip() for match in pattern.finditer(body)}


def data_values(body: str) -> list[str]:
    values = []
    for match in re.finditer(r"Donn(?:é|e)es?\s*:\s*(.+)", body, flags=re.I):
        values.append(normalize(match.group(1)))
    return [value for value in values if value]


def domain_requirements(path: Path, body: str) -> list[str]:
    errors: list[str] = []
    name = path.name.lower()
    lower = body.lower()
    if "sql" in name:
        if "select" not in lower or " from " not in lower:
            errors.append("TD SQL sans requête SELECT/FROM concrète")
        if "résultat" not in lower and "resultat" not in lower and "|" not in body:
            errors.append("TD SQL sans résultat de requête vérifiable")
    if any(token in name for token in ["reseaux", "protocoles", "routage", "chiffrement", "https"]):
        markers = sum(token in lower for token in ["ttl", "ip", "ack", "paquet", "route", "passerelle", "https", "certificat"])
        if markers < 2:
            errors.append("TD réseau/sécurité sans champs, paquets, routes ou décisions explicites")
    if any(token in name for token in ["tris", "dichotomie", "glouton", "knn", "parcours", "programmation_dynamique", "boyer", "diviser", "calculabilite"]):
        markers = sum(
            token in lower
            for token in [
                "pseudo-code",
                "pseudocode",
                "trace",
                "tableau",
                "récurrence",
                "recurrence",
                "invariant",
                "complexité",
                "complexite",
            ]
        )
        if markers < 2:
            errors.append("TD algorithmique sans pseudo-code, trace, invariant, tableau ou complexité")
    return errors


def analyze_one_td(path: Path, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_frontmatter(text)
    rel = path.relative_to(root) if path.is_relative_to(root) else path
    lower = normalize(body)

    for phrase in GENERIC_PHRASES:
        if normalize(phrase) in lower:
            errors.append(f"{rel}: corrigé générique ou formulation non vérifiable -> {phrase}")

    exercises = split_numbered_blocks(body, "Exercice")
    corrections = split_numbered_blocks(body, "Corrigé exercice")
    for number, exercise in exercises.items():
        if len(normalize(exercise)) < 40:
            errors.append(f"{rel}: exercice {number} sans donnée propre suffisante")
        correction = corrections.get(number, "")
        if not correction:
            errors.append(f"{rel}: corrigé exercice {number} absent")
        elif not correction_has_substance(path, exercise, correction):
            errors.append(f"{rel}: corrigé exercice {number} sans preuve disciplinaire suffisante")

    values = data_values(body)
    if len(values) >= 8 and len(set(values)) < 5:
        errors.append(f"{rel}: les 8 exercices réutilisent trop souvent la même donnée")

    normalized_exercises = {normalize(block) for block in exercises.values()}
    if len(exercises) >= 8 and len(normalized_exercises) < 6:
        errors.append(f"{rel}: exercices quasi identiques, variation disciplinaire insuffisante")

    for message in domain_requirements(path, body):
        errors.append(f"{rel}: {message}")
    return errors


def analyze_linked_td_substance(root: Path = ROOT, files: list[Path] | None = None) -> TDSubstanceResult:
    result = TDSubstanceResult()
    paths = files if files is not None else target_td_files(root)
    for path in paths:
        result.checked_files += 1
        result.errors.extend(analyze_one_td(path, root))
    return result


def main() -> int:
    result = analyze_linked_td_substance()
    if result.errors:
        print("check_linked_td_substance: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_linked_td_substance: PASS ({result.checked_files} TD)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
