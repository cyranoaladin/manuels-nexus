#!/usr/bin/env python3
"""Report paper TP that should become executable resources."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import re

from scripts._qa_common import ROOT, sequence_id_from_path, strip_frontmatter
from scripts.check_paper_tp_justification import is_paper_tp


EXECUTABLE_TOPICS_RE = re.compile(
    r"\b(?:SQL|SELECT|JOIN|UPDATE|DELETE|csv|DictReader|table|tri|fonction|test|"
    r"graphe|BFS|DFS|arbre|ABR|récurrence|dynamique|paquet|routage|TTL|réseau|"
    r"algorithme|Python|pseudo-code)\b",
    re.I,
)


@dataclass
class TPExecutableOpportunityResult:
    opportunities: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    paper_count: int = 0
    executable_count: int = 0
    register_path: Path | None = None


def has_executable_assets(tp_path: Path) -> bool:
    sequence = sequence_id_from_path(tp_path)
    code_dir = tp_path.parent / "code"
    if not code_dir.exists():
        return False
    expected = ["starter", "corrige", "tests"]
    names = [path.name.lower() for path in code_dir.glob(f"{sequence}_*.py")]
    return all(any(token in name for name in names) for token in expected)


def opportunity_reason(tp_path: Path, text: str, root: Path = ROOT) -> str | None:
    body = strip_frontmatter(text)
    if not EXECUTABLE_TOPICS_RE.search(body):
        return None
    if has_executable_assets(tp_path):
        return None
    sequence = sequence_id_from_path(tp_path)
    rel = tp_path.relative_to(root).as_posix() if tp_path.is_absolute() and root in tp_path.parents else tp_path.as_posix()
    return (
        f"{rel}: {sequence} TP papier sur notion exécutable "
        "sans starter/corrigé/tests associés"
    )


def write_register(root: Path, opportunities: list[str]) -> Path:
    path = root / "tp_executable_opportunity_register.md"
    lines = [
        "# Registre des opportunités de TP exécutables",
        "",
        "Ce registre signale les TP papier qui portent sur une notion naturellement exécutable. "
        "Il ne valide aucun statut et ne remplace pas la production d'assets.",
        "",
        "| TP papier | Action recommandée | Priorité | Statut |",
        "|---|---|---|---|",
    ]
    if opportunities:
        for item in opportunities:
            tp, reason = item.split(": ", 1)
            lines.append(f"| `{tp}` | Créer starter, corrigé professeur et tests attendus. {reason} | haute | needs_review |")
    else:
        lines.append("| - | Aucun TP papier exécutable prioritaire détecté. | - | needs_review |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def analyze_tp_executable_opportunity(
    root: Path = ROOT,
    write_report: bool = False,
    strict: bool = False,
    max_opportunities: int | None = None,
) -> TPExecutableOpportunityResult:
    result = TPExecutableOpportunityResult()
    for path in sorted((root / "03_progressions" / "supports").rglob("*.md")):
        if "_tp_" not in path.name.lower() and "_TP_" not in path.name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_paper_tp(path, text):
            result.paper_count += 1
            reason = opportunity_reason(path, text, root)
            if reason:
                result.opportunities.append(reason)
        else:
            result.executable_count += 1
    if write_report:
        result.register_path = write_register(root, result.opportunities)
    if strict:
        limit = 8 if max_opportunities is None else max_opportunities
        if len(result.opportunities) > limit:
            result.errors.append(
                f"plus de {limit} opportunités de TP exécutables restantes: {len(result.opportunities)}"
            )
    return result


def main() -> int:
    env_limit = os.environ.get("MAX_EXECUTABLE_TP_OPPORTUNITIES")
    strict = env_limit is not None
    max_opportunities = int(env_limit) if env_limit and env_limit.isdigit() else 8
    result = analyze_tp_executable_opportunity(
        write_report=True,
        strict=strict,
        max_opportunities=max_opportunities,
    )
    print(f"TP papier : {result.paper_count}")
    print(f"TP exécutables : {result.executable_count}")
    print(f"Opportunités de conversion en TP exécutable : {len(result.opportunities)}")
    if result.register_path:
        print(f"Registre : {result.register_path.relative_to(ROOT).as_posix()}")
    for item in result.opportunities[:120]:
        print(f"- {item}")
    if result.errors:
        print("check_tp_executable_opportunity: KO")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print("check_tp_executable_opportunity: PASS (registre informatif)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
