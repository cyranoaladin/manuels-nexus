#!/usr/bin/env python3
"""Controle machine de la classe de defaut variance / ecart-type.

La correction P0 de 1SPE-VARALEA-CO-048 (variance 15 552 000, ecart-type
3943,602..., arrondi 3 944 euros) n'est pas traitee comme un incident isole :
ce controle cherche la CLASSE du defaut dans tout le corpus mathematiques.

Defauts recherches :

* VARIANCE_SIGMA_SWAP        l'ecart-type reprend la variance sans racine ;
* ROOT_MISMATCH              variance etablie mais racine fausse ;
* ROUNDING_MISMATCH          racine correcte mais arrondi faux ;
* UNIT_ON_VARIANCE           unite portee par une variance au lieu du carre ;
* EXACT_EQUALITY_MISMATCH    maillons numeriques distincts relies par egalite ;
* SIGMA_WITHOUT_ORACLE       ecart-type sans variance locale etablie : blocker
                             de certification. Un nombre dans BEGIN-VERIFY ou
                             ailleurs dans le chapitre ne constitue pas une
                             preuve executee et liee a cette affirmation.
* UNPARSED_MATHEMATICAL_CLAIM / UNVERIFIED_VARIANCE_DEPENDENCY
                            affirmation ou dependance non verifiee : blocker
                            de certification, sans erreur produit inventee.

La presence textuelle d'un oracle n'est pas son execution, ni une preuve de son
lien semantique avec l'affirmation. Ce lecteur ne certifie aucun tel heritage.

Limite assumee : l'extraction est lexicale et ne comprend que le sous-langage
arithmetique de scripts/latex_arith.py. Elle ne remplace ni l'execution des
blocs BEGIN-VERIFY, ni la revue humaine disciplinaire.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from latex_arith import UnsupportedExpression, evaluate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MATH_CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"

META_RE = re.compile(r"^% META:\s*(\{.*\})\s*$", re.MULTILINE)
VERIFY_RE = re.compile(r"% BEGIN-VERIFY(.*?)% END-VERIFY", re.DOTALL)
VARIANCE_RE = re.compile(r"V\s*\(\s*([A-Za-z])(?:_\{?[0-9a-z]+\}?)?\s*\)\s*(?==|\\approx)")
SIGMA_RE = re.compile(
    r"\\sigma\s*(?:\(\s*([A-Za-z])(?:_\{?[0-9a-z]+\}?)?\s*\))?\s*(?==|\\approx)"
)
#: Fin d'une affirmation numerique : separateur de phrase ou de mise en forme.
TERMINATOR_RE = re.compile(r"\$|\\\\|\\quad|\\qquad|\\item|\\medskip|\n|(?<!\{),(?!\})|;")
NUMBER_ONLY_RE = re.compile(r"^[0-9][0-9\\,\s]*(?:\{,\}[0-9]+)?$")
UNIT_RE = re.compile(r"~?(euros?|€|kg|km|cm|mm)\b")
SQRT_ARG_RE = re.compile(r"\\sqrt\s*\{")


@dataclass
class Claim:
    """Une affirmation numerique lue dans le texte eleve ou professeur."""

    kind: str
    variable: str | None
    chain: str
    stated_raw: str
    stated_value: float | None
    decimals: int
    approximate: bool
    position: int
    unit: str | None
    sqrt_radicand: float | None
    exact_raw: str
    exact_value: float | None
    unparsed_segments: tuple[str, ...]


@dataclass
class Finding:
    finding_id: str
    chapter_id: str
    object_id: str
    path: str
    defect_class: str
    severity: str
    description: str


def _decimals(raw: str) -> int:
    return len(raw.split("{,}")[1]) if "{,}" in raw else 0


def _balanced_group(text: str, open_index: int) -> str | None:
    depth, index = 0, open_index
    while index < len(text):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : index]
        index += 1
    return None


def _claim_region(text: str, start: int) -> str:
    match = TERMINATOR_RE.search(text, start)
    return text[start : match.start() if match else min(len(text), start + 240)]


def _segments(region: str) -> list[str]:
    parts = re.split(r"\\approx|=", region)
    # A sentence's final full stop may be printed inside math delimiters.
    # Only that terminal punctuation is removed; the expression remains
    # subject to the complete arithmetic reader.
    return [part.strip().removesuffix(".").rstrip() for part in parts if part.strip()]


def _exact_segments(region: str) -> list[str]:
    """Segments anterieurs au premier \\approx : ils sont exacts, pas arrondis."""

    exact_region = re.split(r"\\approx", region)[0]
    return _segments(exact_region)


def _evaluate(segment: str) -> float | None:
    try:
        return float(evaluate(segment))
    except (UnsupportedExpression, ZeroDivisionError, OverflowError, ValueError):
        return None


def _build_claim(kind: str, text: str, match: re.Match[str]) -> Claim:
    region = _claim_region(text, match.end())
    segments = _segments(region)
    # Preserve every recognized assertion, including an empty or unsupported
    # right-hand side. A readable later value does not prove an unreadable
    # earlier equality in the same chain.
    unparsed = tuple(segment for segment in segments if _evaluate(segment) is None)
    if not segments:
        unparsed = (region.strip() or "<missing right-hand side>",)
    stated_raw, stated_value = segments[-1] if segments else "", None
    for segment in reversed(segments):
        value = _evaluate(segment)
        if value is not None:
            stated_raw, stated_value = segment, value
            break

    # La valeur de reference d'une chaine est sa derniere ecriture exacte :
    # comparer une racine a un arrondi intermediaire fabriquerait un faux positif.
    exact_raw, exact_value = stated_raw, stated_value
    for segment in reversed(_exact_segments(region)):
        value = _evaluate(segment)
        if value is not None:
            exact_raw, exact_value = segment, value
            break

    radicand = None
    sqrt_match = SQRT_ARG_RE.search(region)
    if sqrt_match:
        inner = _balanced_group(region, sqrt_match.end() - 1)
        if inner is not None:
            radicand = _evaluate(inner)

    tail = text[match.end() + len(region) :].lstrip().lstrip("$").lstrip()
    unit_match = UNIT_RE.match(tail)
    return Claim(
        kind=kind,
        variable=match.group(1),
        chain=region.strip(),
        stated_raw=stated_raw,
        stated_value=stated_value,
        decimals=_decimals(stated_raw),
        approximate="\\approx" in region,
        position=match.start(),
        unit=unit_match.group(1) if unit_match else None,
        sqrt_radicand=radicand,
        exact_raw=exact_raw,
        exact_value=exact_value,
        unparsed_segments=unparsed,
    )


def extract_claims(text: str) -> list[Claim]:
    claims = []
    for kind, pattern in (("variance", VARIANCE_RE), ("sigma", SIGMA_RE)):
        for match in pattern.finditer(text):
            claims.append(_build_claim(kind, text, match))
    return sorted(claims, key=lambda claim: claim.position)


def _rounds_to(exact: float, stated: float, places: int, approximate: bool) -> bool:
    if approximate or places:
        return abs(round(exact, places) - stated) <= 0.5 * 10**-places + 1e-9
    return math.isclose(exact, stated, rel_tol=1e-9, abs_tol=1e-9)


def _contradictory_equalities(chain: str) -> tuple[str, str] | None:
    """Two unequal rational values in one equality chain prove a contradiction.

    Approximation starts another chain. Unreadable links remain unverified;
    their presence does not make two distinct readable values equal.
    """
    for equalities in re.split(r"\\approx", chain):
        first = None
        for raw in _segments(equalities):
            try:
                value = evaluate(raw)
            except (UnsupportedExpression, ZeroDivisionError, OverflowError, ValueError):
                continue
            if first is None:
                first = (raw, value)
            elif first[1] != value:
                return (first[0], raw)
    return None


def chapter_variance_values(chapter_dir: Path) -> list[float]:
    """Variances exactes affirmees n'importe ou dans le chapitre."""

    values: list[float] = []
    for path in sorted(chapter_dir.rglob("*.tex")):
        text = path.read_text(encoding="utf-8")
        for claim in extract_claims(text):
            if claim.unparsed_segments or _contradictory_equalities(claim.chain):
                continue
            if claim.kind == "variance":
                values.append(claim.exact_value)
            elif claim.sqrt_radicand is not None:
                values.append(claim.sqrt_radicand)
    return values


