#!/usr/bin/env python3
"""Check that TP texts and executable assets describe the same tasks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


@dataclass
class TpTextAssetAlignmentResult:
    errors: list[str] = field(default_factory=list)
    checked_prefixes: int = 0


PREFIX_SPECS = {
    "P06": {
        "required_symbols": [
            "rechercher_premiere_ligne",
            "detecter_doublons",
            "trier_par_nom_atelier",
            "fusionner_presences",
        ],
        "required_text": [
            "rechercher_premiere_ligne",
            "detecter_doublons",
            "trier_par_nom_atelier",
            "fusionner_presences",
        ],
        "forbidden": ["résultat contrôlable sans donnée"],
    },
    "P04": {
        "required_symbols": ["milieu", "stations_chaudes", "moyenne_notes"],
        "required_text": ["milieu", "stations_chaudes", "moyenne_notes"],
        "forbidden": ["resume_mesures"],
    },
    "P05": {
        "required_symbols": [
            "charger_pays_csv",
            "filtrer_par_continent",
            "convertir_populations",
            "trier_par_continent_population",
        ],
        "required_code": ["csv.DictReader", "int("],
        "required_text": [
            "charger_pays_csv",
            "filtrer_par_continent",
            "convertir_populations",
            "trier_par_continent_population",
            "csv.DictReader",
        ],
        "forbidden": ["ville,temp", "Tunis,24"],
    },
    "T01": {
        "required_symbols": ["class Pile", "class File", "empiler", "depiler", "sommet", "enfiler", "defiler", "premier"],
        "required_text": ["class Pile", "class File", "empiler", "depiler", "sommet", "enfiler", "defiler", "premier"],
        "forbidden": ["scenario_structure"],
    },
}

T18_TRACE_TERM_GROUPS = [
    ("texte",),
    ("motif",),
    ("mauvais caractère", "mauvais caractere"),
    ("décalage", "decalage"),
    ("alignement",),
    ("indice",),
]


def support_dirs(root: Path, prefix: str) -> list[Path]:
    base = root / "03_progressions" / "supports"
    return sorted(path for path in base.rglob(prefix) if path.is_dir()) if base.exists() else []


def find_files(root: Path, prefix: str, pattern: str) -> list[Path]:
    return sorted(path for directory in support_dirs(root, prefix) for path in directory.rglob(pattern))


def read_joined(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths if path.exists())


def symbol_present(symbol: str, text: str) -> bool:
    if symbol.startswith("class "):
        return bool(re.search(rf"^\s*class\s+{re.escape(symbol.split()[1])}\b", text, flags=re.M))
    return bool(re.search(rf"\b{re.escape(symbol)}\b", text))


def analyze_prefix(root: Path, prefix: str) -> list[str]:
    errors: list[str] = []
    if prefix == "T18":
        trace_files = find_files(root, prefix, "T18_trace_boyer_moore.md")
        trace_text = read_joined(trace_files)
        normalized = trace_text.lower()
        has_terms = all(any(term in normalized for term in group) for group in T18_TRACE_TERM_GROUPS)
        if not trace_files or "|" not in trace_text or not has_terms:
            errors.append("T18: table de trace Boyer-Moore absente ou incomplète")
        return errors

    spec = PREFIX_SPECS.get(prefix)
    if not spec:
        return errors
    tp_text = read_joined(find_files(root, prefix, f"{prefix}_*tp*.md") + find_files(root, prefix, f"{prefix}_*TP*.md"))
    code_text = read_joined(find_files(root, prefix, "code/*.py"))

    for token in spec["required_text"]:
        if token not in tp_text:
            errors.append(f"{prefix}: TP ne cite pas `{token}`")
    for symbol in spec["required_symbols"]:
        if not symbol_present(symbol, code_text):
            errors.append(f"{prefix}: asset manquant ou non aligné -> {symbol}")
    for token in spec.get("required_code", []):
        if token not in code_text:
            errors.append(f"{prefix}: asset ne contient pas `{token}`")
    combined = f"{tp_text}\n{code_text}"
    for marker in spec["forbidden"]:
        if marker in combined:
            errors.append(f"{prefix}: ancien scénario obsolète encore présent -> {marker}")
    return errors


def analyze_tp_text_asset_alignment(root: Path = ROOT, prefixes: list[str] | None = None) -> TpTextAssetAlignmentResult:
    prefixes = prefixes or ["P04", "P05", "P06", "T01", "T18"]
    result = TpTextAssetAlignmentResult()
    for prefix in prefixes:
        result.checked_prefixes += 1
        result.errors.extend(analyze_prefix(root, prefix))
    return result


def main() -> int:
    result = analyze_tp_text_asset_alignment()
    if result.errors:
        print("check_tp_text_asset_alignment: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_tp_text_asset_alignment: PASS ({result.checked_prefixes} préfixes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
