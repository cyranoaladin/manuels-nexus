#!/usr/bin/env python3
"""Check executable or operational TP assets for the ready batch."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import py_compile
import tempfile

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES


@dataclass
class TpAssetsResult:
    errors: list[str] = field(default_factory=list)


def compile_file(path: Path) -> str | None:
    try:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / (path.stem + ".pyc")
            py_compile.compile(str(path), cfile=str(target), doraise=True)
    except Exception as exc:
        return f"{path}: Python invalide ({exc})"
    return None


def supports_root(root: Path) -> Path:
    candidate = root / "03_progressions" / "supports"
    return candidate if candidate.exists() else root


def prefix_directory(root: Path, prefix: str) -> Path:
    base = supports_root(root)
    matches = sorted(path for path in base.rglob(prefix) if path.is_dir())
    return matches[0] if matches else base / prefix


def analyze_tp_assets(root: Path = ROOT, prefixes: list[str] | None = None) -> TpAssetsResult:
    prefixes = prefixes or FIRST_BATCH_PREFIXES
    result = TpAssetsResult()
    for prefix in prefixes:
        directory = prefix_directory(root, prefix)
        code_dir = directory / "code"
        if not code_dir.exists():
            result.errors.append(f"{prefix}: dossier code absent")
            continue
        expected = {
            "starter": sorted(code_dir.glob(f"{prefix}_starter*.py")),
            "tests_attendus": sorted(code_dir.glob(f"{prefix}_tests_attendus*.py")),
            "corrige_professeur": sorted(code_dir.glob(f"{prefix}_corrige_professeur*.py")),
        }
        for label, paths in expected.items():
            if not paths:
                result.errors.append(f"{prefix}: asset {label} absent")
                continue
            text = paths[0].read_text(encoding="utf-8", errors="replace")
            if "TODO" in text or "pass  # à compléter" in text:
                result.errors.append(f"{paths[0]}: placeholder technique interdit")
            error = compile_file(paths[0])
            if error:
                result.errors.append(error)
    return result


def main() -> int:
    result = analyze_tp_assets()
    if result.errors:
        print("check_first_batch_tp_assets: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print("check_first_batch_tp_assets: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
