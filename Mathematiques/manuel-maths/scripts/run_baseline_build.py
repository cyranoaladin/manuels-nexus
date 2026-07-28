"""Construire un assemblage historique 1SPE et toujours produire son rapport."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
PAGE_RE = re.compile(r"Output written on .*?\((\d+) pages?", re.IGNORECASE)
BUILD_TIMEOUT_SECONDS = 15


def _matching_lines(text: str, pattern: str) -> list[str]:
    regex = re.compile(pattern, re.IGNORECASE)
    return list(dict.fromkeys(line.strip() for line in text.splitlines() if regex.search(line)))


def _page_count(text: str) -> int:
    matches = PAGE_RE.findall(text)
    return int(matches[-1]) if matches else 0


def run_build(
    root: Path,
    variant: str,
    report_path: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> int:
    """Exécuter l'assembleur et écrire le rapport, succès comme échec."""
    root = root.resolve()
    report_path = report_path if report_path.is_absolute() else root / report_path
    build = root / "build" / "MANUEL_1SPE"
    cache = build / ".texmf-var"
    cache.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_stem = build / f"MANUEL_1SPE_{variant}"
    for suffix in (".aux", ".log", ".out", ".pdf", ".toc"):
        artifact_stem.with_suffix(suffix).unlink(missing_ok=True)
    python = root / ".venv" / "bin" / "python"
    command = [
        str(python),
        "scripts/assemble_manuel.py",
        "--variant",
        variant,
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "TEXMFVAR": str(cache),
            "TEXMFCACHE": str(cache),
            "SOURCE_DATE_EPOCH": environment.get("SOURCE_DATE_EPOCH", "0"),
        }
    )
    fonts = root / "gabarits" / "fonts"
    if fonts.is_dir():
        environment["OSFONTDIR"] = str(fonts)

    process_returncode = 127
    stdout = ""
    stderr = ""
    invocation_error = ""
    try:
        process = runner(
            command,
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=BUILD_TIMEOUT_SECONDS,
        )
        process_returncode = process.returncode
        stdout = process.stdout or ""
        stderr = process.stderr or ""
    except subprocess.TimeoutExpired as error:
        invocation_error = f"TimeoutExpired: build exceeded {error.timeout} seconds"
        stdout = error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
    except (OSError, subprocess.SubprocessError) as error:
        invocation_error = f"{type(error).__name__}: {error}"
        stderr = invocation_error

    log_path = build / f"MANUEL_1SPE_{variant}.log"
    pdf_path = build / f"MANUEL_1SPE_{variant}.pdf"
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    diagnostics = "\n".join((stdout, stderr, log_text))
    pages = _page_count(diagnostics)
    errors = _matching_lines(diagnostics, r"^!|fatal error|emergency stop|undefined control sequence")
    if invocation_error:
        errors.insert(0, invocation_error)
    warnings = _matching_lines(diagnostics, r"warning")
    references = _matching_lines(
        diagnostics,
        r"undefined references?|reference .* undefined|citation .* undefined|rerun to get cross-references",
    )
    overflows = _matching_lines(diagnostics, r"(?:over|under)full \\[hv]box")
    succeeded = process_returncode == 0 and pdf_path.is_file()
    report = {
        "schema_version": 1,
        "variant": variant,
        "status": "succeeded" if succeeded else "failed",
        "exit_code": 0 if succeeded else 2,
        "process_returncode": process_returncode,
        "pages": pages,
        "errors": errors,
        "warnings": warnings,
        "references": references,
        "overflows": overflows,
        "command": command,
        "cwd": ".",
        "texmf_cache": cache.relative_to(root).as_posix(),
        "log_path": log_path.relative_to(root).as_posix(),
        "pdf_path": pdf_path.relative_to(root).as_posix(),
        "invocation_error": invocation_error,
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report["exit_code"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("eleve", "professeur"), required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    return run_build(ROOT, arguments.variant, arguments.report)


if __name__ == "__main__":
    sys.exit(main())
