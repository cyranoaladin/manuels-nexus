#!/usr/bin/env python3
"""Build a resource matrix per course sheet / notion."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re
import unicodedata

from scripts._qa_common import ROOT, read_frontmatter, strip_frontmatter


RESOURCE_TYPES = [
    "cours",
    "trace",
    "td",
    "tp",
    "corrige",
    "bareme",
    "evaluation",
    "remediation",
    "version_amenagee",
    "assets",
    "contrat",
]

SUPPORT_PATTERNS = {
    "cours": ("cours",),
    "trace": ("trace",),
    "td": ("td", "TD"),
    "tp": ("tp", "TP"),
    "corrige": ("corrige", "corrigé"),
    "bareme": ("bareme", "barème"),
    "evaluation": ("evaluation", "évaluation"),
    "remediation": ("remediation", "remédiation"),
    "version_amenagee": ("version_amenagee", "version_aménagée"),
}

STOP_TOKENS = {
    "fiche",
    "cours",
    "sql",
    "tables",
    "table",
    "nsi",
    "bac",
    "projet",
    "oral",
    "synthese",
    "synthèse",
    "reprise",
}


@dataclass
class NotionalMatrixResult:
    errors: list[str] = field(default_factory=list)
    rows: list[dict[str, str]] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=lambda: {"produced": 0, "missing": 0})


def level_for(sequence: str) -> str:
    return "premiere" if sequence.startswith("P") else "terminale"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def notion_slug(sheet: Path, metadata: dict[str, Any]) -> str:
    sequence = str(metadata.get("sequence_id") or sheet.name[:3])
    stem = sheet.stem
    prefix = f"{sequence}_fiche_cours_"
    if stem.startswith(prefix):
        return stem[len(prefix) :]
    notion = str(metadata.get("notion") or stem)
    return normalize(notion)


def notion_tokens(slug: str) -> list[str]:
    raw = re.split(r"[_\W]+", slug.lower())
    return [token for token in raw if len(token) >= 3 and token not in STOP_TOKENS]


def support_dir(root: Path, sequence: str) -> Path:
    return root / "03_progressions" / "supports" / level_for(sequence) / sequence


def support_files(root: Path, sequence: str, resource_type: str) -> list[Path]:
    base = support_dir(root, sequence)
    if not base.exists():
        return []
    patterns = SUPPORT_PATTERNS[resource_type]
    files: list[Path] = []
    for path in sorted(base.glob(f"{sequence}_*.md")):
        lower = path.name.lower()
        if any(pattern.lower() in lower for pattern in patterns):
            files.append(path)
    return files


def token_match_score(tokens: list[str], path: Path) -> int:
    if not tokens:
        return 1
    text = normalize(f"{path.stem}\n{strip_frontmatter(path.read_text(encoding='utf-8', errors='replace'))}")
    score = 0
    for token in tokens:
        stem = token[:5] if len(token) > 5 else token
        if token in text or stem in text:
            score += 1
    return score


def support_covers_notion(tokens: list[str], path: Path, single_sheet: bool) -> bool:
    if single_sheet:
        return True
    if not tokens:
        return True
    score = token_match_score(tokens, path)
    return score >= 1


def has_assets(root: Path, sequence: str, tokens: list[str], single_sheet: bool) -> str:
    base = support_dir(root, sequence)
    code_dir = base / "code"
    py_files = sorted(code_dir.glob(f"{sequence}_*.py")) if code_dir.exists() else []
    tp_files = support_files(root, sequence, "tp")
    tp_text = "\n".join(path.read_text(encoding="utf-8", errors="replace").lower() for path in tp_files)
    if "tp_papier" in tp_text or "tp papier" in tp_text:
        return "not_required_paper"
    if "starter code" not in tp_text and "starter_" not in tp_text and "tests attendus" not in tp_text:
        return "not_required_paper"
    if not py_files:
        return "missing"
    return "produced"


def contract_status(root: Path, sequence: str, tokens: list[str], single_sheet: bool) -> str:
    path = root / "03_progressions" / "supports" / "contracts" / f"{sequence}_contract.yml"
    if not path.exists():
        return "missing"
    return "produced"


def analyze_full_notional_resource_matrix(root: Path = ROOT) -> NotionalMatrixResult:
    result = NotionalMatrixResult()
    sheets = sorted((root / "03_progressions" / "fiches_cours").rglob("*_fiche_cours_*.md"))
    sheets_by_sequence: dict[str, list[Path]] = {}
    for sheet in sheets:
        metadata = read_frontmatter(sheet)
        sequence = str(metadata.get("sequence_id") or sheet.name[:3])
        sheets_by_sequence.setdefault(sequence, []).append(sheet)

    for sheet in sheets:
        metadata = read_frontmatter(sheet)
        sequence = str(metadata.get("sequence_id") or sheet.name[:3])
        level = level_for(sequence)
        slug = notion_slug(sheet, metadata)
        tokens = notion_tokens(slug)
        single_sheet = len(sheets_by_sequence.get(sequence, [])) == 1
        row = {
            "niveau": level,
            "séquence": sequence,
            "fiche": sheet.name,
            "notion": str(metadata.get("notion") or slug),
        }
        for resource_type in RESOURCE_TYPES:
            if resource_type == "assets":
                status = has_assets(root, sequence, tokens, single_sheet)
            elif resource_type == "contrat":
                status = contract_status(root, sequence, tokens, single_sheet)
            else:
                candidates = support_files(root, sequence, resource_type)
                status = "produced" if any(support_covers_notion(tokens, path, single_sheet) for path in candidates) else "missing"
            row[resource_type] = status
            if status.startswith("produced") or status == "not_required_paper":
                result.counts["produced"] += 1
            else:
                result.counts["missing"] += 1
                result.errors.append(
                    f"{sequence}/{sheet.name}: ressource notionnelle manquante ou trop générale -> {resource_type} ({slug})"
                )
        row["statut"] = "ok" if all(row[k] != "missing" for k in RESOURCE_TYPES) else "incomplete"
        result.rows.append(row)
    return result


def format_matrix(result: NotionalMatrixResult) -> str:
    headers = ["niveau", "séquence", "fiche", "notion", *RESOURCE_TYPES, "statut"]
    lines = ["| " + " | ".join(headers) + " |", "|---" * len(headers) + "|"]
    for row in result.rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def main() -> int:
    result = analyze_full_notional_resource_matrix()
    print(format_matrix(result))
    total = sum(result.counts.values())
    completeness = (result.counts["produced"] / total * 100.0) if total else 100.0
    print(f"Ressources notionnelles produites: {result.counts['produced']}/{total} ({completeness:.1f}%)")
    print(f"Ressources notionnelles manquantes: {result.counts['missing']}")
    if result.errors:
        print("check_full_notional_resource_matrix: KO")
        for error in result.errors[:220]:
            print(f"- {error}")
        return 1
    print(f"check_full_notional_resource_matrix: PASS ({len(result.rows)} fiches, complétude {completeness:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
