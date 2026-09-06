#!/usr/bin/env python3
"""Validation de la parite eleve/professeur, etancheite et baremes (LOT 4).

Controle :
- Bijection parfaite exercices <-> corriges sur les 12 cibles canoniques
- Absence de fuite professeur dans les PDF eleves
- Coherence et certification de tous les baremes d'evaluation
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

JSON_TARGET = ROOT / "audit/PARITY_BAREMES_VALIDATION.json"
MD_TARGET = ROOT / "audit/PARITY_BAREMES_VALIDATION.md"
GENERATED_BY = "scripts/build_parity_baremes_validation.py"

CANONICAL_BUILDS = {
    "1SPE": (ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE", ROOT / "Mathematiques/manuel-maths"),
    "TSPE_2026_2027": (ROOT / "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027", ROOT / "Mathematiques/manuel-maths"),
    "TCOMPL": (ROOT / "Mathematiques/manuel-maths/build/MANUEL_TCOMPL", ROOT / "Mathematiques/manuel-maths"),
    "TEXPERTES": (ROOT / "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES", ROOT / "Mathematiques/manuel-maths"),
    "1NSI": (ROOT / "NSI/build/MANUEL_1NSI", ROOT / "NSI"),
    "TNSI": (ROOT / "NSI/build/MANUEL_TNSI", ROOT / "NSI"),
}

INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
BAREME_RE = re.compile(r"\\baremeIndicatif\{([^}]*)\}")
BAREME_ENTRY_RE = re.compile(
    r"(Ex\.?\s*\d+|Q\s*\d+[a-z]?)\s*:\s*([0-9]+(?:[.,][0-9]+)?)\s*pts?",
    re.IGNORECASE,
)
BAREME_FLAT_RE = re.compile(r"^\s*([0-9]+(?:[.,][0-9]+)?)\s*(?:points?|pts?)\s*$", re.I)
EVAL_TOTAL_POINTS = 20.0
EXERCICE_LABEL_RE = re.compile(r"\\begin\{exercice\}\{([^}]*)\}")
CORRIGE_LABEL_RE = re.compile(r"\\begin\{corrige\}\{([^}]*)\}")


def audit_baremes(root: Path) -> dict[str, Any]:
    """Verifier les baremes reellement composes, un fichier a la fois.

    Deux conventions coexistent et sont toutes deux legitimes : `Ex. N : M pts`
    porte sur une evaluation entiere (total 20), `Q<n> : M pts` sur une seule
    activite. Un bareme dont on ne peut pas etablir la portee est ambigu ; c'est
    ce que `BAREME_SCOPE_AMBIGUOUS` designe, et non un defaut de total.
    """

    scope_ambiguous: list[dict[str, Any]] = []
    total_mismatch: list[dict[str, Any]] = []
    duplicate_allocation: list[dict[str, Any]] = []
    missing_question: list[dict[str, Any]] = []
    teacher_missing: list[dict[str, Any]] = []
    audited = 0

    for tex in sorted(root.rglob("*.tex")):
        if ".git" in tex.parts or "/build/" in tex.as_posix():
            continue
        text = tex.read_text(encoding="utf-8", errors="ignore")
        match = BAREME_RE.search(text)
        if not match:
            continue
        audited += 1
        rel = tex.relative_to(root).as_posix()
        body = match.group(1)
        entries = BAREME_ENTRY_RE.findall(body)
        flat = BAREME_FLAT_RE.match(body)

        if not entries and not flat:
            scope_ambiguous.append({
                "file": rel,
                "bareme": body[:120],
                "why": "aucune allocation lisible : portee indeterminable",
            })
            continue

        if flat and not entries:
            continue  # total global annonce, sans ventilation : rien a recouper

        labels = [re.sub(r"\s+", "", label).upper() for label, _ in entries]
        kinds = {"EX" if label.startswith("EX") else "Q" for label in labels}
        if len(kinds) > 1:
            scope_ambiguous.append({
                "file": rel,
                "bareme": body[:120],
                "why": "portees melangees dans un meme bareme (Ex. et Q)",
            })
            continue

        seen: dict[str, int] = {}
        for label in labels:
            seen[label] = seen.get(label, 0) + 1
        repeated = sorted(k for k, v in seen.items() if v > 1)
        if repeated:
            duplicate_allocation.append({
                "file": rel,
                "labels": repeated,
                "why": "une meme question recoit deux allocations",
            })

        points = [float(value.replace(",", ".")) for _, value in entries]
        declared_total = sum(points)

        if kinds == {"EX"}:
            # portee evaluation : le total doit valoir le bareme annonce
            if abs(declared_total - EVAL_TOTAL_POINTS) > 1e-9:
                total_mismatch.append({
                    "file": rel,
                    "declared_total": declared_total,
                    "expected_total": EVAL_TOTAL_POINTS,
                    "why": "somme des exercices differente du total de l'epreuve",
                })
            # et coincider avec les points annonces dans le corps
            in_body = [
                float(v.replace(",", "."))
                for v in re.findall(r"\((\d+(?:[.,]\d+)?)\s*points?\)", text)
            ]
            if in_body and abs(sum(in_body) - declared_total) > 1e-9:
                total_mismatch.append({
                    "file": rel,
                    "declared_total": declared_total,
                    "body_total": sum(in_body),
                    "why": "bareme annonce different des points imprimes dans le corps",
                })
            body_exercises = len(re.findall(r"\\textbf\{Exercice\s*\d+\}", text))
            if body_exercises and body_exercises != len(entries):
                missing_question.append({
                    "file": rel,
                    "exercises_in_body": body_exercises,
                    "allocations": len(entries),
                    "why": "exercice compose sans allocation de bareme",
                })

        if kinds == {"Q"}:
            # portee activite : chaque question numerotee doit etre allouee
            enum = re.search(
                r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}", text, re.S
            )
            if enum:
                depth = 0
                top_items = 0
                for token in re.finditer(
                    r"\\begin\{enumerate\}|\\end\{enumerate\}|\\item", enum.group(1)
                ):
                    value = token.group(0)
                    if value == "\\begin{enumerate}":
                        depth += 1
                    elif value == "\\end{enumerate}":
                        depth -= 1
                    elif depth == 0:
                        top_items += 1
                if top_items and top_items > len(entries):
                    missing_question.append({
                        "file": rel,
                        "questions_in_body": top_items,
                        "allocations": len(entries),
                        "why": "question composee sans allocation de bareme",
                    })

        # un sujet barème doit avoir sa contrepartie professeur
        if "/evaluations/" in rel and "-corrige" not in tex.stem:
            corrige = tex.with_name(f"{tex.stem}-corrige{tex.suffix}")
            if not corrige.is_file():
                teacher_missing.append({
                    "file": rel,
                    "expected": corrige.relative_to(root).as_posix(),
                    "why": "sujet d'evaluation sans corrige professeur",
                })

    return {
        "audited_baremes": audited,
        "scope_ambiguous": scope_ambiguous,
        "total_mismatch": total_mismatch,
        "duplicate_allocation": duplicate_allocation,
        "missing_question": missing_question,
        "teacher_missing_required_content": teacher_missing,
    }


def validate_parity_and_baremes() -> dict[str, Any]:
    # 1. Parity bijection
    total_exercises = 0
    total_corrections = 0
    missing_corrections = []
    orphan_corrections = []
    statement_drift = []

    for manual_id, (build_dir, source_root) in CANONICAL_BUILDS.items():
        eleve_master = list(build_dir.glob("*eleve.tex"))[0]
        prof_master = list(build_dir.glob("*professeur.tex"))[0]

        eleve_inputs = INPUT_RE.findall(eleve_master.read_text(encoding="utf-8"))
        prof_inputs = INPUT_RE.findall(prof_master.read_text(encoding="utf-8"))

        ex_files = [p for p in eleve_inputs if "/exercices/" in p and not p.endswith("-CDP.tex")]
        co_files = [p for p in prof_inputs if "/corriges/" in p and "-CO-" in p]

        total_exercises += len(ex_files)
        total_corrections += len(co_files)

        for ex in ex_files:
            co = ex.replace("/exercices/", "/corriges/").replace("-EX-", "-CO-")
            if co not in co_files:
                missing_corrections.append({"manual": manual_id, "exercise": ex, "expected_correction": co})

        for co in co_files:
            ex = co.replace("/corriges/", "/exercices/").replace("-CO-", "-EX-")
            if ex not in ex_files:
                orphan_corrections.append({"manual": manual_id, "correction": co, "expected_exercise": ex})

        # La bijection par nom de fichier ne prouve rien sur le contenu : un
        # corrige nomme CO-007 peut declarer repondre a EX-001. On confronte donc
        # l'etiquette reellement composee de chaque paire.
        for ex in ex_files:
            co = ex.replace("/exercices/", "/corriges/").replace("-EX-", "-CO-")
            if co not in co_files:
                continue
            ex_path = source_root / ex
            co_path = source_root / co
            if not (ex_path.is_file() and co_path.is_file()):
                continue
            ex_label = EXERCICE_LABEL_RE.search(ex_path.read_text(encoding="utf-8", errors="ignore"))
            co_label = CORRIGE_LABEL_RE.search(co_path.read_text(encoding="utf-8", errors="ignore"))
            if not (ex_label and co_label):
                continue
            if ex_label.group(1) != co_label.group(1):
                statement_drift.append({
                    "manual": manual_id,
                    "exercise": ex,
                    "exercise_label": ex_label.group(1),
                    "correction": co,
                    "correction_targets": co_label.group(1),
                })

    # 2. Student separation check (leaks)
    student_checks = (
        ("identifiant interne", r"\b(?:1SPE|TSPE|TCOMPL|TEXPERTES|TEXP|1NSI|TNSI)-[A-Z0-9]+(?:-[A-Z0-9]+)*"),
        ("corrige", r"(?im:\bcorrigés?\b|^[ \t]*corriges\b)"),
        ("bareme", r"(?i:\bbar[èe]me indicatif\b)"),
        ("note enseignant", r"(?i:\b(?:note|réponse|reponse)\s+(?:professeur|enseignant)\b)"),
    )
    leaks = []
    student_pdfs = list(ROOT.glob("Mathematiques/manuel-maths/build/MANUEL_*/*eleve.pdf")) + list(ROOT.glob("NSI/build/MANUEL_*/*eleve.pdf"))
    for pdf in student_pdfs:
        res = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, errors="replace")
        for check_name, pat in student_checks:
            m = re.search(pat, res.stdout)
            if m:
                leaks.append({"pdf": pdf.name, "check": check_name, "snippet": m.group(0)})

    baremes = audit_baremes(ROOT)

    summary = {
        "STUDENT_WITHOUT_CORRECTION": len(missing_corrections),
        "ORPHAN_TEACHER_CORRECTION": len(orphan_corrections),
        "STUDENT_TEACHER_STATEMENT_DRIFT": len(statement_drift),
        "TEACHER_CONTENT_LEAK_IN_STUDENT": len(leaks),
        "BAREME_SCOPE_AMBIGUOUS": len(baremes["scope_ambiguous"]),
        "BAREME_TOTAL_MISMATCH": len(baremes["total_mismatch"]),
        "BAREME_DUPLICATE_ALLOCATION": len(baremes["duplicate_allocation"]),
        "BAREME_MISSING_REQUIRED_QUESTION": len(baremes["missing_question"]),
        "TEACHER_MISSING_REQUIRED_CONTENT": len(baremes["teacher_missing_required_content"]),
        "BAREMES_AUDITED": baremes["audited_baremes"],
        "TOTAL_EXERCISES": total_exercises,
        "TOTAL_CORRECTIONS": total_corrections,
        "STUDENT_PDFS_AUDITED": len(student_pdfs),
    }

    report = {
        "artifact_type": "parity_baremes_validation",
        "generated_by": GENERATED_BY,
        "summary": summary,
        "missing_corrections": missing_corrections,
        "orphan_corrections": orphan_corrections,
        "statement_drift": statement_drift,
        "baremes": baremes,
        "leaks": leaks,
    }
    return report


def main() -> int:
    report = validate_parity_and_baremes()

    with JSON_TARGET.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_lines = [
        "# Rapport de Parite Eleve/Professeur, Etancheite et Baremes (LOT 4)",
        "",
        f"- **Exercices sans corrige** : `{report["summary"]["STUDENT_WITHOUT_CORRECTION"]}`",
        f"- **Corriges orphelins** : `{report["summary"]["ORPHAN_TEACHER_CORRECTION"]}`",
        f"- **Derive d'enonce eleve/professeur** : `{report["summary"]["STUDENT_TEACHER_STATEMENT_DRIFT"]}`",
        f"- **Fuites enseignant dans la version eleve** : `{report["summary"]["TEACHER_CONTENT_LEAK_IN_STUDENT"]}`",
        f"- **Ambigüites de bareme** : `{report["summary"]["BAREME_SCOPE_AMBIGUOUS"]}`",
        f"- **Erreurs de total de bareme** : `{report["summary"]["BAREME_TOTAL_MISMATCH"]}`",
        f"- **Double allocation de points** : `{report["summary"]["BAREME_DUPLICATE_ALLOCATION"]}`",
        f"- **Questions manquantes au bareme** : `{report["summary"]["BAREME_MISSING_REQUIRED_QUESTION"]}`",
        f"- **Total exercices audites** : {report["summary"]["TOTAL_EXERCISES"]}",
        f"- **Total corriges audites** : {report["summary"]["TOTAL_CORRECTIONS"]}",
        f"- **PDFs eleves controles** : {report["summary"]["STUDENT_PDFS_AUDITED"]}",
    ]

    with MD_TARGET.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Rapport genere : {JSON_TARGET}")
    print(f"Summary: {json.dumps(report["summary"], indent=2)}")
    return 0 if (
        report["summary"]["STUDENT_WITHOUT_CORRECTION"] == 0
        and report["summary"]["STUDENT_TEACHER_STATEMENT_DRIFT"] == 0
        and report["summary"]["ORPHAN_TEACHER_CORRECTION"] == 0
        and report["summary"]["TEACHER_CONTENT_LEAK_IN_STUDENT"] == 0
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
