#!/usr/bin/env python3
"""Check that first-batch TP Python assets are pedagogically meaningful."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
import ast
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unicodedata

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES


@dataclass
class TpPedagogyResult:
    errors: list[str] = field(default_factory=list)
    prefix_durations: dict[str, float] = field(default_factory=dict)


PREFIX_TIMEOUT_SECONDS = 20.0
TOTAL_TIMEOUT_SECONDS = 60.0


def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text.lower())
    text = re.sub(r"['\"][^'\"]{8,}['\"]", "'CONST'", text)
    return text.strip()


def code_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()


def find_code_dir(root: Path, prefix: str) -> Path:
    base = root / "03_progressions" / "supports"
    search_root = base if base.exists() else root
    matches = sorted(path for path in search_root.rglob(prefix) if path.is_dir())
    return (matches[0] / "code") if matches else search_root / prefix / "code"


def first_asset(code_dir: Path, pattern: str) -> Path | None:
    matches = sorted(code_dir.glob(pattern))
    return matches[0] if matches else None


def hardcoded_returns(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            value = node.value
            if isinstance(value, ast.Constant):
                return True
            if isinstance(value, ast.Dict):
                constant_values = sum(isinstance(item, ast.Constant) for item in value.values if item is not None)
                if constant_values >= max(1, len(value.values) - 1):
                    return True
    return False


def test_function_names(text: str) -> set[str]:
    return set(re.findall(r"^def\s+(test_[A-Za-z0-9_]+)\s*\(", text, flags=re.M))


def call_arguments(text: str) -> set[str]:
    return set(re.findall(r"\w+\(([^()\n]+)\)", text))


BOUNDARY_NAME_MARKERS = {
    "frontiere",
    "vide",
    "impossible",
    "invalide",
    "absent",
    "inexistant",
    "nul",
    "negatif",
    "superieur",
    "strictement",
    "repete",
    "seconde",
    "suppression",
    "aucun resultat",
    "resultat vide",
    "boundary",
    "empty",
    "invalid",
    "missing",
    "negative",
    "zero",
}


def normalized_test_name(name: str) -> str:
    """Normalise un nom de test pour comparer les familles de cas limites."""
    decomposed = unicodedata.normalize("NFD", name.lower())
    without_accents = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return without_accents.replace("_", " ")


def has_boundary_name(test: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    name = normalized_test_name(test.name)
    return any(marker in name for marker in BOUNDARY_NAME_MARKERS)


def is_boundary_comparison(node: ast.Compare) -> bool:
    """Reconnaît les résultats bornes usuels : None, liste vide ou zéro."""
    values = [node.left, *node.comparators]
    for value in values:
        if isinstance(value, ast.Constant) and value.value in (None, 0):
            return True
        if isinstance(value, ast.List) and not value.elts:
            return True
    return False


def is_pytest_raises(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "raises"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "pytest"
    )


def has_assertion_or_expected_exception(test: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        isinstance(node, ast.Assert)
        or isinstance(node, ast.Try)
        or (isinstance(node, ast.Call) and is_pytest_raises(node))
        for node in ast.walk(test)
    )


def has_boundary_case(text: str) -> bool:
    """Exige un scénario exécutable, pas une simple mention dans un commentaire.

    Une fonction ``test_*`` est reconnue si elle porte un nom de famille limite
    et contient une assertion ou une exception attendue, ou si une assertion
    compare directement le résultat à ``None``, ``[]`` ou ``0``.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test_"):
            continue
        if not has_assertion_or_expected_exception(node):
            continue
        if has_boundary_name(node):
            return True
        if any(
            isinstance(candidate, ast.Assert)
            and isinstance(candidate.test, ast.Compare)
            and is_boundary_comparison(candidate.test)
            for candidate in ast.walk(node)
        ):
            return True
    return False


def tests_are_substantive(text: str) -> list[str]:
    errors: list[str] = []
    tests = test_function_names(text)
    if len(tests) < 3:
        errors.append("tests insuffisants: moins de 3 fonctions test")
    lowered = text.lower()
    if "none" not in lowered and "valueerror" not in lowered and "invalid" not in lowered:
        errors.append("tests insuffisants: entrée invalide absente")
    if not has_boundary_case(text):
        errors.append("tests insuffisants: cas limite absent")
    if len(call_arguments(text)) < 3:
        errors.append("tests insuffisants: moins de 3 entrées distinctes")
    if re.search(r"assert\s+[^=\n]+==\s*['\"][^'\"]+['\"]", text) and len(tests) < 3:
        errors.append("tests insuffisants: validation de constante textuelle")
    return errors


def cleanup_repo_caches(root: Path = ROOT) -> None:
    for cache in root.rglob("__pycache__"):
        if cache.is_dir():
            shutil.rmtree(cache)


