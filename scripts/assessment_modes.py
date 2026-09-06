#!/usr/bin/env python3
"""Modalités d'évaluation, et preuve qu'une évaluation réelle existe.

Le gate exigeait partout deux sujets écrits A et B avec leurs corrigés. Cette
exigence est juste pour un chapitre disciplinaire ; elle ne l'est pas pour un
chapitre dont le programme fait de la démarche de projet une part obligatoire
de l'enseignement. Rédiger deux devoirs sur table pour TNSI-PROJET aurait rendu
la dimension verte sans répondre à un besoin pédagogique.

Le contrat de chapitre déclare donc sa modalité. Mais déclarer ne suffit pas :
chaque modalité doit prouver qu'une évaluation **réelle** existe. Pour un
projet, la preuve est une grille critériée exploitable — des critères, des
poids qui totalisent 100 %, et une preuve attendue en regard de chacun. Un
fichier vide portant le bon nom échoue.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

#: Modalités reconnues. Le défaut reste l'écrit : aucun chapitre ne change de
#: régime sans le déclarer.
WRITTEN_ASSESSMENT = "WRITTEN_ASSESSMENT"
PROJECT_ASSESSMENT = "PROJECT_ASSESSMENT"
PRACTICAL_ASSESSMENT = "PRACTICAL_ASSESSMENT"
SELF_ASSESSMENT = "SELF_ASSESSMENT"

ASSESSMENT_MODES = frozenset({
    WRITTEN_ASSESSMENT, PROJECT_ASSESSMENT, PRACTICAL_ASSESSMENT, SELF_ASSESSMENT,
})

DEFAULT_MODE = WRITTEN_ASSESSMENT

#: Une ligne de grille : critère | poids | preuve attendue.
GRID_ROW = re.compile(
    r"^(?P<criterion>[^&]{3,}?)\s*&\s*(?P<weight>\d{1,3})\s*(?:\\,)?\s*\\?%\s*&\s*(?P<evidence>[^&\\]*)"
)

MIN_CRITERIA = 3
WEIGHT_TOTAL = 100


def declared_mode(contract: dict[str, Any]) -> str:
    """Modalité déclarée par le contrat de chapitre, écrit par défaut."""
    mode = str(contract.get("assessment_mode") or "").strip().upper()
    return mode if mode in ASSESSMENT_MODES else DEFAULT_MODE


def parse_criteria_grid(text: str) -> list[dict[str, Any]]:
    """Lignes exploitables de la grille critériée imprimée."""
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip().rstrip("\\").strip()
        match = GRID_ROW.match(stripped)
        if not match:
            continue
        criterion = match.group("criterion").strip()
        evidence = match.group("evidence").strip()
        if criterion.lower().startswith("\\textbf{critère"):
            continue  # ligne d'en-tête
        rows.append({
            "criterion": criterion,
            "weight": int(match.group("weight")),
            "evidence": evidence,
        })
    return rows


def project_assessment_violations(project_sources: list[Path]) -> list[str]:
    """Motifs pour lesquels un chapitre en régime projet n'est pas évalué.

    On ne vérifie pas qu'un fichier existe : on vérifie que la grille imprimée
    est utilisable par un enseignant.
    """
    if not project_sources:
        return ["aucun objet de projet porteur d'une évaluation"]

    violations: list[str] = []
    grids = []
    for path in project_sources:
        rows = parse_criteria_grid(path.read_text(encoding="utf-8", errors="replace"))
        if rows:
            grids.append((path, rows))

    if not grids:
        return ["aucune grille critériée exploitable dans les objets de projet"]

    for path, rows in grids:
        name = path.name
        if len(rows) < MIN_CRITERIA:
            violations.append(f"{name}: grille trop pauvre ({len(rows)} critère(s))")
        total = sum(row["weight"] for row in rows)
        if total != WEIGHT_TOTAL:
            violations.append(f"{name}: les poids totalisent {total}% au lieu de {WEIGHT_TOTAL}%")
        without_evidence = [row["criterion"] for row in rows if not row["evidence"]]
        if without_evidence:
            violations.append(
                f"{name}: {len(without_evidence)} critère(s) sans preuve attendue"
            )
    return violations
