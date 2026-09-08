#!/usr/bin/env python3
"""Validation de la couverture officielle de programme et de l'exactitude des reponses (LOT 3).

Verifie :
- OFFICIAL_TO_MANUAL : chaque atome officiel obligatoire est projete sur des objets reels
- MANUAL_TO_OFFICIAL : aucun contenu hors programme non etiquete
- Exactitude independante des reponses (SymPy, SQLite, Python)
"""

from __future__ import annotations

import json
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

# Scientific scope only. Editorial, pedagogical and final human decisions
# remain separate in the current index. Execution never supplies these states.
SCIENTIFIC_DIMENSIONS = frozenset({
    "SCIENTIFIC_REVIEW", "DATA_REVIEW", "CODE_EXECUTION_REVIEW", "ORACLE_REVIEW",
    "CORRECTION_ALIGNMENT_REVIEW", "FIGURE_REVIEW", "DOCUMENTARY_HISTORICAL_REVIEW",
})


def _input_snapshot(paths: set[Path]) -> dict[str, str | None]:
    from build_current_review_index import sha256
    return {path.resolve().relative_to(ROOT.resolve()).as_posix()
            if path.resolve().is_relative_to(ROOT.resolve()) else str(path.resolve()):
            sha256(path.read_bytes()) if path.is_file() else None
            for path in sorted(paths)}


def _validation_evidence(index: dict[str, Any], val_files: tuple[Path, ...]) -> dict[str, Any]:
    from scientific_receipt_binding import bind, usable

    current = {row["path"]: row for row in index["objects"]}
    rejected, mismatches, duplicates, objects = [], [], [], []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for vf in val_files:
        relative = vf.relative_to(ROOT).as_posix()
        try:
            receipt = json.loads(vf.read_text(encoding="utf-8"))
            if not isinstance(receipt, dict):
                raise ValueError("receipt is not an object")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            rejected.append({"validation_file": relative, "reason": "UNREADABLE_RECEIPT", "error": str(exc)})
            continue
        binding = bind(receipt, vf.parent.parent, ROOT)
        if not usable(binding):
            rejected.append({"validation_file": relative, "reason": binding.get("reason"), "binding": binding})
            continue
        row = current.get(binding["source_path"])
        if (row is None or row["object_id"] != binding["canonical_object_id"]
                or row["source_sha256"] != binding["current_source_sha256"]):
            rejected.append({"validation_file": relative, "reason": "NOT_IN_CURRENT_REVIEW_OBJECT_SET", "binding": binding})
            continue
        key = (row["path"], row["object_id"])
        grouped.setdefault(key, []).append({"validation_file": relative, "verdict": receipt["verdict"],
                                          "certifies_documentary_claims": receipt.get("certifies_documentary_claims"),
                                          "binding": binding})
        if receipt["verdict"] == "fail":
            mismatches.append({"validation_file": relative, "path": row["path"], "object_id": row["object_id"],
                               "verdict": "fail", "details": receipt.get("details")})

    for (path, object_id), receipts in sorted(grouped.items()):
        row = current[path]
        dimensions = sorted(SCIENTIFIC_DIMENSIONS.intersection(row["required_review_dimensions"]))
        pending = [dim for dim in dimensions if row["reviews"][dim]["state"] != "VALIDATED_BY_EVIDENCE"]
        unique = len(receipts) == 1
        if not unique:
            duplicates.append({"path": path, "object_id": object_id,
                               "validation_files": [receipt["validation_file"] for receipt in receipts]})
        verdict = receipts[0]["verdict"] if unique else "AMBIGUOUS_DUPLICATE_RECEIPTS"
        text = (ROOT / path).read_text(encoding="utf-8")
        executable_claims = any(marker in text for marker in (
            "% BEGIN-VERIFY", "% BEGIN-TRACE", "% PYTHON-SOURCE", r"\begin{python}",
            r"\lstinputlisting", r"\inputminted", r"\begin{minted}", r"\begin{lstlisting}"))
        execution_state = ("CURRENT_EXECUTION_PASSED" if unique and verdict == "pass"
                           else "CURRENT_EXECUTION_REQUIRED" if executable_claims
                           else "NO_EXECUTABLE_CLAIMS_IN_SOURCE")
        # A current independent reading can close a documentary-only object;
        # a machine failure or ambiguous pair of receipts cannot be overruled.
        reviewed = (unique and verdict in {"pass", "manual_review"} and not pending
                    and execution_state != "CURRENT_EXECUTION_REQUIRED")
        objects.append({"path": path, "object_id": object_id, "source_sha256": row["source_sha256"],
                        "semantic_digest": row["semantic_digest"], "dependency_digest": row["dependency_digest"],
                        "verdict": verdict, "receipts": receipts, "required_scientific_dimensions": dimensions,
                        "execution_requirement_state": execution_state,
                        "pending_dimensions": pending,
                        "scientific_review_state": "VALIDATED_BY_EVIDENCE" if reviewed else "PENDING",
                        "human_approval": row["human_approval"]})
    return {"current_objects": objects, "rejected_validations": rejected,
            "mismatches": mismatches, "duplicate_validation_bindings": duplicates}


