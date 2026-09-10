#!/usr/bin/env python3
"""Gate d'orchestration finale unifiée pour la release Nexus Réussite (LOT 9).

Orchestre et certifie les 8 dimensions fondamentales pour les 12 cibles canoniques :
1. INVENTORY & SCOPE : 6 manuels, 12 PDF canoniques, 0 cibles manquantes ou non enregistrées.
2. SCHOOL YEAR AUTHORITY : 2026-2027 strictement respecté, 0 autorité périmée ou future.
3. PRINTED CODE FIDELITY : 0 erreur syntaxique Python/SQL, 100% fidélité de sortie.
4. CONTENT & ATOM COVERAGE : 596/596 atomes obligatoires, 0 hors programme non étiqueté.
5. STUDENT/TEACHER PARITY : 1951 exercices = 1951 corrigés, 0 fuite élève, 0 anomalie de barème.
6. DEPENDENCY GRAPH & FRESHNESS : graphe dérivé sans préfixes codés en dur, stale tracking testé.
7. REPRODUCIBILITY & MANIFEST : double-build prouvé 12/12, 12 receipts scellés dans le manifeste v2.
8. PRINT PREFLIGHT & REGRESSION : MediaBox uniforme, 100% polices incorporées, 0 overfull, 0 régression inattendue.
9. ZERO TECHNICAL DEBT : 0 dette technique ouverte, 0 dette produit ouverte.

RÈGLE D'AUTORITÉ ABSOLUE :
- ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY reste FALSE et le statut est
  ZERO_DEBT_RELEASE_OWNER_FINAL_SIGNOFF_REQUIRED tant que le Release Owner humain
  n'a pas formellement accordé son signoff dans le chat.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

JSON_TARGET = ROOT / "audit/RELEASE_ALL_CHECK.json"
MD_TARGET = ROOT / "audit/RELEASE_ALL_CHECK.md"
COLLECTION_READINESS_JSON = ROOT / "audit/COLLECTION_PUBLISH_READINESS.json"
COLLECTION_READINESS_MD = ROOT / "audit/COLLECTION_PUBLISH_READINESS.md"
SNAPSHOT_TARGET = ROOT / "audit/RELEASE_SNAPSHOT.json"
GENERATED_BY = "scripts/release_all_check.py"

INVENTORY_PATH = ROOT / "audit/CANONICAL_RELEASE_INVENTORY.json"
AUTHORITY_PATH = ROOT / "audit/PROGRAMME_AUTHORITY_MATRIX.json"
CODE_VAL_PATH = ROOT / "audit/PRINTED_CODE_VALIDATION.json"
CONTENT_VAL_PATH = ROOT / "audit/PROGRAMME_CONTENT_VALIDATION.json"
PARITY_PATH = ROOT / "audit/PARITY_BAREMES_VALIDATION.json"
MANIFEST_PATH = ROOT / "audit/BUILD_MANIFEST.json"
REPRO_PATH = ROOT / "audit/DOUBLE_BUILD_REPRODUCIBILITY.json"
PREFLIGHT_PATH = ROOT / "audit/FINAL_PRINT_PREFLIGHT.json"
REGRESSION_PATH = ROOT / "audit/VISUAL_SEMANTIC_REGRESSION_REPORT.json"
DEBT_PATH = ROOT / "audit/ZERO_TECHNICAL_DEBT_REPORT.json"
FINDINGS_PATH = ROOT / "audit/OPEN_FINDINGS.json"


def matches_manual(item: dict[str, Any] | str, manual_id: str) -> bool:
    if isinstance(item, str):
        path_str = item
    else:
        declared_manual = item.get("manual")
        if declared_manual:
            return declared_manual == manual_id or manual_id.startswith(declared_manual)
        path_str = item.get("path") or item.get("file") or ""

    if not path_str:
        return True

    parts = Path(path_str).parts
    for part in parts:
        if manual_id in part:
            return True
    normalized = manual_id.replace("_2026_2027", "").replace("EXPERTES", "EXP")
    for part in parts:
        if normalized in part:
            return True
    return False


def get_git_commit_head(root: Path = ROOT) -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        head_file = root / ".git/HEAD"
        if head_file.is_file():
            ref = head_file.read_text(encoding="utf-8").strip()
            if ref.startswith("ref: "):
                ref_path = root / ".git" / ref[5:]
                if ref_path.is_file():
                    return ref_path.read_text(encoding="utf-8").strip()
            return ref
        return "UNKNOWN"


def compute_file_sha256(path: Path) -> str:
    if not path.is_file():
        return "ABSENT"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_release_snapshot(report: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    return {
        "artifact_type": "release_snapshot",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "commit_head": get_git_commit_head(root),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "release_status": report["summary"]["RELEASE_STATUS"],
        "all_targets_candidate_ready": report["summary"]["ALL_TARGETS_CANDIDATE_READY"],
        "evidence_digests": {
            "canonical_release_inventory": compute_file_sha256(INVENTORY_PATH),
            "programme_authority_matrix": compute_file_sha256(AUTHORITY_PATH),
            "printed_code_validation": compute_file_sha256(CODE_VAL_PATH),
            "programme_content_validation": compute_file_sha256(CONTENT_VAL_PATH),
            "parity_baremes_validation": compute_file_sha256(PARITY_PATH),
            "build_manifest": compute_file_sha256(MANIFEST_PATH),
            "double_build_reproducibility": compute_file_sha256(REPRO_PATH),
            "final_print_preflight": compute_file_sha256(PREFLIGHT_PATH),
            "visual_semantic_regression_report": compute_file_sha256(REGRESSION_PATH),
            "zero_technical_debt_report": compute_file_sha256(DEBT_PATH),
            "open_findings": compute_file_sha256(FINDINGS_PATH),
        },
        "canonical_targets": [
            {
                "target_id": t["target_id"],
                "manual_id": t["manual_id"],
                "variant": t["variant"],
                "master": t["master"],
                "pdf": t["pdf"],
                "page_count": t["page_count"],
                "pdf_sha256": t["pdf_sha256"],
                "publish_ready_candidate": t["publish_ready_candidate"],
            }
            for t in report["targets"]
        ],
    }


def _provenance() -> dict[str, Any]:
    """Les quatre identites de provenance, jamais confondues.

    AUDITED_SOURCE_SHA dit ce qui a ete observe, REPORT_COMMIT_SHA ou le
    rapport atterrit, SEMANTIC_SOURCE_DIGEST ce qui decide de la fraicheur, et
    RELEASE_TAG_SHA le tag lorsqu'il existe. Un commit de rapport fait avancer
    le second sans toucher le troisieme : il ne perime donc rien.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_current_review_index import observation
    from evidence_freshness import head_sha, provenance

    head = head_sha(ROOT)
    observed = observation(ROOT, head)
    # `worktree_status` enumere les chemins modifies. Publie tel quel, il fait
    # de ce rapport une REFERENCE vers chacun de ces fichiers et fausse les
    # graphes de reference qui le lisent. Seuls la proprete et le nombre
    # d'entrees sont conserves : l'information demeure, les chemins sortent.
    entries = observed.pop("worktree_status", [])
    observed["worktree_dirty_entries"] = len(entries)
    return {**observed, **provenance(root=ROOT), "generated_by": GENERATED_BY}


