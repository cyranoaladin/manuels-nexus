#!/usr/bin/env python3
"""La couverture d'un atome officiel doit se prouver jusqu'a la page imprimee.

Declarer une capacite dans une ligne `% META` ne prouve rien : c'est exactement
ce qui a permis a des copies synthetiques de fabriquer de la couverture. Le gate
exige donc la chaine complete, maillon par maillon :

    atome officiel -> mapping canonique -> objet source -> objet compose
                   -> contenu reellement imprime -> page et variante

Un maillon manquant casse la chaine, quelle que soit la METAdonnee declaree.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/COVERAGE_CHAIN.json"
MD_TARGET = ROOT / "audit/COVERAGE_CHAIN.md"
GENERATED_BY = "scripts/check_coverage_chain.py"

COVERAGE = "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
INVENTORY = "audit/CANONICAL_RELEASE_INVENTORY.json"

SOURCE_FIELDS = (
    "course_sources", "method_sources", "exercise_sources",
    "correction_sources", "assessment_sources", "remediation_sources",
)
MANUAL_KEY = {"TSPE": "TSPE_2026_2027"}
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
MACRO = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?")


def _normalise(text: str) -> str:
    folded = unicodedata.normalize("NFD", text.lower())
    folded = "".join(c for c in folded if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", folded).strip()


def _anchors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    body = "\n".join(
        line for line in text.splitlines()[1:] if not line.lstrip().startswith("%")
    )
    plain = re.sub(r"[{}$\\]", " ", MACRO.sub(" ", body))
    pieces = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"(?<=[.;:!?])\s", plain)]

    def usable(piece: str) -> bool:
        if len(piece) < 25 or any(t in piece for t in ("[", "]", "=")):
            return False
        letters = sum(1 for c in piece if c.isalpha() or c.isspace())
        return letters / len(piece) >= 0.75

    return sorted((p for p in pieces if usable(p)), key=len, reverse=True)[:15]


def _assembled(root: Path, master: Path, base: Path) -> set[str]:
    pending, seen = [master.resolve()], set()
    while pending:
        current = pending.pop()
        if current in seen or not current.is_file():
            continue
        seen.add(current)
        for ref in INPUT_RE.findall(current.read_text(encoding="utf-8", errors="ignore")):
            for candidate in (base / ref, current.parent / ref):
                target = candidate if candidate.suffix == ".tex" else candidate.with_suffix(".tex")
                if target.is_file():
                    pending.append(target.resolve())
                    break
    return {p.relative_to(root).as_posix() for p in seen}


def build(root: Path) -> dict[str, Any]:
    coverage = json.loads((root / COVERAGE).read_text(encoding="utf-8"))
    inventory = json.loads((root / INVENTORY).read_text(encoding="utf-8"))

    # Objets composes et texte imprime, une fois par manuel.
    assembled: dict[str, set[str]] = collections.defaultdict(set)
    printed: dict[str, list[str]] = {}
    for target in inventory["canonical_targets"]:
        manual = target["manual_id"]
        master = root / target["master"]
        base = master.parent.parent.parent
        if master.is_file():
            assembled[manual] |= _assembled(root, master, base)
        if target["variant"] == "professeur":
            pdf = root / target["pdf"]
            if pdf.is_file():
                import fitz

                with fitz.open(pdf) as document:
                    printed[manual] = [_normalise(p.get_text()) for p in document]

    results: list[dict[str, Any]] = []
    for row in coverage["rows"]:
        manual = MANUAL_KEY.get(row.get("manual"), row.get("manual"))
        sources = [s for f in SOURCE_FIELDS for s in (row.get(f) or [])]
        atom = {
            "atom_id": row.get("atom_id"),
            "manual": row.get("manual"),
            "declared_sources": len(sources),
        }
        if not sources:
            atom.update(chain="NO_MAPPING", broken_at="canonical_mapping")
            results.append(atom)
            continue

        proven = None
        failures: list[str] = []
        for source in sources:
            relative = source.split("#", 1)[0]
            if not (root / relative).is_file():
                failures.append(f"objet source absent: {relative}")
                continue
            if relative not in assembled.get(manual, set()):
                failures.append(f"objet non compose dans le manuel: {relative}")
                continue
            pages = printed.get(manual)
            if not pages:
                failures.append("aucun PDF imprime pour ce manuel")
                continue
            page = None
            for anchor in _anchors(root / relative):
                probe = _normalise(anchor)[:60]
                if len(probe) < 30:
                    continue
                for number, text in enumerate(pages, 1):
                    if probe in text:
                        page = number
                        break
                if page:
                    break
            if page is None:
                failures.append(f"contenu introuvable dans le PDF: {relative}")
                continue
            proven = {"source": relative, "printed_page": page, "variant": "professeur"}
            break

        if proven:
            atom.update(chain="PROVEN", **proven)
        else:
            atom.update(chain="BROKEN", broken_at="printed_content", failures=failures[:3])
        results.append(atom)

    by_chain = collections.Counter(r["chain"] for r in results)
    return {
        "artifact_type": "coverage_chain",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "chain": [
            "official_atom", "canonical_mapping", "printed_object",
            "actual_relevant_content", "page/variant",
        ],
        "results": results,
        "summary": {
            "ATOMS": len(results),
            "CHAIN_PROVEN": by_chain["PROVEN"],
            "CHAIN_BROKEN": by_chain["BROKEN"],
            "NO_MAPPING": by_chain["NO_MAPPING"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = build(args.root)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = ["# Chaine de preuve de couverture", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0 if report["summary"]["CHAIN_BROKEN"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
