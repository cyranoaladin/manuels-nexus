#!/usr/bin/env python3
"""Les mathematiques de Terminale logees dans les chapitres d'algorithmique NSI.

Le manuel eleve de Premiere NSI imprime, entre un exercice Python de tri et le
chapitre suivant, une fiche intitulee « Deriver une fonction composee », avec la
formule de derivation en chaine et l'exemple f(x) = e^(x^2-3x). Elle porte le
statut `approved` et declare la capacite C1 du chapitre : « ecrire un algorithme
de recherche d'une occurrence dans un tableau ».

Ce n'est pas un clone : son corps est unique, et le registre de clonage ne peut
pas la voir. C'est un defaut d'une autre nature -- du contenu d'une AUTRE
DISCIPLINE et d'un AUTRE NIVEAU, credite a une capacite qu'il ne sert pas.

LE DISCRIMINANT.

Le programme de Premiere NSI ne comporte aucune analyse : ni derivation, ni
limite, ni integrale, ni etude de fonction. Un objet qui demande de deriver, de
dresser un tableau de signes ou d'etudier des variations n'appartient donc pas a
ce niveau, quel que soit le vocabulaire informatique qui l'entoure. C'est un
critere de NIVEAU et de DISCIPLINE, pas une appreciation de style.

A l'inverse, un exercice de k plus proches voisins qui calcule une distance
euclidienne mobilise des mathematiques SANS relever de l'analyse : il reste de
la NSI. Le critere ne le condamne pas.

Aucun objet ne reste UNKNOWN : ce qui ne porte ni marqueur d'analyse ni marqueur
informatique est signale pour arbitrage explicite, jamais classe par defaut.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json"
CHAPTERS = ("1NSI-ALGO-DICHO-GLOUTON-KNN", "1NSI-ALGO-PARCOURS-TRIS")
ROLES = ("cours", "methodes", "exercices", "corriges", "remediation", "evaluations", "qcm")

#: Analyse de Terminale. Absente du programme de Premiere NSI, donc
#: discriminante a elle seule.
CALCULUS = {
    "derivation": r"\bd[ée]riv(?:er|ee|ée|able|ation)",
    "derivee_notation": r"f'\s*\(|u'\s*\(|v'\s*\(|\\dfrac\{\\mathrm\{d\}",
    "variations": r"\bvariations? de\b|tableau de (?:signes|variations)",
    "limite": r"\blimite?s? (?:de|en|quand)\b|\\lim|\blimit\(",
    "primitive_integrale": r"\bprimitives?\b|\bint[ée]grales?\b|\\int\b|integrate\(",
    "exp_log": r"\\mathrm\{e\}\^|\\ln\b|\blogarithme\b|\bexponentielle\b",
    "convexite": r"\bconvexit|\bconcavit|point d'inflexion",
    "asymptote": r"\basymptote",
    "sympy_analyse": r"\bdiff\(|\bsolve\(\s*fp|\boo\b",
}

#: Marqueurs informatiques. Ils n'innocentent pas un objet d'analyse, mais
#: attestent qu'un objet sans analyse releve bien de la NSI.
COMPUTING = {
    "python": r"\\lstinline|lstlisting|>>>|\bdef \w+\(|\bPython\b",
    "algorithmique": r"\balgorithme|\binvariant de boucle|\bterminaison|\bvariant\b",
    "structures": r"\btableau\b|\bliste\b|\bindice\b|\bparcours\b",
    "chapitre": r"\btri (?:par )?(?:insertion|selection|s[ée]lection)|\bdichotom|\bglouton|plus proches voisins|\bk-?NN\b",
    "code_python": r"\bfrom \w+(?:\.\w+)* import\b|\bimport \w+|\breturn\b|\bfor \w+ in\b|\bwhile\b",
}


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _payload(text: str) -> str:
    """Le corps, commentaires LaTeX retires -- mais le bloc VERIFY conserve.

    Un bloc SymPy qui derive et calcule des limites est une preuve de
    discipline aussi forte que l'enonce lui-meme.
    """

    keep = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("% META:"):
            continue
        keep.append(stripped[1:] if stripped.startswith("%") else line)
    return "\n".join(keep)


def _evidence(patterns: dict[str, str], body: str) -> list[str]:
    return sorted(
        name for name, pattern in patterns.items() if re.search(pattern, body, re.I)
    )


def _display_path(path: Path) -> str:
    """Return a stable repository path without assuming fixture location."""

    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def _surface_row(
    *,
    chapter: str,
    role: str,
    path: Path,
    source_kind: str,
    text: str,
    pointers: list[str],
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify one complete source surface and retain auditable evidence.

    The row is deliberately file-scoped: a calculus marker anywhere in a
    contract, QCM source or executable Python file condemns the surface.  The
    supplied pointers identify the structured locations inspected; no source
    is silently reduced to a LaTeX body.
    """

    metadata = meta or {}
    body = _payload(text) if source_kind == "LATEX_OBJECT" else text
    calculus = _evidence(CALCULUS, body)
    computing = _evidence(COMPUTING, body)
    if calculus:
        verdict = "CROSS_DISCIPLINE_TERMINALE_MATHS"
    elif computing:
        verdict = "NSI_NATIVE"
    else:
        verdict = "REQUIRES_EXPLICIT_ADJUDICATION"
    return {
        "chapter": chapter,
        "role": role,
        "source_kind": source_kind,
        "path": _display_path(path),
        "pointers": list(pointers),
        "sha256": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "object_id": metadata.get("id"),
        "declared_status": metadata.get("status"),
        "declared_capacities": list(
            metadata.get("capacites_codes") or metadata.get("capacites") or []
        ),
        "calculus_evidence": calculus,
        "computing_evidence": computing,
        "verdict": verdict,
    }


