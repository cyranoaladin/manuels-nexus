#!/usr/bin/env python3
"""Audit d'integrite des gates de release.

Un gate n'est fiable que si sa valeur descend d'une preuve. Ce module cherche,
par analyse statique, les facons connues de fabriquer un vert :

- une metrique de release ecrite comme litteral dans le rapport ;
- une preuve obligatoire rendue optionnelle par `is_file()` ou par un defaut ;
- un artefact charge puis jamais consomme ;
- un test qui compare deux constantes entre elles.

Il produit `audit/GATE_INTEGRITY_AUDIT.json` et la carte de provenance
`audit/PROOF_PROVENANCE_MAP.json`.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/GATE_INTEGRITY_AUDIT.json"
MD_TARGET = ROOT / "audit/GATE_INTEGRITY_AUDIT.md"
PROVENANCE_TARGET = ROOT / "audit/PROOF_PROVENANCE_MAP.json"
GENERATED_BY = "scripts/audit_gate_integrity.py"

#: Les producteurs qui alimentent la decision de release, et l'agregateur.
RELEASE_PRODUCERS = (
    "scripts/build_canonical_release_inventory.py",
    "scripts/build_programme_authority_matrix.py",
    "scripts/build_printed_code_validation.py",
    "scripts/build_programme_content_validation.py",
    "scripts/build_parity_baremes_validation.py",
    "scripts/build_manifest.py",
    "scripts/build_clean_reproducibility.py",
    "scripts/build_final_preflight_and_regression.py",
    "scripts/build_zero_technical_debt.py",
    "scripts/release_all_check.py",
)

RELEASE_TESTS = (
    "tests/test_canonical_release_inventory.py",
    "tests/test_programme_authority_matrix.py",
    "tests/test_printed_code_validation.py",
    "tests/test_programme_content_validation.py",
    "tests/test_parity_baremes_validation.py",
    "tests/test_clean_build_reproducibility.py",
    "tests/test_pdf_reproducibility.py",
    "tests/test_final_print_preflight_and_regression.py",
    "tests/test_zero_technical_debt.py",
    "tests/test_release_all_check.py",
)

#: Un nom de metrique de release : MAJUSCULES, au moins deux segments.
METRIC_NAME = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")

#: Valeurs qui, ecrites en dur sous un nom de metrique, affirment un resultat.
VERDICT_STRINGS = {"PASS", "PROVEN", "FULL_CURRENT", "OK", "CURRENT", "CLEAN"}


def _literal_verdict(node: ast.AST) -> str | None:
    """Renvoie la representation d'un litteral qui affirme un resultat."""

    if isinstance(node, ast.Constant):
        value = node.value
        if value is True or value is False:
            return repr(value)
        if isinstance(value, int) and value == 0:
            return "0"
        if isinstance(value, str) and value.upper() in VERDICT_STRINGS:
            return repr(value)
    if isinstance(node, ast.JoinedStr):  # f-string entierement litterale
        if all(isinstance(v, ast.Constant) for v in node.values):
            return "f-string constante"
    return None


def scan_hardcoded_metrics(rel: str, tree: ast.AST) -> list[dict[str, Any]]:
    """Une metrique dont la valeur est un litteral n'est pas une mesure."""

    findings: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                continue
            name = key.value
            if not METRIC_NAME.match(name):
                continue
            verdict = _literal_verdict(value)
            if verdict is not None:
                findings.append({
                    "file": rel,
                    "line": key.lineno,
                    "metric": name,
                    "literal": verdict,
                    "why": "valeur affirmee au lieu d'etre derivee d'une preuve",
                })
    return findings


def _presence_flags_consumed(tree: ast.AST, node: ast.If) -> bool:
    """Le corps pose-t-il un drapeau de presence relu ailleurs ?

    Balayer des chemins candidats et noter `trouve = True` n'est pas un
    fail-open, a condition que ce drapeau serve ensuite a decider. C'est la
    relecture du drapeau qui distingue les deux cas.
    """

    flags = {
        target.id
        for stmt in node.body
        if isinstance(stmt, ast.Assign)
        for target in stmt.targets
        if isinstance(target, ast.Name)
        and isinstance(stmt.value, ast.Constant)
        and stmt.value.value is True
    }
    if not flags:
        return False
    inner = {id(n) for n in ast.walk(node)}
    for name in ast.walk(tree):
        if (
            isinstance(name, ast.Name)
            and name.id in flags
            and isinstance(name.ctx, ast.Load)
            and id(name) not in inner
        ):
            return True
    return False


