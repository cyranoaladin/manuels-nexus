#!/usr/bin/env python3
"""Registre de campagne : une ligne par chapitre des six manuels.

Aucun chapitre ne doit manquer. La campagne de publication se juge sur ce
registre : ALL_MACHINE_CONTENT_COMPLETE exige que toutes les lignes soient
machine-completes, et un chapitre absent du registre serait un chapitre oublie.

Le registre MESURE, il n'approuve rien. Les colonnes humaines rapportent l'etat
declare par la gouvernance, jamais un verdict deduit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_editorial_diacritics as diacritics  # noqa: E402
import build_qcm_independent_evidence_v2 as evidence_v2  # noqa: E402
import human_review_governance as governance  # noqa: E402
import qcm_independent_solver as solver  # noqa: E402

JSON_TARGET = ROOT / "audit" / "PUBLISH_READINESS_CHAPTER_MATRIX.json"
MD_TARGET = ROOT / "audit" / "PUBLISH_READINESS_CHAPTER_MATRIX.md"
INVENTORY = ROOT / "audit" / "INVENTAIRE_COLLECTION.json"
COVERAGE_DIR = ROOT / "audit" / "official_program_coverage"
MATH_CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
NSI_CHAPTERS = ROOT / "NSI" / "chapitres"

#: Registres de dette declaree, un par chapitre qui cree des objets.
DECLARED_DEBT_LEDGERS = (
    ROOT / "audit" / "VARALEA_C6C7_REVIEW_DEBT_12.json",
    ROOT / "audit" / "EXPONENTIELLE_C1_METHOD_REVIEW_DEBT_1.json",
)

#: Contrat editorial Nexus de distribution des cles. Ce n'est pas une exigence
#: du B.O. : c'est une regle de qualite du manuel.
KEY_SPREAD_MAX = 1
KEY_RUN_MAX = 2


def _chapter_dir(chapter: str) -> Path | None:
    for root in (MATH_CHAPTERS, NSI_CHAPTERS):
        candidate = root / chapter
        if candidate.is_dir():
            return candidate
    return None


#: L'inventaire nomme le manuel TSPE_2026_2027, l'artefact de couverture
#: TSPE. Sans cette correspondance, onze chapitres paraissent sans programme.
COVERAGE_FILE_BY_MANUAL = {"TSPE_2026_2027": "TSPE"}


def _programme(chapter: str, manual: str) -> dict[str, Any]:
    path = COVERAGE_DIR / f"{COVERAGE_FILE_BY_MANUAL.get(manual, manual)}.json"
    if not path.is_file():
        return {
            "official_atoms": None,
            "mapped": None,
            "missing": None,
            "wrong_year": None,
            "status": "NO_COVERAGE_ARTIFACT",
        }
    rows = [
        row
        for row in json.loads(path.read_text(encoding="utf-8"))["rows"]
        if row.get("chapter") == chapter
    ]
    mandatory = [row for row in rows if row.get("mandatory") == "YES"]
    mapped = [row for row in mandatory if row.get("contract_capacity")]
    wrong_year = [row for row in rows if row.get("wrong_programme_year") is True]
    return {
        "official_atoms": len(rows),
        "mandatory_atoms": len(mandatory),
        "mapped": len(mapped),
        "missing": len(mandatory) - len(mapped),
        "wrong_year": len(wrong_year),
        "status": "COMPLETE" if len(mapped) == len(mandatory) and not wrong_year else "GAP",
    }


def _qcm(chapter: str, directory: Path) -> dict[str, Any]:
    candidates = sorted((directory / "qcm").glob("*-QCM.json")) if directory else []
    if not candidates:
        return {"present": False, "status": "NO_QCM"}
    document = json.loads(candidates[0].read_text(encoding="utf-8"))
    questions = document.get("questions", [])
    keys = Counter(q["correcte"] for q in questions)
    for letter in "ABCD":
        keys.setdefault(letter, 0)
    sequence = [q["correcte"] for q in questions]
    run = longest = 1
    for index in range(1, len(sequence)):
        run = run + 1 if sequence[index] == sequence[index - 1] else 1
        longest = max(longest, run)
    spread = max(keys.values()) - min(keys.values()) if keys else 0
    coverage_gaps = [
        q["id"]
        for q in questions
        if not evidence_v2._diagnostic_coverage(q)["complete"]
    ]
    equivalent = [
        q["id"] for q in questions if evidence_v2._equivalent_option_groups(q)
    ]
    return {
        "present": True,
        "questions": len(questions),
        "key_distribution": dict(sorted(keys.items())),
        "key_spread": spread,
        "longest_identical_run": longest if questions else 0,
        "distribution_contract_met": bool(
            questions
            and spread <= KEY_SPREAD_MAX
            and longest <= KEY_RUN_MAX
            and all(keys[letter] for letter in "ABCD")
        ),
        "equivalent_option_questions": equivalent,
        "diagnostic_or_remediation_gaps": coverage_gaps,
        "capacities_assessed": sorted({q.get("capacite") for q in questions if q.get("capacite")}),
        "status": (
            "COMPLETE"
            if questions
            and spread <= KEY_SPREAD_MAX
            and longest <= KEY_RUN_MAX
            and all(keys[letter] for letter in "ABCD")
            and not equivalent
            and not coverage_gaps
            else "GAP"
        ),
    }


def _diacritics(directory: Path) -> dict[str, Any]:
    if directory is None:
        return {"unambiguous": None, "ambiguous": None, "status": "NO_SOURCE"}
    report = diacritics.scan_paths(sorted(directory.rglob("*.tex")))
    return {
        "unambiguous": report["UNAMBIGUOUS_DIACRITICS_DEBT"],
        "ambiguous": report["AMBIGUOUS_REQUIRING_CONTEXT"],
        "status": "COMPLETE" if report["UNAMBIGUOUS_DIACRITICS_DEBT"] == 0 else "GAP",
    }


def _oracle(directory: Path) -> dict[str, Any]:
    """Verdicts de l'oracle SymPy, lus dans les recus du chapitre."""

    if directory is None:
        return {"pass": None, "manual_review": None, "fail": None, "status": "NO_SOURCE"}
    verdicts: Counter = Counter()
    for receipt in sorted((directory / "validations").glob("*.sympy.json")):
        try:
            verdicts[json.loads(receipt.read_text(encoding="utf-8"))["verdict"]] += 1
        except (json.JSONDecodeError, KeyError, OSError):
            verdicts["unreadable"] += 1
    return {
        "pass": verdicts.get("pass", 0),
        "manual_review": verdicts.get("manual_review", 0),
        "fail": verdicts.get("fail", 0) + verdicts.get("unreadable", 0),
        "receipts": sum(verdicts.values()),
        "status": "COMPLETE" if not verdicts.get("fail") and not verdicts.get("unreadable") else "GAP",
    }


