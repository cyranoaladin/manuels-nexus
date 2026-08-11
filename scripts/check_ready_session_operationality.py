#!/usr/bin/env python3
"""Recalculate ready sessions from operational criteria, not only file presence."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES
from scripts.check_session_referenced_files_exist import extract_refs, file_exists_anywhere, session_blocks

SESSION_FILES = [
    ROOT / "03_progressions" / "seances_premiere.md",
    ROOT / "03_progressions" / "seances_terminale.md",
]
FORBIDDEN_STUDENT_RE = re.compile(r"\b[PT]\d{2}_(?:corrige|bareme)_[A-Za-z0-9_]+\.md\b")
GENERIC_LIVRABLES = {
    "production élève vérifiable.",
    "production élève vérifiable",
    "production élève vérifiable dans trace écrite.",
}


@dataclass
class ReadyOperationalityResult:
    errors: list[str] = field(default_factory=list)
    ready_sessions: int = 0
    theoretical_sessions: int = 0

    @property
    def usable_percent(self) -> float:
        total = self.ready_sessions + self.theoretical_sessions
        return round(self.ready_sessions * 100 / total, 1) if total else 0.0


def line_value(block: str, key: str) -> str:
    prefix = f"- {key} : "
    for line in block.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def concrete_livrable(value: str) -> bool:
    lowered = value.lower().strip()
    if lowered in GENERIC_LIVRABLES:
        return False
    if "production élève vérifiable" in lowered and not any(token in lowered for token in [".py", ".md", "assertion", "tableau", "réponse", "trace", "sortie"]):
        return False
    return any(token in lowered for token in [".py", ".md", "assertion", "tableau", "réponse", "trace", "sortie", "capture", "test"])


def remediation_is_linked(value: str) -> bool:
    lowered = value.lower()
    return "ef" in lowered or "erreur fréquente" in lowered


def analyze_block(root: Path, session_id: str, block: str) -> list[str]:
    errors: list[str] = []
    refs = extract_refs(block)
    if not refs:
        errors.append(f"{session_id}: aucun fichier cité")
    for ref in refs:
        if ref != "carnet_de_bord.md" and not file_exists_anywhere(root, ref):
            errors.append(f"{session_id}: fichier cité absent -> {ref}")
    docs_line = line_value(block, "Document utilisé")
    if FORBIDDEN_STUDENT_RE.search(docs_line):
        errors.append(f"{session_id}: document professeur cité comme document élève")
    livrable = line_value(block, "Livrable") or line_value(block, "Livrable projet")
    if not concrete_livrable(livrable):
        errors.append(f"{session_id}: livrable non concret")
    remediation = line_value(block, "Remédiation")
    if remediation and not remediation_is_linked(remediation):
        errors.append(f"{session_id}: remédiation non reliée à une erreur fréquente")
    if any(ref.startswith(session_id.split("-", 1)[0] + "_tp_") for ref in refs):
        support_root = root / "03_progressions" / "supports"
        search_root = support_root if support_root.exists() else root
        code_dir = next(
            (path for path in search_root.rglob(session_id.split("-", 1)[0]) if path.is_dir()),
            search_root,
        ) / "code"
        if not code_dir.exists():
            errors.append(f"{session_id}: TP cité sans dossier code")
    return errors


def analyze_ready_sessions(
    root: Path = ROOT,
    session_files: list[Path] | None = None,
    prefixes: list[str] | None = None,
) -> ReadyOperationalityResult:
    session_files = session_files or SESSION_FILES
    prefixes = prefixes or FIRST_BATCH_PREFIXES
    prefix_set = set(prefixes)
    result = ReadyOperationalityResult()
    for session_file in session_files:
        if not session_file.exists():
            result.errors.append(f"session file missing: {session_file.name}")
            continue
        for session_id, block in session_blocks(session_file):
            prefix = session_id.split("-", 1)[0]
            if prefix not in prefix_set:
                if "Statut support : théorique non prêt" in block:
                    result.theoretical_sessions += 1
                continue
            errors = analyze_block(root, session_id, block)
            if errors:
                result.theoretical_sessions += 1
                result.errors.extend(errors)
            else:
                result.ready_sessions += 1
    return result


def main() -> int:
    result = analyze_ready_sessions()
    print(f"Nombre de séances prêtes opérationnelles : {result.ready_sessions}")
    print(f"Nombre de séances théoriques ou non opérationnelles : {result.theoretical_sessions}")
    print(f"Pourcentage réellement exploitable recalculé : {result.usable_percent:.1f}%")
    if result.errors:
        print("check_ready_session_operationality: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_ready_session_operationality: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