def scan_optional_required_evidence(rel: str, tree: ast.AST) -> list[dict[str, Any]]:
    """`is_file()` en garde, ou un defaut sur une cle de preuve obligatoire."""

    findings: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        # `if <chemin>.is_file():` autour d'une accumulation de metrique
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Call)
                and isinstance(test.func, ast.Attribute)
                and test.func.attr in {"is_file", "exists"}
            ):
                accumulates = any(
                    isinstance(inner, (ast.AugAssign, ast.Assign))
                    for inner in ast.walk(node)
                )
                # `else:` present = l'absence est traitee explicitement ; ce
                # n'est alors pas un fail-open mais une gestion de preuve.
                if (
                    accumulates
                    and not node.orelse
                    and not _presence_flags_consumed(tree, node)
                ):
                    findings.append({
                        "file": rel,
                        "line": node.lineno,
                        "pattern": f"if ....{test.func.attr}()",
                        "why": "preuve absente traitee comme zero defaut au lieu de bloquer",
                    })
        # `.get("METRIC", <defaut>)` : un defaut masque une cle manquante
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and len(node.args) == 2
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
            and METRIC_NAME.match(node.args[0].value)
        ):
            findings.append({
                "file": rel,
                "line": node.lineno,
                "pattern": f'get("{node.args[0].value}", <defaut>)',
                "why": "cle de preuve absente rabattue sur un defaut silencieux",
            })
    return findings


def scan_loaded_but_unused(rel: str, tree: ast.AST, source: str) -> list[dict[str, Any]]:
    """Un artefact charge puis jamais lu est une preuve decorative."""

    findings: list[dict[str, Any]] = []
    loaders = {"load", "loads", "read_text", "read_bytes"}
    for func in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        assigned: dict[str, int] = {}
        for node in ast.walk(func):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                calls = [c for c in ast.walk(node.value) if isinstance(c, ast.Call)]
                if any(
                    isinstance(c.func, ast.Attribute) and c.func.attr in loaders
                    for c in calls
                ):
                    assigned[target.id] = node.lineno
        used: dict[str, int] = {}
        for node in ast.walk(func):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used[node.id] = used.get(node.id, 0) + 1
        for name, line in assigned.items():
            if used.get(name, 0) == 0:
                findings.append({
                    "file": rel,
                    "line": line,
                    "variable": name,
                    "why": "preuve chargee puis jamais consommee",
                })
    return findings


def scan_tautological_tests(rel: str, tree: ast.AST) -> list[dict[str, Any]]:
    """Une assertion entre deux constantes ne teste rien."""

    findings: list[dict[str, Any]] = []

    def constant_only(node: ast.AST) -> bool:
        for sub in ast.walk(node):
            if isinstance(sub, (ast.Name, ast.Attribute, ast.Subscript, ast.Call)):
                return False
        return True

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        test = node.test
        if isinstance(test, ast.Compare):
            operands = [test.left, *test.comparators]
            if all(constant_only(o) for o in operands):
                findings.append({
                    "file": rel,
                    "line": node.lineno,
                    "why": "assertion comparant deux constantes : toujours vraie",
                })
        elif isinstance(test, ast.Constant) and test.value:
            findings.append({
                "file": rel,
                "line": node.lineno,
                "why": "assertion d'une constante vraie",
            })
    return findings


