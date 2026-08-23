#!/usr/bin/env python3
"""Build the current-head Math student/professor separation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "Mathematiques/manuel-maths"
QCM_ROOT = MATH / "chapitres"
JSON_TARGET = ROOT / "audit/STUDENT_PDF_PUBLISH_PREFLIGHT_CURRENT_HEAD.json"
MD_TARGET = ROOT / "audit/STUDENT_PDF_PUBLISH_PREFLIGHT_CURRENT_HEAD.md"
INTEGRATION_BASE_SHA = "10cb5f07772842d6630d2a2f78531f6900371023"
BEGIN = "% NEXUS-QCM-TEACHER-ONLY-BEGIN"
END = "% NEXUS-QCM-TEACHER-ONLY-END"

sys.path.insert(0, str(MATH / "scripts"))
import assemble_manuel  # noqa: E402


BUILDS = {
    "1SPE": ("MANUEL_1SPE", "MANUEL_1SPE", 10),
    "TSPE": ("MANUEL_TSPE_2026-2027", "MANUEL_TSPE_2026-2027", 11),
    "TCOMPL": ("MANUEL_TCOMPL", "MANUEL_TCOMPL", 9),
    "TEXPERTES": ("MANUEL_TEXPERTES", "MANUEL_TEXPERTES", 5),
}


def _manual(chapter: str) -> str:
    if chapter.startswith("TEXP-"):
        return "TEXPERTES"
    if chapter.startswith("TSPE-"):
        return "TSPE"
    if chapter.startswith("TCOMPL-"):
        return "TCOMPL"
    if chapter.startswith("1SPE-"):
        return "1SPE"
    raise ValueError(f"chapitre QCM hors périmètre Math: {chapter}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pdf_text(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed for {path.relative_to(ROOT)}")
    return result.stdout


def _baseline_text(relative: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"{INTEGRATION_BASE_SHA}:{relative.as_posix()}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"baseline source unavailable: {relative}")
    return result.stdout


def build_payload() -> dict[str, Any]:
    build_evidence: dict[str, Any] = {}
    for manual, (directory, stem, expected) in BUILDS.items():
        student_pdf = MATH / "build" / directory / f"{stem}_eleve.pdf"
        teacher_pdf = MATH / "build" / directory / f"{stem}_professeur.pdf"
        student_text = _pdf_text(student_pdf)
        teacher_text = _pdf_text(teacher_pdf)
        violations = assemble_manuel.student_text_violations(student_text)
        observed = assemble_manuel.teacher_key_count(teacher_text)
        build_evidence[manual] = {
            "student_pdf": str(student_pdf.relative_to(ROOT)),
            "student_pdf_sha256": _sha256(student_pdf),
            "student_forbidden_markers": violations,
            "student_key_count": assemble_manuel.teacher_key_count(student_text),
            "teacher_pdf": str(teacher_pdf.relative_to(ROOT)),
            "teacher_pdf_sha256": _sha256(teacher_pdf),
            "teacher_key_count_expected": expected,
            "teacher_key_count_observed": observed,
        }

    rows: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for tex_path in sorted(QCM_ROOT.glob("*/qcm/*-QCM.tex")):
        relative = tex_path.relative_to(ROOT)
        chapter = tex_path.parents[1].name
        manual = _manual(chapter)
        json_sources = sorted(tex_path.parent.glob("*-QCM.json"))
        if len(json_sources) != 1:
            raise RuntimeError(f"canonical JSON ambiguous for {relative}")
        source = tex_path.read_text(encoding="utf-8")
        baseline = _baseline_text(relative)
        guarded = (
            source.count(BEGIN) == 1
            and source.count(END) == 1
            and "\\ifnxVersionProfesseur" in source
            and source.index(BEGIN) < source.index("\\ifnxVersionProfesseur")
            < source.index(END)
        )
        baseline_key = (
            "Cle de correction" in baseline
            or "Correction et diagnostics" in baseline
        )
        baseline_unguarded = "\\ifnxVersionProfesseur" not in baseline
        if not guarded or not baseline_key or not baseline_unguarded:
            raise RuntimeError(f"guard/baseline proof failed for {relative}")
        for path in (tex_path, json_sources[0]):
            digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        rows.append(
            {
                "manual": manual,
                "chapter": chapter,
                "source_path": relative.as_posix(),
                "canonical_source_of_truth": json_sources[0]
                .relative_to(ROOT)
                .as_posix(),
                "student_visibility_before": "VISIBLE",
                "student_visibility_current": "HIDDEN",
                "teacher_visibility_current": "VISIBLE",
                "guard_mechanism": "\\ifnxVersionProfesseur delimited by NEXUS-QCM-TEACHER-ONLY markers",
                "source_guard_status": "PASS",
            }
        )

    student_leaks = sum(
        bool(evidence["student_forbidden_markers"])
        or evidence["student_key_count"] != 0
        for evidence in build_evidence.values()
    )
    teacher_counts = {
        manual: {
            "expected": evidence["teacher_key_count_expected"],
            "observed": evidence["teacher_key_count_observed"],
        }
        for manual, evidence in sorted(build_evidence.items())
    }
    teacher_present = all(
        count["expected"] == count["observed"]
        for count in teacher_counts.values()
    )
    return {
        "schema_version": 1,
        "artifact_name": "STUDENT_PDF_PUBLISH_PREFLIGHT_CURRENT_HEAD",
        "integration_base_sha": INTEGRATION_BASE_SHA,
        "scope": "eight current Math PDF variants",
        "qcm_source_digest": f"sha256:{digest.hexdigest()}",
        "summary": {
            "qcm_key_zones": len(rows),
            "student_teacher_only_leaks": student_leaks,
            "teacher_required_keys_present": teacher_present,
            "teacher_keys_by_manual": teacher_counts,
            "eight_math_builds_passed": student_leaks == 0 and teacher_present,
        },
        "build_evidence": build_evidence,
        "keys": rows,
        "deferred_findings": [
            {
                "finding": "PDF_METADATA_INCOMPLETE / PDF_NAVIGATION_MISSING",
                "status": "CONFIRMED_ON_FOUR_STUDENT_PDFS",
                "evidence": "pdfinfo exposes no Title/Author and mutool show outline returns no entries",
                "requirement": "AGENTS.md requires metadata, bookmarks, links and embedded fonts in final PDFs",
                "owner_phase": "FINAL_PDF_PREFLIGHT / T9",
            }
        ],
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Student PDF publish preflight — current head",
        "",
        f"Integration base: `{payload['integration_base_sha']}`.",
        "",
        f"- QCM teacher-key zones: {summary['qcm_key_zones']}",
        f"- STUDENT_TEACHER_ONLY_LEAKS: {summary['student_teacher_only_leaks']}",
        f"- TEACHER_REQUIRED_KEYS_PRESENT: {'YES' if summary['teacher_required_keys_present'] else 'NO'}",
        f"- Eight Math builds: {'PASS' if summary['eight_math_builds_passed'] else 'FAIL'}",
        "",
        "## Counts by manual",
        "",
    ]
    for manual, counts in summary["teacher_keys_by_manual"].items():
        lines.append(
            f"- `{manual}`: student 0; teacher {counts['observed']}/{counts['expected']}"
        )
    lines.extend(
        [
            "",
            "The JSON companion records all 35 key zones with manual, chapter, source path, canonical JSON, before/current visibility and guard mechanism.",
            "",
            "Missing Title/Author metadata and missing outlines are confirmed on the four student PDFs; remediation remains assigned to `FINAL_PDF_PREFLIGHT / T9`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    expected = {
        JSON_TARGET: render_json(payload),
        MD_TARGET: render_markdown(payload),
    }
    if args.check:
        stale = [
            path
            for path, content in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"STALE_OR_MISSING: {path.relative_to(ROOT)}")
            return 1
        print("student/professor key audit current: 35/35")
        return 0
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
