#!/usr/bin/env python3
"""Rattacher la couverture aux objets reellement composes dans le manuel.

Les matrices NSI declarent leurs sources sur le corpus d'ecriture
(`corpus_nsi/…`, des fichiers Markdown) et non sur les objets du manuel
publie. Le contenu est peut-etre enseigne, mais le mapping ne le prouve pas :
il designe un artefact que le lecteur ne recoit jamais.

Ce module cherche, dans le chapitre que l'atome declare, l'objet compose qui
porte reellement la notion, et ne repointe que lorsqu'il le trouve. Un atome
sans objet porteur reste casse : il devient un vrai constat, pas un maquillage.
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
MATRIX_ROOT = ROOT / "audit/official_program_coverage"
JSON_TARGET = ROOT / "audit/COVERAGE_REPOINT_TO_MANUAL.json"

ROLE_FIELD = {
    "cours": "course_sources", "methodes": "method_sources",
    "exercices": "exercise_sources", "corriges": "correction_sources",
    "evaluations": "assessment_sources", "remediation": "remediation_sources",
    "qcm": "assessment_sources", "projet": "exercise_sources",
}
STOPWORDS = {
    "les", "des", "une", "aux", "leur", "dans", "pour", "avec", "sur", "par",
    "que", "qui", "dont", "est", "sont", "etre", "avoir", "faire", "plus",
    "tout", "cette", "elle", "eleves", "eleve", "doivent", "savoir", "notion",
    "notions", "utiliser", "connaitre", "ecrire", "positif", "simple",
}
MIN_TERM = 6
MIN_HITS = 2


def _fold(text: str) -> str:
    folded = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in folded if unicodedata.category(c) != "Mn")


def _terms(wording: str) -> list[str]:
    words = re.findall(r"[a-zA-Zàâäéèêëîïôöùûüç]+", wording)
    out: list[str] = []
    for word in words:
        folded = _fold(word)
        if len(folded) >= MIN_TERM and folded not in STOPWORDS and folded not in out:
            out.append(folded)
    return out


def _chapter_capacities(root: Path, chapter: str) -> dict[str, str]:
    """Correspondance reference officielle <-> code local, lue dans le contrat."""

    contract = root / "NSI/chapitres" / chapter / "contrat.yaml"
    if not contract.is_file():
        return {}
    mapping: dict[str, str] = {}
    for line in contract.read_text(encoding="utf-8", errors="ignore").splitlines():
        code = re.search(r"code:\s*([A-Za-z0-9_-]+)", line)
        ref = re.search(r"ref_capacite:\s*([A-Za-z0-9_-]+)", line)
        if code and ref:
            mapping[ref.group(1)] = code.group(1)
            mapping[code.group(1)] = code.group(1)
    return mapping


def _declared_capacities(text: str) -> set[str]:
    head = text.split("\n", 1)[0]
    if not head.startswith("% META:"):
        return set()
    try:
        meta = json.loads(head[len("% META:"):].strip())
    except json.JSONDecodeError:
        return set()
    values = (meta.get("capacites_codes") or []) + (meta.get("capacites") or [])
    out: set[str] = set()
    for value in values:
        out.add(str(value))
        out.add(str(value).rsplit("-", 1)[-1])
    return out


def build(root: Path, *, apply: bool, manuals: tuple[str, ...]) -> dict[str, Any]:
    chain = json.loads((root / "audit/COVERAGE_CHAIN.json").read_text(encoding="utf-8"))
    broken = {
        r["atom_id"] for r in chain["results"]
        if r["chain"] == "BROKEN" and r["manual"] in manuals
    }

    # Texte de chaque objet compose, par chapitre.
    by_chapter: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for path in sorted((root / "NSI/chapitres").rglob("*.tex")):
        if "_harvest" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        chapter = relative.split("/chapitres/", 1)[1].split("/", 1)[0]
        # Les blocs `% BEGIN-VERIFY` sont des commentaires LaTeX : ils ne sont
        # jamais imprimes. Les lire ferait croire qu'une notion est enseignee
        # alors qu'elle n'atteint jamais la page.
        printed_only = "\n".join(
            line
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if not line.lstrip().startswith("%")
        )
        by_chapter[chapter].append((relative, _fold(printed_only)))

    repointed: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    for name in sorted(MATRIX_ROOT.glob("*.json")):
        payload = json.loads(name.read_text(encoding="utf-8"))
        if payload.get("manual") not in manuals:
            continue
        touched = False
        for row in payload.get("rows", []):
            if row.get("atom_id") not in broken:
                continue
            chapter = str(row.get("chapter") or "")
            wording = str(row.get("official_wording_or_short_paraphrase") or "")
            terms = _terms(wording)
            # La capacite declaree designe le candidat ; elle ne le prouve pas.
            # La preuve reste le contenu imprime, verifie par le gate de chaine.
            capacities = _chapter_capacities(root, chapter)
            declared_capacity = str(row.get("contract_capacity") or "")
            # Un objet peut declarer la reference officielle (P-BASE-01) ou le
            # code local (C1) : les deux designent la meme capacite.
            accepted = {c for c in (declared_capacity, capacities.get(declared_capacity)) if c}
            accepted |= {f"{chapter}-{c}" for c in list(accepted)}
            # « Recursivite. » ne fournit qu'un mot : exiger deux correspondances
            # exactes rendrait invisible une notion pourtant enseignee. On
            # compare donc aussi par radical, et on abaisse le seuil quand
            # l'enonce officiel est trop court pour en fournir deux.
            stems = [t[:6] for t in terms if len(t) >= 6]
            required = MIN_HITS if len(terms) >= 3 else 1
            best: tuple[int, str] | None = None
            for relative, body in by_chapter.get(chapter, []):
                hits = sum(1 for term in terms if term in body)
                if hits < required:
                    hits = max(hits, sum(1 for stem in stems if stem in body))
                if accepted:
                    declared = _declared_capacities(
                        (root / relative).read_text(encoding="utf-8", errors="ignore")
                    )
                    if declared & accepted:
                        # Un objet qui sert explicitement la capacite prime sur
                        # une simple coincidence de vocabulaire.
                        hits += 10
                if hits >= required and (best is None or hits > best[0]):
                    best = (hits, relative)
            if best is None:
                unmatched.append({
                    "atom_id": row["atom_id"], "chapter": chapter,
                    "why": "aucun objet compose du chapitre ne porte la notion",
                })
                continue
            hits, relative = best
            role = relative.split("/chapitres/", 1)[1].split("/")[1]
            field = ROLE_FIELD.get(role, "course_sources")
            if relative not in row.get(field, []):
                row.setdefault(field, []).append(relative)
            evidence = row.setdefault("evidence_paths", [])
            if relative not in evidence:
                evidence.append(relative)
            row["source_content_state"] = "PRESENT"
            touched = True
            repointed.append({
                "atom_id": row["atom_id"], "chapter": chapter,
                "source": relative, "term_hits": hits, "terms": len(terms),
            })
        if touched and apply:
            name.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    return {
        "artifact_type": "coverage_repoint_to_manual",
        "generated_by": "scripts/repoint_coverage_to_manual.py",
        "repointed": repointed,
        "unmatched": unmatched,
        "summary": {
            "BROKEN_CHAINS_CONSIDERED": len(broken),
            "REPOINTED_TO_MANUAL_OBJECT": len(repointed),
            "NO_MANUAL_OBJECT_FOUND": len(unmatched),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--manual", action="append", default=None)
    args = parser.parse_args()
    manuals = tuple(args.manual or ("1NSI", "TNSI"))
    report = build(args.root, apply=args.apply, manuals=manuals)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
