#!/usr/bin/env python3
"""Check one official capacity per programme YAML identifier."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "00_programmes_officiels/programme_nsi_2019.yaml"
FORBIDDEN = {"P-DATA-BASE-02", "P-DATA-BASE-05", "P-DATA-CONSTR-02", "P-DATA-CONSTR-03", "P-IHM-01", "P-IHM-03", "P-IHM-04", "P-ARCH-01", "P-ARCH-02", "P-ARCH-03", "P-ARCH-04", "P-LANG-03", "P-ALGO-01", "P-ALGO-02", "T-HIST-01", "T-STRUCT-01", "T-STRUCT-02", "T-STRUCT-03", "T-STRUCT-04", "T-STRUCT-05", "T-BDD-01", "T-BDD-03", "T-ARCH-02", "T-ARCH-04", "T-LANG-01", "T-LANG-02", "T-LANG-03", "T-LANG-04", "T-ALGO-01", "T-ALGO-02"}


def main() -> int:
    errors: list[str] = []
    data = yaml.safe_load(PROGRAM.read_text(encoding="utf-8")) or {}
    seen: set[str] = set()
    for level, rows in (data.get("programmes") or {}).items():
        for row in rows or []:
            ident = str(row.get("id") or "")
            capacities = row.get("capacite_attendue") or []
            if ident in seen:
                errors.append(f"duplicate id {ident}")
            seen.add(ident)
            if ident in FORBIDDEN:
                errors.append(f"aggregated legacy id still present: {ident}")
            if not re.match(r"^[PT]-[A-Z]+(?:-[A-Z]+)*-[0-9]{2}[A-Z]?$", ident):
                errors.append(f"invalid id format: {ident}")
            if not isinstance(capacities, list) or len(capacities) != 1:
                errors.append(f"{ident}: expected exactly one capacity, found {len(capacities) if isinstance(capacities, list) else 'invalid'}")
            if not row.get("rubrique") or not row.get("contenu"):
                errors.append(f"{ident}: rubrique or contenu missing")
    required = {"T-BDD-03B", "T-BDD-03F", "T-BDD-03G", "T-BDD-03H", "T-ALGO-02A", "T-ALGO-02B", "T-ALGO-02C", "T-ALGO-02D", "P-ALGO-02A", "P-ALGO-02B", "P-TABLE-01", "P-TABLE-02", "P-TABLE-03", "P-TABLE-04"}
    for ident in sorted(required - seen):
        errors.append(f"required atomic id missing: {ident}")
    if errors:
        print("check_program_yaml_atomicity: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_program_yaml_atomicity: PASS")
    print(f"- atomic capacities: {len(seen)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