def _assessments(directory: Path) -> dict[str, Any]:
    if directory is None:
        return {"variants": [], "status": "NO_SOURCE"}
    found = sorted(p.stem for p in (directory / "evaluations").glob("*.tex")) if (directory / "evaluations").is_dir() else []
    subjects = [name for name in found if not name.endswith("-corrige")]
    corrections = [name for name in found if name.endswith("-corrige")]
    return {
        "subjects": subjects,
        "corrections": corrections,
        "status": "COMPLETE"
        if len(subjects) >= 2 and len(corrections) >= len(subjects)
        else "GAP",
    }


def _evidence_routing(chapter: str, routed: dict[str, Counter]) -> dict[str, Any]:
    counts = routed.get(chapter, Counter())
    total = sum(counts.values())
    return {
        "questions_routed": total,
        "carried_forward": counts.get("CARRIED_FORWARD_IDENTICAL", 0),
        "machine_recalculated": counts.get("MACHINE_RECALCULATED", 0),
        "human_review_required": counts.get("HUMAN_REVIEW_REQUIRED", 0),
        "unknown": 0,
        "status": "COMPLETE" if total else "NO_QCM",
    }


def _declared_debt() -> dict[str, list[dict[str, Any]]]:
    by_chapter: dict[str, list[dict[str, Any]]] = {}
    for path in DECLARED_DEBT_LEDGERS:
        if not path.is_file():
            continue
        ledger = json.loads(path.read_text(encoding="utf-8"))
        by_chapter.setdefault(ledger["chapter"], []).append(
            {
                "ledger_id": ledger["ledger_id"],
                "count": ledger["count"],
                "object_ids": sorted(e["object_id"] for e in ledger["entries"]),
                "release_blocking": ledger["release_blocking"],
            }
        )
    return by_chapter


