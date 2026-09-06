#!/usr/bin/env python3
"""Triage des atomes declares couverts sans source de contenu.

Un atome peut etre declare couvert sans qu'aucune source ne soit enregistree,
et pourtant etre reellement enseigne : les capacites transversales du programme
de mathematiques sont explicitement a integrer au fil de l'annee, pas a isoler
dans un chapitre. On interroge donc le texte reellement imprime, manuel par
manuel, avant de conclure a une lacune.

Trois etats seulement, et jamais un exercice cree pour fermer une metrique.
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
JSON_TARGET = ROOT / "audit/FALSE_COVERAGE_TRIAGE.json"
MD_TARGET = ROOT / "audit/FALSE_COVERAGE_TRIAGE.md"
GENERATED_BY = "scripts/build_false_coverage_triage.py"

MANUAL_PDF = {
    "1SPE": "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf",
    "TSPE": "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf",
    "TCOMPL": "Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_professeur.pdf",
    "TEXPERTES": "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_professeur.pdf",
    "1NSI": "NSI/build/MANUEL_1NSI/MANUEL_1NSI_professeur.pdf",
    "TNSI": "NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf",
}

#: Mots trop courants pour temoigner de quoi que ce soit.
STOPWORDS = {
    "les", "des", "une", "aux", "leur", "dans", "pour", "avec", "sur", "par", "que",
    "qui", "dont", "est", "sont", "etre", "avoir", "faire", "plus", "moins", "tout",
    "toute", "cette", "elle", "ils", "elles", "eleves", "eleve", "doivent", "savoir",
    "connaitre", "mobiliser", "utiliser", "employer", "formuler", "lire", "ecrire",
    "simple", "notion", "notions", "expression", "expressions", "proposition",
    "propositions", "montrer", "fausse", "vraie", "contenant", "leurs", "ainsi",
}
MIN_TERM_LENGTH = 6
#: En deca, une occurrence isolee ne prouve pas un enseignement.
EVIDENCE_THRESHOLD = 3
#: Un mot present partout ne discrimine rien : il ne peut pas servir de preuve.
GENERIC_CEILING = 60
#: Un atome n'est couvert que si un objet source precis peut etre nomme.
MIN_TERMS_IN_SOURCE = 2

#: Prefixe des chapitres appartenant a chaque manuel.
MANUAL_CHAPTER_PREFIX = {
    "1SPE": "1SPE", "TSPE": "TSPE", "TCOMPL": "TCOMPL", "TEXPERTES": "TEXP",
    "1NSI": "1NSI", "TNSI": "TNSI",
}


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _terms(wording: str) -> list[str]:
    words = re.findall(r"[a-zA-Zàâäéèêëîïôöùûüç]+", wording)
    seen: list[str] = []
    for word in words:
        folded = _fold(word)
        if len(folded) < MIN_TERM_LENGTH or folded in STOPWORDS:
            continue
        if folded not in seen:
            seen.append(folded)
    return seen


def _pdf_text(path: Path) -> str:
    import fitz

    with fitz.open(path) as document:
        return _fold("".join(page.get_text() for page in document))


def build(root: Path) -> dict[str, Any]:
    validation = json.loads(
        (root / "audit/PROGRAMME_CONTENT_VALIDATION.json").read_text(encoding="utf-8")
    )
    coverage = json.loads(
        (root / "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json").read_text(encoding="utf-8")
    )
    rows = {r["atom_id"]: r for r in coverage["rows"]}
    atoms = [rows[a["atom_id"]] for a in validation["false_coverage"] if a["atom_id"] in rows]

    corpus: dict[str, str] = {}
    for manual, relative in MANUAL_PDF.items():
        path = root / relative
        if path.is_file():
            corpus[manual] = _pdf_text(path)

    # Chercher l'objet qui porte reellement la notion, plutot que compter des
    # mots : un atome n'est couvert que si l'on peut nommer sa source.
    sources: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for manual, subdir in (
        ("1SPE", "Mathematiques/manuel-maths/chapitres"),
        ("TSPE", "Mathematiques/manuel-maths/chapitres"),
        ("TCOMPL", "Mathematiques/manuel-maths/chapitres"),
        ("TEXPERTES", "Mathematiques/manuel-maths/chapitres"),
        ("1NSI", "NSI/chapitres"),
        ("TNSI", "NSI/chapitres"),
    ):
        base = root / subdir
        if not base.is_dir():
            continue
        for path in base.rglob("*.tex"):
            if "_harvest" in path.parts:
                continue
            # Un atome de 1SPE ne peut pas etre couvert par un chapitre de
            # terminale : la source doit appartenir au manuel qui declare l'atome.
            chapter_dir = path.relative_to(base).parts[0]
            if not chapter_dir.startswith(MANUAL_CHAPTER_PREFIX[manual]):
                continue
            sources[manual].append(
                (path.relative_to(root).as_posix(), _fold(path.read_text(encoding="utf-8", errors="ignore")))
            )

    entries: list[dict[str, Any]] = []
    for atom in atoms:
        manual = atom.get("manual")
        wording = str(atom.get("official_wording_or_short_paraphrase") or "")
        terms = _terms(wording)
        text = corpus.get(manual)
        if text is None:
            entries.append({
                "atom_id": atom["atom_id"], "manual": manual,
                "state": "NON_APPLICABLE_MAPPING_ERROR",
                "why": "aucun manuel imprime ne correspond a ce rattachement",
                "terms": terms, "evidence": {}, "candidate_source": None,
            })
            continue

        printed = {term: text.count(term) for term in terms}
        # Un terme omnipresent ne temoigne de rien ; un terme absent non plus.
        discriminating = [
            term for term, count in printed.items()
            if EVIDENCE_THRESHOLD <= count < GENERIC_CEILING
        ]
        missing = [term for term, count in printed.items() if count == 0]

        candidate = None
        best = 0
        for path, body in sources.get(manual, []):
            hits = sum(1 for term in terms if term in body)
            if hits > best:
                best, candidate = hits, path

        if best >= MIN_TERMS_IN_SOURCE and discriminating and not missing:
            state = "COVERED_BY_REAL_CONTENT"
            why = (
                f"un objet source porte {best} des {len(terms)} termes de l'atome ; "
                "la notion est enseignee, seule son inscription dans la matrice manque"
            )
        elif missing:
            state = "TRUE_CONTENT_GAP"
            why = (
                "des termes centraux de l'atome n'apparaissent nulle part dans le "
                f"manuel imprime : {', '.join(sorted(missing)[:4])}"
            )
        else:
            state = "TRUE_CONTENT_GAP"
            why = "aucun objet source ne porte assez de la notion pour l'attester"

        entries.append({
            "atom_id": atom["atom_id"], "manual": manual,
            "chapter": atom.get("chapter"),
            "capacity": atom.get("contract_capacity"),
            "NOR": atom.get("NOR"),
            "obligation": atom.get("obligation_type"),
            "official_wording": wording[:220],
            "state": state, "why": why,
            "terms": terms,
            "missing_terms": sorted(missing),
            "discriminating_terms": sorted(discriminating),
            "candidate_source": candidate,
            "candidate_source_term_hits": best,
            "evidence": dict(sorted(printed.items(), key=lambda kv: -kv[1])[:6]),
        })

    by_state = collections.Counter(e["state"] for e in entries)
    return {
        "artifact_type": "false_coverage_triage",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "evidence_threshold": EVIDENCE_THRESHOLD,
        "entries": entries,
        "summary": {
            "FALSE_COVERAGE_TRIAGED": len(entries),
            "COVERED_BY_REAL_CONTENT": by_state["COVERED_BY_REAL_CONTENT"],
            "TRUE_CONTENT_GAP": by_state["TRUE_CONTENT_GAP"],
            "NON_APPLICABLE_MAPPING_ERROR": by_state["NON_APPLICABLE_MAPPING_ERROR"],
            "BY_MANUAL": dict(collections.Counter(e["manual"] for e in entries)),
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
    lines = ["# Triage des fausses couvertures", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