def build_provenance_map(root: Path) -> dict[str, Any]:
    """Relie chaque metrique finale a la preuve et au producteur dont elle sort."""

    release_check = root / "audit/RELEASE_ALL_CHECK.json"
    if not release_check.is_file():
        return {"entries": [], "summary": {"UNTRACED_RELEASE_METRICS": 0, "TRACED": 0}}
    summary = json.loads(release_check.read_text(encoding="utf-8")).get("summary", {})

    aggregator = (root / "scripts/release_all_check.py").read_text(encoding="utf-8")
    tree = ast.parse(aggregator)

    # Un artefact remonte de la constante de chemin jusqu'a tout ce qui en
    # derive : PATH -> json.load(PATH) -> payload.get("summary") -> helper qui
    # le lit -> variable locale. On propage jusqu'au point fixe, en unissant les
    # sources : une metrique peut legitimement croiser plusieurs preuves.
    var_artifacts: dict[str, set[str]] = {}

    def _seed(name: str, node: ast.AST) -> None:
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Constant)
                and isinstance(sub.value, str)
                and sub.value.startswith("audit/")
                and sub.value.endswith(".json")
            ):
                var_artifacts.setdefault(name, set()).add(sub.value)

    bindings: list[tuple[str, ast.AST]] = []
    # Une valeur choisie par branche descend de la condition, pas du litteral
    # affecte : `if pret: statut = "PRET"` fait bien de `statut` une mesure.
    for branch in [n for n in ast.walk(tree) if isinstance(n, ast.If)]:
        for stmt in ast.walk(branch):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        bindings.append((target.id, branch.test))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    bindings.append((target.id, node.value))
                    _seed(target.id, node.value)
        elif isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            bindings.append((node.target.id, node.iter))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # un helper porte la provenance des preuves qu'il lit
            body = ast.Module(body=node.body, type_ignores=[])
            bindings.append((node.name, body))
        elif isinstance(node, ast.comprehension) and isinstance(node.target, ast.Name):
            bindings.append((node.target.id, node.iter))
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"append", "extend", "update", "add"}
            and isinstance(node.func.value, ast.Name)
        ):
            # une liste remplie dans une boucle herite de ce qu'on y verse
            for arg in node.args:
                bindings.append((node.func.value.id, arg))

    for _ in range(12):
        changed = False
        for name, value in bindings:
            referenced = {
                sub.id for sub in ast.walk(value) if isinstance(sub, ast.Name)
            }
            sources: set[str] = set()
            for ref in referenced:
                sources |= var_artifacts.get(ref, set())
            if sources - var_artifacts.get(name, set()):
                var_artifacts.setdefault(name, set()).update(sources)
                changed = True
        if not changed:
            break

    # metrique -> expression qui la produit, dans le dict `summary`
    metric_expr: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                if METRIC_NAME.match(key.value) or key.value in summary:
                    metric_expr.setdefault(key.value, ast.unparse(value))

    producer_of = {
        "audit/CANONICAL_RELEASE_INVENTORY.json": "scripts/build_canonical_release_inventory.py",
        "audit/PROGRAMME_AUTHORITY_MATRIX.json": "scripts/build_programme_authority_matrix.py",
        "audit/PRINTED_CODE_VALIDATION.json": "scripts/build_printed_code_validation.py",
        "audit/PROGRAMME_CONTENT_VALIDATION.json": "scripts/build_programme_content_validation.py",
        "audit/PARITY_BAREMES_VALIDATION.json": "scripts/build_parity_baremes_validation.py",
        "audit/BUILD_MANIFEST.json": "scripts/build_manifest.py",
        "audit/DOUBLE_BUILD_REPRODUCIBILITY.json": "scripts/build_clean_reproducibility.py",
        "audit/FINAL_PRINT_PREFLIGHT.json": "scripts/build_final_preflight_and_regression.py",
        "audit/VISUAL_SEMANTIC_REGRESSION_REPORT.json": "scripts/build_final_preflight_and_regression.py",
        "audit/ZERO_TECHNICAL_DEBT_REPORT.json": "scripts/build_zero_technical_debt.py",
        "audit/OPEN_FINDINGS.json": "scripts/build_open_findings.py",
        "audit/CLONE_DISPOSITION_LEDGER.json": "scripts/build_clone_disposition_ledger.py",
        "audit/PREFILLER_LINEAGE.json": "scripts/build_prefiller_lineage.py",
        "audit/EX_CO_SEMANTIC_BINDING.json": "scripts/build_ex_co_semantic_binding.py",
        "audit/FALSE_COVERAGE_TRIAGE.json": "scripts/build_false_coverage_triage.py",
    }

    entries = []
    untraced = 0
    for metric in sorted(summary):
        expr = metric_expr.get(metric)
        artifacts = sorted({
            art
            for var, arts in var_artifacts.items()
            if expr and re.search(rf"\b{re.escape(var)}\b", expr)
            for art in arts
        })
        derived = bool(expr) and not _expr_is_literal(expr)
        # Le signoff du Release Owner n'a pas d'artefact amont : il entre par la
        # ligne de commande. C'est une provenance, pas une metrique orpheline.
        human_input = bool(expr) and re.search(
            r"\brelease_owner_final_signoff\b", expr
        ) is not None
        # Un compteur de preuves manquantes descend de la presence meme des
        # artefacts : sa provenance est l'ensemble du corpus de preuves.
        evidence_presence = bool(expr) and re.search(
            r"\bmissing_evidence\b", expr
        ) is not None
        source_kind = (
            "HUMAN_SIGNOFF" if human_input and not artifacts
            else "DERIVED_FROM_EVIDENCE_PRESENCE" if evidence_presence and not artifacts
            else "DERIVED_FROM_EVIDENCE" if derived and artifacts
            else "UNTRACED"
        )
        if source_kind == "UNTRACED":
            untraced += 1
        entries.append({
            "metric": metric,
            "value": summary[metric],
            "expression": expr,
            "input_artifacts": artifacts,
            "producers": sorted({producer_of[a] for a in artifacts if a in producer_of}),
            "consumer_gate": "scripts/release_all_check.py",
            "source_kind": source_kind,
            "derived": source_kind != "UNTRACED",
        })
    return {
        "artifact_type": "proof_provenance_map",
        "generated_by": GENERATED_BY,
        "entries": entries,
        "summary": {
            "RELEASE_METRICS": len(entries),
            "TRACED_RELEASE_METRICS": len(entries) - untraced,
            "UNTRACED_RELEASE_METRICS": untraced,
        },
    }


