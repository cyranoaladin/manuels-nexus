#!/usr/bin/env python3
"""Check SQL examples against their announced results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re
import sqlite3

from scripts._qa_common import ROOT


TARGET_ROOTS = [
    ROOT / "03_progressions" / "supports" / "terminale" / "T10",
    ROOT / "03_progressions" / "fiches_cours" / "terminale" / "T10",
]

EXPECTED_LINE_RE = re.compile(r"(?:réponse|résultat|sortie|après|question)\s+(?:attendue?|finale?|secondaire|principale)?", re.I)
NOTE_FILTER_RE = re.compile(r"note\s*>=\s*(\d+)", re.I)
NAME_NOTE_RE = re.compile(r"\b([A-ZÉÈÀÂÊÎÔÛÇ][A-Za-zÉÈÀÂÊÎÔÛÇéèàâêîôûç-]+)\s+(\d{1,2})\b")
NAME_NOTE_TABLE_RE = re.compile(r"\|\s*([A-ZÉÈÀÂÊÎÔÛÇ][A-Za-zÉÈÀÂÊÎÔÛÇéèàâêîôûç-]+)\s*\|\s*(\d{1,2})\s*\|")
NON_PERSON_RESULT_WORDS = {"Question", "Réponse", "Reponse", "Exercice", "Point"}
UPDATE_RE = re.compile(r"\bUPDATE\s+\w+\s+SET\b", re.I)
DELETE_RE = re.compile(r"\bDELETE\s+FROM\s+\w+\b", re.I)
INSERT_RE = re.compile(r"\bINSERT\s+INTO\s+\w+\b", re.I)
SQL_IN_BACKTICKS_RE = re.compile(r"`\s*((?:SELECT|INSERT|UPDATE|DELETE)\b[^`]+?)\s*`", re.I | re.S)
SQL_LINE_RE = re.compile(r"\b((?:SELECT|INSERT|UPDATE|DELETE)\b[^;\n]*(?:;|$))", re.I)


INSTRUCTION_OPERATION_RE = {
    "WHERE": re.compile(r"\b(?:filtrer|ne garder que|lignes? (?:pour lesquelles?|où))\b", re.I),
    "JOIN": re.compile(r"\b(?:joindre|jointure|associer chaque note à (?:un|son) élève)\b", re.I),
    "INSERT": re.compile(r"\b(?:insérer|ajouter)\b", re.I),
    "UPDATE": re.compile(r"\b(?:mettre à jour|modifier)\b", re.I),
    "DELETE": re.compile(r"\b(?:supprimer|retirer|effacer)\b", re.I),
}
ANSWER_OPERATION_LABEL_RE = re.compile(
    r"(?:réponse|résultat)\s+attendu[e]?\s*:\s*(SELECT|WHERE|JOIN|INSERT|UPDATE|DELETE)\b",
    re.I,
)


@dataclass
class SqlConsistencyResult:
    errors: list[str] = field(default_factory=list)
    files_checked: int = 0


def expected_lines(text: str) -> list[str]:
    lines = text.splitlines()
    result: list[str] = []
    for line in lines:
        if EXPECTED_LINE_RE.search(line) or "JOIN ->" in line or "->" in line:
            result.append(line)
    return result


def line_is_warning(line: str) -> bool:
    return bool(
        re.search(
            r"sans\s+`?where|erreur|risque|dangereu|pi[eè]ge|trop large|"
            r"modifie toutes|supprime toutes|toutes les lignes|interdit",
            line,
            re.I,
        )
    )


def create_demo_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE Eleve(id_eleve INTEGER PRIMARY KEY, nom TEXT, classe TEXT)")
    conn.execute("CREATE TABLE Note(id_note INTEGER PRIMARY KEY, id_eleve INTEGER, matiere TEXT, note INTEGER)")
    conn.executemany(
        "INSERT INTO Eleve VALUES (?, ?, ?)",
        [(1, "Ada", "T1"), (2, "Linus", "T2"), (3, "Grace", "T1"), (4, "Alan", "T2")],
    )
    conn.executemany(
        "INSERT INTO Note VALUES (?, ?, ?, ?)",
        [
            (10, 1, "NSI", 17),
            (11, 2, "NSI", 13),
            (12, 3, "NSI", 15),
            (13, 1, "MATHS", 14),
            (14, 4, "NSI", 9),
            (15, 3, "MATHS", 18),
        ],
    )
    return conn


def normalize_query(query: str) -> str:
    query = re.sub(r"\s+", " ", query.strip().rstrip(";"))
    query = query.split("->", 1)[0].strip()
    return query


def execute_sql_query(query: str) -> list[tuple[Any, ...]]:
    query = normalize_query(query)
    if not query.upper().startswith("SELECT"):
        raise ValueError("not a SELECT query")
    with create_demo_connection() as conn:
        cursor = conn.execute(query)
        return [tuple(row) for row in cursor.fetchall()]


def execute_sql_update_summary(query: str) -> dict[int, int]:
    query = normalize_query(query)
    if not query.upper().startswith("UPDATE"):
        raise ValueError("not an UPDATE query")
    with create_demo_connection() as conn:
        conn.execute(query)
        rows = conn.execute("SELECT id_note, note FROM Note ORDER BY id_note").fetchall()
        return {int(id_note): int(note) for id_note, note in rows}


def execute_sql_delete_summary(query: str) -> dict[int, int]:
    query = normalize_query(query)
    if not query.upper().startswith("DELETE"):
        raise ValueError("not a DELETE query")
    with create_demo_connection() as conn:
        conn.execute(query)
        rows = conn.execute("SELECT id_note, note FROM Note ORDER BY id_note").fetchall()
        return {int(id_note): int(note) for id_note, note in rows}


def execute_sql_inserted_row(query: str, id_note: int) -> tuple[int, int, str, int] | None:
    query = normalize_query(query)
    if not query.upper().startswith("INSERT"):
        raise ValueError("not an INSERT query")
    with create_demo_connection() as conn:
        conn.execute(query)
        row = conn.execute(
            "SELECT id_note, id_eleve, matiere, note FROM Note WHERE id_note = ?",
            (id_note,),
        ).fetchone()
        if row is None:
            return None
        return int(row[0]), int(row[1]), str(row[2]), int(row[3])


def extract_sql_statements(text: str) -> list[str]:
    result: list[str] = []
    for regex in (SQL_IN_BACKTICKS_RE, SQL_LINE_RE):
        for match in regex.finditer(text):
            query = normalize_query(match.group(1))
            upper = query.upper()
            if upper.startswith("SELECT") and " FROM " not in f" {upper} ":
                continue
            if upper.startswith("DELETE") and " FROM " not in f" {upper} ":
                continue
            if upper.startswith("UPDATE") and " SET " not in f" {upper} ":
                continue
            if upper.startswith("INSERT") and " INTO " not in f" {upper} ":
                continue
            if upper.startswith("INSERT") and " VALUES " not in f" {upper} ":
                continue
            if query and query not in result:
                result.append(query)
    return result


def query_targets_demo_schema(query: str) -> bool:
    lowered = query.lower()
    return "eleve" in lowered or "note" in lowered


def announced_person_note_pairs(text: str) -> list[tuple[str, int]]:
    pairs: list[tuple[str, int]] = []
    for line in expected_lines(text):
        for name, raw_note in NAME_NOTE_RE.findall(line):
            if name not in NON_PERSON_RESULT_WORDS:
                pairs.append((name, int(raw_note)))
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not re.search(r"\|\s*nom\s*\|\s*note\s*\|", line, re.I):
            continue
        for row in lines[index + 2:]:
            if not row.lstrip().startswith("|"):
                break
            match = NAME_NOTE_TABLE_RE.search(row)
            if not match:
                continue
            name, raw_note = match.groups()
            if name not in NON_PERSON_RESULT_WORDS and name.lower() not in {"nom", "note"}:
                pairs.append((name, int(raw_note)))
    return pairs


def split_markdown_sections(text: str) -> list[str]:
    """Keep each heading with its body so query/result pairs stay local."""
    starts = [match.start() for match in re.finditer(r"(?m)^#{2,6}\s+", text)]
    if not starts:
        return [text]
    sections: list[str] = []
    if starts[0] > 0:
        sections.append(text[:starts[0]])
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        sections.append(text[start:end])
    return [section for section in sections if section.strip()]


def sql_block_errors(text: str) -> list[str]:
    errors: list[str] = []
    statements = extract_sql_statements(text)

    lines = text.splitlines()
    for index, line in enumerate(lines):
        answer_match = ANSWER_OPERATION_LABEL_RE.search(line)
        if not answer_match:
            continue
        announced_operation = answer_match.group(1).upper()
        local_instruction = " ".join(lines[max(0, index - 3):index])
        expected_operations = {
            operation
            for operation, regex in INSTRUCTION_OPERATION_RE.items()
            if regex.search(local_instruction)
        }
        if len(expected_operations) != 1:
            continue
        expected = next(iter(expected_operations))
        allowed_labels = {expected}
        if expected in {"WHERE", "JOIN"}:
            allowed_labels.add("SELECT")
        if announced_operation not in allowed_labels:
            errors.append(
                f"consigne {expected} associée à une réponse étiquetée {announced_operation}"
            )

    filters = [int(value) for value in NOTE_FILTER_RE.findall(text)]
    for threshold in filters:
        for line in expected_lines(text):
            for name, raw_note in NAME_NOTE_RE.findall(line):
                if name in NON_PERSON_RESULT_WORDS:
                    continue
                note = int(raw_note)
                if note < threshold:
                    errors.append(
                        f"condition note >= {threshold} contredite par le résultat {name} {note}"
                    )

    all_lines = text.splitlines()
    section_is_warning = line_is_warning(text)
    for index, line in enumerate(all_lines):
        context = " ".join(all_lines[max(0, index - 2):min(len(all_lines), index + 3)])
        complete_statement = ";" in line
        if (
            complete_statement
            and UPDATE_RE.search(line)
            and "WHERE" not in line.upper()
            and not section_is_warning
            and not line_is_warning(context)
        ):
            errors.append("UPDATE sans WHERE présenté comme requête opérationnelle")
        if (
            complete_statement
            and DELETE_RE.search(line)
            and "WHERE" not in line.upper()
            and not section_is_warning
            and not line_is_warning(context)
        ):
            errors.append("DELETE sans WHERE présenté comme requête opérationnelle")
        is_join_query = bool(re.search(r"(?:^|`|\s)SELECT\s+.+?\s+FROM\s+.+?\s+JOIN\b", line, re.I))
        if is_join_query and " ON " not in f" {line.upper()} ":
            if not re.search(r"sans\s+on|cartésien|non maîtrisée|erreur|cas limite", line, re.I):
                errors.append("JOIN sans condition non signalée comme produit cartésien ou erreur")

    for query in statements:
        upper = query.upper()
        if " JOIN " in upper and " ON " not in f" {upper} ":
            if not re.search(r"sans\s+on|cartésien|produit cartésien|erreur|interdit", text, re.I):
                errors.append("JOIN sans ON non traité explicitement comme produit cartésien")
        if not query_targets_demo_schema(query):
            continue
        try:
            if upper.startswith("SELECT"):
                actual = execute_sql_query(query)
                expected_pairs = announced_person_note_pairs(text)
                has_note_result_table = bool(re.search(r"\|\s*nom\s*\|\s*note\s*\|", text, re.I))
                projects_name_note = bool(
                    re.search(
                        r"SELECT\s+(?:\w+\.)?nom\s*,\s*(?:\w+\.)?note\s+FROM\b",
                        query,
                        re.I,
                    )
                )
                if expected_pairs and has_note_result_table and projects_name_note and actual and len(actual[0]) >= 2:
                    actual_pairs = {(str(row[0]), int(row[1])) for row in actual if len(row) >= 2 and isinstance(row[1], int)}
                    expected_set = set(expected_pairs)
                    if expected_set != actual_pairs:
                        errors.append(
                            f"résultat SQL annoncé {sorted(expected_set)} différent du résultat SQLite {sorted(actual_pairs)}"
                        )
            elif upper.startswith("UPDATE") and "WHERE" in upper:
                summary = execute_sql_update_summary(query)
                if re.search(r"Ada\s+18", text) and summary.get(10) != 18:
                    errors.append("UPDATE annoncé Ada 18 mais SQLite ne produit pas Ada 18")
                if re.search(r"Linus\s+18", text) and summary.get(11) != 18:
                    errors.append("UPDATE annoncé Linus 18 mais la requête ciblée ne le modifie pas")
            elif upper.startswith("DELETE") and "WHERE" in upper:
                summary = execute_sql_delete_summary(query)
                if re.search(r"Linus\s+(?:retiré|retire|supprimé|supprime|absent)", text, re.I) and 11 in summary:
                    errors.append("DELETE annoncé Linus retiré mais SQLite le conserve")
                if re.search(r"Ada\s+(?:retirée|retiree|supprimée|supprimee|absent)", text, re.I) and 10 in summary:
                    errors.append("DELETE annoncé Ada retirée mais SQLite la conserve")
            elif upper.startswith("INSERT"):
                with create_demo_connection() as conn:
                    conn.execute(query)
        except sqlite3.Error as exc:
            if not re.search(r"erreur|interdit|corriger|à éviter|a éviter", text, re.I):
                errors.append(f"requête SQL non exécutable sur le schéma de référence: {query} ({exc})")

    if re.search(r"UPDATE\s+Note\s+SET\s+note\s*=\s*18\s+WHERE\s+id_note\s*=\s*10", text, re.I):
        if re.search(r"Linus\s+18", text):
            errors.append("UPDATE id_note=10 modifie Linus alors que seule la note d'Ada est ciblée")
    if re.search(r"DELETE\s+FROM\s+Note\s+WHERE\s+id_note\s*=\s*11", text, re.I):
        if re.search(r"Ada\s+(?:retirée|supprimée|effacée)", text, re.I):
            errors.append("DELETE id_note=11 retire Ada alors que seule la note de Linus est ciblée")
    return errors


def sql_block_is_consistent(text: str) -> bool:
    return not sql_block_errors(text)


def candidate_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for base in TARGET_ROOTS:
        if not base.exists():
            continue
        files.extend(sorted(base.glob("*.md")))
    return files


def analyze_sql_query_result_consistency(root: Path = ROOT) -> SqlConsistencyResult:
    result = SqlConsistencyResult()
    for path in candidate_files(root):
        result.files_checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for section in split_markdown_sections(text):
            for error in sql_block_errors(section):
                result.errors.append(f"{path.relative_to(root).as_posix()}: {error}")
    return result


def main() -> int:
    result = analyze_sql_query_result_consistency()
    if result.errors:
        print("check_sql_query_result_consistency: KO")
        for error in result.errors[:200]:
            print(f"- {error}")
        return 1
    print(f"check_sql_query_result_consistency: PASS ({result.files_checked} fichiers T10)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
