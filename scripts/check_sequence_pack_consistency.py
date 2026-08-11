#!/usr/bin/env python3
"""Check that each sequence pack keeps one coherent disciplinary thread."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, strip_frontmatter


@dataclass
class PackConsistencyResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


P05_REQUIRED_TERMS = [
    "pays_monde.csv",
    "PAYS",
    "CAPITALE",
    "CONTINENT",
    "POPULATION",
    "csv.reader",
    "csv.DictReader",
    "filtrage",
    "int(row[\"POPULATION\"])",
    "tri numérique",
    "tri lexicographique",
    "tri par continent puis population",
    "ligne invalide",
    "P-TABLE-01",
    "P-TABLE-02",
]

OLD_P05_MARKERS = [
    "ville,temp",
    "Tunis,24",
    "trois villes dont deux Tunis",
    "24`, `26`, champ vide",
    "moyenne = 25",
    "température",
]


def sequence_files(root: Path, prefix: str) -> list[Path]:
    files: list[Path] = []
    files.extend(sorted((root / "03_progressions" / "supports").rglob(f"{prefix}_*.md")))
    files.extend(sorted((root / "03_progressions" / "fiches_cours").rglob(f"{prefix}_*.md")))
    contract = root / "03_progressions" / "supports" / "contracts" / f"{prefix}_contract.yml"
    if contract.exists():
        files.append(contract)
    return files


def contains_any(text: str, markers: list[str]) -> list[str]:
    lower = text.lower()
    return [marker for marker in markers if marker.lower() in lower]


def p05_pack_errors(path: Path, text: str, root: Path) -> list[str]:
    rel = path.relative_to(root) if path.is_relative_to(root) else path
    body = strip_frontmatter(text)
    errors: list[str] = []
    old = contains_any(body, OLD_P05_MARKERS)
    if old:
        errors.append(f"{rel}: fil conducteur P05 contradictoire pays_monde/villes-temp -> {', '.join(old)}")
    required = contains_any(body, P05_REQUIRED_TERMS)
    if "pays_monde.csv" in body and len(required) < len(P05_REQUIRED_TERMS):
        missing = [term for term in P05_REQUIRED_TERMS if term not in required]
        errors.append(f"{rel}: fil pays_monde incomplet, éléments manquants -> {', '.join(missing[:8])}")
    return errors


def analyze_sequence_pack_consistency(root: Path = ROOT, prefixes: list[str] | None = None) -> PackConsistencyResult:
    prefixes = prefixes or ["P05"]
    result = PackConsistencyResult()
    for prefix in prefixes:
        files = sequence_files(root, prefix)
        if not files:
            result.errors.append(f"{prefix}: aucun fichier de paquet trouvé")
            continue
        for path in files:
            result.checked_files += 1
            text = path.read_text(encoding="utf-8", errors="replace")
            if prefix == "P05":
                result.errors.extend(p05_pack_errors(path, text, root))
        if prefix == "P05":
            joined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in files)
            has_pays = "pays_monde.csv" in joined
            has_old = bool(re.search(r"ville,temp|Tunis,24|trois villes dont deux Tunis", joined, flags=re.I))
            if has_pays and has_old:
                result.errors.append("P05: le paquet mélange `pays_monde.csv` et l'ancien scénario `ville,temp`/`Tunis`")
    return result


def main() -> int:
    result = analyze_sequence_pack_consistency()
    if result.errors:
        print("check_sequence_pack_consistency: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print(f"check_sequence_pack_consistency: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