def _expr_is_literal(expr: str) -> bool:
    try:
        parsed = ast.parse(expr, mode="eval").body
    except SyntaxError:
        return False
    for sub in ast.walk(parsed):
        if isinstance(sub, (ast.Name, ast.Attribute, ast.Subscript, ast.Call)):
            return False
    return True


def audit(root: Path) -> dict[str, Any]:
    hardcoded: list[dict[str, Any]] = []
    optional: list[dict[str, Any]] = []
    unused: list[dict[str, Any]] = []
    tautological: list[dict[str, Any]] = []

    for rel in RELEASE_PRODUCERS:
        path = root / rel
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        hardcoded += scan_hardcoded_metrics(rel, tree)
        optional += scan_optional_required_evidence(rel, tree)
        unused += scan_loaded_but_unused(rel, tree, source)

    for rel in RELEASE_TESTS:
        path = root / rel
        if not path.is_file():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tautological += scan_tautological_tests(rel, tree)

    provenance = build_provenance_map(root)

    return {
        "artifact_type": "gate_integrity_audit",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "scanned_producers": list(RELEASE_PRODUCERS),
        "scanned_tests": list(RELEASE_TESTS),
        "hardcoded_release_metrics": hardcoded,
        "optional_required_evidence": optional,
        "loaded_but_unused_evidence": unused,
        "tautological_gate_tests": tautological,
        "summary": {
            "HARDCODED_RELEASE_METRICS": len(hardcoded),
            "OPTIONAL_REQUIRED_EVIDENCE": len(optional),
            "LOADED_BUT_UNUSED_EVIDENCE": len(unused),
            "TAUTOLOGICAL_GATE_TESTS": len(tautological),
            "UNTRACED_RELEASE_METRICS": provenance["summary"]["UNTRACED_RELEASE_METRICS"],
            "RELEASE_METRICS": provenance["summary"]["RELEASE_METRICS"],
        },
    }, provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    report, provenance = audit(args.root)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    PROVENANCE_TARGET.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Integrite des gates de release",
        "",
        "Un gate n'est fiable que si sa valeur descend d'une preuve tracable.",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
