#!/usr/bin/env python3
"""Registre de couverture des reponses, pour toutes les paires EX/CO.

Le graphe EX/CO echoue fermé sur `UNKNOWN` quand une paire est
structurellement saine : identite, cardinalite et perimetre ne prouvent pas
qu'un corrige REPONDE a son exercice. Ce registre est l'autorite semantique
qui manquait.

Ce qu'il etablit : une COUVERTURE -- chaque question de l'exercice recoit une
reponse reperable. Ce qu'il n'etablit PAS : que la reponse soit juste.
L'exactitude reste prouvee ailleurs (blocs d'execution, oracle SymPy, revue
humaine). Le registre nomme donc son statut `ANSWER_COVERAGE_ESTABLISHED` et
jamais « verifie » : confondre les deux ferait passer un corrige complet mais
faux pour un corrige valide.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUTPUT = ROOT / "audit/EX_CO_ANSWER_COVERAGE_LEDGER.json"
CORPORA = (
    ROOT / "Mathematiques" / "manuel-maths" / "chapitres",
    ROOT / "NSI" / "chapitres",
)


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _meta(text: str) -> dict[str, Any]:
    try:
        return json.loads(text.split("META:", 1)[1].split("\n", 1)[0])
    except (IndexError, json.JSONDecodeError):
        return {}


def build_ledger() -> dict[str, Any]:
    coverage = _load("ex_co_answer_coverage", "scripts/ex_co_answer_coverage.py")

    exercises: dict[str, Path] = {}
    corrections: list[tuple[str, Path, dict[str, Any]]] = []
    for corpus in CORPORA:
        if not corpus.is_dir():
            continue
        for chapter in sorted(corpus.iterdir()):
            if not (chapter / "contrat.yaml").is_file():
                continue
            for sub in ("exercices", "corriges"):
                directory = chapter / sub
                if not directory.is_dir():
                    continue
                for path in sorted(directory.glob("*.tex")):
                    meta = _meta(path.read_text(encoding="utf-8", errors="replace"))
                    identifier = meta.get("id")
                    if not isinstance(identifier, str):
                        continue
                    if sub == "exercices":
                        exercises[identifier] = path
                    else:
                        corrections.append((chapter.name, path, meta))

    rows: list[dict[str, Any]] = []
    for chapter, path, meta in corrections:
        reference = next(
            (
                str(meta[key]).strip()
                for key in ("exercice_id", "exercice_ref")
                if isinstance(meta.get(key), str) and str(meta[key]).strip()
            ),
            None,
        )
        exercise = exercises.get(reference) if reference else None
        if exercise is None:
            # L'appariement est l'affaire du graphe EX/CO, pas de ce registre.
            continue
        verdict, evidence = coverage.classify(
            coverage.pedagogical_body(exercise),
            coverage.pedagogical_body(path),
        )
        rows.append(
            {
                "chapter": chapter,
                "correction_id": meta.get("id"),
                "exercise_id": reference,
                "correction_path": str(path.relative_to(ROOT)),
                "exercise_path": str(exercise.relative_to(ROOT)),
                "verdict": verdict,
                "evidence": evidence,
            }
        )

    rows.sort(key=lambda row: (row["chapter"], str(row["correction_id"])))
    per_chapter: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: collections.defaultdict(int)
    )
    for row in rows:
        per_chapter[row["chapter"]][row["verdict"]] += 1
    digest = hashlib.sha256(
        "\n".join(f"{r['correction_id']}:{r['verdict']}" for r in rows).encode("utf-8")
    ).hexdigest()
    return {
        "artifact_type": "ex_co_answer_coverage_ledger",
        "schema_version": 1,
        "establishes": "ANSWER_COVERAGE_ONLY_NOT_SCIENTIFIC_CORRECTNESS",
        "totals": dict(collections.Counter(row["verdict"] for row in rows)),
        "per_chapter": {k: dict(v) for k, v in sorted(per_chapter.items())},
        "relation_set_digest": "sha256:" + digest,
        "relations": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    ledger = build_ledger()
    payload = json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != payload:
            print("EX_CO_ANSWER_COVERAGE_LEDGER stale")
            return 1
        print("EX_CO_ANSWER_COVERAGE_LEDGER a jour")
        return 0
    OUTPUT.write_text(payload, encoding="utf-8")
    print(f"wrote {OUTPUT.name}: {ledger['totals']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
