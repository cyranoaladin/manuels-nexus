#!/usr/bin/env python3
"""D'ou vient la cible de cinquante exercices par chapitre ?

Avant d'ecrire quoi que ce soit pour « completer » un chapitre, il faut savoir
si ce nombre est une exigence de release ou une habitude de production. La
difference decide du sort de plusieurs centaines d'objets : combler un volume
qui n'a jamais ete exige, c'est refabriquer le remplissage qu'on repare.

Ce producteur cherche la trace de la regle dans TOUT le depot -- prompts,
directives, specs, tests, producteurs -- et classe chaque trace.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_TARGET = ROOT / "audit/FIFTY_EXERCISES_POLICY_ORIGIN.json"
MD_TARGET = ROOT / "audit/FIFTY_EXERCISES_POLICY_ORIGIN.md"
GENERATED_BY = "scripts/build_fifty_exercises_policy_origin.py"

OWNER = "EXPLICIT_RELEASE_OWNER_REQUIREMENT"
GUIDELINE = "EDITORIAL_GUIDELINE"
GENERATOR = "GENERATOR_ASSUMPTION"
FILLER = "SYNTHETIC_FILLER_ARTIFACT"
UNKNOWN = "UNKNOWN"
CLASSES = (OWNER, GUIDELINE, GENERATOR, FILLER, UNKNOWN)

#: Les traces reelles, chacune verifiee a la main dans le depot. Le
#: classement n'est pas devine : il decoule de la NATURE du document ou la
#: regle vit, et cette nature est verifiable en ouvrant le fichier.
TRACES = (
    {
        "source": "PROMPT_MISSION_COLLECTION.md",
        "locator": "### 3.4 Ce qui NE change PAS",
        "quote": "matrice ≥2 ex/case et ≥50 ex/chapitre",
        "classification": OWNER,
        "why": (
            "le prompt de mission ecrit par le Release Owner, dans une section "
            "intitulee « Ce qui NE change PAS » : c'est une directive humaine "
            "explicite, pas une convention d'outil"
        ),
    },
    {
        "source": "scripts/chapter_readiness.py",
        "locator": "TARGET_EXERCISES = min(50, max(24, 6 * C))",
        "quote": "TARGET_EXERCISES = min(50, max(24, 6 * C))",
        "classification": GENERATOR,
        "why": (
            "un seuil interne a un tableau de bord que son propre en-tete "
            "declare « non autoritaire pour la release » ; il derive la cible "
            "du nombre de capacites au lieu de l'imposer"
        ),
    },
    {
        "source": (
            "Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/"
            "LOT-4_addendum_seuil_E5.md"
        ),
        "locator": "| **Total** | 20 | 20 | 10 | **50** |",
        "quote": "Ratio 40/40/20 exactement conforme à E5/F01",
        "classification": GUIDELINE,
        "why": (
            "un compte rendu de production qui atteint cinquante pour un "
            "chapitre donne ; il documente une realisation, il n'edicte rien"
        ),
    },
)


def _grep(motif: str) -> list[str]:
    sortie = subprocess.run(
        ["git", "grep", "-n", "-I", motif, "--", ".", ":!audit", ":!.git"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout
    return [ligne for ligne in sortie.splitlines() if ligne.strip()]


def build(root: Path = ROOT) -> dict[str, Any]:
    traces = []
    for trace in TRACES:
        chemin = root / trace["source"]
        present = chemin.is_file() and trace["locator"] in chemin.read_text(
            encoding="utf-8", errors="replace"
        )
        traces.append(dict(trace, verified_in_tree=present))

    # Un test ou un gate qui EXIGERAIT cinquante serait la trace la plus
    # forte : on la cherche explicitement, et son absence est un fait.
    # Un `50` isole ne prouve rien : le corpus en contient dans des enonces
    # (« seuil de 2 500 »). On exige que la ligne porte un COMPTE d'exercices
    # ET une contrainte, et que le nombre soit un jeton a lui seul.
    compte = re.compile(
        r"(?:exercice|exercise)[a-z_]*\s*(?:\)|\]|\.[a-z_]+\(\))?\s*"
        r"(?:[<>]=?|==)\s*50\b"
        r"|50\s*(?:[<>]=?|==)\s*[a-z_]*(?:exercice|exercise)",
        re.I,
    )
    gates = [
        ligne
        for ligne in _grep(r"\b50\b")
        if ligne.startswith(("tests/", "scripts/")) and compte.search(ligne)
    ]

    exigence_release = any(
        t["classification"] == OWNER and t["verified_in_tree"] for t in traces
    )
    summary = {
        "FIFTY_EXERCISES_POLICY_ORIGIN": sorted(
            {t["classification"] for t in traces if t["verified_in_tree"]}
        ),
        "FIFTY_EXERCISES_RELEASE_REQUIREMENT": (
            "SUPERSEDED_EXPLICIT_REQUIREMENT" if exigence_release
            else "NOT_A_RELEASE_REQUIREMENT"
        ),
        "TRACES_FOUND": sum(1 for t in traces if t["verified_in_tree"]),
        "RELEASE_GATES_ENFORCING_FIFTY": len(gates),
        "APPROVES_NOTHING": True,
    }
    return {
        "artifact_type": "fifty_exercises_policy_origin",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "classes": list(CLASSES),
        "summary": summary,
        "traces": traces,
        "release_gates_enforcing_fifty": gates,
        "current_authority": (
            "La decision humaine du 2026-09-07 ne fixe aucun nombre : « le "
            "volume est une consequence de la qualite, jamais la cible ». Elle "
            "est posterieure a la directive du 2026-07-16 et la remplace pour "
            "la reconstruction. La directive anterieure est donc remontee "
            "comme preuve, sans etre appliquee : aucun objet ne sera cree pour "
            "atteindre cinquante."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Origine de la cible « cinquante exercices par chapitre »",
        "",
        f"- `FIFTY_EXERCISES_POLICY_ORIGIN` : `{', '.join(s['FIFTY_EXERCISES_POLICY_ORIGIN'])}`",
        f"- `FIFTY_EXERCISES_RELEASE_REQUIREMENT` : "
        f"`{s['FIFTY_EXERCISES_RELEASE_REQUIREMENT']}`",
        f"- gates de release imposant cinquante : `{s['RELEASE_GATES_ENFORCING_FIFTY']}`",
        "",
        "## Traces",
        "",
    ]
    for trace in payload["traces"]:
        lignes += [
            f"### `{trace['source']}` — `{trace['classification']}`",
            "",
            f"> {trace['quote']}",
            "",
            trace["why"].capitalize() + ".",
            "",
        ]
    lignes += ["## Autorite courante", "", payload["current_authority"], ""]
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build(ROOT)
    rendus = {
        JSON_TARGET: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MD_TARGET: render_markdown(payload),
    }
    if args.check:
        ecarts = [
            str(p.relative_to(ROOT))
            for p, c in rendus.items()
            if not p.is_file() or p.read_text(encoding="utf-8") != c
        ]
        for e in ecarts:
            print(f"diff: {e}")
        return 1 if ecarts else 0
    for chemin, contenu in rendus.items():
        chemin.write_text(contenu, encoding="utf-8")
        print(f"wrote {chemin.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
