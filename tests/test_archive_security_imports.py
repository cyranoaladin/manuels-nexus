from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_DIRS = (ROOT / "scripts", ROOT / "scrapping_NSI")
WRAPPER = ROOT / "scripts" / "archive_security.py"
CANONICAL_IMPL = ROOT / "scrapping_NSI" / "safe_archive.py"


_DATA_DIRS = {"ressources_nsi_extraites", "ressources_nsi_extraites_v2",
               "ressources_nsi_centralisees", "sqlite_data", ".venv"}


def _production_python_files() -> list[Path]:
    files: list[Path] = []
    for directory in PRODUCTION_DIRS:
        files.extend(
            path
            for path in directory.rglob("*.py")
            if path.is_file()
            and not path.name.startswith("test_")
            and not (_DATA_DIRS & set(path.parts))
        )
    return sorted(files)


def test_production_imports_archive_security_through_scripts_namespace() -> None:
    offenders: list[str] = []
    for path in _production_python_files():
        if path in {WRAPPER, CANONICAL_IMPL}:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module in {"archive_security", "scrapping_NSI.safe_archive"}:
                    offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}:{node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in {"archive_security", "scrapping_NSI.safe_archive"}:
                        offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}:{alias.name}")

    assert offenders == []


def test_scripts_package_exists_for_archive_security_imports() -> None:
    assert (ROOT / "scripts" / "__init__.py").is_file()


def test_no_direct_extractall_remains_in_production_code() -> None:
    offenders: list[str] = []
    for path in _production_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "extractall":
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")

    assert offenders == []


def test_run_audit_extracted_source_script_executes_without_import_error() -> None:
    completed = subprocess.run(
        [sys.executable, "-c", "import scripts.run_audit_extracted_source"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=10,
    )

    assert completed.returncode == 0, completed.stdout