def run_tests(code_dir: Path, tests: Path, module_name: str, timeout_seconds: float = 5.0) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env["TP_MODULE"] = module_name
    process = subprocess.Popen(
        [sys.executable, str(tests.name)],
        cwd=code_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, _ = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            process.poll()
        stdout, _ = process.communicate()
        raise subprocess.TimeoutExpired(process.args, timeout_seconds, output=stdout) from exc
    return subprocess.CompletedProcess(process.args, process.returncode, stdout, None)


def analyze_prefix(root: Path, prefix: str, prefix_timeout_seconds: float = PREFIX_TIMEOUT_SECONDS) -> tuple[list[str], float]:
    started = time.monotonic()
    errors: list[str] = []
    code_dir = find_code_dir(root, prefix)
    starter = first_asset(code_dir, f"{prefix}_starter*.py")
    tests = first_asset(code_dir, f"{prefix}_tests_attendus*.py")
    corrige = first_asset(code_dir, f"{prefix}_corrige_professeur*.py")
    if not starter or not tests or not corrige:
        return [f"{prefix}: assets TP incomplets"], time.monotonic() - started

    starter_text = starter.read_text(encoding="utf-8", errors="replace")
    corrige_text = corrige.read_text(encoding="utf-8", errors="replace")
    tests_text = tests.read_text(encoding="utf-8", errors="replace")

    if hardcoded_returns(starter):
        errors.append(f"{starter}: starter hardcodé ou solution complète")
    if code_similarity(starter_text, corrige_text) >= 0.82:
        errors.append(f"{prefix}: corrigé professeur quasi identique au starter")
    errors.extend(f"{tests}: {error}" for error in tests_are_substantive(tests_text))

    with tempfile.TemporaryDirectory() as raw:
        temp_code = Path(raw)
        for path in [starter, tests, corrige]:
            shutil.copy2(path, temp_code / path.name)
        corrige_module = corrige.stem
        starter_module = starter.stem
        try:
            corrige_run = run_tests(temp_code, temp_code / tests.name, corrige_module)
            if corrige_run.returncode != 0:
                errors.append(f"{prefix}: les tests attendus échouent sur le corrigé professeur")
        except subprocess.TimeoutExpired:
            errors.append(f"{prefix}: timeout des tests sur le corrigé professeur")
        try:
            starter_run = run_tests(temp_code, temp_code / tests.name, starter_module)
            if starter_run.returncode == 0:
                errors.append(f"{prefix}: le starter valide les tests complets")
        except subprocess.TimeoutExpired:
            errors.append(f"{prefix}: timeout des tests sur le starter")
        for cache in temp_code.rglob("__pycache__"):
            shutil.rmtree(cache)
    duration = time.monotonic() - started
    if duration > prefix_timeout_seconds:
        errors.append(f"{prefix}: durée préfixe trop longue ({duration:.2f}s > {prefix_timeout_seconds:.2f}s)")
    return errors, duration


def analyze_tp_pedagogy(
    root: Path = ROOT,
    prefixes: list[str] | None = None,
    prefix_timeout_seconds: float = PREFIX_TIMEOUT_SECONDS,
    total_timeout_seconds: float = TOTAL_TIMEOUT_SECONDS,
) -> TpPedagogyResult:
    prefixes = prefixes or FIRST_BATCH_PREFIXES
    result = TpPedagogyResult()
    started = time.monotonic()
    try:
        for prefix in prefixes:
            print(f"check_tp_pedagogical_assets: préfixe {prefix}", flush=True)
            errors, duration = analyze_prefix(root, prefix, prefix_timeout_seconds)
            result.prefix_durations[prefix] = duration
            result.errors.extend(errors)
            elapsed = time.monotonic() - started
            if elapsed > total_timeout_seconds:
                result.errors.append(f"durée totale trop longue ({elapsed:.2f}s > {total_timeout_seconds:.2f}s)")
                break
        total = time.monotonic() - started
        if total > total_timeout_seconds and not any("durée totale" in error for error in result.errors):
            result.errors.append(f"durée totale trop longue ({total:.2f}s > {total_timeout_seconds:.2f}s)")
        return result
    finally:
        cleanup_repo_caches(root)


def main() -> int:
    result = analyze_tp_pedagogy()
    if result.errors:
        print("check_tp_pedagogical_assets: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    slow = {prefix: duration for prefix, duration in result.prefix_durations.items() if duration > 5.0}
    if slow:
        print("Préfixes TP lents:")
        for prefix, duration in sorted(slow.items()):
            print(f"- {prefix}: {duration:.2f}s")
    print("check_tp_pedagogical_assets: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