#: Debut d'une question de QCM. Absent des autres objets : le cloisonnement
#: est alors sans effet et le fichier entier reste une seule portee.
QUESTION_RE = re.compile(r"\\item\s*\\textbf\{\[Q\d+\]\}")


def _scope_start(question_starts: list[int], position: int) -> int:
    """Debut de la portee d'appariement contenant `position`."""

    start = 0
    for boundary in question_starts:
        if boundary <= position:
            start = boundary
        else:
            break
    return start


def audit_object(
    path: Path, chapter_id: str, chapter_variances: list[float] | None = None
) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    meta_match = META_RE.search(text)
    object_id = json.loads(meta_match.group(1))["id"] if meta_match else path.stem
    verify_match = VERIFY_RE.search(text)
    body = text[verify_match.end() :] if verify_match else text

    claims = extract_claims(body)
    # Un QCM est une suite de questions independantes : une variance affirmee
    # dans une question ne dit rien d'un ecart-type affirme dans une autre.
    # Sans ce cloisonnement, la derniere variance du fichier est appariee a
    # n'importe quel sigma ulterieur et fabrique un faux P0.
    question_starts = [match.start() for match in QUESTION_RE.finditer(body)]
    findings: list[Finding] = []
    relative = (
        path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
    )

    def add(defect: str, severity: str, description: str) -> None:
        findings.append(
            Finding(
                finding_id=f"{object_id}-{defect}-{len(findings) + 1:02d}",
                chapter_id=chapter_id,
                object_id=object_id,
                path=relative,
                defect_class=defect,
                severity=severity,
                description=description,
            )
        )

    contradictory_positions: set[int] = set()
    for claim in claims:
        if claim.unparsed_segments:
            add(
                "UNPARSED_MATHEMATICAL_CLAIM", "CERTIFICATION_BLOCKER",
                f"{claim.kind}({claim.variable or '?'}) non verifiee : "
                f"segments hors du lecteur exact {list(claim.unparsed_segments)!r}. "
                "Aucune valeur de remplacement ni preuve de faussete n'est deduite.",
            )
        contradiction = _contradictory_equalities(claim.chain)
        if contradiction:
            contradictory_positions.add(claim.position)
            add(
                "EXACT_EQUALITY_MISMATCH", "P0",
                f"{claim.kind}({claim.variable or '?'}) : les expressions exactes "
                f"{contradiction[0]!r} et {contradiction[1]!r} sont reliees par "
                "egalite mais leurs valeurs rationnelles sont distinctes.",
            )

    variances = [claim for claim in claims if claim.kind == "variance"]
    for sigma in (claim for claim in claims if claim.kind == "sigma"):
        if sigma.unparsed_segments or sigma.position in contradictory_positions:
            continue
        scope_start = _scope_start(question_starts, sigma.position)
        upstream = [
            claim
            for claim in variances
            if scope_start <= claim.position < sigma.position
            and (sigma.variable is None or claim.variable == sigma.variable)
        ]
        # An explicit root can establish its own arithmetic. If a variance is
        # supplied locally, it must also agree with that variance below.
        if sigma.sqrt_radicand is not None and not upstream:
            exact = math.sqrt(sigma.sqrt_radicand) if sigma.sqrt_radicand >= 0 else float("nan")
            if not _rounds_to(exact, sigma.stated_value, sigma.decimals, sigma.approximate):
                add(
                    "ROUNDING_MISMATCH",
                    "P0",
                    f"sigma = {sigma.stated_raw} alors que la racine ecrite vaut "
                    f"{exact:.6f} (arrondi attendu "
                    f"{round(exact, sigma.decimals):.{sigma.decimals}f})",
                )
            continue

        if not upstream:
            add(
                "SIGMA_WITHOUT_ORACLE", "CERTIFICATION_BLOCKER",
                f"ecart-type {sigma.stated_raw} sans variance locale etablie. "
                "Un nombre dans BEGIN-VERIFY ou dans un autre objet ne prouve "
                "ni l'execution ni le lien semantique avec cette affirmation.",
            )
            continue

        variance = upstream[-1]
        if variance.unparsed_segments or variance.position in contradictory_positions:
            add(
                "UNVERIFIED_VARIANCE_DEPENDENCY", "CERTIFICATION_BLOCKER",
                f"sigma({sigma.variable or '?'}) = {sigma.stated_raw} depend de "
                f"la variance amont non verifiee {variance.chain!r}; une variance "
                "plus ancienne ne lui est pas substituee.",
            )
            continue
        if variance.exact_value < 0:
            add("ROOT_MISMATCH", "P0", f"variance negative affirmee : {variance.exact_raw}")
            continue
        exact = math.sqrt(variance.exact_value)
        if _rounds_to(exact, sigma.stated_value, sigma.decimals, sigma.approximate):
            continue
        if math.isclose(sigma.stated_value, variance.exact_value, rel_tol=1e-9):
            add(
                "VARIANCE_SIGMA_SWAP",
                "P0",
                f"sigma({sigma.variable or '?'}) = {sigma.stated_raw} reprend la variance "
                f"au lieu de sa racine {exact:.6f}",
            )
        elif exact > 0 and abs(sigma.stated_value - exact) / exact < 0.05:
            add(
                "ROUNDING_MISMATCH",
                "P0",
                f"sigma({sigma.variable or '?'}) = {sigma.stated_raw} alors que "
                f"sqrt({variance.exact_raw}) = {exact:.6f} (arrondi attendu "
                f"{round(exact, sigma.decimals):.{sigma.decimals}f})",
            )
        else:
            add(
                "ROOT_MISMATCH",
                "P0",
                f"sigma({sigma.variable or '?'}) = {sigma.stated_raw} incompatible avec "
                f"V({variance.variable}) = {variance.exact_raw} (racine {exact:.6f})",
            )

    for variance in variances:
        if variance.unit:
            add(
                "UNIT_ON_VARIANCE",
                "P1",
                f"V({variance.variable}) = {variance.stated_raw} porte l'unite "
                f"{variance.unit!r} : une variance s'exprime dans l'unite au carre",
            )

    return findings


