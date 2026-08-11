#!/usr/bin/env python3
"""Report operational and theoretical sessions with required next actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_session_referenced_files_exist import (
    analyze_sessions,
    describe_session,
    session_blocks,
)


@dataclass
class SessionOperationalizationResult:
    operational_count: int = 0
    theoretical_count: int = 0
    theoretical_sessions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def session_files(root: Path = ROOT) -> list[Path]:
    base = root / "03_progressions"
    return [path for path in [base / "seances_premiere.md", base / "seances_terminale.md"] if path.exists()]


def analyze_table_format(files: list[Path], root: Path) -> SessionOperationalizationResult:
    result = SessionOperationalizationResult()
    for path in files:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("|") or "---" in line or "Séance" in line:
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells:
                continue
            line_text = " | ".join(cells)
            session_id = next((cell for cell in cells if re.search(r"[PT]\d{2}-S\d+", cell)), cells[0])
            if re.search(r"théorique|theorique|non opérationnelle|non operationnelle|à créer|a creer", line_text, re.I):
                result.theoretical_count += 1
                result.theoretical_sessions.append(
                    f"{path.relative_to(root).as_posix()}: {session_id} -> ressource à rendre opérationnelle"
                )
            elif re.search(r"prête|prete|opérationnelle|operationnelle|réelle|reelle", line_text, re.I):
                result.operational_count += 1
    return result


def analyze_session_operationalization_plan(root: Path = ROOT) -> SessionOperationalizationResult:
    result = SessionOperationalizationResult()
    files = session_files(root)
    session_analysis = analyze_sessions(root=root, session_files=files)
    if session_analysis.total_sessions == 0:
        return analyze_table_format(files, root)
    result.operational_count = session_analysis.ready_sessions
    result.theoretical_count = session_analysis.theoretical_sessions

    for path in files:
        for session_id, block in session_blocks(path):
            info = describe_session(root, session_id, block)
            if info.existing_specific_refs and not info.theoretical:
                continue
            if info.theoretical:
                reason = "support spécifique non relié dans la séance"
                action = "remplacer la mention théorique par les supports produits et vérifiés"
            elif not info.existing_specific_refs:
                reason = "aucun support spécifique existant détecté"
                action = "produire ou référencer un cours/TD/TP/trace réel"
            else:
                reason = "séance explicitement non opérationnelle"
                action = "lever le statut théorique après vérification des supports"
            result.theoretical_sessions.append(
                f"{path.relative_to(root).as_posix()}: {session_id} -> {reason}; action: {action}"
            )
    return result


def main() -> int:
    result = analyze_session_operationalization_plan()
    print(f"Nombre de séances opérationnelles : {result.operational_count}")
    print(f"Nombre de séances théoriques : {result.theoretical_count}")
    if result.theoretical_sessions:
        print("Séances théoriques à traiter :")
        for item in result.theoretical_sessions[:220]:
            print(f"- {item}")
    print("check_session_operationalization_plan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
