#!/usr/bin/env python3
"""Check that session statuses follow the resources that now exist."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_session_referenced_files_exist import (
    describe_session,
    session_blocks,
)


SESSION_FILES = [
    ROOT / "03_progressions" / "seances_premiere.md",
    ROOT / "03_progressions" / "seances_terminale.md",
]


@dataclass
class SessionResourceAlignmentResult:
    operational_count: int = 0
    theoretical_count: int = 0
    theoretical_with_existing_supports: int = 0
    corrected_candidates: list[str] = field(default_factory=list)
    rows: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def sequence_supports_exist(root: Path, prefix: str) -> bool:
    level = "premiere" if prefix.startswith("P") else "terminale"
    base = root / "03_progressions" / "supports" / level / prefix
    if not base.exists():
        return False
    required = ["cours", "trace", "td", "tp", "corrige", "bareme", "evaluation", "remediation", "version_amenagee"]
    names = [path.name.lower() for path in base.glob(f"{prefix}_*.md")]
    return all(any(token in name for name in names) for token in required)


def find_support(root: Path, filename: str) -> Path | None:
    matches = sorted(path for path in root.rglob(filename) if path.is_file())
    return matches[0] if len(matches) == 1 else None


def support_is_teacher_only(filename: str) -> bool:
    lowered = filename.lower()
    return any(token in lowered for token in ["corrige", "corrigé", "bareme", "barème", "guide_professeur"])


def session_capacities(block: str) -> set[str]:
    return set(re.findall(r"\b[PT](?:-[A-Z]+)+-\d{2}[A-Z]?\b", block))


def capacities_visible_in_refs(root: Path, capacities: set[str], refs: list[str]) -> bool:
    if not capacities:
        return True
    texts: list[str] = []
    for ref in refs:
        path = find_support(root, ref)
        if path:
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
    joined = "\n".join(texts)
    return all(capacity in joined for capacity in capacities)


def analyze_session_to_resource_alignment(root: Path = ROOT) -> SessionResourceAlignmentResult:
    result = SessionResourceAlignmentResult()
    files = [
        root / "03_progressions" / "seances_premiere.md",
        root / "03_progressions" / "seances_terminale.md",
    ]
    for path in files:
        if not path.exists():
            continue
        for session_id, block in session_blocks(path):
            info = describe_session(root, session_id, block)
            prefix = session_id.split("-", 1)[0]
            status = "operational" if info.existing_specific_refs and not info.theoretical else "theoretical"
            action = "aucune" if status == "operational" else "relier aux supports produits"
            blockage = ""
            refs_display = ", ".join(info.refs) if info.refs else "-"
            if info.existing_specific_refs and not info.theoretical:
                result.operational_count += 1
            else:
                result.theoretical_count += 1

            if any(support_is_teacher_only(ref) for ref in info.refs):
                blockage = "support professeur cité comme support élève"
                result.errors.append(f"{path.relative_to(root).as_posix()}: {session_id} cite un support professeur")
            if info.existing_specific_refs and not capacities_visible_in_refs(root, session_capacities(block), info.existing_specific_refs):
                blockage = "capacité absente des supports cités"
                result.errors.append(
                    f"{path.relative_to(root).as_posix()}: {session_id} capacité officielle non visible dans les supports cités"
                )
            if info.theoretical and info.existing_specific_refs:
                result.theoretical_with_existing_supports += 1
                blockage = "théorique malgré supports cités existants"
                result.errors.append(
                    f"{path.relative_to(root).as_posix()}: {session_id} marqué théorique alors que les supports cités existent"
                )
            elif info.theoretical and sequence_supports_exist(root, prefix):
                blockage = "théorique malgré paquet de supports produit"
                result.corrected_candidates.append(
                    f"{path.relative_to(root).as_posix()}: {session_id} -> supports {prefix} produits, séance à relier"
                )
                result.errors.append(
                    f"{path.relative_to(root).as_posix()}: {session_id} théorique alors que le paquet {prefix} est produit"
                )
            result.rows.append(
                {
                    "séance": session_id,
                    "statut actuel": status,
                    "supports cités": refs_display,
                    "supports existants": ", ".join(info.existing_specific_refs) if info.existing_specific_refs else "-",
                    "action": action,
                    "blocage": blockage,
                }
            )
    return result


def main() -> int:
    result = analyze_session_to_resource_alignment()
    print(f"Séances opérationnelles : {result.operational_count}")
    print(f"Séances théoriques ou non reliées : {result.theoretical_count}")
    print(f"Séances théoriques avec supports cités existants : {result.theoretical_with_existing_supports}")
    print("| séance | statut actuel | supports cités | supports existants | action | blocage |")
    print("|---|---|---|---|---|---|")
    for row in result.rows[:260]:
        print(
            "| "
            + " | ".join(
                row[key].replace("|", "/")
                for key in ["séance", "statut actuel", "supports cités", "supports existants", "action", "blocage"]
            )
            + " |"
        )
    if result.corrected_candidates:
        print("Séances théoriques avec paquet de ressources produit :")
        for item in result.corrected_candidates[:220]:
            print(f"- {item}")
    if result.errors:
        print("check_session_to_resource_alignment: KO")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print("check_session_to_resource_alignment: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
