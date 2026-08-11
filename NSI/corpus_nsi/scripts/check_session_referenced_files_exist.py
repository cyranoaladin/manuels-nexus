#!/usr/bin/env python3
"""Check that session planning references real, specific teaching supports."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path

from scripts._qa_common import load_pilot_scope

ROOT = Path(__file__).resolve().parents[1]
SESSION_FILES = [
    ROOT / "03_progressions/seances_premiere.md",
    ROOT / "03_progressions/seances_terminale.md",
]
REGISTER = ROOT / "missing_documents_register_v2.md"

FILE_REF_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*\.[a-z]{2,4})\b")
SESSION_RE = re.compile(r"^### Séance ([PT]\d{2}-S\d+)", re.M)
SPECIFIC_RE = re.compile(r"^[PT]\d{2}_[A-Za-z0-9_]+\.[a-z]{2,4}$")
FIRST_BATCH_PREFIXES = set(load_pilot_scope().get("first_batch_prefixes", []))

REF_FIELDS = {
    "Document utilisé",
    "Livrable",
    "Trace écrite",
    "Devoir ou préparation",
    "Remédiation",
    "Livrable projet",
}
GENERIC_FILES = {
    "cours_eleve.md",
    "td.md",
    "tp.md",
    "corrige.md",
    "trace_ecrite.md",
    "evaluation.md",
    "bareme.md",
    "version_amenagee.md",
    "fiche_methode.md",
    "aides_progressives.md",
}
GLOBAL_ALLOWLIST = {"carnet_de_bord.md"}
CRITICAL_TYPES = {"cours", "td", "tp", "évaluation", "evaluation", "corrigé", "corrige", "trace", "barème", "bareme"}
REGISTER_COLUMNS = [
    "Fichier",
    "Niveau",
    "Séquence",
    "Séance(s)",
    "Type",
    "Priorité",
    "Statut",
    "Responsable",
    "Date cible",
    "Source possible",
    "Lien Drive éventuel",
    "Dépendance",
    "Décision",
    "Blocage si absent",
]
REGISTER_EXTRA_COLUMNS = [
    "Fiche(s) concernée(s)",
    "Impact pédagogique",
]
DECISIONS = {"créer", "importer", "abandonner"}


@dataclass
class SessionInfo:
    session_id: str
    block: str
    refs: list[str]
    specific_refs: list[str]
    generic_refs: list[str]
    existing_specific_refs: list[str]
    theoretical: bool


@dataclass
class AnalysisResult:
    errors: list[str] = field(default_factory=list)
    total_sessions: int = 0
    ready_sessions: int = 0
    theoretical_sessions: int = 0
    first_batch_ready: int = 0
    first_batch_theoretical: int = 0

    @property
    def usable_percent(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return round(self.ready_sessions * 100 / self.total_sessions, 1)


def parse_register(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    if not path.exists():
        return {}, [f"{path.name} absent"]
    rows: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    header: list[str] | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| ") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0] == "Fichier":
            header = cells
            if header not in (REGISTER_COLUMNS, REGISTER_COLUMNS + REGISTER_EXTRA_COLUMNS):
                errors.append(f"{path.name}: colonnes invalides")
            continue
        if not cells or header is None:
            continue
        if len(cells) != len(header):
            errors.append(f"{path.name}: ligne mal formée -> {line[:120]}")
            continue
        row = dict(zip(header, cells))
        filename = row["Fichier"].strip("`")
        rows[filename] = row
        for key in header:
            if not row[key]:
                errors.append(f"{filename}: champ registre vide -> {key}")
        if row["Décision"].lower() not in DECISIONS:
            errors.append(f"{filename}: Décision invalide -> {row['Décision']}")
        if row["Priorité"].lower() == "haute" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["Date cible"]):
            errors.append(f"{filename}: priorité haute sans date cible précise")
    return rows, errors


def session_blocks(session_path: Path) -> list[tuple[str, str]]:
    text = session_path.read_text(encoding="utf-8", errors="replace")
    starts = [(m.group(1), m.start()) for m in SESSION_RE.finditer(text)]
    blocks: list[tuple[str, str]] = []
    for index, (session_id, start) in enumerate(starts):
        end = starts[index + 1][1] if index + 1 < len(starts) else len(text)
        blocks.append((session_id, text[start:end]))
    return blocks


def extract_refs(block: str) -> list[str]:
    refs: list[str] = []
    for line in block.splitlines():
        if not line.startswith("- ") or " : " not in line:
            continue
        key, value = line[2:].split(" : ", 1)
        if key.strip() not in REF_FIELDS:
            continue
        for match in FILE_REF_RE.finditer(value):
            filename = match.group(1)
            if filename not in refs and filename not in GLOBAL_ALLOWLIST:
                refs.append(filename)
    return refs


def file_exists_anywhere(root: Path, filename: str) -> bool:
    return any(path.is_file() for path in root.rglob(filename))


def block_is_theoretical(block: str) -> bool:
    return "Statut support : théorique non prêt" in block


def describe_session(root: Path, session_id: str, block: str) -> SessionInfo:
    refs = extract_refs(block)
    specific = [ref for ref in refs if SPECIFIC_RE.fullmatch(ref)]
    generic = [ref for ref in refs if ref in GENERIC_FILES]
    existing = [ref for ref in specific if file_exists_anywhere(root, ref)]
    return SessionInfo(
        session_id=session_id,
        block=block,
        refs=refs,
        specific_refs=specific,
        generic_refs=generic,
        existing_specific_refs=existing,
        theoretical=block_is_theoretical(block),
    )


def is_blocking_absence(row: dict[str, str]) -> bool:
    if row.get("Blocage si absent", "").lower() in {"oui", "yes", "true"}:
        return True
    return row.get("Type", "").lower() in CRITICAL_TYPES


def analyze_sessions(root: Path = ROOT, session_files: list[Path] | None = None, register_path: Path = REGISTER) -> AnalysisResult:
    session_files = session_files or SESSION_FILES
    register_rows, register_errors = parse_register(register_path)
    result = AnalysisResult(errors=list(register_errors))

    missing_specific_sessions = 0
    explicit_theoretical_without_specific = 0

    for session_file in session_files:
        if not session_file.exists():
            result.errors.append(f"session file missing: {session_file.name}")
            continue
        for session_id, block in session_blocks(session_file):
            info = describe_session(root, session_id, block)
            result.total_sessions += 1
            prefix = session_id.split("-", 1)[0]

            if info.generic_refs and not info.specific_refs:
                result.errors.append(f"{session_id}: séance fondée seulement sur des fichiers génériques -> {', '.join(info.generic_refs)}")

            if not info.existing_specific_refs:
                result.theoretical_sessions += 1
                missing_specific_sessions += 1
                if info.theoretical:
                    explicit_theoretical_without_specific += 1
                else:
                    result.errors.append(f"{session_id}: aucun support spécifique existant et séance non marquée théorique")
            else:
                result.ready_sessions += 1

            if prefix in FIRST_BATCH_PREFIXES:
                if info.existing_specific_refs:
                    result.first_batch_ready += 1
                else:
                    result.first_batch_theoretical += 1
                    result.errors.append(f"{session_id}: première tranche sans support spécifique existant")

            for filename in info.specific_refs:
                row = register_rows.get(filename)
                exists = file_exists_anywhere(root, filename)
                if row and row.get("Décision", "").lower() == "abandonner":
                    result.errors.append(f"{session_id}: fichier marqué abandonner encore cité -> {filename}")
                if not exists:
                    if row is None:
                        result.errors.append(f"{session_id}: {filename} absent et non inscrit au registre v2")
                    elif is_blocking_absence(row):
                        result.errors.append(f"{session_id}: document bloquant absent -> {filename}")
                    elif row.get("Priorité", "").lower() == "haute" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row.get("Date cible", "")):
                        result.errors.append(f"{filename}: priorité haute sans date cible précise")

    if result.total_sessions:
        missing_ratio = missing_specific_sessions / result.total_sessions
        unmarked_theoretical = missing_specific_sessions - explicit_theoretical_without_specific
        if missing_ratio > 0.20 and unmarked_theoretical:
            result.errors.append(
                f"plus de 20% des séances sans support spécifique et non assumées comme théoriques: "
                f"{missing_specific_sessions}/{result.total_sessions} = {missing_ratio:.1%}"
            )

    return result


def main() -> None:
    result = analyze_sessions()
    print(f"Nombre de séances prêtes : {result.ready_sessions}")
    print(f"Nombre de séances théoriques : {result.theoretical_sessions}")
    print(f"Pourcentage de séances réellement exploitables : {result.usable_percent:.1f}%")
    if result.errors:
        print("check_session_referenced_files_exist: KO")
        for error in result.errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("check_session_referenced_files_exist: PASS")


if __name__ == "__main__":
    main()
