#!/usr/bin/env python3
"""Périmètre de test de la release 1SPE : une preuve de portée, pas une exception.

Ce producteur ne désactive rien, ne marque rien `skip`, ne touche pas à pytest.
Il DÉRIVE l'ensemble des tests qu'une release limitée au manuel 1SPE doit voir
verts, et il le dérive de preuves, jamais de noms de fichiers.

Le raisonnement va dans le sens qui ne peut pas rétrécir le périmètre par
accident : **un test appartient au périmètre 1SPE sauf s'il existe une preuve
positive qu'il est exclusivement 1NSI.**

Trois surfaces sont calculées :

* `SHARED_RUNTIME_USED_BY_1SPE` — ce que la construction 1SPE consomme
  réellement. Côté LaTeX, la liste est LUE dans les `.fls` des deux variantes :
  c'est le moteur lui-même qui dit quels fichiers il a ouverts. Côté Python,
  c'est la fermeture transitive des imports des producteurs et des gates du
  manuel, à partir de racines déclarées.

* `SURFACE_1SPE` — sources, artefacts et PDF du manuel 1SPE.

* la surface de chaque module de test — ses imports de premier rang et les
  chemins du dépôt qu'il désigne, extraits de son AST (`ROOT / "a" / "b"` et
  littéraux résolus).

Un module de test est `MANUAL_1NSI_EXCLUSIVE` si, et seulement si, sa surface
est non vide et n'intersecte ni `SURFACE_1SPE` ni `SHARED_RUNTIME_USED_BY_1SPE`,
et qu'elle touche au moins un chemin propre à NSI. Tout le reste est dans le
périmètre.

Les résultats ne sont jamais devinés : ils sont lus dans des captures pytest
réelles passées en entrée.

Métriques bloquantes : `FAILURES_TOUCHING_1SPE`,
`FAILURES_TOUCHING_SHARED_RUNTIME_USED_BY_1SPE`, `UNKNOWN_SCOPE`.
`GLOBAL_SUPPORTED_SUITE_STATUS` est rapporté tel qu'il est, et n'est jamais
appelé `GREEN` s'il est rouge.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_RELEASE_TEST_GATE.json"
MD_TARGET = ROOT / "audit/1SPE_RELEASE_TEST_GATE.md"
GENERATED_BY = "scripts/build_1spe_release_test_gate.py"

TESTPATHS = (
    Path("Mathematiques/manuel-maths/tests"),
    Path("NSI/tests"),
    Path("tests"),
)

# Racines Python de la construction et des gates du manuel. La fermeture
# transitive de leurs imports EST le runtime partagé côté Python : ce sont les
# modules dont une régression casserait la fabrication ou la preuve du 1SPE.
PYTHON_ROOTS = (
    Path("Mathematiques/manuel-maths/scripts/assemble_manuel.py"),
    Path("Mathematiques/manuel-maths/scripts/assemble_livrets.py"),
    Path("Mathematiques/manuel-maths/scripts/margin_ledger.py"),
    Path("Mathematiques/manuel-maths/scripts/margin_contract.py"),
    Path("Mathematiques/manuel-maths/scripts/pdf_integrity.py"),
    Path("Mathematiques/manuel-maths/scripts/pdf_reproducibility.py"),
    Path("Mathematiques/manuel-maths/scripts/check_latex.py"),
    Path("scripts/build_1spe_pagination_baseline_ratification.py"),
    Path("scripts/build_d7_proof_bundle.py"),
    Path("scripts/manual_source_surface.py"),
)

FLS_FILES = (
    Path("Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.fls"),
    Path("Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.fls"),
)

# Un chemin est propre à NSI s'il vit sous NSI/, ou s'il nomme un manuel NSI.
NSI_MARKERS = ("1NSI", "TNSI", "nsi")

SUMMARY_RE = re.compile(r"(?:(?P<failed>\d+) failed[,\s]+)?(?P<passed>\d+) passed")


class GateError(RuntimeError):
    """Une preuve manque, ou une portée reste inconnue."""


def _reject(message: str) -> None:
    raise GateError(message)


def tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        _reject("git ls-files a échoué : la portée ne peut pas être prouvée")
    return set(result.stdout.split())


# ---------------------------------------------------------------------------
#  Surface d'un module Python : ses imports et les chemins qu'il désigne
# ---------------------------------------------------------------------------


def _path_chain(node: ast.AST) -> list[str] | None:
    """Reconstruit `ROOT / "a" / "b/c"` en ["a", "b/c"]."""

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _path_chain(node.left)
        if left is None:
            return None
        if isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
            return left + [node.right.value]
        return None
    if isinstance(node, ast.Name):
        return []
    if isinstance(node, ast.Attribute):
        return []
    if isinstance(node, ast.Call):
        return []
    return None


def module_surface(path: Path, tracked: set[str]) -> dict[str, Any]:
    """Les chemins du dépôt que ce module désigne, plus ses imports."""

    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError as error:  # pragma: no cover - source cassée
        _reject(f"{relative(path)} n'est pas analysable : {error}")

    designated: set[str] = set()
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            chain = _path_chain(node)
            if chain:
                candidate = "/".join(chain).lstrip("./")
                if candidate in tracked:
                    designated.add(candidate)
                else:
                    # Un préfixe connu suffit : `ROOT / "audit" / "reviews"`
                    # désigne un répertoire suivi, pas un fichier.
                    for entry in tracked:
                        if entry.startswith(candidate.rstrip("/") + "/"):
                            designated.add(candidate.rstrip("/"))
                            break
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value.strip().lstrip("./")
            if "/" in value and value in tracked:
                designated.add(value)

    # Un import de premier rang qui correspond à un module suivi du dépôt est
    # lui aussi une dépendance de surface.
    for name in sorted(imports):
        for directory in ("scripts", "Mathematiques/manuel-maths/scripts", "NSI/scripts"):
            candidate = f"{directory}/{name}.py"
            if candidate in tracked:
                designated.add(candidate)
    return {"designated_paths": sorted(designated), "imports": sorted(imports)}


def python_import_closure(roots: Iterable[Path], tracked: set[str]) -> set[str]:
    """Fermeture transitive des imports de premier rang, dans le dépôt."""

    pending = [relative(ROOT / root) for root in roots if (ROOT / root).is_file()]
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        surface = module_surface(ROOT / current, tracked)
        for candidate in surface["designated_paths"]:
            if not candidate.endswith(".py") or candidate in seen:
                continue
            # Un test n'est pas un composant du runtime : il l'exerce.
            if "/tests/" in candidate or candidate.startswith("tests/"):
                continue
            pending.append(candidate)
    return seen


# ---------------------------------------------------------------------------
#  Runtime partagé réellement consommé par la construction 1SPE
# ---------------------------------------------------------------------------


def fls_inputs(tracked: set[str]) -> dict[str, list[str]]:
    """Ce que le moteur a OUVERT, lu dans les `.fls` des deux variantes."""

    per_file: dict[str, list[str]] = {}
    for fls in FLS_FILES:
        path = ROOT / fls
        if not path.is_file():
            _reject(
                f"{relative(path)} absent : la portée LaTeX ne peut pas être "
                "prouvée sans la trace d'ouverture du moteur"
            )
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        # Le `.fls` declare lui-meme le repertoire depuis lequel le moteur a
        # tourne : c'est la seule base correcte pour ses chemins relatifs. Le
        # supposer egal au repertoire de sortie donnait des chemins qui
        # n'existent pas, et donc un runtime partage VIDE cote LaTeX.
        working = ROOT
        for line in lines:
            if line.startswith("PWD "):
                working = Path(line[len("PWD ") :].strip())
                break
        found: set[str] = set()
        for line in lines:
            if not line.startswith("INPUT "):
                continue
            raw = line[len("INPUT ") :].strip()
            resolved = Path(raw) if raw.startswith("/") else (working / raw)
            try:
                candidate = resolved.resolve().relative_to(ROOT).as_posix()
            except (ValueError, OSError):
                continue  # fichier de la distribution TeX, hors depot
            if candidate in tracked:
                found.add(candidate)
        if not found:
            _reject(
                f"{relative(path)} ne designe aucun fichier suivi du depot : "
                "la portee LaTeX serait vide, ce qui est faux"
            )
        per_file[relative(path)] = sorted(found)
    return per_file


def is_1spe_path(candidate: str) -> bool:
    if "1SPE" in candidate:
        return True
    return candidate.startswith("Mathematiques/manuel-maths/transversal/")


def is_nsi_path(candidate: str) -> bool:
    if candidate.startswith("NSI/"):
        return True
    upper = candidate.upper()
    return any(marker.upper() in upper for marker in ("1NSI", "TNSI"))


def build_scopes(tracked: set[str]) -> dict[str, Any]:
    latex_inputs = fls_inputs(tracked)
    latex_shared = {
        candidate
        for entries in latex_inputs.values()
        for candidate in entries
        if not is_1spe_path(candidate)
        and not candidate.startswith("Mathematiques/manuel-maths/chapitres/")
    }
    python_shared = python_import_closure(PYTHON_ROOTS, tracked)
    surface_1spe = {candidate for candidate in tracked if is_1spe_path(candidate)}
    return {
        "latex_inputs_per_variant": latex_inputs,
        "SHARED_RUNTIME_USED_BY_1SPE": sorted(latex_shared | python_shared),
        "shared_runtime_latex": sorted(latex_shared),
        "shared_runtime_python": sorted(python_shared),
        "SURFACE_1SPE_size": len(surface_1spe),
        "_surface_1spe": surface_1spe,
        "_shared": latex_shared | python_shared,
    }


# ---------------------------------------------------------------------------
#  Classement des modules de test
# ---------------------------------------------------------------------------


def test_modules() -> list[Path]:
    modules: list[Path] = []
    for directory in TESTPATHS:
        base = ROOT / directory
        if not base.is_dir():
            _reject(f"testpath absent : {directory}")
        modules.extend(sorted(base.glob("test_*.py")))
    return modules


# Filet de securite textuel : un module qui NOMME le manuel 1SPE ou son arbre
# reste dans le perimetre, meme si son AST ne designe aucun chemin suivi --
# une collecte par glob echappe a l'analyse statique, pas a ces mots.
MENTIONS_1SPE = re.compile(r"1SPE|MANUEL_1SPE|manuel-maths|Mathematiques")


def classify(path: Path, scopes: dict[str, Any], tracked: set[str]) -> dict[str, Any]:
    surface = module_surface(path, tracked)
    mentions_1spe = bool(MENTIONS_1SPE.search(path.read_text(encoding="utf-8", errors="replace")))
    designated = set(surface["designated_paths"])
    touches_1spe = sorted(designated & scopes["_surface_1spe"])
    touches_shared = sorted(designated & scopes["_shared"])
    touches_nsi = sorted(
        candidate for candidate in designated if is_nsi_path(candidate)
    )

    # Un module de test qui vit sous le manuel de mathematiques ne peut pas
    # etre exclusivement 1NSI, quoi qu'il designe par ailleurs.
    lives_under_maths = relative(path).startswith("Mathematiques/")
    if touches_1spe or touches_shared or lives_under_maths or mentions_1spe:
        scope = "IN_1SPE_RELEASE_SCOPE"
        if touches_1spe or touches_shared:
            reason = "designates 1SPE surface or shared runtime consumed by 1SPE"
        elif lives_under_maths:
            reason = "lives under the mathematics manual"
        else:
            reason = "names the 1SPE manual or its tree in its own source"
    elif touches_nsi:
        scope = "MANUAL_1NSI_EXCLUSIVE"
        reason = (
            "designates NSI paths only, and none of them is consumed by the "
            "1SPE build or its gates"
        )
    else:
        # Aucune preuve d'exclusivité 1NSI : le module reste dans le périmètre.
        # Le sens du doute est délibéré — un périmètre de release ne doit pas
        # rétrécir faute de preuve.
        scope = "IN_1SPE_RELEASE_SCOPE"
        reason = "no positive evidence of 1NSI exclusivity"
    return {
        "module": relative(path),
        "scope": scope,
        "reason": reason,
        "designated_1spe_paths": touches_1spe[:12],
        "designated_shared_paths": touches_shared[:12],
        "designated_nsi_paths": touches_nsi[:12],
        "designated_path_count": len(designated),
        "mentions_1spe_in_source": mentions_1spe,
    }


# ---------------------------------------------------------------------------
#  Lecture des captures pytest
# ---------------------------------------------------------------------------


def _capture_label(path: Path) -> str:
    """Nom de la capture, meme si elle vit hors du depot (fixtures)."""

    try:
        return relative(path)
    except ValueError:
        return path.as_posix()


def parse_capture(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    failed = sorted(
        {
            line[len("FAILED ") :].strip()
            for line in text.splitlines()
            if line.startswith("FAILED ")
        }
    )
    errored = sorted(
        {
            line[len("ERROR ") :].strip()
            for line in text.splitlines()
            if line.startswith("ERROR ")
        }
    )
    counts = {"passed": 0, "failed": 0}
    for match in SUMMARY_RE.finditer(text[-4000:]):
        counts["passed"] = int(match.group("passed"))
        counts["failed"] = int(match.group("failed") or 0)
    return {
        "capture": _capture_label(path),
        "failed_node_ids": failed,
        "error_node_ids": errored,
        **counts,
    }


def module_of(node_id: str) -> str:
    return node_id.split("::", 1)[0]


def build(global_capture: Path | None, gate_capture: Path | None) -> dict[str, Any]:
    tracked = tracked_paths()
    scopes = build_scopes(tracked)
    rows = [classify(path, scopes, tracked) for path in test_modules()]
    in_scope = {row["module"] for row in rows if row["scope"] == "IN_1SPE_RELEASE_SCOPE"}
    exclusive = {row["module"] for row in rows if row["scope"] == "MANUAL_1NSI_EXCLUSIVE"}
    unknown = [row for row in rows if row["scope"] not in {
        "IN_1SPE_RELEASE_SCOPE", "MANUAL_1NSI_EXCLUSIVE"
    }]

    payload: dict[str, Any] = {
        "artifact_type": "1spe_release_test_gate",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "source_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip(),
        "this_is_not_a_pytest_exception": (
            "aucun test n'est desactive, skippe ou xfail par cet artefact ; "
            "il nomme le perimetre qu'une release scopee 1SPE doit voir vert"
        ),
        "scope_direction": (
            "un module est dans le perimetre SAUF preuve positive d'exclusivite 1NSI"
        ),
        "shared_runtime_evidence": {
            "latex": "lignes INPUT des .fls des deux variantes 1SPE",
            "python": "fermeture transitive des imports des producteurs et gates 1SPE",
            "python_roots": [root.as_posix() for root in PYTHON_ROOTS],
        },
        "latex_inputs_per_variant": scopes["latex_inputs_per_variant"],
        "SHARED_RUNTIME_USED_BY_1SPE": scopes["SHARED_RUNTIME_USED_BY_1SPE"],
        "modules": rows,
        "gate_modules": sorted(in_scope),
        "out_of_gate_modules": sorted(exclusive),
        "summary": {
            "TEST_MODULES": len(rows),
            "GATE_MODULES": len(in_scope),
            "MANUAL_1NSI_EXCLUSIVE_MODULES": len(exclusive),
            "UNKNOWN_SCOPE": len(unknown),
            "SHARED_RUNTIME_USED_BY_1SPE_SIZE": len(
                scopes["SHARED_RUNTIME_USED_BY_1SPE"]
            ),
        },
    }

    if global_capture is not None:
        observed = parse_capture(global_capture)
        failures = observed["failed_node_ids"] + observed["error_node_ids"]
        touching_gate = sorted(
            node for node in failures if module_of(node) in in_scope
        )
        outside = sorted(node for node in failures if module_of(node) in exclusive)
        unattributed = sorted(
            node
            for node in failures
            if module_of(node) not in in_scope | exclusive
        )
        payload["global_supported_suite"] = {
            **observed,
            "GLOBAL_SUPPORTED_SUITE_STATUS": "GREEN" if not failures else "RED",
            "failures_in_1spe_release_scope": touching_gate,
            "failures_1nsi_exclusive": outside,
            "failures_of_unattributed_module": unattributed,
        }
        payload["summary"]["GLOBAL_SUPPORTED_SUITE_STATUS"] = (
            "GREEN" if not failures else "RED"
        )
        payload["summary"]["GLOBAL_FAILURES"] = len(failures)
        payload["summary"]["FAILURES_TOUCHING_1SPE"] = len(touching_gate)
        payload["summary"]["FAILURES_1NSI_EXCLUSIVE"] = len(outside)
        payload["summary"]["FAILURES_OF_UNATTRIBUTED_MODULE"] = len(unattributed)
        # Un échec 1NSI-exclusif ne peut, par construction du classement, ni
        # désigner la surface 1SPE ni le runtime partagé : c'est exactement ce
        # qui l'a rendu exclusif. On le REDIT ici comme une métrique, pour
        # qu'elle soit lisible et refutable.
        payload["summary"]["FAILURES_TOUCHING_SHARED_RUNTIME_USED_BY_1SPE"] = sum(
            1
            for row in rows
            if row["module"] in {module_of(node) for node in failures}
            and row["designated_shared_paths"]
        )

    if gate_capture is not None:
        observed = parse_capture(gate_capture)
        # Un verdict sans son reçu n'est pas rejouable : la commande, l'horaire,
        # l'état de l'arbre avant et après, et l'empreinte du journal disent
        # SUR QUOI ce PASS a été prononcé.
        metadata_path = gate_capture.with_name("run-meta.txt")
        if metadata_path.is_file():
            payload["gate_run_receipt"] = dict(
                line.split("=", 1)
                for line in metadata_path.read_text(encoding="utf-8").splitlines()
                if "=" in line
            )
        failures = observed["failed_node_ids"] + observed["error_node_ids"]
        payload["gate_run"] = {
            **observed,
            "1SPE_RELEASE_TEST_GATE": "PASS" if not failures else "FAIL",
        }
        payload["summary"]["1SPE_RELEASE_TEST_GATE"] = (
            "PASS" if not failures else "FAIL"
        )
        # Un registre de blocage lit des COMPTES : « PASS » est une chaîne, donc
        # vrai, donc un bloqueur ouvert. Le nombre d'échecs du périmètre est la
        # même information, sous la forme qu'une métrique bloquante attend.
        payload["summary"]["GATE_FAILURES"] = len(failures)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Périmètre de test de la release 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"SHA : `{payload['source_sha']}`",
        "",
        "> " + payload["this_is_not_a_pytest_exception"],
        "",
        "> " + payload["scope_direction"],
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in summary.items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Modules hors périmètre — exclusivité 1NSI prouvée",
        "",
        "| Module | Chemins NSI désignés |",
        "|---|---|",
    ]
    by_module = {row["module"]: row for row in payload["modules"]}
    for module in payload["out_of_gate_modules"]:
        row = by_module[module]
        lines.append(
            f"| `{module}` | {', '.join(f'`{p}`' for p in row['designated_nsi_paths'][:4])} |"
        )
    if "global_supported_suite" in payload:
        observed = payload["global_supported_suite"]
        lines += [
            "",
            "## Suite globale supportée",
            "",
            f"- capture : `{observed['capture']}`",
            f"- statut : **{observed['GLOBAL_SUPPORTED_SUITE_STATUS']}** "
            f"({observed['passed']} passés, {observed['failed']} échoués)",
            f"- échecs dans le périmètre 1SPE : "
            f"{len(observed['failures_in_1spe_release_scope'])}",
            f"- échecs 1NSI exclusifs : {len(observed['failures_1nsi_exclusive'])}",
            "",
        ]
        for node in observed["failures_1nsi_exclusive"]:
            lines.append(f"  - `{node}`")
    if "gate_run" in payload:
        observed = payload["gate_run"]
        lines += [
            "",
            "## Exécution du périmètre",
            "",
            f"- capture : `{observed['capture']}`",
            f"- `1SPE_RELEASE_TEST_GATE` : **{observed['1SPE_RELEASE_TEST_GATE']}** "
            f"({observed['passed']} passés, {observed['failed']} échoués)",
        ]
    lines += [
        "",
        "## Runtime partagé consommé par la construction 1SPE",
        "",
        f"{summary['SHARED_RUNTIME_USED_BY_1SPE_SIZE']} chemins, lus dans les "
        "`.fls` des deux variantes et dans la fermeture des imports.",
        "",
    ]
    for candidate in payload["SHARED_RUNTIME_USED_BY_1SPE"]:
        lines.append(f"- `{candidate}`")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--global-capture", type=Path, help="capture pytest de la suite complète"
    )
    parser.add_argument(
        "--gate-capture", type=Path, help="capture pytest du périmètre 1SPE"
    )
    parser.add_argument("--print-gate-args", action="store_true",
                        help="écrire les modules du périmètre, un par ligne")
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build(arguments.global_capture, arguments.gate_capture)
    except GateError as error:
        print(f"1SPE-RELEASE-TEST-GATE-ERROR: {error}", file=sys.stderr)
        return 2

    if arguments.print_gate_args:
        for module in payload["gate_modules"]:
            print(module)
        return 0

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {relative(JSON_TARGET)} et {relative(MD_TARGET)}")

    blocking = ["UNKNOWN_SCOPE", "FAILURES_TOUCHING_1SPE",
                "FAILURES_TOUCHING_SHARED_RUNTIME_USED_BY_1SPE"]
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"].get(name) for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
