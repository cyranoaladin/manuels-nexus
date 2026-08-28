#!/usr/bin/env python3
"""Build the evidence-first scientific answer-key audit for Math QCMs.

Structural validity is not scientific validation.  Every source question is
inventoried, but a PASS/FAIL is emitted only when an independent checker is
registered for that exact chapter/question pair.  All other rows remain
CONTENT_REVIEW_PENDING.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QCM_ROOT = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
JSON_TARGET = ROOT / "audit" / "QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"
MD_TARGET = ROOT / "audit" / "QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.md"


def _manual(chapter: str) -> str:
    if chapter.startswith("1SPE-"):
        return "1SPE"
    if chapter.startswith("TSPE-"):
        return "TSPE"
    if chapter.startswith("TCOMPL-"):
        return "TCOMPL"
    if chapter.startswith("TEXP-"):
        return "TEXPERTES"
    return "OTHER_EXPLICIT"


def _git_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _source_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _options(question: dict[str, Any]) -> dict[str, str]:
    raw = question.get("options")
    if isinstance(raw, dict):
        return {str(key): str(value) for key, value in raw.items()}
    if isinstance(raw, list):
        return {chr(65 + index): str(value) for index, value in enumerate(raw)}
    return {}


def _diagnostic_structure(question: dict[str, Any]) -> tuple[str, list[str]]:
    options = _options(question)
    diagnostics = question.get("diagnostics") or {}
    declared = question.get("correcte")
    issues: list[str] = []
    if declared not in options:
        issues.append("DECLARED_ANSWER_NOT_IN_OPTIONS")
    if declared in diagnostics:
        issues.append("CORRECT_ANSWER_HAS_ERROR_DIAGNOSTIC")
    for letter in options:
        if letter == declared:
            continue
        diagnostic = diagnostics.get(letter)
        if not isinstance(diagnostic, dict):
            issues.append(f"{letter}:DIAGNOSTIC_MISSING")
            continue
        if not str(diagnostic.get("erreur", "")).strip():
            issues.append(f"{letter}:ERROR_EXPLANATION_EMPTY")
        elif "consulter le cours" in str(diagnostic.get("erreur", "")).casefold():
            issues.append(f"{letter}:GENERIC_DIAGNOSTIC")
        if not str(diagnostic.get("renvoi", "")).strip():
            issues.append(f"{letter}:REMEDIATION_REFERENCE_EMPTY")
    return ("PASS" if not issues else "FAIL", issues)


def _check_second_degree_q16(question: dict[str, Any]) -> dict[str, Any]:
    expected_value = 4 * (30 - 2 * 4) * (20 - 2 * 4)
    options = _options(question)
    matches = [
        letter
        for letter, wording in options.items()
        if re.search(rf"V\(4\)\s*=\s*{expected_value}(?:\D|$)", wording)
    ]
    if len(matches) > 1:
        status = "FAIL"
        failure = "MULTIPLE_CORRECT_OPTIONS"
        correct_answer = None
    elif not matches:
        status = "FAIL"
        failure = "NO_CORRECT_OPTION"
        correct_answer = None
    else:
        correct_answer = matches[0]
        status = "PASS" if question.get("correcte") == correct_answer else "FAIL"
        failure = None if status == "PASS" else "WRONG_ANSWER_KEY"

    structural_status, structural_issues = _diagnostic_structure(question)
    diagnostics = question.get("diagnostics") or {}
    expected_evidence = {
        "A": ("1664", "2x"),
        "B": ("2400", "dimensions"),
        "C": ("264", "hauteur"),
    }
    scientific_issues = list(structural_issues)
    for letter, snippets in expected_evidence.items():
        explanation = str((diagnostics.get(letter) or {}).get("erreur", ""))
        if not all(snippet in explanation for snippet in snippets):
            scientific_issues.append(f"{letter}:DIAGNOSTIC_NOT_TIED_TO_DISTRACTOR")
    diagnostic_consistency = (
        "PASS" if structural_status == "PASS" and not scientific_issues else "FAIL"
    )
    return {
        "independent_recalculation": "4 * (30 - 2*4) * (20 - 2*4) = 1056",
        "correct_answer": correct_answer,
        "answer_key_status": status,
        "answer_key_failure": failure,
        "diagnostic_consistency": diagnostic_consistency,
        "diagnostic_details": scientific_issues,
        "review_status": "INDEPENDENT_RECALCULATION_COMPLETE_HUMAN_APPROVAL_PENDING",
    }


def _check_registered_case(
    question: dict[str, Any],
    *,
    correct_answer: str,
    independent_recalculation: str,
    initial_failure: str,
    required_fragments: tuple[str, ...] = (),
    required_option_fragments: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, Any]:
    serialized = json.dumps(question, ensure_ascii=False)
    missing_fragments = [fragment for fragment in required_fragments if fragment not in serialized]
    options = _options(question)
    option_fragment_issues = [
        f"{letter}:OPTION_FRAGMENT_MISSING:{fragment}"
        for letter, fragments in (required_option_fragments or {}).items()
        for fragment in fragments
        if fragment not in options.get(letter, "")
    ]
    diagnostic_only_failure = initial_failure == "INVALID_DISTRACTOR_DIAGNOSTIC"
    if question.get("correcte") != correct_answer:
        answer_key_status = "FAIL"
        answer_key_failure = "WRONG_ANSWER_KEY"
    elif (missing_fragments or option_fragment_issues) and not diagnostic_only_failure:
        answer_key_status = "FAIL"
        answer_key_failure = initial_failure
    else:
        answer_key_status = "PASS"
        answer_key_failure = None

    structural_status, structural_issues = _diagnostic_structure(question)
    diagnostic_issues = list(structural_issues)
    if diagnostic_only_failure:
        diagnostic_issues.extend(
            f"MISSING_CORRECTED_SOURCE_FRAGMENT:{item}" for item in missing_fragments
        )
        diagnostic_issues.extend(option_fragment_issues)
    diagnostics = question.get("diagnostics") or {}
    for letter in _options(question):
        if letter == correct_answer:
            continue
        explanation = str((diagnostics.get(letter) or {}).get("erreur", "")).strip()
        normalized = explanation.casefold()
        if "consulter le cours" in normalized or "option incorrecte" in normalized:
            diagnostic_issues.append(f"{letter}:GENERIC_DIAGNOSTIC")
        elif len(explanation) < 40:
            diagnostic_issues.append(f"{letter}:DIAGNOSTIC_TOO_SHORT_FOR_ERROR_MODEL")
    diagnostic_consistency = (
        "PASS" if structural_status == "PASS" and not diagnostic_issues else "FAIL"
    )
    return {
        "independent_recalculation": independent_recalculation,
        "correct_answer": correct_answer,
        "answer_key_status": answer_key_status,
        "answer_key_failure": answer_key_failure,
        "diagnostic_consistency": diagnostic_consistency,
        "diagnostic_details": diagnostic_issues
        + [f"MISSING_CORRECTED_SOURCE_FRAGMENT:{item}" for item in missing_fragments],
        "review_status": "INDEPENDENT_RECALCULATION_COMPLETE_HUMAN_APPROVAL_PENDING",
    }


REVIEW_CASES: dict[tuple[str, str], dict[str, Any]] = {
    ("1SPE-SUITES", "Q1"): {
        "correct_answer": "A",
        "independent_recalculation": "u_3=2*3^2-3*3+1=18-9+1=10.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("1SPE-SUITES", "Q9"): {
        "correct_answer": "B",
        "independent_recalculation": "Definition: u_(n+1)=q*u_n permits q=0 and zero terms; quotient characterization is conditional.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("1SPE-SUITES", "Q19"): {
        "correct_answer": "C",
        "independent_recalculation": "Starting at 2, three loop iterations give 7, 22, then 67.",
        "initial_failure": "NO_CORRECT_OPTION",
        "required_fragments": ("$67$",),
    },
    ("1SPE-SUITES", "Q4"): {
        "correct_answer": "C",
        "independent_recalculation": "u_(n+1)-u_n=4, while u_0=-7 and u_1=-3.",
        "initial_failure": "INVALID_DISTRACTOR_DIAGNOSTIC",
        "required_fragments": ("donc la difference vaut $4$",),
    },
    ("1SPE-SUITES", "Q11"): {
        "correct_answer": "B",
        "independent_recalculation": "1+3+9+27+81=(3^5-1)/(3-1)=121.",
        "initial_failure": "INVALID_DISTRACTOR_DIAGNOSTIC",
        "required_fragments": ("double de la somme correcte",),
        "required_option_fragments": {"D": ("$10$",)},
    },
    ("1SPE-EXPONENTIELLE", "Q1"): {
        "correct_answer": "B",
        "independent_recalculation": "f'=f and f(0)=1 uniquely defines exp; f(1)=e was an equivalent second option.",
        "initial_failure": "MULTIPLE_CORRECT_OPTIONS",
        "required_fragments": ("f(1) = 1",),
    },
    ("1SPE-GEOMETRIE-REPEREE", "Q5"): {
        "correct_answer": "B",
        "independent_recalculation": "(2,5) dot (-5,2)=0; opposite vector (5,-2) was also a director.",
        "initial_failure": "MULTIPLE_CORRECT_OPTIONS",
        "required_fragments": ("(2 ; -5)",),
    },
    ("1SPE-PROBA-COND", "Q8"): {
        "correct_answer": "D",
        "independent_recalculation": "P(A)=1/3*1/2+2/3*1/4=1/3.",
        "initial_failure": "MULTIPLE_CORRECT_OPTIONS",
        "required_fragments": ("$1/4$", "$1/6$", "$1/3$"),
    },
    ("1SPE-PROBA-COND", "Q17"): {
        "correct_answer": "C",
        "independent_recalculation": "With sensitivity=specificity=99% and prevalence 0.1%, PPV=0.00099/(0.00099+0.00999) about 9.0%.",
        "initial_failure": "NO_CORRECT_OPTION",
        "required_fragments": ("specificite de 99", "proche de 9"),
    },
    ("1SPE-PRODUIT-SCALAIRE", "Q8"): {
        "correct_answer": "B",
        "independent_recalculation": "(2,3) dot (3,-2)=0; both norms were also sqrt(13).",
        "initial_failure": "MULTIPLE_CORRECT_OPTIONS",
        "required_fragments": ("normes differentes",),
    },
    ("1SPE-DERIVATION-GLOBAL", "Q8"): {
        "correct_answer": "C",
        "independent_recalculation": "f'<0 on an interval implies f is strictly decreasing there.",
        "initial_failure": "INVALID_DISTRACTOR_DIAGNOSTIC",
        "required_fragments": ("pas sur la convexite",),
    },
    ("1SPE-DERIVATION-GLOBAL", "Q9"): {
        "correct_answer": "C",
        "independent_recalculation": "A derivative sign change from + to - gives a local maximum.",
        "initial_failure": "INVALID_DISTRACTOR_DIAGNOSTIC",
        "required_fragments": ("comportement de $f$",),
    },
    ("1SPE-SECOND-DEGRE", "Q3"): {
        "correct_answer": "A",
        "independent_recalculation": "3(x-1)^2+5=3x^2-6x+8.",
        "initial_failure": "INVALID_DISTRACTOR_DIAGNOSTIC",
        "required_fragments": ("omet le terme lineaire",),
    },
    ("1SPE-SECOND-DEGRE", "Q7"): {
        "correct_answer": "A",
        "independent_recalculation": "Delta=(-5)^2-4*1*6=1.",
        "initial_failure": "INVALID_DISTRACTOR_DIAGNOSTIC",
        "required_fragments": ("obtenir $-11$",),
    },
    ("TSPE-DERIVATION-CONVEXITE", "Q3"): {
        "correct_answer": "B",
        "independent_recalculation": "d/dx[(3x-2)^4]=12(3x-2)^3; options B and D were identical.",
        "initial_failure": "MULTIPLE_CORRECT_OPTIONS",
        "required_fragments": ("12(3x-2)^4",),
    },
    ("TSPE-DERIVATION-CONVEXITE", "Q6"): {
        "correct_answer": "B",
        "independent_recalculation": "f'=3(x-1)(x+1): local maximum at -1 and local minimum at 1.",
        "initial_failure": "WRONG_ANSWER_KEY",
        "required_fragments": ("maximum en $x = -1$",),
    },
    ("TSPE-DERIVATION-CONVEXITE", "Q15"): {
        "correct_answer": "A",
        "independent_recalculation": "exp(0.1)=1.105170... > 1.1, so the tangent approximation is below the curve.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-GEOMETRIE-ESPACE", "Q1"): {
        "correct_answer": "C",
        "independent_recalculation": "Two nonparallel space lines are either intersecting or skew.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-GEOMETRIE-ESPACE", "Q2"): {
        "correct_answer": "B",
        "independent_recalculation": "Orthogonality is equivalent to u dot v = 0.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-GEOMETRIE-ESPACE", "Q3"): {
        "correct_answer": "A",
        "independent_recalculation": "A normal is proportional to (2,-3,1); the former option D was its opposite.",
        "initial_failure": "MULTIPLE_CORRECT_OPTIONS",
        "required_fragments": ("(-2,3,1)",),
    },
    ("TSPE-GEOMETRIE-ESPACE", "Q4"): {
        "correct_answer": "A",
        "independent_recalculation": "An affine line has one scalar parameter in a parametric representation.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-GEOMETRIE-ESPACE", "Q5"): {
        "correct_answer": "B",
        "independent_recalculation": "The orthogonal projection minimizes distance to the plane.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-LOGARITHME", "Q1"): {
        "correct_answer": "B",
        "independent_recalculation": "ln(2x)=ln(2)+ln(x) for x>0.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-LOGARITHME", "Q2"): {
        "correct_answer": "B",
        "independent_recalculation": "d/dx ln(5x+1)=5/(5x+1).",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-LOGARITHME", "Q3"): {
        "correct_answer": "C",
        "independent_recalculation": "lim_(x->+infinity) ln(x)=+infinity.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-LOGARITHME", "Q4"): {
        "correct_answer": "B",
        "independent_recalculation": "lim_(x->0+) x*ln(x)=0.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-LOGARITHME", "Q5"): {
        "correct_answer": "B",
        "independent_recalculation": "Apply ln to exp(2x)=7, giving 2x=ln(7).",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-PRIMITIVES-EQDIFF", "Q1"): {
        "correct_answer": "C",
        "independent_recalculation": "d/dx[(1/3)exp(3x)]=exp(3x).",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-PRIMITIVES-EQDIFF", "Q2"): {
        "correct_answer": "C",
        "independent_recalculation": "(F-G)'=0 on an interval, hence F-G is constant.",
        "initial_failure": "MULTIPLE_CORRECT_OPTIONS",
        "required_option_fragments": {"B": ("pente non nulle",)},
    },
    ("TSPE-PRIMITIVES-EQDIFF", "Q3"): {
        "correct_answer": "B",
        "independent_recalculation": "Solutions of y'=5y are y=C*exp(5x).",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-PRIMITIVES-EQDIFF", "Q4"): {
        "correct_answer": "A",
        "independent_recalculation": "For a constant solution, 0=3*y_0-12, hence y_0=4.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-PRIMITIVES-EQDIFF", "Q5"): {
        "correct_answer": "B",
        "independent_recalculation": "First verify y_p'=a*y_p+f before using the particular solution.",
        "initial_failure": "WRONG_ANSWER_KEY",
    },
    ("TSPE-PROBABILITES", "Q4"): {
        "correct_answer": "A",
        "independent_recalculation": "Var(X+Y)=Var(X)+Var(Y)+2Cov(X,Y); equality iff Cov(X,Y)=0.",
        "initial_failure": "NO_CORRECT_OPTION",
        "required_fragments": ("Cov(X,Y)=0", "necessaire et suffisante"),
    },
    ("TSPE-TRIGONOMETRIE", "Q5"): {
        "correct_answer": "B",
        "independent_recalculation": "A maximum on a closed interval requires checking interior critical points and endpoints.",
        "initial_failure": "NO_CORRECT_OPTION",
        "required_fragments": ("ainsi que les bornes",),
    },
    ("TEXP-GRAPHES", "Q3"): {
        "correct_answer": "A",
        "independent_recalculation": "A connected graph has an Euler trail iff it has 0 or 2 odd-degree vertices.",
        "initial_failure": "NO_CORRECT_OPTION",
        "required_fragments": ("graphe connexe",),
    },
    ("TSPE-CONTINUITE", "Q4"): {
        "correct_answer": "C",
        "independent_recalculation": "Strict monotonicity on each branch plus IVT gives exactly one level-3 solution per branch.",
        "initial_failure": "NO_CORRECT_OPTION",
        "required_fragments": ("strictement",),
    },
    ("TSPE-SUITES-LIMITES", "Q6"): {
        "correct_answer": "B",
        "independent_recalculation": "With v_n=u_n-30, v_(n+1)=0.7*v_n, so the ratio is 0.7.",
        "initial_failure": "NO_CORRECT_OPTION",
        "required_fragments": ("v_n=u_n-30",),
    },
}


def _registered_checker(spec: dict[str, Any]):
    return lambda question: _check_registered_case(question, **spec)


CHECKERS = {("1SPE-SECOND-DEGRE", "Q16"): _check_second_degree_q16}
CHECKERS.update({key: _registered_checker(spec) for key, spec in REVIEW_CASES.items()})


def build_audit() -> dict[str, Any]:
    source_paths = sorted(QCM_ROOT.glob("*/qcm/*-QCM.json"))
    rows: list[dict[str, Any]] = []
    for path in source_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        chapter = data["chapitre"]
        for question in data["questions"]:
            structural_status, structural_issues = _diagnostic_structure(question)
            row: dict[str, Any] = {
                "question_id": question["id"],
                "manual": _manual(chapter),
                "chapter": chapter,
                "capacity": question.get("capacite"),
                "declared_correct_answer": question.get("correcte"),
                "independent_recalculation": None,
                "correct_answer": None,
                "answer_key_status": "CONTENT_REVIEW_PENDING",
                "answer_key_failure": None,
                "diagnostic_consistency": "CONTENT_REVIEW_PENDING",
                "diagnostic_details": [],
                "diagnostic_structural_status": structural_status,
                "diagnostic_structural_details": structural_issues,
                "review_status": "SCIENTIFIC_REVIEW_PENDING",
                "source_path": str(path.relative_to(ROOT)),
            }
            checker = CHECKERS.get((chapter, question["id"]))
            if checker is not None:
                row.update(checker(question))
            rows.append(row)

    reviewed = [row for row in rows if row["answer_key_status"] != "CONTENT_REVIEW_PENDING"]
    objective_failures = Counter(
        row["answer_key_failure"] for row in reviewed if row["answer_key_failure"]
    )
    invalid_diagnostics = sum(
        row["diagnostic_consistency"] == "FAIL" for row in reviewed
    )
    pending = sum(row["answer_key_status"] == "CONTENT_REVIEW_PENDING" for row in rows)
    known_invalid_diagnostic_entries = {
        (row["chapter"], row["question_id"], issue.split(":", 1)[0])
        for row in rows
        for issue in row["diagnostic_structural_details"]
        if len(issue.split(":", 1)[0]) == 1
        and issue.split(":", 1)[0].isalpha()
    }
    questions_with_known_invalid_diagnostics = sum(
        row["diagnostic_structural_status"] == "FAIL" for row in rows
    )
    manuals = Counter(row["manual"] for row in rows)
    return {
        "schema_version": 1,
        "artifact_name": "QCM_SCIENTIFIC_ANSWER_KEY_AUDIT",
        "status": "IN_PROGRESS" if pending else "COMPLETE",
        "base_git_sha": _git_sha(),
        "qcm_source_digest": _source_digest(source_paths),
        "methodology": {
            "json_is_canonical": True,
            "structural_validation_is_scientific_validation": False,
            "pass_requires_independent_recalculation": True,
            "unreviewed_state": "CONTENT_REVIEW_PENDING",
            "human_approval_required_for_critical_corrections": True,
        },
        "summary": {
            "qcm_files": len(source_paths),
            "total_questions": len(rows),
            "questions_by_manual": dict(sorted(manuals.items())),
            "independently_recalculated": len(reviewed),
            "content_review_pending": pending,
            "known_invalid_distractor_diagnostic_entries": len(
                known_invalid_diagnostic_entries
            ),
            "questions_with_known_invalid_distractor_diagnostics": (
                questions_with_known_invalid_diagnostics
            ),
            "objective_counters": {
                "scope": "INDEPENDENTLY_RECALCULATED_QUESTIONS_ONLY",
                "WRONG_ANSWER_KEY": objective_failures["WRONG_ANSWER_KEY"],
                "MULTIPLE_CORRECT_OPTIONS": objective_failures["MULTIPLE_CORRECT_OPTIONS"],
                "NO_CORRECT_OPTION": objective_failures["NO_CORRECT_OPTION"],
                "INVALID_DISTRACTOR_DIAGNOSTIC": invalid_diagnostics,
            },
            "scientific_zero_claim_authorized": pending == 0
            and not objective_failures
            and invalid_diagnostics == 0,
        },
        "questions": rows,
    }


def render_json(audit: dict[str, Any]) -> str:
    return json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(audit: dict[str, Any]) -> str:
    summary = audit["summary"]
    counters = summary["objective_counters"]
    pending_by_chapter = Counter(
        row["chapter"]
        for row in audit["questions"]
        if row["answer_key_status"] == "CONTENT_REVIEW_PENDING"
    )
    reviewed_rows = [
        row for row in audit["questions"] if row["answer_key_status"] != "CONTENT_REVIEW_PENDING"
    ]
    lines = [
        "# QCM SCIENTIFIC ANSWER KEY AUDIT",
        "",
        f"Status: **{audit['status']}**",
        "",
        "This audit never equates structural validity with scientific correctness. "
        "A question remains `CONTENT_REVIEW_PENDING` until an independent recalculation "
        "or proof has been recorded.",
        "",
        "## Summary",
        "",
        f"- QCM JSON files: {summary['qcm_files']}",
        f"- Questions inventoried: {summary['total_questions']}",
        f"- Independently recalculated: {summary['independently_recalculated']}",
        f"- Content review pending: {summary['content_review_pending']}",
        f"- Known invalid distractor diagnostic entries: {summary['known_invalid_distractor_diagnostic_entries']}",
        f"- Questions with known invalid distractor diagnostics: {summary['questions_with_known_invalid_distractor_diagnostics']}",
        f"- Scientific zero claim authorized: {str(summary['scientific_zero_claim_authorized']).upper()}",
        f"- WRONG_ANSWER_KEY (reviewed scope): {counters['WRONG_ANSWER_KEY']}",
        f"- MULTIPLE_CORRECT_OPTIONS (reviewed scope): {counters['MULTIPLE_CORRECT_OPTIONS']}",
        f"- NO_CORRECT_OPTION (reviewed scope): {counters['NO_CORRECT_OPTION']}",
        f"- INVALID_DISTRACTOR_DIAGNOSTIC (reviewed scope): {counters['INVALID_DISTRACTOR_DIAGNOSTIC']}",
        "",
        "## Independently recalculated questions",
        "",
        "| Manual | Chapter | Question | Declared | Recalculation | Correct | Key | Diagnostics | Review state |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in reviewed_rows:
        lines.append(
            f"| {row['manual']} | {row['chapter']} | {row['question_id']} | "
            f"{row['declared_correct_answer']} | {row['independent_recalculation']} | "
            f"{row['correct_answer']} | {row['answer_key_status']} | "
            f"{row['diagnostic_consistency']} | {row['review_status']} |"
        )
    lines.extend(["", "## Pending scientific review by chapter", ""])
    for chapter, count in sorted(pending_by_chapter.items()):
        lines.append(f"- `{chapter}`: {count}")
    lines.extend(
        [
            "",
            "The complete per-question evidence, including capacity and source path, is in "
            "`audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    args = parser.parse_args()
    audit = build_audit()
    expected = {JSON_TARGET: render_json(audit), MD_TARGET: render_markdown(audit)}
    if args.check:
        stale = [path for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"STALE_OR_MISSING: {path.relative_to(ROOT)}")
            return 1
        print(f"QCM scientific audit current: {audit['summary']['total_questions']} questions")
        return 0
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
