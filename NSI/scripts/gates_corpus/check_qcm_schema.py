#!/usr/bin/env python3
"""Gate : verifie la structure des QCM (nombre de questions, capacites couvertes).

Adapte depuis corpus_nsi check_qcm_schema.py.
Le corpus source utilise qcm.json, le manuel utilise des .tex.
Ce gate verifie le nombre de questions et la couverture des capacites.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

QUESTION_RE = re.compile(r"\\textbf\{Q(\d+)\.\}\s*\(C(\d+)\)")
MIN_QUESTIONS = 15


def main() -> int:
    chap_arg = None
    strict = "--strict" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--chap" and i + 1 < len(sys.argv):
            chap_arg = sys.argv[i + 1]

    chap_dirs = []
    if chap_arg:
        d = ROOT / "chapitres" / chap_arg
        if d.exists():
            chap_dirs = [d]
    else:
        chap_dirs = sorted(d for d in (ROOT / "chapitres").iterdir() if d.is_dir())

    errors: list[str] = []
    for chap_dir in chap_dirs:
        qcm_dir = chap_dir / "qcm"
        if not qcm_dir.exists():
            continue

        questions: list[tuple[int, str]] = []
        for f in sorted(qcm_dir.glob("*.tex")):
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in QUESTION_RE.finditer(text):
                questions.append((int(m.group(1)), m.group(2)))

        chap_name = chap_dir.name
        n = len(questions)
        if n < MIN_QUESTIONS:
            errors.append(f"{chap_name}: {n} questions QCM (minimum {MIN_QUESTIONS})")

        caps = {c for _, c in questions}
        # En strict, verifier la couverture des capacites du contrat
        if strict:
            contrat_path = chap_dir / "contrat.yaml"
            if contrat_path.exists():
                import yaml
                contrat = yaml.safe_load(contrat_path.read_text(encoding="utf-8"))
                expected_caps = {c["code"] for c in contrat.get("capacites", [])}
                missing_caps = expected_caps - {f"C{c}" for c in caps}
                if missing_caps:
                    errors.append(f"{chap_name}: capacites non couvertes par le QCM: {sorted(missing_caps)}")

        print(f"{chap_name}: {n} questions QCM, capacites couvertes: {sorted(caps)}")

    if errors:
        print(f"\nWARN -- {len(errors)} problemes QCM :")
        for e in errors:
            print(f"  {e}")

    if strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