def validate_programme_and_content(*, inventory=None) -> dict[str, Any]:
    import build_current_review_index as current_review

    val_files = tuple(sorted(ROOT.glob("**/validations/*.execution.json")))
    disposition_path = ROOT / "audit/MANUAL_REVIEW_ADVERSARIAL_DISPOSITION.json"
    input_paths = {ATOMS_PATH, COVERAGE_PATH, disposition_path, Path(__file__),
                   Path(__file__).with_name("scientific_receipt_binding.py"), *val_files}
    inputs_before = _input_snapshot(input_paths)
    index = current_review.build_fresh(ROOT, inventory)
    # 1. Official programme atoms & coverage
    atoms_data = json.load(ATOMS_PATH.open("r", encoding="utf-8"))
    atoms = atoms_data.get("atoms", [])
    mandatory_atoms = [a for a in atoms if a.get("mandatory") == "YES"]

    cov_data = json.load(COVERAGE_PATH.open("r", encoding="utf-8"))
    cov_rows = cov_data.get("rows", [])

    unmapped_atoms = [r["atom_id"] for r in cov_rows if r.get("coverage_status") == "UNMAPPED"]

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

    # 2. This producer has no semantic out-of-programme detector. Do not turn
    # an empty local list into a zero-defect assertion.

    # 3. Execution is separately bound to source and verifier; scientific
    # credit comes only from the freshly derived independent review index.
    evidence = _validation_evidence(index, val_files)
    objects = evidence["current_objects"]
    manual_reviews = [{**row, "classification": "SEMANTICALLY_REVIEWED"
                       if row["scientific_review_state"] == "VALIDATED_BY_EVIDENCE" else "UNREVIEWED",
                       "concrete_defect": None}
                      for row in objects if row["verdict"] == "manual_review"]
    unreviewed = [row for row in manual_reviews if row["classification"] == "UNREVIEWED"]
    disposition = json.loads(disposition_path.read_text(encoding="utf-8")) if disposition_path.is_file() else {}
    current_review.assert_current(ROOT, index)
    if tuple(sorted(ROOT.glob("**/validations/*.execution.json"))) != val_files:
        raise ValueError("execution receipt population changed during programme validation")
    if _input_snapshot(input_paths) != inputs_before:
        raise ValueError("programme validation input changed during observation")

    # Summary
    summary = {
        "MANDATORY_ATOMS_COUNT": len(mandatory_atoms),
        "MAPPED_ATOMS_COUNT": len(cov_rows) - len(unmapped_atoms),
        "OFFICIAL_ATOMS_UNCOVERED": len(unmapped_atoms),
        "FALSE_COVERAGE": len(false_coverage),
        "UNLABELLED_OUT_OF_PROGRAMME_CONTENT": None,
        "OUT_OF_PROGRAMME_SEMANTIC_AUDIT_STATUS": "NOT_EVALUATED_BY_THIS_PRODUCER",
        "INDEPENDENT_ANSWER_MISMATCH": len(evidence["mismatches"]),
        "TOTAL_INDEPENDENT_VALIDATIONS": len(val_files),
        "CURRENT_VALIDATION_OBJECTS": len(objects),
        "CURRENT_EXECUTION_PASSED": sum(row["verdict"] == "pass" for row in objects),
        "PASSED_INDEPENDENT_VALIDATIONS": sum(row["scientific_review_state"] == "VALIDATED_BY_EVIDENCE" for row in objects),
        "INDEPENDENT_REVIEW_PENDING": sum(row["scientific_review_state"] != "VALIDATED_BY_EVIDENCE" for row in objects),
        "REJECTED_VALIDATION_RECEIPTS": len(evidence["rejected_validations"]),
        "DUPLICATE_VALIDATION_BINDINGS": len(evidence["duplicate_validation_bindings"]),
        "MANUAL_REVIEWS_COUNT": len(manual_reviews),
        "CONCRETE_DEFECTS_FOUND": None,
        "CONCRETE_DEFECTS_STATUS": "NOT_RECOMPUTED_FROM_CURRENT_FINDINGS",
        "UNREVIEWED_MANUAL_OBJECTS": len(unreviewed),
        "NON_FORMALIZABLE_NO_CONCRETE_DEFECT": 0,
        "SEMANTICALLY_REVIEWED_MANUAL_OBJECTS": sum(row["classification"] == "SEMANTICALLY_REVIEWED" for row in manual_reviews),
    }

    report = {
        "artifact_type": "programme_content_validation",
        "generated_by": GENERATED_BY,
        "observation": index["observation"],
        "scope": "CURRENT_EXECUTION_RECEIPT_OBJECTS_AND_STRUCTURAL_PROGRAMME_SOURCE_BINDINGS",
        "certifies_full_programme_semantic_coverage": False,
        "input_digests": {**index["input_digests"], **inputs_before},
        "summary": summary,
        "unmapped_atoms": unmapped_atoms,
        "false_coverage": false_coverage,
        **evidence,
        "manual_reviews": manual_reviews,
        "unreviewed_manual_objects": unreviewed,
        "historical_dispositions": {"path": str(disposition_path.relative_to(ROOT)),
                                    "current_credit": False, "entries": disposition.get("entries", [])},
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
        "Portée : reçus d'exécution présents et rattachements structurels du programme ; aucune certification globale.",
        f"- **Fichiers de reçus observés** : {report['summary']['TOTAL_INDEPENDENT_VALIDATIONS']}",
        f"- **Exécutions courantes passées** : {report['summary']['CURRENT_EXECUTION_PASSED']}",
        f"- **Objets scientifiquement relus dans la portée requise** : {report['summary']['PASSED_INDEPENDENT_VALIDATIONS']}",
        f"- **Revues courantes en attente** : {report['summary']['INDEPENDENT_REVIEW_PENDING']}",
        f"- **Reçus rejetés / liaisons dupliquées** : {report['summary']['REJECTED_VALIDATION_RECEIPTS']} / {report['summary']['DUPLICATE_VALIDATION_BINDINGS']}",
        f"- **Objets de revue manuelle (théorique/conceptuel)** : {report['summary']['MANUAL_REVIEWS_COUNT']}",
        f"- **Défauts concrets trouvés** : `{report['summary']['CONCRETE_DEFECTS_FOUND']}`",
        "Les défauts concrets et les contenus hors programme ne sont pas évalués par ce producteur.",
        "",
        "## Analyse adversariale des revues manuelles",
        f"- Objets en verdict `manual_review` : {report['summary']['MANUAL_REVIEWS_COUNT']}",
        f"- Revue scientifique actuelle liée : {report['summary']['SEMANTICALLY_REVIEWED_MANUAL_OBJECTS']}",
        f"- Défauts concrets encore ouverts : `{report['summary']['CONCRETE_DEFECTS_FOUND']}`",
        f"- Objets sans revue actuelle complète : `{report['summary']['UNREVIEWED_MANUAL_OBJECTS']}`",
        "Les dispositions historiques sont conservées sans crédit courant.",
    ]

    with MD_TARGET.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Rapport genere : {JSON_TARGET}")
    print(f"Summary: {json.dumps(report["summary"], indent=2)}")
    return 0 if (
        report["summary"]["OFFICIAL_ATOMS_UNCOVERED"] == 0
        and report["summary"]["FALSE_COVERAGE"] == 0
        and report["summary"]["INDEPENDENT_ANSWER_MISMATCH"] == 0
        and report["summary"]["INDEPENDENT_REVIEW_PENDING"] == 0
        and report["summary"]["REJECTED_VALIDATION_RECEIPTS"] == 0
        and report["summary"]["DUPLICATE_VALIDATION_BINDINGS"] == 0
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
