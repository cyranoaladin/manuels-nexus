#!/usr/bin/env python3
"""Verifie les deux banques d'epreuve TNSI contre leur plan et contre l'autorite.

Le plan a ete depose avant le moindre sujet (`tnsi_exam_bank_blueprint`). Ce
producteur verifie que ce qui a ete ecrit lui correspond — pas l'inverse. Un
sujet qui apparait sans etre au plan est un defaut, au meme titre qu'un sujet
du plan qui manque.

CE QUI EST VERIFIE.

`MISSING_FROM_PLAN`          un exercice planifie n'existe pas.
`PRESENT_WITHOUT_PLAN`       un fichier de banque n'est pas au plan.
`CAPACITY_MISMATCH`          les capacites declarees ne sont pas celles du plan,
                             ou ne figurent pas au contrat du chapitre.
`SUBJECT_NOT_THREE_EXERCISES` un sujet n'a pas exactement trois exercices.
`SUBJECT_DURATION_MISMATCH`  la somme des durees ne fait pas les 3 h 30
                             de MENE2516123N.
`SUBJECT_DOMAINS_NOT_DISTINCT` deux exercices d'un sujet couvrent le meme
                             domaine : un candidat fort sur un seul domaine
                             prendrait toute la note.
`EXERCISES_NOT_INDEPENDENT`  un exercice reutilise un identifiant introduit par
                             un autre exercice du meme sujet. C'est la
                             contrainte la plus forte du texte officiel :
                             « trois exercices independants ».
`MISSING_AUTHORING_STEP`     l'une des cinq etapes manque — enonce, oracle,
                             corrige, critique, portee pedagogique.
`ORACLE_FAILED`              un bloc de verification ne passe pas.
`MISSING_ORIGINALITY_NOTICE` le fichier ne porte pas la mention qui le
                             distingue d'un sujet officiel.
`FRAGILE_TABULAR_MARKUP`     `\\lstinline{...}` colle a un `&`.

L'INDEPENDANCE, ET CE QU'ELLE N'EST PAS. Deux exercices peuvent parler
d'arbres tous les deux sans cesser d'etre independants. Ce qui est interdit,
c'est qu'un exercice s'appuie sur un objet DEFINI par un autre : une classe,
une fonction, une variable nommee dans son enonce. Le controle porte donc sur
les identifiants definis dans les blocs de code, pas sur les themes.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402
from amenagement_profiles import FRAGILE_IN_TABULAR  # noqa: E402
from tnsi_exam_bank_blueprint import (  # noqa: E402
    AUTHORITY,
    AUTHORING_STEPS,
    DOMAINS,
    PRACTICAL_NOT_APPLICABLE,
    PRACTICAL_SITUATIONS,
    WRITTEN_SUBJECTS,
)

OUTPUT_JSON = ROOT / "audit/TNSI_EXAM_BANK_AUDIT.json"
OUTPUT_MD = ROOT / "audit/TNSI_EXAM_BANK_AUDIT.md"

META = re.compile(r"^%\s*META:\s*(\{.*\})\s*$")
VERIFY = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)
NOTICE = "ORIGINAL_NEXUS_TRAINING_MATERIAL_NOT_OFFICIAL_EXAM_CONTENT"

STEP_MARKERS = {
    "REDACTION": re.compile(r"\\subsection\*\{[EÉ]nonc[ée]\}"),
    "ORACLE": VERIFY,
    "CORRECTION": re.compile(r"\\subsection\*\{Corrig[ée]\}"),
    "CRITIQUE": re.compile(r"\\subsection\*\{Critique\}"),
    "PEDAGOGIE": re.compile(r"\\subsection\*\{Port[ée]e p[ée]dagogique\}"),
}

PYTHON_BLOCK = re.compile(r"\\begin\{python\}(.*?)\\end\{python\}", re.S)


def read_meta(text: str) -> dict[str, Any]:
    match = META.match(text.split("\n", 1)[0].strip())
    if match is None:
        raise ValueError("META absente")
    return json.loads(match.group(1))


def oracle_source(text: str) -> str | None:
    match = VERIFY.search(text)
    if match is None:
        return None
    return "\n".join(
        line[2:] if line.startswith("% ") else line[1:] if line.startswith("%") else line
        for line in match.group(1).rstrip().split("\n")
    )


def run_oracle(source: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-c", source], capture_output=True, text=True, timeout=120,
    )
    tail = result.stderr.strip().split("\n")[-1] if result.stderr.strip() else ""
    return result.returncode == 0, tail


def defined_names(text: str) -> set[str]:
    """Identifiants DEFINIS par les blocs de code de l'enonce.

    On ne lit que la partie enonce : le corrige redefinit legitimement ce que
    l'enonce a introduit, et le compter creerait de fausses dependances.
    """
    enonce = text.split("\\subsection*{Corrig", 1)[0]
    names: set[str] = set()
    for block in PYTHON_BLOCK.findall(enonce):
        try:
            tree = ast.parse(block)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
    return names


def _bank_files(root: Path, rubric: str) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in sorted((root / "NSI/chapitres").glob(f"*/{rubric}/*.tex")):
        meta = read_meta(path.read_text(encoding="utf-8"))
        found[str(meta["id"])] = path
    return found


def _contract_refs(root: Path, chapter: str) -> set[str]:
    import yaml  # noqa: PLC0415

    contract = yaml.safe_load(
        (root / "NSI/chapitres" / chapter / "contrat.yaml").read_text(encoding="utf-8")
    ) or {}
    return {
        str(c["ref_capacite"]) for c in (contract.get("capacites") or [])
        if isinstance(c, dict) and c.get("ref_capacite")
    }


def audit_written(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    found = _bank_files(root, "banque_ecrite")
    planned = {
        exercise["id"]: (subject, exercise)
        for subject in WRITTEN_SUBJECTS
        for exercise in subject["exercices"]
    }
    records: list[dict[str, Any]] = []

    for identifier, (subject, plan) in sorted(planned.items()):
        findings: list[str] = []
        path = found.get(identifier)
        if path is None:
            records.append({
                "exercise_id": identifier, "subject": subject["subject_id"],
                "path": None, "findings": ["MISSING_FROM_PLAN"],
            })
            continue
        text = path.read_text(encoding="utf-8")
        meta = read_meta(text)

        chapter = DOMAINS[plan["domain"]]
        declared = set(meta.get("capacites") or [])
        if declared != set(plan["capacites"]):
            findings.append("CAPACITY_MISMATCH")
        elif not declared <= _contract_refs(root, chapter):
            findings.append("CAPACITY_MISMATCH")
        if str(meta.get("chapitre")) != chapter:
            findings.append("CAPACITY_MISMATCH")

        for step, marker in STEP_MARKERS.items():
            if not marker.search(text):
                findings.append(f"MISSING_AUTHORING_STEP:{step}")
        source = oracle_source(text)
        oracle_ok, detail = (True, "")
        if source is None:
            oracle_ok = False
            detail = "aucun bloc de verification"
        else:
            oracle_ok, detail = run_oracle(source)
        if not oracle_ok:
            findings.append("ORACLE_FAILED")
        if NOTICE not in text:
            findings.append("MISSING_ORIGINALITY_NOTICE")
        if FRAGILE_IN_TABULAR.search(text):
            findings.append("FRAGILE_TABULAR_MARKUP")

        records.append({
            "exercise_id": identifier,
            "subject": subject["subject_id"],
            "chapter": chapter,
            "domain": plan["domain"],
            "path": path.relative_to(root).as_posix(),
            "duree_min": meta.get("duree_min"),
            "capacites": sorted(declared),
            "oracle": {"ran": source is not None, "passed": oracle_ok, "detail": detail},
            "defined_names": sorted(defined_names(text)),
            "findings": sorted(set(findings)),
        })

    for identifier in sorted(set(found) - set(planned)):
        records.append({
            "exercise_id": identifier,
            "path": found[identifier].relative_to(root).as_posix(),
            "findings": ["PRESENT_WITHOUT_PLAN"],
        })

    subjects: list[dict[str, Any]] = []
    by_id = {r["exercise_id"]: r for r in records}
    for subject in WRITTEN_SUBJECTS:
        rows = [by_id[e["id"]] for e in subject["exercices"] if e["id"] in by_id]
        findings = []
        if len(rows) != AUTHORITY["ecrit"]["exercices"]:
            findings.append("SUBJECT_NOT_THREE_EXERCISES")
        total = sum(r.get("duree_min") or 0 for r in rows)
        if total != int(AUTHORITY["ecrit"]["duree_h"] * 60):
            findings.append("SUBJECT_DURATION_MISMATCH")
        domains = [r.get("domain") for r in rows if r.get("domain")]
        if len(set(domains)) != len(domains):
            findings.append("SUBJECT_DOMAINS_NOT_DISTINCT")

        shared: list[str] = []
        for i, left in enumerate(rows):
            for right in rows[i + 1:]:
                common = set(left.get("defined_names") or []) & set(
                    right.get("defined_names") or []
                )
                if common:
                    shared.append(
                        f"{left['exercise_id']}/{right['exercise_id']}: "
                        f"{sorted(common)}"
                    )
        if shared:
            findings.append("EXERCISES_NOT_INDEPENDENT")

        subjects.append({
            "subject_id": subject["subject_id"],
            "titre": subject["titre"],
            "exercices": [r["exercise_id"] for r in rows],
            "duree_totale_min": total,
            "domains": domains,
            "shared_identifiers": shared,
            "findings": sorted(set(findings)),
        })
    return records, subjects


def audit_practical(root: Path) -> list[dict[str, Any]]:
    found = _bank_files(root, "banque_pratique")
    planned = {situation["id"]: situation for situation in PRACTICAL_SITUATIONS}
    records: list[dict[str, Any]] = []
    for identifier, plan in sorted(planned.items()):
        path = found.get(identifier)
        if path is None:
            records.append({
                "situation_id": identifier, "path": None,
                "findings": ["MISSING_FROM_PLAN"],
            })
            continue
        text = path.read_text(encoding="utf-8")
        meta = read_meta(text)
        findings: list[str] = []
        if set(meta.get("capacites") or []) != set(plan["capacites"]):
            findings.append("CAPACITY_MISMATCH")
        if meta.get("duree_min") != plan["duree_min"]:
            findings.append("DURATION_MISMATCH")
        if NOTICE not in text:
            findings.append("MISSING_ORIGINALITY_NOTICE")
        source = oracle_source(text)
        passed, detail = (False, "aucun bloc de verification")
        if source is not None:
            passed, detail = run_oracle(source)
        if not passed:
            findings.append("ORACLE_FAILED")
        records.append({
            "situation_id": identifier,
            "chapter": DOMAINS[plan["domain"]],
            "domain": plan["domain"],
            "path": path.relative_to(root).as_posix(),
            "duree_min": meta.get("duree_min"),
            "oracle": {"passed": passed, "detail": detail},
            "findings": sorted(set(findings)),
        })
    for identifier in sorted(set(found) - set(planned)):
        records.append({
            "situation_id": identifier,
            "path": found[identifier].relative_to(root).as_posix(),
            "findings": ["PRESENT_WITHOUT_PLAN"],
        })
    return records


def build(root: Path = ROOT) -> dict[str, Any]:
    written, subjects = audit_written(root)
    practical = audit_practical(root)

    counts: dict[str, int] = {}
    for row in written + subjects + practical:
        for finding in row["findings"]:
            key = finding.split(":", 1)[0]
            counts[key] = counts.get(key, 0) + 1

    summary = {
        "AUTHORITY": AUTHORITY["official_ref"],
        "WRITTEN_SUBJECTS": len(subjects),
        "WRITTEN_EXERCISES_PLANNED": sum(len(s["exercices"]) for s in WRITTEN_SUBJECTS),
        "WRITTEN_EXERCISES_AUTHORED": sum(
            1 for r in written if r.get("path") and "MISSING_FROM_PLAN" not in r["findings"]
        ),
        "WRITTEN_ORACLES_PASSED": sum(
            1 for r in written if (r.get("oracle") or {}).get("passed")
        ),
        "PRACTICAL_SITUATIONS_PLANNED": len(PRACTICAL_SITUATIONS),
        "PRACTICAL_SITUATIONS_AUTHORED": sum(
            1 for r in practical if r.get("path")
        ),
        "PRACTICAL_ORACLES_PASSED": sum(
            1 for r in practical if (r.get("oracle") or {}).get("passed")
        ),
        "MISSING_FROM_PLAN": counts.get("MISSING_FROM_PLAN", 0),
        "PRESENT_WITHOUT_PLAN": counts.get("PRESENT_WITHOUT_PLAN", 0),
        "CAPACITY_MISMATCH": counts.get("CAPACITY_MISMATCH", 0),
        "SUBJECT_NOT_THREE_EXERCISES": counts.get("SUBJECT_NOT_THREE_EXERCISES", 0),
        "SUBJECT_DURATION_MISMATCH": counts.get("SUBJECT_DURATION_MISMATCH", 0),
        "SUBJECT_DOMAINS_NOT_DISTINCT": counts.get("SUBJECT_DOMAINS_NOT_DISTINCT", 0),
        "EXERCISES_NOT_INDEPENDENT": counts.get("EXERCISES_NOT_INDEPENDENT", 0),
        "MISSING_AUTHORING_STEP": counts.get("MISSING_AUTHORING_STEP", 0),
        "ORACLE_FAILED": counts.get("ORACLE_FAILED", 0),
        "MISSING_ORIGINALITY_NOTICE": counts.get("MISSING_ORIGINALITY_NOTICE", 0),
        "FRAGILE_TABULAR_MARKUP": counts.get("FRAGILE_TABULAR_MARKUP", 0),
        "BANK_DEFECTS": sum(counts.values()),
    }
    inputs = [
        row["path"] for row in written + practical if row.get("path")
    ] + ["scripts/tnsi_exam_bank_blueprint.py"]

    payload = {
        "artifact_type": "tnsi_exam_bank_audit",
        "schema_version": 1,
        "generated_by": "scripts/build_tnsi_exam_bank_audit.py",
        "approves_nothing": True,
        "authority": AUTHORITY,
        "authoring_steps": list(AUTHORING_STEPS),
        "practical_not_applicable": PRACTICAL_NOT_APPLICABLE,
        "summary": summary,
        "subjects": subjects,
        "written": written,
        "practical": practical,
    }
    payload["freshness"] = freshness.stamp(inputs, root=root)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Banques d'épreuve TNSI — audit contre le plan",
        "",
        f"Autorité : `{s['AUTHORITY']}`, écrit "
        f"{payload['authority']['ecrit']['duree_h']} h en "
        f"{payload['authority']['ecrit']['exercices']} exercices indépendants ; "
        f"pratique {payload['authority']['pratique']['duree_h']} h.",
        "",
        f"- Sujets écrits : `{s['WRITTEN_SUBJECTS']}`",
        f"- Exercices écrits : `{s['WRITTEN_EXERCISES_AUTHORED']}` / `{s['WRITTEN_EXERCISES_PLANNED']}`",
        f"- Oracles écrits verts : `{s['WRITTEN_ORACLES_PASSED']}`",
        f"- Situations pratiques : `{s['PRACTICAL_SITUATIONS_AUTHORED']}` / `{s['PRACTICAL_SITUATIONS_PLANNED']}`",
        f"- Oracles pratiques verts : `{s['PRACTICAL_ORACLES_PASSED']}`",
        f"- `EXERCISES_NOT_INDEPENDENT` : `{s['EXERCISES_NOT_INDEPENDENT']}`",
        f"- `BANK_DEFECTS` : `{s['BANK_DEFECTS']}`",
        "",
        "| Sujet | Exercices | Durée | Domaines | Défauts |",
        "|---|---|---|---|---|",
    ]
    for subject in payload["subjects"]:
        lines.append(
            f"| `{subject['subject_id']}` | {len(subject['exercices'])} | "
            f"{subject['duree_totale_min']} min | "
            f"{', '.join(subject['domains'])} | "
            f"{', '.join(subject['findings']) or '—'} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT_JSON.is_file():
            print("TNSI_EXAM_BANK_AUDIT check: MISSING")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("TNSI_EXAM_BANK_AUDIT check: STALE")
            return 1
        print("TNSI_EXAM_BANK_AUDIT check: OK")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
