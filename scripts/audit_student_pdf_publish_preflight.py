#!/usr/bin/env python3
"""Read-only publish preflight for the six canonical student PDF variants."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit" / "STUDENT_PDF_PUBLISH_PREFLIGHT.json"
OUTPUT_MD = ROOT / "audit" / "STUDENT_PDF_PUBLISH_PREFLIGHT.md"
PDFS = {
    "1SPE": "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf",
    "TSPE": "Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf",
    "TCOMPL": "Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_eleve.pdf",
    "TEXPERTES": "Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_eleve.pdf",
    "1NSI": "NSI/build/MANUEL_1NSI/MANUEL_1NSI_eleve.pdf",
    "TNSI": "NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.pdf",
}
MARKERS = {
    "CLE_DE_CORRECTION": r"\bcle\s+de\s+correction\b",
    "CORRIGE_PROFESSEUR": r"\bcorrige\s+professeur\b",
    "BAREME_PROFESSEUR": r"\bbareme\s+professeur\b",
    "REPONSES_RESERVEES": r"\breponses?\s+reservees?\b",
    "TEACHER_ONLY": r"\bteacher\s+only\b",
}


def normalize(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def bookmark_count(items: list) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += bookmark_count(item)
        else:
            total += 1
    return total


def release_eligible(*, leaks: int, metadata: int, navigation: int, missing: int, final_source_sha_match: bool) -> bool:
    return (
        leaks == metadata == navigation == missing == 0
        and final_source_sha_match
    )


def scan_pdf(manual: str, relative: str) -> dict:
    path = ROOT / relative
    if not path.exists():
        return {
            "manual": manual,
            "path": relative,
            "exists": False,
            "teacher_only_content_leak": 0,
            "marker_occurrences": {},
            "title": None,
            "author": None,
            "bookmark_count": 0,
            "findings": ["PDF_MISSING"],
        }

    reader = PdfReader(str(path))
    metadata = reader.metadata or {}
    extracted = subprocess.check_output(
        ["pdftotext", "-layout", str(path), "-"],
        text=True,
        errors="replace",
    )
    searchable = normalize(extracted)
    occurrences = {
        marker: len(re.findall(pattern, searchable))
        for marker, pattern in MARKERS.items()
    }
    occurrences = {marker: count for marker, count in occurrences.items() if count}
    title = metadata.get("/Title")
    author = metadata.get("/Author")
    bookmarks = bookmark_count(reader.outline)
    findings = []
    if occurrences:
        findings.append("TEACHER_ONLY_CONTENT_LEAK")
    if not title or not author:
        findings.append("PDF_METADATA_INCOMPLETE")
    if bookmarks == 0:
        findings.append("PDF_NAVIGATION_MISSING")
    return {
        "manual": manual,
        "path": relative,
        "exists": True,
        "pdf_sha256": sha256(path),
        "pages": len(reader.pages),
        "teacher_only_content_leak": sum(occurrences.values()),
        "marker_occurrences": occurrences,
        "title": title,
        "author": author,
        "bookmark_count": bookmarks,
        "findings": findings,
    }


def build_payload() -> dict:
    variants = [scan_pdf(manual, path) for manual, path in PDFS.items()]
    current_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    manifest = json.loads((ROOT / "audit" / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    leaks = sum("TEACHER_ONLY_CONTENT_LEAK" in row["findings"] for row in variants)
    metadata = sum("PDF_METADATA_INCOMPLETE" in row["findings"] for row in variants)
    navigation = sum("PDF_NAVIGATION_MISSING" in row["findings"] for row in variants)
    missing = sum("PDF_MISSING" in row["findings"] for row in variants)
    final_source_sha_match = manifest["provenance"]["head_sha"] == current_head and not dirty
    eligible = release_eligible(
        leaks=leaks,
        metadata=metadata,
        navigation=navigation,
        missing=missing,
        final_source_sha_match=final_source_sha_match,
    )
    return {
        "artifact_type": "STUDENT_PDF_PUBLISH_PREFLIGHT",
        "schema_version": 1,
        "generated_on": "2026-08-23",
        "scope": "six canonical student build PDFs; MANUELS_PDF_PUBLICATION explicitly excluded",
        "provenance": {
            "current_source_sha": current_head,
            "working_tree_dirty": dirty,
            "build_manifest_source_sha": manifest["provenance"]["head_sha"],
            "build_manifest_source_digest": manifest["source_digest"],
            "final_source_sha_match": final_source_sha_match,
        },
        "summary": {
            "variants_scanned": len(variants),
            "teacher_only_content_leak_documents": leaks,
            "pdf_metadata_incomplete": metadata,
            "pdf_navigation_missing": navigation,
            "pdf_missing": missing,
            "release_candidate_eligible": eligible,
        },
        "variants": variants,
    }


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Préflight publication — variantes élève",
        "",
        "Contrôle read-only des six PDF élève canoniques présents dans les répertoires de build. L'ancien hub `MANUELS_PDF_PUBLICATION` est explicitement exclu.",
        "",
        "## Résultat",
        "",
        f"- PDF contrôlés : {summary['variants_scanned']} / 6",
        f"- `TEACHER_ONLY_CONTENT_LEAK` : {summary['teacher_only_content_leak_documents']} document(s)",
        f"- `PDF_METADATA_INCOMPLETE` : {summary['pdf_metadata_incomplete']} document(s)",
        f"- `PDF_NAVIGATION_MISSING` : {summary['pdf_navigation_missing']} document(s)",
        f"- Release candidate admissible : **{str(summary['release_candidate_eligible']).lower()}**",
        "",
        "## Par manuel",
        "",
    ]
    for row in payload["variants"]:
        findings = ", ".join(row["findings"]) or "PASS"
        lines.append(
            f"- `{row['manual']}` : {findings}; marqueurs={row['teacher_only_content_leak']}; "
            f"signets={row['bookmark_count']}; Title={bool(row['title'])}; Author={bool(row['author'])}."
        )
    lines.extend(
        [
            "",
            "## Décision",
            "",
            "Les PDF Math observés sont des artefacts périmés et ne peuvent pas être empaquetés. Le gate doit être rejoué après reconstruction au `FINAL_SOURCE_SHA`; seuls des builds dont la provenance correspond exactement à ce SHA peuvent devenir release candidates.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    md_text = render_markdown(payload)

    if args.check:
        mismatches = [
            str(path.relative_to(ROOT))
            for path, expected in ((OUTPUT_JSON, json_text), (OUTPUT_MD, md_text))
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        if mismatches:
            print("Artifacts out of date: " + ", ".join(mismatches))
            return 1
        print("Student PDF preflight artifacts are current")
        return 0

    if args.gate:
        findings = sorted({finding for row in payload["variants"] for finding in row["findings"]})
        if findings or not payload["summary"]["release_candidate_eligible"]:
            print("PUBLISH PREFLIGHT RED: " + ", ".join(findings or ["PROVENANCE_MISMATCH"]))
            return 1
        print("PUBLISH PREFLIGHT GREEN")
        return 0

    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_MD.write_text(md_text, encoding="utf-8")
    print("Wrote student PDF publish preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