def audit_chapter(chapter_dir: Path) -> list[Finding]:
    variances = chapter_variance_values(chapter_dir)
    findings: list[Finding] = []
    for path in sorted(chapter_dir.rglob("*.tex")):
        findings.extend(audit_object(path, chapter_dir.name, variances))
    return findings


def audit_corpus(chapters: list[str] | None = None) -> dict:
    directories = (
        [MATH_CHAPTERS / name for name in chapters]
        if chapters
        else sorted(path for path in MATH_CHAPTERS.iterdir() if path.is_dir())
    )
    findings: list[Finding] = []
    for directory in directories:
        findings.extend(audit_chapter(directory))
    return {
        "artifact_type": "variance_sigma_consistency_audit",
        "schema_version": 1,
        "generated_by": "scripts/audit_variance_sigma_consistency.py",
        "defect_classes": [
            "VARIANCE_SIGMA_SWAP",
            "ROOT_MISMATCH",
            "ROUNDING_MISMATCH",
            "UNIT_ON_VARIANCE",
            "EXACT_EQUALITY_MISMATCH",
            "SIGMA_WITHOUT_ORACLE",
            "SIGMA_NOT_SELF_CONTAINED",
            "UNPARSED_MATHEMATICAL_CLAIM",
            "UNVERIFIED_VARIANCE_DEPENDENCY",
        ],
        "scope_chapters": [directory.name for directory in directories],
        "findings": [asdict(finding) for finding in findings],
        "finding_count": len(findings),
        "p0_count": sum(1 for finding in findings if finding.severity == "P0"),
        "unparsed_claim_count": sum(
            finding.defect_class == "UNPARSED_MATHEMATICAL_CLAIM" for finding in findings
        ),
        "certification_blocker_count": sum(
            finding.severity == "CERTIFICATION_BLOCKER" for finding in findings
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", action="append", help="limiter a un chapitre")
    parser.add_argument("--out", help="ecrire le rapport JSON dans ce fichier")
    args = parser.parse_args(argv)

    report = audit_corpus(args.chapter)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 1 if report["p0_count"] or report["certification_blocker_count"] else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
