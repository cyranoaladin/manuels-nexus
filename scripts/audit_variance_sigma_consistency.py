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
* SIGMA_WITHOUT_ORACLE       ecart-type numerique sans variance etablie, sans
                             assertion dans le bloc BEGIN-VERIFY et sans variance
                             correspondante ailleurs dans le chapitre ;
* SIGMA_NOT_SELF_CONTAINED   ecart-type exact mais etabli dans un autre objet du
                             chapitre : observation non bloquante.

Le dernier controle est celui qui capture exactement 1SPE-VARALEA-CO-048 : une
valeur approchee affirmee dans le texte que rien ne rattache ni a une variance
ecrite, ni a l'oracle sympy de l'objet.

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
    stated_value: float
    decimals: int
    approximate: bool
    position: int
    unit: str | None
    sqrt_radicand: float | None
    exact_raw: str
    exact_value: float


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
    return [part.strip() for part in parts if part.strip()]


def _exact_segments(region: str) -> list[str]:
    """Segments anterieurs au premier \\approx : ils sont exacts, pas arrondis."""

    exact_region = re.split(r"\\approx", region)[0]
    return _segments(exact_region)


def _evaluate(segment: str) -> float | None:
    try:
        return float(evaluate(segment))
    except (UnsupportedExpression, ZeroDivisionError, OverflowError, ValueError):
        return None


def _build_claim(kind: str, text: str, match: re.Match[str]) -> Claim | None:
    region = _claim_region(text, match.end())
    segments = _segments(region)
    if not segments:
        return None
    stated_raw, stated_value = "", None
    for segment in reversed(segments):
        value = _evaluate(segment)
        if value is not None:
            stated_raw, stated_value = segment, value
            break
    if stated_value is None:
        return None

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
    )


def extract_claims(text: str) -> list[Claim]:
    claims = []
    for kind, pattern in (("variance", VARIANCE_RE), ("sigma", SIGMA_RE)):
        for match in pattern.finditer(text):
            claim = _build_claim(kind, text, match)
            if claim is not None:
                claims.append(claim)
    return sorted(claims, key=lambda claim: claim.position)


def _rounds_to(exact: float, stated: float, places: int, approximate: bool) -> bool:
    if approximate or places:
        return abs(round(exact, places) - stated) <= 0.5 * 10**-places + 1e-9
    return math.isclose(exact, stated, rel_tol=1e-9, abs_tol=1e-9)


def _oracle_mentions(verify: str, value: float, places: int) -> bool:
    """Le bloc BEGIN-VERIFY porte-t-il une trace de cette valeur ?"""

    for token in re.findall(r"\d+(?:\.\d+)?", verify):
        try:
            candidate = float(token)
        except ValueError:
            continue
        if abs(candidate - value) <= 0.5 * 10**-places + 1e-9:
            return True
        if value > 0 and abs(candidate - value**2) <= max(1.0, value**2 * 1e-9):
            return True
    return False


def chapter_variance_values(chapter_dir: Path) -> list[float]:
    """Variances exactes affirmees n'importe ou dans le chapitre."""

    values: list[float] = []
    for path in sorted(chapter_dir.rglob("*.tex")):
        text = path.read_text(encoding="utf-8")
        for claim in extract_claims(text):
            if claim.kind == "variance":
                values.append(claim.exact_value)
            elif claim.sqrt_radicand is not None:
                values.append(claim.sqrt_radicand)
    return values


def audit_object(
    path: Path, chapter_id: str, chapter_variances: list[float] | None = None
) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    meta_match = META_RE.search(text)
    object_id = json.loads(meta_match.group(1))["id"] if meta_match else path.stem
    verify_match = VERIFY_RE.search(text)
    verify = verify_match.group(1) if verify_match else ""
    body = text[verify_match.end() :] if verify_match else text

    claims = extract_claims(body)
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

    variances = [claim for claim in claims if claim.kind == "variance"]
    for sigma in (claim for claim in claims if claim.kind == "sigma"):
        # Une racine explicite est auto-portante : sqrt(radicande) est verifiable.
        if sigma.sqrt_radicand is not None:
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

        upstream = [
            claim
            for claim in variances
            if claim.position < sigma.position
            and (sigma.variable is None or claim.variable == sigma.variable)
        ]
        if not upstream:
            if _oracle_mentions(verify, sigma.stated_value, sigma.decimals):
                continue
            elsewhere = any(
                value >= 0
                and _rounds_to(math.sqrt(value), sigma.stated_value, sigma.decimals, True)
                for value in (chapter_variances or [])
            )
            if elsewhere:
                add(
                    "SIGMA_NOT_SELF_CONTAINED",
                    "P2",
                    f"ecart-type {sigma.stated_raw} exact mais etabli dans un autre objet "
                    f"du chapitre : l'objet ne porte ni variance ecrite ni oracle propre",
                )
            else:
                add(
                    "SIGMA_WITHOUT_ORACLE",
                    "P0",
                    f"ecart-type {sigma.stated_raw} affirme sans variance ecrite, sans "
                    f"assertion dans le bloc BEGIN-VERIFY et sans variance correspondante "
                    f"ailleurs dans le chapitre",
                )
            continue

        variance = upstream[-1]
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
            "SIGMA_WITHOUT_ORACLE",
            "SIGMA_NOT_SELF_CONTAINED",
        ],
        "scope_chapters": [directory.name for directory in directories],
        "findings": [asdict(finding) for finding in findings],
        "finding_count": len(findings),
        "p0_count": sum(1 for finding in findings if finding.severity == "P0"),
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
    return 1 if report["p0_count"] else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