def _risk_score(row: dict[str, Any]) -> int:
    """Priorite de traitement. Plus haut = plus risque."""

    score = 0
    programme = row["programme"]
    if programme.get("status") == "GAP":
        score += 40 * max(1, programme.get("missing") or 0)
    score += 60 * (programme.get("wrong_year") or 0)
    qcm = row["qcm"]
    if qcm.get("present"):
        if not qcm["distribution_contract_met"]:
            score += 10 + 3 * qcm["key_spread"]
            if min(qcm["key_distribution"].values()) == 0:
                score += 15
        score += 12 * len(qcm["diagnostic_or_remediation_gaps"])
        score += 25 * len(qcm["equivalent_option_questions"])
    else:
        score += 30
    score += 2 * (row["diacritics"].get("unambiguous") or 0)
    oracle = row["oracle"]
    score += 50 * (oracle.get("fail") or 0)
    if row["assessments"].get("status") == "GAP":
        score += 20
    if row["human"]["review_a"] != "PENDING_UNASSIGNED" or row["human"]["review_b"] != "PENDING_UNASSIGNED":
        score += 0
    return score


_POLICY_CACHE: dict[str, Any] = {}


def _policy() -> dict[str, Any]:
    if not _POLICY_CACHE:
        _POLICY_CACHE.update(governance.load_policy(ROOT))
    return _POLICY_CACHE


