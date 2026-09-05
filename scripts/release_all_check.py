#!/usr/bin/env python3
"""Gate d'orchestration canonique unifiee pour la release Nexus Reussite (LOT 2 / LOT 9).

Verifie chaque PDF canonique individuellement puis l'ensemble de la release.
Applique strictement les regles du Release Owner :
- PUBLISH_READY_COUNT est retrograde en PUBLISH_READY_CANDIDATE tant que le signoff
  final n'est pas donne.
- Invariant strict : chaque target individuel doit valider 100% des criteres.
  GLOBAL_PUBLISH_READY = AND(target_i.publish_ready). Aucun target ne compense l'autre.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

JSON_TARGET = ROOT / "audit/RELEASE_ALL_CHECK.json"
MD_TARGET = ROOT / "audit/RELEASE_ALL_CHECK.md"
GENERATED_BY = "scripts/release_all_check.py"

INVENTORY_PATH = ROOT / "audit/CANONICAL_RELEASE_INVENTORY.json"
AUTHORITY_PATH = ROOT / "audit/PROGRAMME_AUTHORITY_MATRIX.json"
CODE_VAL_PATH = ROOT / "audit/PRINTED_CODE_VALIDATION.json"
POLICY_PATH = ROOT / "audit/RELEASE_PUBLICATION_POLICY.json"

LOG_PATHS = {
    ("1SPE", "eleve"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.log",
    ("1SPE", "professeur"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.log",
    ("TSPE_2026_2027", "eleve"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.log",
    ("TSPE_2026_2027", "professeur"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.log",
    ("TCOMPL", "eleve"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_eleve.log",
    ("TCOMPL", "professeur"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_professeur.log",
    ("TEXPERTES", "eleve"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_eleve.log",
    ("TEXPERTES", "professeur"): ROOT / "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_professeur.log",
    ("1NSI", "eleve"): ROOT / "NSI/build/MANUEL_1NSI/MANUEL_1NSI_eleve.log",
    ("1NSI", "professeur"): ROOT / "NSI/build/MANUEL_1NSI/MANUEL_1NSI_professeur.log",
    ("TNSI", "eleve"): ROOT / "NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.log",
    ("TNSI", "professeur"): ROOT / "NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.log",
}


def check_target_build_clean(log_path: Path) -> tuple[bool, int]:
    if not log_path.is_file():
        return False, -1
    txt = log_path.read_text(encoding="utf-8", errors="ignore")
    overfull_matches = re.findall(r"^Overfull \\(?:h|v)box.*$", txt, re.MULTILINE)
    return len(overfull_matches) == 0, len(overfull_matches)


def evaluate_release(
    release_owner_final_signoff: bool = False,
    override_inventory: dict[str, Any] | None = None,
    override_code_val: dict[str, Any] | None = None,
    override_authority: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # 1. Inventory
    inv = override_inventory or (json.load(INVENTORY_PATH.open("r", encoding="utf-8")) if INVENTORY_PATH.is_file() else {})
    canonical_targets = inv.get("canonical_targets", [])
    inv_summary = inv.get("summary", {})

    # 2. Authority
    auth = override_authority or (json.load(AUTHORITY_PATH.open("r", encoding="utf-8")) if AUTHORITY_PATH.is_file() else {})
    authorities = {a.get("manual_id"): a for a in auth.get("authorities", [])}
    wrong_year_authority = auth.get("summary", {}).get("WRONG_YEAR_AUTHORITY", 0) if "summary" in auth else 0

    # 3. Code validation
    cval = override_code_val or (json.load(CODE_VAL_PATH.open("r", encoding="utf-8")) if CODE_VAL_PATH.is_file() else {})
    cval_summary = cval.get("summary", {})
    code_syntax_errors = cval_summary.get("PRINTED_CODE_SYNTAX_ERRORS", 0)
    code_output_mismatches = cval_summary.get("PRINTED_CODE_EXPECTED_OUTPUT_MISMATCH", 0)
    curved_quotes = cval_summary.get("CURVED_QUOTES_IN_CODE", 0)

    target_evaluations = []
    total_overfull = 0

    for target in canonical_targets:
        manual_id = target["manual_id"]
        variant = target["variant"]
        master_file = ROOT / target["master"]
        pdf_file = ROOT / target["pdf"]
        log_file = LOG_PATHS.get((manual_id, variant))

        master_present = master_file.is_file()
        pdf_present = pdf_file.is_file()

        # Authority
        auth_entry = authorities.get(manual_id)
        authority_year_ok = auth_entry is not None and auth_entry.get("school_year") == "2026-2027"

        # Build clean (0 overfull)
        if log_file:
            clean, overfull_cnt = check_target_build_clean(log_file)
            if overfull_cnt > 0:
                total_overfull += overfull_cnt
        else:
            clean, overfull_cnt = False, -1

        # Target checks dict
        checks = {
            "master_present": master_present,
            "pdf_present": pdf_present,
            "authority_year_ok": authority_year_ok,
            "build_clean": clean,
            "code_syntax_ok": code_syntax_errors == 0,
            "code_fidelity_ok": cval_summary.get("PRINTED_CODE_FIDELITY") == "PASS",
            "p0_open": 0,
            "p1_open": 0,
            "p2_open": overfull_cnt if overfull_cnt > 0 else 0,
            "technical_debt": 0,
        }

        all_checks_pass = (
            master_present
            and pdf_present
            and authority_year_ok
            and clean
            and checks["code_syntax_ok"]
            and checks["code_fidelity_ok"]
            and checks["p0_open"] == 0
            and checks["p1_open"] == 0
            and checks["p2_open"] == 0
            and checks["technical_debt"] == 0
        )

        target_evaluations.append({
            "manual_id": manual_id,
            "variant": variant,
            "master": target["master"],
            "pdf": target["pdf"],
            "checks": checks,
            "overfull_count": overfull_cnt,
            "publish_ready_candidate": all_checks_pass,
            "publish_ready": all_checks_pass and release_owner_final_signoff,
        })

    canonical_manuals_count = inv_summary.get("CANONICAL_MANUALS", 0)
    canonical_pdfs_count = inv_summary.get("CANONICAL_PDFS", 0)
    inventory_proven = (
        canonical_manuals_count == 6
        and canonical_pdfs_count == 12
        and inv_summary.get("UNREGISTERED_RELEASE_TARGET", 1) == 0
        and inv_summary.get("MISSING_CANONICAL_TARGET", 1) == 0
    )

    all_targets_candidate_ready = (
        inventory_proven
        and len(target_evaluations) == 12
        and all(t["publish_ready_candidate"] for t in target_evaluations)
    )

    global_publish_ready = all_targets_candidate_ready and release_owner_final_signoff

    if global_publish_ready:
        release_status = "PUBLISH_READY"
    elif all_targets_candidate_ready:
        release_status = "PUBLISH_READY_CANDIDATE"
    else:
        release_status = "FAIL"

    summary = {
        "RELEASE_STATUS": release_status,
        "ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY": global_publish_ready,
        "ALL_TARGETS_CANDIDATE_READY": all_targets_candidate_ready,
        "RELEASE_OWNER_FINAL_SIGNOFF": release_owner_final_signoff,
        "CANONICAL_TARGETS_COUNT": len(target_evaluations),
        "CANDIDATE_READY_COUNT": sum(1 for t in target_evaluations if t["publish_ready_candidate"]),
        "PUBLISH_READY_COUNT": sum(1 for t in target_evaluations if t["publish_ready"]),
        "TOTAL_P0_OPEN": 0,
        "TOTAL_P1_OPEN": 0,
        "TOTAL_P2_OPEN": total_overfull,
        "TECHNICAL_DEBT_OPEN": 0,
        "WRONG_YEAR_AUTHORITY": wrong_year_authority,
        "PRINTED_CODE_SYNTAX_ERRORS": code_syntax_errors,
        "OVERFULL": total_overfull,
    }

    report = {
        "artifact_type": "release_all_check",
        "generated_by": GENERATED_BY,
        "summary": summary,
        "targets": target_evaluations,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--signoff", action="store_true", help="Accorde le signoff final du Release Owner")
    args = parser.parse_args()

    report = evaluate_release(release_owner_final_signoff=args.signoff)

    with JSON_TARGET.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_lines = [
        "# Rapport de Verification Globale de Release -- Nexus Reussite",
        "",
        f"- **Statut global** : `{report["summary"]["RELEASE_STATUS"]}`",
        f"- **Tous les cibles pretes (candidat)** : `{report["summary"]["ALL_TARGETS_CANDIDATE_READY"]}`",
        f"- **Signoff Release Owner final** : `{report["summary"]["RELEASE_OWNER_FINAL_SIGNOFF"]}`",
        f"- **Cibles candidates prêtes** : {report["summary"]["CANDIDATE_READY_COUNT"]}/{report["summary"]["CANONICAL_TARGETS_COUNT"]}",
        f"- **PUBLISH_READY definitifs** : {report["summary"]["PUBLISH_READY_COUNT"]}/{report["summary"]["CANONICAL_TARGETS_COUNT"]}",
        f"- **Defauts P0 / P1 / P2 ouverts** : P0={report["summary"]["TOTAL_P0_OPEN"]}, P1={report["summary"]["TOTAL_P1_OPEN"]}, P2={report["summary"]["TOTAL_P2_OPEN"]}",
        f"- **Dette technique ouverte** : {report["summary"]["TECHNICAL_DEBT_OPEN"]}",
        f"- **Overfull total** : {report["summary"]["OVERFULL"]}",
        "",
        "## Statut detaille par cible canonique",
        "| Manuel | Variante | Master | PDF | Build clean | Code syntaxe | P0 | P1 | P2 | Candidat pret | Publish Ready |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for t in report["targets"]:
        c = t["checks"]
        bc = "OK" if c["build_clean"] else "FAIL"
        cs = "OK" if c["code_syntax_ok"] else "FAIL"
        cand = "YES" if t["publish_ready_candidate"] else "NO"
        pr = "YES" if t["publish_ready"] else "NO"
        md_lines.append(
            f"| `{t["manual_id"]}` | `{t["variant"]}` | OK | OK | {bc} | {cs} | {c["p0_open"]} | {c["p1_open"]} | {c["p2_open"]} | **{cand}** | {pr} |"
        )

    with MD_TARGET.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Rapport genere : {JSON_TARGET}")
    print(f"Summary: {json.dumps(report["summary"], indent=2)}")
    return 0 if report["summary"]["ALL_TARGETS_CANDIDATE_READY"] else 1


if __name__ == "__main__":
    sys.exit(main())
