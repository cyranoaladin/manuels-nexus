#!/usr/bin/env python3
"""Build the exact Overfull/Underfull ledger for the observed 1SPE smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit" / "LATEX_LAYOUT_WARNING_LEDGER.json"
BUILD_SOURCE_SHA = "5d935e720a82e207d7a8769f6bd2608ef1160322"
SOURCE_FREEZE_SHA = "c667f12b1792f31981b6b5894c8c604df1bce634"

STYLE = "gabarits/common/nexus-pages-froides.sty"
GEOMETRY = (
    "Mathematiques/manuel-maths/chapitres/1SPE-GEOMETRIE-REPEREE/"
    "cours/13_C4_positions_relatives.tex"
)
VARALEA = (
    "Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/"
    "remediation/1SPE-VARALEA-FR-R2.tex"
)
SOURCE_HASHES = {
    STYLE: "4e1f7fae36ffa3b871bbe728ec9c7fcbf4b473c9f614660edb6cb057f8282bd8",
    GEOMETRY: "847f436dbe89fef7a4ec62d1a086a5589d3841cca31b06ae2902055bcdae1aa5",
    VARALEA: "92ceac6e53a53a324049d84503f90e73cefbc8df13a81e6919601946533fec29",
}

ARTIFACTS = {
    "eleve": {
        "log_path": "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.log",
        "log_sha256": "5d9012de67936afd12689e29617c744556e155c0d0ad5dfcca61d379215b3423",
        "pdf_path": "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf",
        "pdf_sha256": "8afb6144d8595359b01a4251c3241165fc9cba0302d14a60c8e2bcc1c8ae42de",
    },
    "professeur": {
        "log_path": "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.log",
        "log_sha256": "b55d98208a0f630940c79e13c06dc7072fd4b6f4a8464227384adfe813c0d50b",
        "pdf_path": "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf",
        "pdf_sha256": "70a492798fcee072fa1824dfa5adc17fb33bf596d1213a75f42f8a488c47228e",
    },
}

# variant, PDF page, rendered page number, log line, .toc line, title
TOC_ROWS = (
    ("eleve", 7, 119, 2754, 101, "Dérivation : point de vue local"),
    ("eleve", 7, 149, 2759, 137, "Dérivation : applications aux variations"),
    ("eleve", 7, 185, 2764, 174, "Fonction exponentielle"),
    ("eleve", 8, 215, 3223, 211, "Trigonométrie"),
    ("eleve", 8, 233, 3228, 244, "Produit scalaire"),
    ("eleve", 8, 258, 3233, 280, "Géométrie repérée"),
    ("eleve", 8, 283, 3238, 319, "Probabilités conditionnelles et indépendance"),
    ("eleve", 8, 311, 3243, 356, "Variables aléatoires"),
    ("eleve", 9, 345, 3248, 399, "Formulaire"),
    ("eleve", 9, 349, 3253, 400, "Mémo Python"),
    ("professeur", 7, 136, 2755, 58, "Fonctions polynômes du second degré"),
    ("professeur", 7, 238, 2760, 101, "Dérivation : point de vue local"),
    ("professeur", 7, 293, 2765, 137, "Dérivation : applications aux variations"),
    ("professeur", 7, 362, 2770, 174, "Fonction exponentielle"),
    ("professeur", 8, 416, 3229, 211, "Trigonométrie"),
    ("professeur", 8, 444, 3234, 244, "Produit scalaire"),
    ("professeur", 8, 483, 3239, 280, "Géométrie repérée"),
    ("professeur", 8, 523, 3244, 319, "Probabilités conditionnelles et indépendance"),
    ("professeur", 8, 564, 3249, 356, "Variables aléatoires"),
    ("professeur", 9, 613, 3254, 399, "Formulaire"),
    ("professeur", 9, 617, 3259, 400, "Mémo Python"),
)

# variant, object, chapter, source, range, PDF page, log line, badness, visible
UNDERFULL_ROWS = (
    (
        "eleve",
        "1SPE-GEOREP-CR-013",
        "1SPE-GEOMETRIE-REPEREE",
        GEOMETRY,
        "17-21",
        265,
        12892,
        5217,
        False,
    ),
    (
        "professeur",
        "1SPE-GEOREP-CR-013",
        "1SPE-GEOMETRIE-REPEREE",
        GEOMETRY,
        "17-21",
        491,
        21113,
        5217,
        False,
    ),
    (
        "eleve",
        "1SPE-VARALEA-FR-R2",
        "1SPE-VARIABLES-ALEATOIRES",
        VARALEA,
        "7-9",
        342,
        14813,
        2460,
        True,
    ),
    (
        "professeur",
        "1SPE-VARALEA-FR-R2",
        "1SPE-VARIABLES-ALEATOIRES",
        VARALEA,
        "7-9",
        600,
        24992,
        2460,
        True,
    ),
)


def _git_blob_sha256(revision: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def _causal_source_proofs() -> list[dict[str, Any]]:
    proofs = []
    for path, expected in SOURCE_HASHES.items():
        build_hash = _git_blob_sha256(BUILD_SOURCE_SHA, path)
        freeze_hash = _git_blob_sha256(SOURCE_FREEZE_SHA, path)
        if build_hash != expected or freeze_hash != expected:
            raise ValueError(
                f"causal source changed between observed build and freeze: {path}"
            )
        proofs.append(
            {
                "path": path,
                "sha256": expected,
                "build_source_sha": BUILD_SOURCE_SHA,
                "freeze_source_sha": SOURCE_FREEZE_SHA,
                "unchanged_from_build_to_freeze": True,
            }
        )
    return proofs


def _visual(pdf_page: int, visible: bool, observation: str) -> dict[str, Any]:
    return {
        "method": "RASTER_INSPECTION",
        "dpi": 200,
        "pdf_page": pdf_page,
        "visible_defect": visible,
        "observation": observation,
        "human_approval": False,
    }


def _artifact_fields(variant: str) -> dict[str, str]:
    evidence = ARTIFACTS[variant]
    return {
        "log_path": evidence["log_path"],
        "log_sha256": evidence["log_sha256"],
        "pdf_path": evidence["pdf_path"],
        "pdf_sha256": evidence["pdf_sha256"],
    }


def _toc_warning(index: int, row: tuple[Any, ...]) -> dict[str, Any]:
    variant, pdf_page, rendered, log_line, toc_line, title = row
    return {
        "warning_id": f"1SPE-LAYOUT-W{index:03d}",
        "manual": "1SPE",
        "chapter": "FRONT_MATTER_TOC",
        "object_id": None,
        "warning_type": "OVERFULL_HBOX",
        "variant": variant,
        "source": STYLE,
        "source_sha256": SOURCE_HASHES[STYLE],
        "source_line_range": "116-130",
        "toc_line": toc_line,
        "log_line": log_line,
        "pdf_page": pdf_page,
        "rendered_page_number": rendered,
        "title": title,
        "amount_pt": 0.95421,
        "badness": None,
        "visible": False,
        "classification": "PROJECT_TOC_PAGE_NUMBER_BOX_NONVISIBLE",
        "actionable": True,
        "resolution_state": "OPEN",
        "owner_phase": "STYLE_CANONICALISATION",
        "release_relevance": "GLOBAL_LAYOUT_LOG_CLEANLINESS",
        "visual_inspection": _visual(
            pdf_page,
            False,
            "No clipping, collision, or visible overflow at the TOC page-number box.",
        ),
        **_artifact_fields(variant),
    }


def _underfull_warning(index: int, row: tuple[Any, ...]) -> dict[str, Any]:
    variant, object_id, chapter, source, line_range, pdf_page, log_line, badness, visible = row
    if visible:
        classification = "VISIBLE_FORMULA_LINEBREAK_DEFECT"
        observation = (
            "The P(A)= prefix is isolated at the right edge and the summation begins "
            "on the following line; the defect is visible."
        )
    else:
        classification = "INSPECTED_NONVISIBLE_JUSTIFICATION_DEFECT"
        observation = "No visible spacing, clipping, or collision defect on the rendered page."
    return {
        "warning_id": f"1SPE-LAYOUT-W{index:03d}",
        "manual": "1SPE",
        "chapter": chapter,
        "object_id": object_id,
        "warning_type": "UNDERFULL_HBOX",
        "variant": variant,
        "source": source,
        "source_sha256": SOURCE_HASHES[source],
        "source_line_range": line_range,
        "toc_line": None,
        "log_line": log_line,
        "pdf_page": pdf_page,
        "rendered_page_number": None,
        "title": None,
        "amount_pt": None,
        "badness": badness,
        "visible": visible,
        "classification": classification,
        "actionable": True,
        "resolution_state": "OPEN",
        "owner_phase": (
            "WAVE_1SPE_VARIABLES_ALEATOIRES"
            if chapter == "1SPE-VARIABLES-ALEATOIRES"
            else "WAVE_1SPE_GEOMETRIE_REPEREE"
        ),
        "release_relevance": "GLOBAL_LAYOUT_LOG_CLEANLINESS",
        "visual_inspection": _visual(pdf_page, visible, observation),
        **_artifact_fields(variant),
    }


def build_ledger() -> dict[str, Any]:
    warnings = [
        *(_toc_warning(index, row) for index, row in enumerate(TOC_ROWS, 1)),
        *(
            _underfull_warning(index, row)
            for index, row in enumerate(UNDERFULL_ROWS, len(TOC_ROWS) + 1)
        ),
    ]
    return {
        "artifact_type": "latex_layout_warning_ledger",
        "scope": "OVERFULL_UNDERFULL",
        "scope_warning": (
            "This exact 25-row scope does not prove all LaTeX warning families classified; "
            "the named out-of-scope families require separate triage."
        ),
        "build_source_sha": BUILD_SOURCE_SHA,
        "applicable_source_freeze_sha": SOURCE_FREEZE_SHA,
        "summary": {
            "total": 25,
            "overfull": 21,
            "underfull": 4,
            "visible_overfull": 0,
            "visible_underfull": 2,
            "unclassified": 0,
            "unknown": 0,
            "by_variant": {"eleve": 12, "professeur": 13},
        },
        "evidence": {
            "artifacts": ARTIFACTS,
            "artifact_hash_semantics": (
                "Hashes identify the observed build outputs; mutable build paths are not "
                "asserted to retain those bytes after the observation."
            ),
            "visual_inspection": {
                "method": "PDF_RASTER",
                "dpi": 200,
                "pages_inspected": {
                    "eleve": [7, 8, 9, 265, 342],
                    "professeur": [7, 8, 9, 491, 599, 600],
                },
                "human_approval": False,
            },
        },
        "causal_source_proofs": _causal_source_proofs(),
        "warnings": warnings,
        "out_of_scope_warning_families": [
            {
                "family": "TYPEAREA_WARNING",
                "eleve_count": 1,
                "professeur_count": 1,
                "status": "REQUIRES_SEPARATE_TRIAGE",
            },
            {
                "family": "SCRLAYER_FOOTHEIGHT_TOO_LOW",
                "eleve_count": 3,
                "professeur_count": 3,
                "status": "REQUIRES_SEPARATE_TRIAGE",
            },
            {
                "family": "PDF_BACKEND_POP_EMPTY_COLOR_PAGE_STACK",
                "eleve_count": 943,
                "professeur_count": 3008,
                "status": "REQUIRES_SEPARATE_TRIAGE",
            },
            {
                "family": "MICROTYPE_MISSING_CHARACTER_INFO",
                "eleve_count": 1888,
                "professeur_count": 1913,
                "status": "INFORMATION_NOT_WARNING_REQUIRES_SEPARATE_REVIEW",
            },
        ],
    }


def validate_ledger(payload: dict[str, Any]) -> None:
    expected = build_ledger()
    if payload != expected:
        raise ValueError("layout warning ledger differs from exact observed evidence")

    warnings = payload["warnings"]
    if len(warnings) != 25 or len({row["warning_id"] for row in warnings}) != 25:
        raise ValueError("layout warning ledger must contain 25 unique rows")
    types = Counter(row["warning_type"] for row in warnings)
    if types != {"OVERFULL_HBOX": 21, "UNDERFULL_HBOX": 4}:
        raise ValueError("layout warning ledger partition is not 21+4")
    if any("UNKNOWN" in row["classification"] for row in warnings):
        raise ValueError("UNKNOWN classifications are forbidden")
    if any(row["classification"] == "BENIGN_SMALL_AMOUNT" for row in warnings):
        raise ValueError("small magnitude is not a visual classification")
    if any(not row["visual_inspection"] for row in warnings):
        raise ValueError("every warning requires visual inspection evidence")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the fixed ledger is stale")
    args = parser.parse_args()

    payload = build_ledger()
    validate_ledger(payload)
    rendered = render_json(payload)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
    else:
        _write_atomic(OUTPUT, rendered)
    print("PASS: 21 Overfull + 4 Underfull; visible=2; UNKNOWN=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
