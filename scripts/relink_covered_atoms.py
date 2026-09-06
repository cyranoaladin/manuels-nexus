#!/usr/bin/env python3
"""Inscrire, pour un atome deja couvert, la source qui le couvre reellement.

Certains atomes sont declares rattaches sans qu'aucune source ne soit
enregistree, alors que le contenu existe et s'imprime. Ce n'est pas une lacune
pedagogique : c'est une preuve manquante. Ce module ecrit la source dans la
matrice canonique du manuel, avec la page ou l'objet apparait reellement.

Aucun contenu pedagogique n'est touche.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TRIAGE = ROOT / "audit/FALSE_COVERAGE_TRIAGE.json"
MATRIX_ROOT = ROOT / "audit/official_program_coverage"

ROLE_FIELD = {
    "cours": "course_sources",
    "methodes": "method_sources",
    "exercices": "exercise_sources",
    "corriges": "correction_sources",
    "evaluations": "assessment_sources",
    "remediation": "remediation_sources",
    "qcm": "assessment_sources",
    "projet": "exercise_sources",
    "coups_de_pouce": "method_sources",
}
MANUAL_PDF = {
    "1SPE": "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf",
    "TSPE": "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf",
    "TCOMPL": "Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_professeur.pdf",
    "TEXPERTES": "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_professeur.pdf",
    "1NSI": "NSI/build/MANUEL_1NSI/MANUEL_1NSI_professeur.pdf",
    "TNSI": "NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf",
}
MATRIX_NAME = {"TSPE": "TSPE", "1SPE": "1SPE", "TCOMPL": "TCOMPL",
               "TEXPERTES": "TEXPERTES", "1NSI": "1NSI", "TNSI": "TNSI"}


def _normalise(text: str) -> str:
    """Comparer ce qui est lu, pas ce qui est ecrit.

    Le PDF recompose les espaces, coupe les mots et perd la ponctuation de
    source. On rapproche donc les deux cotes sur une forme reduite.
    """

    import unicodedata

    folded = unicodedata.normalize("NFD", text.lower())
    folded = "".join(c for c in folded if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", folded).strip()


def _anchor_candidates(source: Path) -> list[str]:
    """Plusieurs phrases du texte imprime, de la plus longue a la plus courte."""

    text = source.read_text(encoding="utf-8", errors="ignore")
    body = "\n".join(
        line for line in text.splitlines()[1:] if not line.lstrip().startswith("%")
    )
    plain = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", " ", body)
    plain = re.sub(r"[{}$\\]", " ", plain)
    pieces = [
        re.sub(r"\s+", " ", piece).strip()
        for piece in re.split(r"(?<=[.;:!?])\s", plain)
    ]

    def usable(piece: str) -> bool:
        # Un residu de macro (« [label= .] ») ou une phrase surtout symbolique
        # ne se retrouve pas tel quel dans le PDF : ce sont de mauvais reperes.
        if len(piece) < 25 or any(token in piece for token in ("[", "]", "=")):
            return False
        letters = sum(1 for c in piece if c.isalpha() or c.isspace())
        return letters / len(piece) >= 0.75

    return sorted((p for p in pieces if usable(p)), key=len, reverse=True)[:20]


def _page_of(pdf: Path, candidates: list[str]) -> tuple[int | None, str | None]:
    import fitz

    with fitz.open(pdf) as document:
        pages = [_normalise(page.get_text()) for page in document]
    for phrase in candidates:
        needle = _normalise(phrase)
        # Une ancre trop courte retrouverait n'importe quoi.
        for length in (90, 60, 40):
            probe = needle[:length]
            if len(probe) < 30:
                continue
            for number, page in enumerate(pages, 1):
                if probe in page:
                    return number, phrase
    return None, None


def relink(root: Path, *, apply: bool) -> dict[str, Any]:
    triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
    covered = [e for e in triage["entries"] if e["state"] == "COVERED_BY_REAL_CONTENT"]

    matrices: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    for entry in covered:
        manual = entry["manual"]
        source_rel = entry["candidate_source"]
        source = root / source_rel
        role = source_rel.split("/chapitres/", 1)[1].split("/")[1]
        field = ROLE_FIELD.get(role)
        candidates = _anchor_candidates(source) if source.is_file() else []
        pdf = root / MANUAL_PDF[manual]
        page, phrase = (
            _page_of(pdf, candidates) if (candidates and pdf.is_file()) else (None, None)
        )

        name = MATRIX_NAME[manual]
        if name not in matrices:
            matrices[name] = json.loads(
                (MATRIX_ROOT / f"{name}.json").read_text(encoding="utf-8")
            )
        row = next(
            (r for r in matrices[name]["rows"] if r["atom_id"] == entry["atom_id"]), None
        )
        applied = False
        if row is not None and field:
            if source_rel not in row.get(field, []):
                row.setdefault(field, []).append(source_rel)
            evidence = row.setdefault("evidence_paths", [])
            if source_rel not in evidence:
                evidence.append(source_rel)
            row["gap_type"] = None
            row["source_content_state"] = "PRESENT"
            # La raison de lacune devient fausse des lors qu'une source est
            # inscrite : la remplacer, plutot que laisser deux affirmations
            # contradictoires dans la meme ligne.
            row["gap_reason"] = (
                "Preuve de couverture retablie : le contenu existe et s'imprime ; "
                f"seule son inscription manquait. Source : {source_rel}"
                + (f", page {page} de la variante professeur." if page else ".")
            )
            if page:
                row["official_page_or_anchor"] = row.get("official_page_or_anchor")
                row["printed_page"] = page
            applied = True
        results.append({
            "atom_id": entry["atom_id"], "manual": manual, "role": role,
            "field": field, "source": source_rel, "printed_page": page,
            "anchor": (phrase or "")[:90], "applied": applied,
        })

    if apply:
        for name, payload in matrices.items():
            # Conserver l'ordre des cles d'origine : trier reecrirait le
            # fichier entier et rendrait la revue du changement impossible.
            (MATRIX_ROOT / f"{name}.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    return {
        "artifact_type": "covered_atom_relink",
        "generated_by": "scripts/relink_covered_atoms.py",
        "results": results,
        "summary": {
            "COVERED_ATOMS": len(covered),
            "RELINKED": sum(1 for r in results if r["applied"]),
            "WITH_PRINTED_PAGE": sum(1 for r in results if r["printed_page"]),
        },
    }



def filler_to_canonical(root: Path) -> dict[str, str]:
    """Correspondance copie -> objet canonique, etablie par la lignee.

    Une couverture declaree sur une copie n'etait pas une couverture : le
    filler heritait d'une capacite qu'il ne faisait que dupliquer. La source
    doit donc pointer sur l'objet authentique du groupe, pas disparaitre.
    """

    lineage_path = root / "audit/PREFILLER_LINEAGE.json"
    if not lineage_path.is_file():
        return {}
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for group in lineage["groups"]:
        canonical = group.get("canonical_path")
        if not canonical:
            continue
        for filler in group.get("filler_paths", []):
            if filler != canonical:
                mapping[filler] = canonical
    return mapping


def repoint_removed_sources(root: Path, *, apply: bool) -> dict[str, Any]:
    """Rediriger vers le canonique toute source de couverture supprimee."""

    mapping = filler_to_canonical(root)
    changes: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    fields = (
        "course_sources", "method_sources", "exercise_sources",
        "correction_sources", "assessment_sources", "remediation_sources",
        "evidence_paths",
    )
    for matrix in sorted(MATRIX_ROOT.glob("*.json")):
        payload = json.loads(matrix.read_text(encoding="utf-8"))
        touched = False
        for row in payload.get("rows", []):
            for field in fields:
                values = row.get(field)
                if not isinstance(values, list):
                    continue
                rewritten = []
                for value in values:
                    target = str(value).split("#", 1)[0]
                    if (root / target).exists():
                        rewritten.append(value)
                        continue
                    canonical = mapping.get(target)
                    if canonical and (root / canonical).exists():
                        rewritten.append(canonical)
                        changes.append({
                            "atom_id": row.get("atom_id"), "field": field,
                            "was": target, "now": canonical,
                        })
                        touched = True
                    else:
                        unresolved.append({
                            "atom_id": row.get("atom_id"), "field": field,
                            "missing": target,
                        })
                # dedupliquer sans changer l'ordre
                seen: list[str] = []
                for value in rewritten:
                    if value not in seen:
                        seen.append(value)
                if seen != values:
                    row[field] = seen
                    touched = True
        if touched and apply:
            matrix.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    return {"repointed": changes, "unresolved": unresolved}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    repoint = repoint_removed_sources(args.root, apply=args.apply)
    report = relink(args.root, apply=args.apply)
    report["repointed_removed_sources"] = repoint["repointed"]
    report["unresolved_removed_sources"] = repoint["unresolved"]
    report["summary"]["REPOINTED_TO_CANONICAL"] = len(repoint["repointed"])
    report["summary"]["UNRESOLVED_REMOVED_SOURCES"] = len(repoint["unresolved"])
    (ROOT / "audit/COVERED_ATOM_RELINK.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["summary"], indent=2))
    for r in report["results"]:
        print(f"  {r['atom_id']:22s} p.{str(r['printed_page'] or '?'):>4s}  {r['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
