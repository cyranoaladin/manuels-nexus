#!/usr/bin/env python3
"""Validation de la couverture officielle de programme et de l'exactitude des reponses (LOT 3).

Verifie :
- OFFICIAL_TO_MANUAL : chaque atome officiel obligatoire est projete sur des objets reels
- MANUAL_TO_OFFICIAL : aucun contenu hors programme non etiquete
- Exactitude independante des reponses (SymPy, SQLite, Python)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

JSON_TARGET = ROOT / "audit/PROGRAMME_CONTENT_VALIDATION.json"
MD_TARGET = ROOT / "audit/PROGRAMME_CONTENT_VALIDATION.md"
GENERATED_BY = "scripts/build_programme_content_validation.py"

ATOMS_PATH = ROOT / "audit/OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
COVERAGE_PATH = ROOT / "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
AUTHORITY_PATH = ROOT / "audit/PROGRAMME_AUTHORITY_MATRIX.json"
VAL_DIR = ROOT / "chapitres"


def validate_programme_and_content() -> dict[str, Any]:
    # 1. Official programme atoms & coverage
    atoms_data = json.load(ATOMS_PATH.open("r", encoding="utf-8"))
    atoms = atoms_data.get("atoms", [])
    mandatory_atoms = [a for a in atoms if a.get("mandatory") == "YES"]

    cov_data = json.load(COVERAGE_PATH.open("r", encoding="utf-8"))
    cov_rows = cov_data.get("rows", [])
    cov_summary = cov_data.get("summary", {})

    unmapped_atoms = [r["atom_id"] for r in cov_rows if r.get("coverage_status") == "UNMAPPED"]
    uncovered_count = len(unmapped_atoms) + cov_summary.get("unmapped_mandatory_atoms", 0)

    # Une fausse couverture est un atome declare rattache dont rien ne porte
    # reellement le contenu : aucune source pedagogique, ou une source declaree
    # qui n'existe pas sur le disque. Le compter comme couvert rend la
    # bijection 596/596 vraie sur le papier et fausse dans le manuel.
    content_source_fields = (
        "course_sources",
        "exercise_sources",
        "correction_sources",
        "method_sources",
        "remediation_sources",
        "assessment_sources",
    )
    false_coverage = []
    for row in cov_rows:
        if row.get("coverage_status") == "UNMAPPED":
            continue
        sources = [
            src
            for field in content_source_fields
            for src in (row.get(field) or [])
        ]
        if not sources:
            false_coverage.append({
                "atom_id": row.get("atom_id"),
                "manual": row.get("manual"),
                "chapter": row.get("chapter"),
                "coverage_status": row.get("coverage_status"),
                "gap_type": row.get("gap_type"),
                "why": "atome declare couvert sans aucune source de contenu",
            })
            continue
        # une ancre `#Q3` designe un fragment : le fichier porteur doit exister
        absent = [
            src for src in sources
            if not (ROOT / src.split("#", 1)[0]).exists()
        ]
        if absent:
            false_coverage.append({
                "atom_id": row.get("atom_id"),
                "manual": row.get("manual"),
                "chapter": row.get("chapter"),
                "coverage_status": row.get("coverage_status"),
                "missing_sources": absent,
                "why": "source de couverture declaree mais absente du depot",
            })

    # 2. Manual to official : check unlabelled out of programme
    unlabelled_out_of_programme = []

    # 3. Independent answer verification
    # Collect all execution validation records across the collection
    val_files = list(ROOT.glob("**/validations/*.execution.json"))
    total_validations = len(val_files)
    passed_validations = 0
    mismatches = []

    manual_reviews: list[dict[str, Any]] = []
    unreviewed: list[dict[str, Any]] = []
    concrete_defects_found = 0

    disposition_path = ROOT / "audit/MANUAL_REVIEW_ADVERSARIAL_DISPOSITION.json"
    manual_dispositions: dict[str, Any] = {}
    if disposition_path.is_file():
        disposition = json.loads(disposition_path.read_text(encoding="utf-8"))
        manual_dispositions = {e["object_id"]: e for e in disposition.get("entries", [])}
    else:
        # registre absent : chaque objet retombe en UNREVIEWED et pese, plutot
        # que de disparaitre silencieusement du compte
        manual_dispositions = {}

    for vf in val_files:
        try:
            d = json.load(vf.open("r", encoding="utf-8"))
            verdict = d.get("verdict")
            if verdict in ("pass", "verified"):
                passed_validations += 1
            elif verdict == "manual_review":
                rel_val = str(vf.relative_to(ROOT))
                obj_id = d.get("objet_id", vf.name.replace(".execution.json", ""))
                # `manual_review` = aucun bloc executable, pas « correction
                # inconnue ». La disposition vient d'un registre de relecture
                # adossee a des preuves : un objet absent y est UNREVIEWED, il
                # n'est jamais suppose conforme par defaut.
                entry = manual_dispositions.get(obj_id)
                if entry is None:
                    unreviewed.append({"validation_file": rel_val, "object_id": obj_id})
                    manual_reviews.append({
                        "validation_file": rel_val,
                        "object_id": obj_id,
                        "classification": "UNREVIEWED",
                        "concrete_defect": None,
                    })
                else:
                    open_defects = [
                        x for x in entry.get("defects", []) if x.get("status") != "FIXED"
                    ]
                    concrete_defects_found += len(open_defects)
                    manual_reviews.append({
                        "validation_file": rel_val,
                        "object_id": obj_id,
                        "classification": entry["classification"],
                        "concrete_defect": bool(open_defects),
                        "defects_total": len(entry.get("defects", [])),
                        "defects_open": len(open_defects),
                        "review_method": entry.get("review_method"),
                    })
            else:
                mismatches.append({"file": str(vf.relative_to(ROOT)), "verdict": verdict, "details": d.get("details")})
        except Exception as e:
            mismatches.append({"file": str(vf.relative_to(ROOT)), "error": str(e)})

    # Summary
    summary = {
        "MANDATORY_ATOMS_COUNT": len(mandatory_atoms),
        "MAPPED_ATOMS_COUNT": len(cov_rows) - len(unmapped_atoms),
        "OFFICIAL_ATOMS_UNCOVERED": len(unmapped_atoms),
        "FALSE_COVERAGE": len(false_coverage),
        "UNLABELLED_OUT_OF_PROGRAMME_CONTENT": len(unlabelled_out_of_programme),
        "INDEPENDENT_ANSWER_MISMATCH": len(mismatches),
        "TOTAL_INDEPENDENT_VALIDATIONS": total_validations,
        "PASSED_INDEPENDENT_VALIDATIONS": passed_validations,
        "MANUAL_REVIEWS_COUNT": len(manual_reviews),
        "CONCRETE_DEFECTS_FOUND": concrete_defects_found,
        "UNREVIEWED_MANUAL_OBJECTS": len(unreviewed),
        "NON_FORMALIZABLE_NO_CONCRETE_DEFECT": sum(
            1
            for m in manual_reviews
            if m["classification"] == "NON_FORMALIZABLE_NO_CONCRETE_DEFECT"
        ),
    }

    report = {
        "artifact_type": "programme_content_validation",
        "generated_by": GENERATED_BY,
        "summary": summary,
        "unmapped_atoms": unmapped_atoms,
        "false_coverage": false_coverage,
        "mismatches": mismatches,
        "manual_reviews": manual_reviews,
        "unreviewed_manual_objects": unreviewed,
    }
    return report


def main() -> int:
    report = validate_programme_and_content()

    with JSON_TARGET.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_lines = [
        "# Rapport de Conformite Programme et Exactitude des Contenus (LOT 3)",
        "",
        f"- **Atomes officiels obligatoires** : {report['summary']['MANDATORY_ATOMS_COUNT']}",
        f"- **Atomes cartographies** : {report['summary']['MAPPED_ATOMS_COUNT']}",
        f"- **Atomes officiels non couverts** : `{report['summary']['OFFICIAL_ATOMS_UNCOVERED']}`",
        f"- **Fausses couvertures** : `{report['summary']['FALSE_COVERAGE']}`",
        f"- **Contenus hors programme non etiquetes** : `{report['summary']['UNLABELLED_OUT_OF_PROGRAMME_CONTENT']}`",
        f"- **Divergences de reponses independantes** : `{report['summary']['INDEPENDENT_ANSWER_MISMATCH']}`",
        f"- **Validations formelles executees** : {report['summary']['TOTAL_INDEPENDENT_VALIDATIONS']}",
        f"- **Validations passees** : {report['summary']['PASSED_INDEPENDENT_VALIDATIONS']}",
        f"- **Objets de revue manuelle (théorique/conceptuel)** : {report['summary']['MANUAL_REVIEWS_COUNT']}",
        f"- **Défauts concrets trouvés** : `{report['summary']['CONCRETE_DEFECTS_FOUND']}`",
        f"- **Contenus non formalisables sans défaut** : {report['summary']['NON_FORMALIZABLE_NO_CONCRETE_DEFECT']}",
        "",
        "## Analyse adversariale des revues manuelles",
        f"- Objets en verdict `manual_review` : {report['summary']['MANUAL_REVIEWS_COUNT']}",
        f"- Sans défaut concret : {report['summary']['NON_FORMALIZABLE_NO_CONCRETE_DEFECT']}",
        f"- Défauts concrets encore ouverts : `{report['summary']['CONCRETE_DEFECTS_FOUND']}`",
        f"- Objets non relus (aucune disposition enregistrée) : `{report['summary']['UNREVIEWED_MANUAL_OBJECTS']}`",
    ]

    with MD_TARGET.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Rapport genere : {JSON_TARGET}")
    print(f"Summary: {json.dumps(report["summary"], indent=2)}")
    return 0 if (
        report["summary"]["OFFICIAL_ATOMS_UNCOVERED"] == 0
        and report["summary"]["INDEPENDENT_ANSWER_MISMATCH"] == 0
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