def build_matrix() -> dict[str, Any]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    evidence = json.loads(
        (ROOT / "audit" / "QCM_INDEPENDENT_EVIDENCE_V2.json").read_text(encoding="utf-8")
    )
    routed: dict[str, Counter] = {}
    for entry in evidence["questions"]:
        routed.setdefault(entry["chapter"], Counter())[entry["evidence_status"]] += 1
    declared_debt = _declared_debt()

    rows: list[dict[str, Any]] = []
    for manual_id, manual in sorted(inventory["manuals"].items()):
        for chapter in sorted(manual["chapters"]):
            directory = _chapter_dir(chapter)
            try:
                scope = governance.build_scope(chapter, ROOT)
                object_count = scope.object_count
                object_digest = scope.object_set_digest
                unassembled = scope.unassembled_object_ids()
            except Exception as error:  # noqa: BLE001 - un chapitre non gouverne se voit
                object_count = None
                object_digest = None
                unassembled = [f"SCOPE_ERROR:{type(error).__name__}"]
            state = {}
            try:
                state = governance.evaluate_state(chapter, _policy(), ROOT)
            except Exception:  # noqa: BLE001 - un chapitre non gouverne se voit
                state = {}
            row = {
                "manual": manual_id,
                "chapter": chapter,
                "object_count": object_count,
                "object_set_digest": object_digest,
                "unassembled_object_ids": unassembled,
                "programme": _programme(chapter, manual_id),
                "oracle": _oracle(directory),
                "qcm": _qcm(chapter, directory),
                "evidence_routing": _evidence_routing(chapter, routed),
                "diacritics": _diacritics(directory),
                "assessments": _assessments(directory),
                "declared_review_debt": declared_debt.get(chapter, []),
                "human": {
                    "review_a": (state.get("review_a") or {}).get("state", "UNKNOWN"),
                    "review_b": (state.get("review_b") or {}).get("state", "UNKNOWN"),
                    "qcm_human_approval": state.get("qcm_human_approval", "UNKNOWN"),
                    "publication_approval": state.get("publication_approval", False),
                },
            }
            row["machine_dimensions"] = {
                "programme": row["programme"]["status"],
                "oracle": row["oracle"]["status"],
                "qcm": row["qcm"].get("status", "NO_QCM"),
                "diacritics": row["diacritics"]["status"],
                "assessments": row["assessments"]["status"],
                "evidence_routing": row["evidence_routing"]["status"],
            }
            row["vertical_machine_status"] = (
                "MACHINE_REVIEW_COMPLETE"
                if all(
                    value in {"COMPLETE", "NO_QCM"}
                    for value in row["machine_dimensions"].values()
                )
                and not unassembled
                else "INCOMPLETE"
            )
            row["human_closure_status"] = (
                "CLOSED"
                if row["human"]["review_a"] == "APPROVED"
                and row["human"]["review_b"] == "APPROVED"
                else "PENDING"
            )
            row["risk_score"] = _risk_score(row)
            rows.append(row)

    complete = [r for r in rows if r["vertical_machine_status"] == "MACHINE_REVIEW_COMPLETE"]
    return {
        "artifact_type": "publish_readiness_chapter_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_publish_readiness_chapter_matrix.py",
        "approves_nothing": True,
        "manuals": sorted(inventory["manuals"]),
        "counts": {
            "manuals": len(inventory["manuals"]),
            "chapters": len(rows),
            "machine_review_complete": len(complete),
            "machine_review_incomplete": len(rows) - len(complete),
            "human_closed": sum(1 for r in rows if r["human_closure_status"] == "CLOSED"),
        },
        "ALL_MACHINE_CONTENT_COMPLETE": len(complete) == len(rows),
        "next_by_risk": [
            {"chapter": r["chapter"], "manual": r["manual"], "risk_score": r["risk_score"]}
            for r in sorted(
                (r for r in rows if r["vertical_machine_status"] != "MACHINE_REVIEW_COMPLETE"),
                key=lambda item: (-item["risk_score"], item["chapter"]),
            )
        ],
        "chapters": rows,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    counts = payload["counts"]
    lines = [
        "<!-- generated by build_publish_readiness_chapter_matrix.py -->",
        "",
        "# Registre de campagne — lecture par chapitre",
        "",
        f"- Manuels : {counts['manuals']}",
        f"- Chapitres : {counts['chapters']}",
        f"- Machine review complete : {counts['machine_review_complete']}",
        f"- Machine review incomplete : {counts['machine_review_incomplete']}",
        f"- ALL_MACHINE_CONTENT_COMPLETE : {payload['ALL_MACHINE_CONTENT_COMPLETE']}",
        "",
        "| manuel | chapitre | objets | programme | oracle | QCM | diacritiques | evals | statut machine | risque |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in payload["chapters"]:
        dims = row["machine_dimensions"]
        lines.append(
            f"| {row['manual']} | {row['chapter']} | {row['object_count']} "
            f"| {dims['programme']} | {dims['oracle']} | {dims['qcm']} "
            f"| {dims['diacritics']} | {dims['assessments']} "
            f"| {row['vertical_machine_status']} | {row['risk_score']} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_matrix()
    rendered_json = render_json(payload)
    rendered_md = render_md(payload)
    if args.check:
        stale = [
            str(t.relative_to(ROOT))
            for t, r in ((JSON_TARGET, rendered_json), (MD_TARGET, rendered_md))
            if not t.is_file() or t.read_text(encoding="utf-8") != r
        ]
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print(
            f"PASS matrice: {payload['counts']['chapters']} chapitres, "
            f"{payload['counts']['machine_review_complete']} machine-complets"
        )
        return 0
    JSON_TARGET.write_text(rendered_json, encoding="utf-8")
    MD_TARGET.write_text(rendered_md, encoding="utf-8")
    print(
        f"wrote {JSON_TARGET.name}: {payload['counts']['chapters']} chapitres, "
        f"{payload['counts']['machine_review_complete']} machine-complets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
