#!/usr/bin/env python3
"""Check semantic consistency of missing_documents_register_v2.md."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import unicodedata

from scripts._qa_common import ROOT, read_frontmatter, sequence_id_from_path
from scripts._course_sheets_common import parse_markdown_table, sheet_files

REGISTER = "missing_documents_register_v2.md"
BLOCKING_SECTION = "supports absents bloquant une fiche liée"
GENERAL_SECTION = "dettes pédagogiques générales"
ARCHIVE_SECTION = "archives"

GENERIC_TOKENS = {
    "fiche",
    "cours",
    "supports",
    "support",
    "td",
    "tp",
    "evaluation",
    "evaluations",
    "premiere",
    "terminale",
    "sequence",
    "seance",
    "projet",
    "oral",
}

FORBIDDEN_THEME_PAIRS = [
    ({"reseaux", "reseau", "paquets", "routage"}, {"web", "html", "css", "dom", "http"}),
    ({"reseaux", "reseau", "paquets"}, {"fonctions", "tests", "specifications"}),
    ({"web", "html", "css", "dom"}, {"fonctions", "tests", "specifications"}),
    ({"graphes", "graphe"}, {"arbres", "abr", "recherche"}),
    ({"bdd", "bases", "donnees", "sql"}, {"graphes", "graphe"}),
    ({"architecture", "processus"}, {"bfs", "dfs", "cycles", "chemins"}),
]


@dataclass
class RegisterRow:
    section: str
    values: dict[str, str]


@dataclass
class SemanticRegisterResult:
    errors: list[str] = field(default_factory=list)
    checked_rows: int = 0


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokens(value: str) -> set[str]:
    return {token for token in normalize_text(value).split() if len(token) > 2 and token not in GENERIC_TOKENS}


def section_key(title: str) -> str:
    normalized = normalize_text(title)
    if BLOCKING_SECTION.replace("é", "e") in normalized:
        return "blocking"
    if GENERAL_SECTION in normalized:
        return "general"
    if ARCHIVE_SECTION in normalized or "abandon" in normalized:
        return "archive"
    return "other"


def register_rows(root: Path) -> list[RegisterRow]:
    path = root / REGISTER
    if not path.exists():
        return []
    rows: list[RegisterRow] = []
    section = "other"
    table_lines: list[str] = []

    def flush() -> None:
        nonlocal table_lines
        if not table_lines:
            return
        parsed = parse_markdown_table("\n".join(table_lines))
        rows.extend(RegisterRow(section, row) for row in parsed if "Fichier" in row)
        table_lines = []

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("## "):
            flush()
            section = section_key(line.lstrip("# ").strip())
        elif line.startswith("|"):
            table_lines.append(line)
        else:
            flush()
    flush()
    return rows


def sheet_index(root: Path) -> dict[str, tuple[Path, dict[str, object], set[str]]]:
    index: dict[str, tuple[Path, dict[str, object], set[str]]] = {}
    for path in sheet_files(root):
        metadata = read_frontmatter(path)
        haystack = " ".join(
            [
                path.stem,
                str(metadata.get("theme") or ""),
                str(metadata.get("notion") or ""),
                str(metadata.get("sequence_id") or ""),
            ]
        )
        index[path.name] = (path, metadata, tokens(haystack))
    return index


def fiche_names(value: str) -> list[str]:
    if not value:
        return []
    raw = re.split(r"[;,]", value)
    return [item.strip() for item in raw if item.strip() and item.strip().lower() not in {"na", "n/a", "aucune"}]


def theme_pair_forbidden(file_tokens: set[str], fiche_tokens: set[str]) -> bool:
    for left, right in FORBIDDEN_THEME_PAIRS:
        if file_tokens & left and fiche_tokens & right:
            return True
        if file_tokens & right and fiche_tokens & left:
            return True
    return False


def analyze_missing_register_semantic_consistency(root: Path = ROOT) -> SemanticRegisterResult:
    result = SemanticRegisterResult()
    path = root / REGISTER
    if not path.exists():
        result.errors.append(f"{REGISTER} absent")
        return result
    sheets = sheet_index(root)
    for item in register_rows(root):
        row = item.values
        filename = row.get("Fichier", "").strip()
        if not filename:
            continue
        result.checked_rows += 1
        status = normalize_text(row.get("Statut", ""))
        decision = normalize_text(row.get("Décision", row.get("Decision", "")))
        sequence = row.get("Séquence", row.get("Sequence", "")).strip()
        file_prefix = filename[:3] if re.match(r"^[PT]\d{2}", filename) else ""

        if status == "absent" and file_prefix and sequence != file_prefix:
            result.errors.append(f"{filename}: préfixe {file_prefix} incohérent avec séquence {sequence}")
        if item.section == "archive" and decision != "abandonner":
            result.errors.append(f"{filename}: archive/abandon sans décision abandonner")

        file_tokens = tokens(filename)
        for fiche in fiche_names(row.get("Fiche(s) concernée(s)", "")):
            if fiche in {"progression annuelle", "aucune fiche liée", "aucune fiche opérationnelle"}:
                continue
            if fiche not in sheets:
                if item.section == "blocking":
                    result.errors.append(f"{filename}: fiche concernée introuvable -> {fiche}")
                continue
            sheet_path, metadata, fiche_tokens = sheets[fiche]
            sheet_sequence = str(metadata.get("sequence_id") or sequence_id_from_path(sheet_path))
            readiness = str(metadata.get("readiness") or "").strip()
            if sequence and sheet_sequence != sequence:
                result.errors.append(f"{filename}: séquence registre {sequence} différente de la fiche {sheet_sequence}")
            if status == "absent" and item.section == "blocking" and readiness == "operational":
                result.errors.append(f"{filename}: fiche opérationnelle listée comme bloquée -> {fiche}")
            if status == "absent" and item.section != "archive":
                overlap = file_tokens & fiche_tokens
                if not overlap:
                    result.errors.append(f"{filename}: thème incohérent avec {fiche}")
                if theme_pair_forbidden(file_tokens, fiche_tokens):
                    result.errors.append(f"{filename}: thème incohérent, association thématique suspecte avec {fiche}")
    return result


def main() -> int:
    result = analyze_missing_register_semantic_consistency()
    if result.errors:
        print("check_missing_register_semantic_consistency: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_missing_register_semantic_consistency: PASS ({result.checked_rows} lignes vérifiées)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