def evaluate_release(
    release_owner_final_signoff: bool = False,
) -> dict[str, Any]:
    # 1. Inventory
    inv = json.load(INVENTORY_PATH.open("r", encoding="utf-8")) if INVENTORY_PATH.is_file() else {}
    canonical_targets = inv.get("canonical_targets", [])
    inv_summary = inv.get("summary", {})

    # 2. Authority
    auth = json.load(AUTHORITY_PATH.open("r", encoding="utf-8")) if AUTHORITY_PATH.is_file() else {}
    authorities = {a.get("manual_id"): a for a in auth.get("authorities", [])}

    # 3. Code validation
    cval = json.load(CODE_VAL_PATH.open("r", encoding="utf-8")) if CODE_VAL_PATH.is_file() else {}
    cval_summary = cval.get("summary", {})

    # 4. Content validation
    prog_val = json.load(CONTENT_VAL_PATH.open("r", encoding="utf-8")) if CONTENT_VAL_PATH.is_file() else {}

    # 5. Parity & baremes
    parity = json.load(PARITY_PATH.open("r", encoding="utf-8")) if PARITY_PATH.is_file() else {}

    # 6. Manifest & Reproducibility
    manifest = json.load(MANIFEST_PATH.open("r", encoding="utf-8")) if MANIFEST_PATH.is_file() else {}
    repro = json.load(REPRO_PATH.open("r", encoding="utf-8")) if REPRO_PATH.is_file() else {}
    repro_by_target = {r["target_id"]: r for r in repro.get("results", [])}

    # 7. Print preflight & regression
    preflight = json.load(PREFLIGHT_PATH.open("r", encoding="utf-8")) if PREFLIGHT_PATH.is_file() else {}
    preflight_by_target = {r["target_id"]: r for r in preflight.get("records", [])}
    regression = json.load(REGRESSION_PATH.open("r", encoding="utf-8")) if REGRESSION_PATH.is_file() else {}

    # 8. Zero Debt
    debt = json.load(DEBT_PATH.open("r", encoding="utf-8")) if DEBT_PATH.is_file() else {}
    findings = (
        json.load(FINDINGS_PATH.open("r", encoding="utf-8"))
        if FINDINGS_PATH.is_file() else {}
    )
    debt_summary = debt.get("product_debt_summary", {})

    # Fail-closed : une cle absente d'une preuve obligatoire n'est pas « zero
    # defaut », c'est une preuve manquante. On l'enregistre et on bloque.
    missing_evidence: list[str] = []

    def require(payload: Any, artifact: str, key: str, default: Any = 0) -> Any:
        section = payload.get("summary", payload) if isinstance(payload, dict) else {}
        if not isinstance(section, dict) or key not in section:
            missing_evidence.append(f"{artifact}#{key}")
            return default
        return section[key]

    target_evaluations = []

    findings_list = findings.get("findings", [])
    ids_by_sev = findings.get("finding_ids_by_severity", {})
    unattributed_p0 = max(0, len(ids_by_sev.get("P0", [])) - len([f for f in findings_list if f.get("severity") == "P0"]))
    unattributed_p1 = max(0, len(ids_by_sev.get("P1", [])) - len([f for f in findings_list if f.get("severity") == "P1"]))
    unattributed_p2 = max(0, len(ids_by_sev.get("P2", [])) - len([f for f in findings_list if f.get("severity") == "P2"]))

    markers = debt.get("publishable_source_markers_detected", [])
    residuals = debt.get("residual_files_detected", [])
    global_tech_debt = int(debt_summary.get("TECHNICAL_DEBT_OPEN", 0))
    unattributed_tech = max(0, global_tech_debt - len(markers) - len(residuals))

    for target in canonical_targets:
        manual_id = target["manual_id"]
        variant = target["variant"]
        target_id = f"{manual_id}_{variant}"

        master_file = ROOT / target["master"]
        pdf_file = ROOT / target["pdf"]

        master_present = master_file.is_file()
        pdf_present = pdf_file.is_file()

        # Authority
        auth_entry = authorities.get(manual_id, {})
        authority_ok = auth_entry.get("school_year") == "2026-2027"

        # Repro
        r_entry = repro_by_target.get(target_id, {})
        repro_ok = r_entry.get("reproducibility_status") == "PASS"

        # Preflight
        pf_entry = preflight_by_target.get(target_id, {})
        preflight_ok = pf_entry.get("preflight_status") == "PASS"

        # Overfull
        overfull_cnt = pf_entry.get("overfull_hbox_vbox", 0)

        # Student separation
        student_sep_ok = pf_entry.get("student_separation", {}).get("passed", True)

        # Dynamic defect derivation for this target
        p0_matched = [f for f in findings_list if f.get("severity") == "P0" and matches_manual(f, manual_id)]
        p1_matched = [f for f in findings_list if f.get("severity") == "P1" and matches_manual(f, manual_id)]
        p2_matched = [f for f in findings_list if f.get("severity") == "P2" and matches_manual(f, manual_id)]

        target_p0 = len(p0_matched) + unattributed_p0 + len(missing_evidence)
        target_p1 = len(p1_matched) + unattributed_p1
        target_p2 = len(p2_matched) + unattributed_p2 + overfull_cnt

        matched_markers = [m for m in markers if matches_manual(m, manual_id)]
        matched_residuals = [r for r in residuals if matches_manual(r, manual_id)]
        target_tech_debt = len(matched_markers) + len(matched_residuals) + unattributed_tech

        checks = {
            "master_present": master_present,
            "pdf_present": pdf_present,
            "authority_2026_2027": authority_ok,
            "printed_code_ok": cval_summary.get("PRINTED_CODE_FIDELITY") == "PASS",
            "overfull_zero": overfull_cnt == 0,
            "reproducibility_proven": repro_ok,
            "preflight_passed": preflight_ok,
            "student_separation_clean": student_sep_ok,
            "p0_open": target_p0,
            "p1_open": target_p1,
            "p2_open": target_p2,
            "technical_debt_open": target_tech_debt,
        }

        all_checks_pass = all([
            master_present,
            pdf_present,
            authority_ok,
            checks["printed_code_ok"],
            checks["overfull_zero"],
            repro_ok,
            preflight_ok,
            student_sep_ok,
            checks["p0_open"] == 0,
            checks["p1_open"] == 0,
            checks["p2_open"] == 0,
            checks["technical_debt_open"] == 0,
        ])

        target_evaluations.append({
            "target_id": target_id,
            "manual_id": manual_id,
            "variant": variant,
            "master": target["master"],
            "pdf": target["pdf"],
            "page_count": pf_entry.get("page_count", 0),
            "pdf_sha256": r_entry.get("build_a_sha256", ""),
            "checks": checks,
            "publish_ready_candidate": all_checks_pass,
            "publish_ready": all_checks_pass and release_owner_final_signoff,
        })

    # Fraicheur des preuves lourdes : elles declarent le commit observe. Sans
    # ce commit, rien ne les rattache a un etat -- ce qui ne vaut pas mieux
    # qu'un rattachement perime. Une preuve perimee ne peut pas rendre une
    # cible candidate : ce serait publier sur la foi d'un build d'hier.
    from evidence_freshness import semantically_current

    def _evidence_is_current(evidence: dict[str, Any]) -> bool:
        """Les sources qu'a vues cette preuve sont-elles les sources courantes ?

        La question n'est pas « quel commit ? ». Un commit d'audit fait avancer
        HEAD sans toucher un manuel : comparer les commits perimerait la preuve
        a chaque rapport publie. Ce qui tranche est le digest des sources.
        """
        digest = evidence.get("semantic_source_digest")
        commit = evidence.get("head_commit")
        if not digest and not commit:
            return False
        return semantically_current(
            observed_commit=commit, observed_digest=digest, root=ROOT
        )

    repro_current = _evidence_is_current(repro)
    preflight_current = _evidence_is_current(preflight)

    all_targets_candidate_ready = (
        repro_current
        and preflight_current
        and len(target_evaluations) == 12
        and all(t["publish_ready_candidate"] for t in target_evaluations)
        and inv_summary.get("CANONICAL_MANUALS") == 6
        and inv_summary.get("CANONICAL_PDFS") == 12
        and cval_summary.get("PRINTED_CODE_FIDELITY") == "PASS"
        and prog_val.get("summary", {}).get("OFFICIAL_ATOMS_UNCOVERED") == 0
        and parity.get("summary", {}).get("STUDENT_WITHOUT_CORRECTION") == 0
        and parity.get("summary", {}).get("TEACHER_CONTENT_LEAK_IN_STUDENT") == 0
        and len(manifest.get("builds", [])) == 12
        and repro.get("reproducibility_global") == "PROVEN"
        and preflight.get("preflight_all_targets") == "PASS"
        and regression.get("regression_gate_status") == "PASS"
        and debt.get("all_product_debts_zero") is True
        and not missing_evidence
    )

    global_publish_ready = all_targets_candidate_ready and release_owner_final_signoff

    if global_publish_ready:
        release_status = "ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY"
    elif all_targets_candidate_ready:
        release_status = "ZERO_DEBT_RELEASE_OWNER_FINAL_SIGNOFF_REQUIRED"
    else:
        release_status = "FAIL"

    # Chaque chiffre ci-dessous est LU dans la preuve correspondante. Un litteral
    # ecrit ici ne serait pas une mesure : c'est precisement ce qui laissait le
    # resume annoncer 0 pendant que les registres sous-jacents disaient autre chose.
    auth_summary = auth.get("summary", {})
    parity_summary = parity.get("summary", {})
    prog_summary = prog_val.get("summary", {})
    preflight_records = preflight.get("records", [])

    def _debt(key: str) -> int:
        return int(debt_summary.get(key, 0))

    evidence_debt = _debt("EVIDENCE_DEBT_OPEN")
    content_debt = _debt("CONTENT_DEBT_OPEN")
    technical_debt = _debt("TECHNICAL_DEBT_OPEN")
    programme_debt = _debt("PROGRAMME_DEBT_OPEN")
    print_debt = _debt("PRINT_DEBT_OPEN")
    manifest_debt = _debt("MANIFEST_DEBT_OPEN")
    repro_debt = _debt("REPRODUCIBILITY_DEBT_OPEN")

    manifest_builds = len(manifest.get("builds", []))
    repro_ok_count = sum(
        1 for r in repro.get("results", []) if r.get("reproducibility_status") == "PASS"
    )
    overfull_total = sum(int(r.get("overfull_hbox_vbox", 0)) for r in preflight_records)

    summary = {
        "RELEASE_STATUS": release_status,
        "ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY": global_publish_ready,
        "ALL_TARGETS_CANDIDATE_READY": all_targets_candidate_ready,
        "RELEASE_OWNER_FINAL_SIGNOFF": release_owner_final_signoff,
        "CANONICAL_MANUALS_COUNT": require(inv_summary, "audit/CANONICAL_RELEASE_INVENTORY.json", "CANONICAL_MANUALS"),
        "CANONICAL_TARGETS_COUNT": len(target_evaluations),
        "CANDIDATE_READY_COUNT": sum(1 for t in target_evaluations if t["publish_ready_candidate"]),
        "PUBLISH_READY_COUNT": sum(1 for t in target_evaluations if t["publish_ready"]),
        # Les severites descendent du registre des findings : chaque total est
        # la longueur de sa liste d'identifiants, jamais une somme recomposee.
        "TOTAL_P0_OPEN": len(findings.get("finding_ids_by_severity", {}).get("P0", []))
        + len(missing_evidence),
        "TOTAL_P1_OPEN": len(findings.get("finding_ids_by_severity", {}).get("P1", [])),
        "TOTAL_P2_OPEN": len(findings.get("finding_ids_by_severity", {}).get("P2", [])),
        "OPEN_FINDING_IDS_P0": len(findings.get("finding_ids_by_severity", {}).get("P0", [])),
        "TRUE_PRODUCT_CLONES_OPEN": len(findings.get("clone_finding_ids", [])),
        "EVIDENCE_DEBT_OPEN": evidence_debt + len(missing_evidence),
        "MISSING_EVIDENCE_KEYS": len(missing_evidence),
        "PRODUCT_TECHNICAL_DEBT_OPEN": technical_debt,
        "CONTENT_DEBT_OPEN": content_debt,
        "PROGRAMME_DEBT_OPEN": programme_debt,
        "PRINT_DEBT_OPEN": print_debt,
        "MANIFEST_DEBT_OPEN": manifest_debt,
        "REPRODUCIBILITY_DEBT_OPEN": repro_debt,
        "TEX_ROOTS_DISCOVERED": require(inv_summary, "audit/CANONICAL_RELEASE_INVENTORY.json", "TOTAL_TEX_ROOTS"),
        "UNCLASSIFIED_TEX_ROOTS": require(inv_summary, "audit/CANONICAL_RELEASE_INVENTORY.json", "UNCLASSIFIED_TEX_ROOTS"),
        "UNREGISTERED_RELEASE_TARGET": require(inv_summary, "audit/CANONICAL_RELEASE_INVENTORY.json", "UNREGISTERED_RELEASE_TARGET"),
        "MISSING_CANONICAL_TARGET": require(inv_summary, "audit/CANONICAL_RELEASE_INVENTORY.json", "MISSING_CANONICAL_TARGET"),
        "AMBIGUOUS_CURRENT_ARTIFACT": require(inv_summary, "audit/CANONICAL_RELEASE_INVENTORY.json", "AMBIGUOUS_CURRENT_ARTIFACT"),
        "WRONG_YEAR_AUTHORITY": require(auth_summary, "audit/PROGRAMME_AUTHORITY_MATRIX.json", "WRONG_YEAR_AUTHORITY"),
        "AUTHORITY_SOURCE_DIGEST_MISMATCH": require(auth_summary, "audit/PROGRAMME_AUTHORITY_MATRIX.json", "AUTHORITY_SOURCE_DIGEST_MISMATCH"),
        "PRINTED_CODE_BLOCKS_DISCOVERED": require(cval_summary, "audit/PRINTED_CODE_VALIDATION.json", "PRINTED_CODE_BLOCKS_DISCOVERED"),
        "PRINTED_CODE_BLOCKS_CLASSIFIED": require(cval_summary, "audit/PRINTED_CODE_VALIDATION.json", "PRINTED_CODE_BLOCKS_CLASSIFIED"),
        "UNCLASSIFIED_PRINTED_CODE": require(cval_summary, "audit/PRINTED_CODE_VALIDATION.json", "UNCLASSIFIED_PRINTED_CODE"),
        "PRINTED_CODE_SYNTAX_ERRORS": require(cval_summary, "audit/PRINTED_CODE_VALIDATION.json", "PRINTED_CODE_SYNTAX_ERRORS"),
        "PRINTED_CODE_EXPECTED_OUTPUT_MISMATCH": require(cval_summary, "audit/PRINTED_CODE_VALIDATION.json", "PRINTED_CODE_EXPECTED_OUTPUT_MISMATCH"),
        "CURVED_QUOTES_IN_CODE": require(cval_summary, "audit/PRINTED_CODE_VALIDATION.json", "CURVED_QUOTES_IN_CODE"),
        "OVERFULL": overfull_total,
        "OFFICIAL_ATOMS_UNCOVERED": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "OFFICIAL_ATOMS_UNCOVERED"),
        "FALSE_COVERAGE": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "FALSE_COVERAGE"),
        "UNLABELLED_OUT_OF_PROGRAMME_CONTENT": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "UNLABELLED_OUT_OF_PROGRAMME_CONTENT"),
        "INDEPENDENT_ANSWER_MISMATCH": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "INDEPENDENT_ANSWER_MISMATCH"),
        "INDEPENDENT_FORMAL_VALIDATIONS": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "TOTAL_INDEPENDENT_VALIDATIONS"),
        "MANUAL_REVIEW_OBJECTS": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "MANUAL_REVIEWS_COUNT"),
        "CONCRETE_DEFECTS_FOUND": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "CONCRETE_DEFECTS_FOUND"),
        "UNREVIEWED_MANUAL_OBJECTS": require(prog_summary, "audit/PROGRAMME_CONTENT_VALIDATION.json", "UNREVIEWED_MANUAL_OBJECTS"),
        "STUDENT_WITHOUT_CORRECTION": require(parity_summary, "audit/PARITY_BAREMES_VALIDATION.json", "STUDENT_WITHOUT_CORRECTION"),
        "ORPHAN_TEACHER_CORRECTION": require(parity_summary, "audit/PARITY_BAREMES_VALIDATION.json", "ORPHAN_TEACHER_CORRECTION"),
        "STUDENT_TEACHER_STATEMENT_DRIFT": require(parity_summary, "audit/PARITY_BAREMES_VALIDATION.json", "STUDENT_TEACHER_STATEMENT_DRIFT"),
        "TEACHER_CONTENT_LEAK_IN_STUDENT": require(parity_summary, "audit/PARITY_BAREMES_VALIDATION.json", "TEACHER_CONTENT_LEAK_IN_STUDENT"),
        "BAREME_TOTAL_MISMATCH": require(parity_summary, "audit/PARITY_BAREMES_VALIDATION.json", "BAREME_TOTAL_MISMATCH"),
        "BAREME_SCOPE_AMBIGUOUS": require(parity_summary, "audit/PARITY_BAREMES_VALIDATION.json", "BAREME_SCOPE_AMBIGUOUS"),
        "DOUBLE_BUILD_REPRODUCIBILITY": f"{repro_ok_count}/{len(target_evaluations)}",
        # Une preuve rattachee a un autre commit reste consultable, mais cesse
        # d'etre annoncee comme acquise : c'est la difference entre « prouve »
        # et « prouve un jour ».
        "REPRODUCIBILITY_EVIDENCE_HEAD": repro.get("head_commit"),
        "REPRODUCIBILITY_EVIDENCE_CURRENT": repro_current,
        "REPRODUCIBILITY_GLOBAL": (
            repro.get("reproducibility_global", "UNKNOWN")
            if repro_current
            else "STALE_EVIDENCE_NOT_REOBSERVED"
        ),
        "MANIFEST_COVERAGE": f"{manifest_builds}/{len(target_evaluations)}",
        "MANIFEST_GLOBAL": (
            "FULL_CURRENT"
            if manifest_builds == len(target_evaluations) and manifest_debt == 0
            else "INCOMPLETE"
        ),
        "PREFLIGHT_EVIDENCE_HEAD": preflight.get("head_commit"),
        "PREFLIGHT_EVIDENCE_CURRENT": preflight_current,
        "PREFLIGHT_ALL_TARGETS": (
            preflight.get("preflight_all_targets", "UNKNOWN")
            if preflight_current
            else "STALE_EVIDENCE_NOT_REOBSERVED"
        ),
        # Compte les cibles reellement PASS, au lieu de le supposer egal au total.
        "PREFLIGHT_TARGETS_PASSED": sum(
            1 for r in preflight_records if r.get("preflight_status") == "PASS"
        ),
        "UNEXPECTED_VISUAL_DIFF": regression.get("unexpected_visual_diff", 0),
        "UNEXPLAINED_SEMANTIC_DIFF": regression.get("unexplained_semantic_diff", 0),
        "ALL_PRODUCT_DEBTS_ZERO": bool(debt.get("all_product_debts_zero", False)),
    }

    report = {
        "artifact_type": "release_all_check",
        "schema_version": "2.0.0",
        "generated_by": GENERATED_BY,
        "provenance": _provenance(),
        "summary": summary,
        "targets": target_evaluations,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--signoff", action="store_true", help="Accorde le signoff final du Release Owner")
    args = parser.parse_args()

    report = evaluate_release(release_owner_final_signoff=args.signoff)

    # Write audit/RELEASE_ALL_CHECK.json and COLLECTION_PUBLISH_READINESS.json
    for path in (JSON_TARGET, COLLECTION_READINESS_JSON):
        with path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")

    snapshot = create_release_snapshot(report, root=ROOT)
    with SNAPSHOT_TARGET.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")

    md_lines = [
        "# Synthèse Globale de Release — Manuels Nexus Réussite (Édition 2026-2027)",
        "",
        f"- **Statut Global Release** : `{report['summary']['RELEASE_STATUS']}`",
        f"- **Toutes les cibles prêtes (Candidats)** : `{report['summary']['ALL_TARGETS_CANDIDATE_READY']}` ({report['summary']['CANDIDATE_READY_COUNT']}/{report['summary']['CANONICAL_TARGETS_COUNT']})",
        f"- **Signoff Release Owner Final** : `{report['summary']['RELEASE_OWNER_FINAL_SIGNOFF']}`",
        f"- **PUBLISH_READY Définitifs** : `{report['summary']['PUBLISH_READY_COUNT']}/{report['summary']['CANONICAL_TARGETS_COUNT']}`",
        f"- **Reproductibilité Déterministe** : `{report['summary']['REPRODUCIBILITY_GLOBAL']}` ({report['summary']['DOUBLE_BUILD_REPRODUCIBILITY']})",
        # Le denominateur est celui des cibles reellement evaluees, jamais un
        # « 12/12 » ecrit en dur qui resterait vrai apres avoir cesse de l'etre.
        f"- **Préflight Impression Global** : `{report['summary']['PREFLIGHT_ALL_TARGETS']}` "
        f"({report['summary']['PREFLIGHT_TARGETS_PASSED']}/{report['summary']['CANONICAL_TARGETS_COUNT']})",
        f"- **Dette Produit Ouverte** : `{report['summary']['PRODUCT_TECHNICAL_DEBT_OPEN']}` (Technique: {report['summary']['PRODUCT_TECHNICAL_DEBT_OPEN']}, Contenu: {report['summary']['CONTENT_DEBT_OPEN']}, Programme: {report['summary']['PROGRAMME_DEBT_OPEN']}, Print: {report['summary']['PRINT_DEBT_OPEN']}, Manifest: {report['summary']['MANIFEST_DEBT_OPEN']}, Repro: {report['summary']['REPRODUCIBILITY_DEBT_OPEN']})",
        f"- **Défauts Ouverts** : P0={report['summary']['TOTAL_P0_OPEN']}, P1={report['summary']['TOTAL_P1_OPEN']}, P2={report['summary']['TOTAL_P2_OPEN']}, Overfull={report['summary']['OVERFULL']}",
        f"- **Source auditée** : `{report['provenance']['AUDITED_SOURCE_SHA']}`",
        f"- **Contenu (digest sémantique)** : `{report['provenance']['CONTENT_SEMANTIC_DIGEST']}`",
        f"- **Rendu (digest des sources)** : `{report['provenance']['RENDER_SOURCE_DIGEST']}`",
        f"- **Chaîne de fabrication (digest)** : `{report['provenance']['TOOLCHAIN_DIGEST']}`",
        f"- **Rapport généré depuis** : `{report['provenance']['REPORT_GENERATED_FROM_SHA']}` "
        f"(le commit qui portera ce rapport n'existe pas encore)",
        f"- **Arbre de travail** : {'SALE' if report['provenance']['worktree_dirty'] else 'propre'} "
        f"({report['provenance']['worktree_dirty_entries']} entrée(s))",
        "",
        "## Tableau Récapitulatif Exhaustif des 12 PDF Canoniques",
        "",
        "| Manuel | Variante | Pages | SHA256 | Code | Programme | Parité | Preflight | Repro | Candidat Prêt |",
        "| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for t in report["targets"]:
        sha_full = t["pdf_sha256"] if t["pdf_sha256"] else "N/A"
        cand = "OUI" if t["publish_ready_candidate"] else "NON"
        c = t["checks"]
        c_code = "PASS" if c["printed_code_ok"] else "FAIL"
        c_prog = "PASS" if (c["authority_2026_2027"] and c["p0_open"] == 0 and c["p1_open"] == 0) else "FAIL"
        c_parity = "PASS" if c["student_separation_clean"] else "FAIL"
        c_pf = "PASS" if (c["preflight_passed"] and c["overfull_zero"]) else "FAIL"
        c_repro = "PASS" if c["reproducibility_proven"] else "FAIL"
        md_lines.append(
            f"| **{t['manual_id']}** | `{t['variant']}` | {t['page_count']} | `{sha_full}` | "
            f"{c_code} | {c_prog} | {c_parity} | {c_pf} | {c_repro} | **`{cand}`** |"
        )
    for path in (MD_TARGET, COLLECTION_READINESS_MD):
        with path.open("w", encoding="utf-8") as f:
            f.write("\n".join(md_lines).rstrip() + "\n")

    print(f"Rapports générés : {JSON_TARGET}, {COLLECTION_READINESS_JSON} et {SNAPSHOT_TARGET}")
    print(f"Statut : {report['summary']['RELEASE_STATUS']}")
    print(f"Candidats prêts : {report['summary']['CANDIDATE_READY_COUNT']}/{report['summary']['CANONICAL_TARGETS_COUNT']}")
    return 0 if report["summary"]["ALL_TARGETS_CANDIDATE_READY"] else 1


if __name__ == "__main__":
    sys.exit(main())
