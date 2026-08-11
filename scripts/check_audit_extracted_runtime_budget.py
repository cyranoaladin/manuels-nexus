#!/usr/bin/env python3
"""Measure the portable extracted-source audit command budget on source_clean."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import inspect
import os
import signal
import subprocess
import tempfile
import time
from types import FunctionType


from scripts._qa_common import ROOT
from scripts.archive_security import safe_extract_tar


@dataclass
class MeasuredCommand:
    command: str
    seconds: float
    returncode: int


@dataclass
class RuntimeBudgetResult:
    errors: list[str] = field(default_factory=list)
    commands: list[MeasuredCommand] = field(default_factory=list)
    total_seconds: float = 0.0
    mode: str = ""


def make_target_commands(root: Path, target: str) -> list[str]:
    makefile = (root / "Makefile").read_text(encoding="utf-8")
    lines = makefile.splitlines()
    commands: list[str] = []
    in_target = False
    for line in lines:
        if line.startswith(f"{target}:"):
            in_target = True
            continue
        if in_target and line and not line.startswith("\t") and not line.startswith(" "):
            break
        if in_target and line.startswith("\t"):
            command = line.strip()
            if command and not command.startswith("@"):
                commands.append(command)
    return commands


def audit_extracted_commands(root: Path = ROOT) -> list[str]:
    local_commands = make_target_commands(root, "audit-extracted-source-local")
    if local_commands:
        return local_commands
    return make_target_commands(root, "audit-extracted-source")


def run_command(command: str, root: Path, timeout_seconds: int = 120) -> MeasuredCommand:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("NSI_DOCUMENTS_DRIVE_ROOT", None)
    start = time.monotonic()
    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            command,
            cwd=root,
            env=env,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        stdout, _ = process.communicate(timeout=timeout_seconds)
        returncode = process.returncode
    except subprocess.TimeoutExpired:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=3)
            except Exception:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except Exception as kill_error:
                    _kill_failed = str(kill_error)
        return MeasuredCommand(command, timeout_seconds, 124)
    seconds = time.monotonic() - start
    return MeasuredCommand(command, seconds, returncode)


def evaluate_runtime_budget(
    commands: list[MeasuredCommand],
    total_budget: float = 180.0,
    slow_threshold: float = 10.0,
) -> RuntimeBudgetResult:
    result = RuntimeBudgetResult(commands=commands, total_seconds=sum(item.seconds for item in commands))
    if result.total_seconds > total_budget:
        result.errors.append(f"durée totale {result.total_seconds:.2f}s > budget {total_budget:.0f}s")
    for item in commands:
        if item.returncode != 0:
            result.errors.append(f"commande en échec ({item.returncode}) -> {item.command}")
        if item.seconds > slow_threshold:
            result.errors.append(f"commande lente > {slow_threshold:.0f}s: {item.seconds:.2f}s -> {item.command}")
    return result


def extract_source_clean(root: Path = ROOT) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    archive = root / "dist" / "source_clean.tar.gz"
    if not archive.exists():
        raise FileNotFoundError(f"{archive.relative_to(root).as_posix()} absent")
    temp = tempfile.TemporaryDirectory()
    temp_path = Path(temp.name)
    safe_extract_tar(archive, temp_path)
    extracted = temp_path / "nsi-enseignement"
    if not extracted.exists():
        candidates = [path for path in temp_path.iterdir() if path.is_dir()]
        if len(candidates) == 1:
            extracted = candidates[0]
    if not extracted.exists():
        temp.cleanup()
        raise FileNotFoundError("racine nsi-enseignement absente de source_clean.tar.gz")
    return temp, extracted


def source_clean_root(root: Path = ROOT) -> bool:
    return (root / "Makefile").exists() and not (root / ".git").exists()


def measured_root(root: Path = ROOT) -> tuple[str, tempfile.TemporaryDirectory[str] | None, Path]:
    archive = root / "dist" / "source_clean.tar.gz"
    if archive.exists():
        temp, extracted = extract_source_clean(root)
        return "repository_archive", temp, extracted
    if source_clean_root(root):
        return "source_clean_extracted", None, root
    if (root / "Makefile").exists():
        return "source_tree_without_archive", None, root
    raise FileNotFoundError("ni dist/source_clean.tar.gz ni Makefile de source propre")


def analyze_audit_extracted_runtime_budget(root: Path = ROOT) -> RuntimeBudgetResult:
    start_total = time.monotonic()
    try:
        mode, temp, audit_root = measured_root(root)
    except Exception as exc:
        return RuntimeBudgetResult(errors=[str(exc)])
    try:
        commands = audit_extracted_commands(audit_root)
        measured = [run_command(command, audit_root, timeout_seconds=180) for command in commands]
        result = evaluate_runtime_budget(measured)
        result.mode = mode
        result.total_seconds = time.monotonic() - start_total
        if any(path.name == "__pycache__" for path in audit_root.rglob("__pycache__")):
            result.errors.append("archive extraite salie par __pycache__")
        return result
    finally:
        if temp is not None:
            temp.cleanup()


def uses_source_archive_extraction(func: FunctionType) -> bool:
    source = inspect.getsource(func)
    return "extract_source_clean" in source or "measured_root" in source or "source_clean.tar.gz" in source


def main() -> int:
    result = analyze_audit_extracted_runtime_budget()
    print(f"mode={result.mode or 'unknown'}", flush=True)
    print("Durées audit-extracted-source:")
    for item in result.commands:
        print(f"- {item.seconds:.2f}s rc={item.returncode} :: {item.command}", flush=True)
    print(f"Durée totale audit-extracted-source: {result.total_seconds:.2f}s", flush=True)
    if result.errors:
        print("check_audit_extracted_runtime_budget: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print("check_audit_extracted_runtime_budget: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
