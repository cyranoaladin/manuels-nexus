#!/usr/bin/env python3
"""Detecte les options de QCM mathematiquement equivalentes et le desequilibre
de distribution des bonnes reponses.

Deux options ne peuvent pas porter deux diagnostics distincts si elles valent
la meme chose : l'eleve qui choisit cette valeur devient indiagnosticable. La
comparaison ne peut donc pas etre textuelle -- 3/6, 1/2, 0,5 et 50 % sont la
meme valeur.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
OUTPUT_JSON = ROOT / "audit" / "QCM_OPTION_EQUIVALENCE.json"

BRACED = r"(?:[^{}]|\{[^{}]*\})*"


def numeric_value(raw: Any) -> Fraction | None:
    """Valeur d'une option quand elle est numeriquement comparable."""

    s = " ".join(str(raw).split()).strip()
    s = s.strip("$").strip()
    s = re.sub(r"\\(?:text|mathrm|mbox)\s*\{[^}]*\}", "", s)
    s = re.sub(r"\\[,;:!\s]", "", s).strip()
    s = re.sub(r"(euros?|€|%)\s*$", lambda m: "%" if m.group(1) == "%" else "", s).strip()
    percent = s.endswith("%")
    if percent:
        s = s[:-1].strip()
    m = re.fullmatch(r"\\d?frac\s*\{(" + BRACED + r")\}\s*\{(" + BRACED + r")\}", s)
    if m:
        a, b = numeric_value(m.group(1)), numeric_value(m.group(2))
        value = a / b if a is not None and b else None
    else:
        t = s.replace("{,}", ".").replace(",", ".")
        t = re.sub(r"^\{?(-?)\\?", r"\1", t).strip("{} ")
        try:
            value = Fraction(t)
        except (ValueError, ZeroDivisionError):
            value = None
    if value is not None and percent:
        value = value / 100
    return value


def audit_chapter(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    questions = document.get("questions") or []
    equivalences, comparable, total_options = [], 0, 0
    for question in questions:
        options = question.get("options") or {}
        values: dict[Fraction, list[str]] = {}
        for letter, text in options.items():
            total_options += 1
            value = numeric_value(text)
            if value is None:
                continue
            comparable += 1
            values.setdefault(value, []).append(letter)
        for value, letters in values.items():
            if len(letters) > 1:
                equivalences.append({
                    "question": question.get("id"),
                    "capacite": question.get("capacite"),
                    "value": str(value),
                    "options": sorted(letters),
                    "texts": {k: options[k] for k in letters},
                    "key_involved": question.get("correcte") in letters,
                    "distinct_diagnostics": len({
                        json.dumps((question.get("diagnostics") or {}).get(k), sort_keys=True)
                        for k in letters
                    }) > 1,
                })
    keys = Counter(q.get("correcte") for q in questions if q.get("correcte"))
    letters = sorted({letter for q in questions for letter in (q.get("options") or {})})
    counts = {letter: keys.get(letter, 0) for letter in letters} or dict(keys)
    spread = (max(counts.values()) - min(counts.values())) if counts else 0
    run, longest, previous = 0, 0, None
    for q in questions:
        current = q.get("correcte")
        run = run + 1 if current == previous else 1
        longest = max(longest, run)
        previous = current
    return {
        "chapter": path.parents[1].name,
        "questions": len(questions),
        "options_total": total_options,
        "options_numerically_comparable": comparable,
        "equivalent_option_groups": equivalences,
        "key_distribution": counts,
        "key_spread": spread,
        "max_consecutive_identical_keys": longest,
        "distribution_contract_met": spread <= 1 and longest <= 2 and all(counts.values()),
    }


def build_report() -> dict[str, Any]:
    chapters = [audit_chapter(p) for p in sorted(CHAPTERS.glob("*/qcm/*-QCM.json"))]
    return {
        "artifact_type": "qcm_option_equivalence",
        "schema_version": 1,
        "generated_by": "scripts/audit_qcm_option_equivalence.py",
        "contract": {
            "equivalent_options_allowed": False,
            "key_spread_max": 1,
            "max_consecutive_identical_keys": 2,
            "all_positions_used": True,
        },
        "totals": {
            "chapters": len(chapters),
            "questions": sum(c["questions"] for c in chapters),
            "equivalent_option_groups": sum(len(c["equivalent_option_groups"]) for c in chapters),
            "chapters_failing_distribution": sum(
                1 for c in chapters if not c["distribution_contract_met"]
            ),
        },
        "chapters": chapters,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_report()
    rendered = render_json(payload)
    if args.check:
        if not OUTPUT_JSON.is_file() or OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            raise SystemExit("STALE: audit/QCM_OPTION_EQUIVALENCE.json")
        print(json.dumps(payload["totals"], ensure_ascii=False))
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    print(json.dumps(payload["totals"], ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