def build_ledger() -> dict[str, Any]:
    clone = _clone_module()
    rows: list[dict[str, Any]] = []
    for chapter in CHAPTERS:
        base = ROOT / "NSI/chapitres" / chapter
        for role in ROLES:
            directory = base / role
            if not directory.is_dir():
                continue
            for path in sorted(directory.glob("*.tex")):
                text = path.read_text(encoding="utf-8", errors="replace")
                meta = clone.read_meta(text)
                rows.append(
                    _surface_row(
                        chapter=chapter,
                        role=role,
                        path=path,
                        source_kind="LATEX_OBJECT",
                        text=text,
                        pointers=["$"],
                        meta=meta,
                    )
                )

        contract = base / "contrat.yaml"
        if contract.is_file():
            rows.append(
                _surface_row(
                    chapter=chapter,
                    role="contract",
                    path=contract,
                    source_kind="YAML_CONTRACT",
                    text=contract.read_text(encoding="utf-8", errors="replace"),
                    pointers=["$"],
                )
            )

        qcm_sources = sorted((base / "qcm").glob("*-QCM.json"))
        if len(qcm_sources) > 1:
            raise ValueError(
                f"{chapter}: multiple authoritative QCM JSON sources: "
                + ", ".join(_display_path(path) for path in qcm_sources)
            )
        for path in qcm_sources:
            rows.append(
                _surface_row(
                    chapter=chapter,
                    role="qcm_source",
                    path=path,
                    source_kind="JSON_QCM",
                    text=path.read_text(encoding="utf-8", errors="replace"),
                    pointers=["$"],
                )
            )

        for path in sorted((base / "code").glob("*.py")):
            rows.append(
                _surface_row(
                    chapter=chapter,
                    role="code",
                    path=path,
                    source_kind="PYTHON_CODE",
                    text=path.read_text(encoding="utf-8", errors="replace"),
                    pointers=["$"],
                )
            )

    verdicts = collections.Counter(row["verdict"] for row in rows)
    condemned = sorted(
        row["path"]
        for row in rows
        if row["verdict"] == "CROSS_DISCIPLINE_TERMINALE_MATHS"
    )
    per_chapter: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for row in rows:
        per_chapter[row["chapter"]][row["verdict"]] += 1
        if row["verdict"] == "CROSS_DISCIPLINE_TERMINALE_MATHS":
            per_chapter[row["chapter"]][f"role:{row['role']}"] += 1

    approved_but_foreign = sorted(
        row["path"]
        for row in rows
        if row["verdict"] == "CROSS_DISCIPLINE_TERMINALE_MATHS"
        and row["declared_status"] == "approved"
    )
    return {
        "artifact_type": "nsi_cross_discipline_content_ledger",
        "schema_version": 2,
        "generated_by": "scripts/build_nsi_cross_discipline_ledger.py",
        "finding": "P0_CROSS_DISCIPLINE_CONTENT_CONTAMINATION",
        "distinct_from": (
            "P0_PEDAGOGICAL_CONTENT_CLONING : un objet peut etre unique et "
            "malgre tout etranger a sa discipline ; la detection de clonage ne "
            "le verrait jamais"
        ),
        "discriminator": (
            "le programme de Premiere NSI ne comporte aucune analyse : "
            "derivation, limite, integrale, etude de fonction. Un objet qui "
            "les mobilise n'appartient pas a ce niveau, quel que soit le "
            "vocabulaire informatique qui l'entoure"
        ),
        "counts": dict(sorted(verdicts.items())),
        "unknown": verdicts["REQUIRES_EXPLICIT_ADJUDICATION"],
        "objects_scanned": len(rows),
        "condemned_count": len(condemned),
        "condemned_while_approved": approved_but_foreign,
        "per_chapter": {k: dict(sorted(v.items())) for k, v in sorted(per_chapter.items())},
        "condemned_paths": condemned,
        "condemned_set_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(condemned, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "objects": rows,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    payload = build_ledger()
    rendered = render(payload)
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: {payload['condemned_count']} condamnes, "
        f"UNKNOWN={payload['unknown']}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
